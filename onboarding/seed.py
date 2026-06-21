#!/usr/bin/env python3
"""
MADB first-run seeder — the activation wedge.

Problem it solves: a brand-new MADB install has an empty store, so the user's
first few sessions produce *nothing* on recall and they never hit the "wait, it
remembered?!" moment that makes MADB click. This plants a small, clearly-labelled
causal DAG (see onboarding/seed_memories.json) so session #1 already has something
to recall AND a lineage to walk with trace_cause.

Transport: speaks MCP JSON-RPC over **stdio** to the same server `claude mcp add
madb` registers — it launches `uvx madb-mcp-server` as a subprocess and talks to
it over stdin/stdout. No third-party deps — stdlib only.

Usage:
    python seed.py                 # plant the guided-tour DAG (idempotent)
    python seed.py --verify        # plant, then recall + trace_cause to show the aha
    python seed.py --clear         # forget every onboarding_demo record (clean store)
    MADB_MCP_CMD="python -m madb_mcp_server" python seed.py   # custom launch command

Idempotent: each memory carries a stable idempotency_key, so re-running does not
duplicate. The whole tour lives under tenant "onboarding-tour" and tag
"onboarding_demo" so it never mixes with the user's real memory.
"""
from __future__ import annotations

import argparse
import json
import os
import queue
import re
import shlex
import subprocess
import sys
import threading
from pathlib import Path

# Command that launches the MADB MCP server over stdio. Matches what
# `claude mcp add madb -- uvx madb-mcp-server` runs. Override with MADB_MCP_CMD.
MCP_CMD = os.environ.get("MADB_MCP_CMD", "uvx madb-mcp-server")
SEED_FILE = Path(__file__).with_name("seed_memories.json")
_RESPONSE_TIMEOUT_S = 60.0
_UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


class McpClient:
    """Minimal MCP stdio client: spawn server, initialize → tools/call.

    Messages are newline-delimited JSON-RPC over the child's stdin/stdout (the
    MCP stdio transport). A background thread drains stdout into a queue so reads
    can time out cross-platform instead of blocking forever on a dead server.
    """

    def __init__(self, cmd: str) -> None:
        self.cmd = shlex.split(cmd)
        self.proc: subprocess.Popen | None = None
        self._id = 0
        self._lines: queue.Queue[str | None] = queue.Queue()
        self._reader: threading.Thread | None = None

    def start(self) -> None:
        self.proc = subprocess.Popen(
            self.cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,  # server prints startup notices here; keep our output clean
            text=True,
            bufsize=1,  # line-buffered
        )
        self._reader = threading.Thread(target=self._drain_stdout, daemon=True)
        self._reader.start()

    def _drain_stdout(self) -> None:
        assert self.proc and self.proc.stdout
        for line in self.proc.stdout:
            self._lines.put(line)
        self._lines.put(None)  # EOF sentinel

    def _write(self, body: dict) -> None:
        assert self.proc and self.proc.stdin
        self.proc.stdin.write(json.dumps(body) + "\n")
        self.proc.stdin.flush()

    def _read_response(self, want_id: int) -> dict:
        """Return the JSON-RPC response with id == want_id, skipping any
        notifications/log lines the server emits in between."""
        while True:
            try:
                line = self._lines.get(timeout=_RESPONSE_TIMEOUT_S)
            except queue.Empty as e:
                raise RuntimeError("timed out waiting for MADB server response") from e
            if line is None:
                raise RuntimeError("MADB server closed the connection unexpectedly")
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue  # not a JSON-RPC frame (stray output) — ignore
            if isinstance(msg, dict) and msg.get("id") == want_id:
                return msg

    def _request(self, method: str, params: dict | None) -> dict:
        self._id += 1
        rid = self._id
        body = {"jsonrpc": "2.0", "id": rid, "method": method}
        if params is not None:
            body["params"] = params
        self._write(body)
        return self._read_response(rid)

    def _notify(self, method: str, params: dict | None = None) -> None:
        body = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            body["params"] = params
        self._write(body)

    def initialize(self) -> None:
        self._request(
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "madb-seed", "version": "0.2"},
            },
        )
        self._notify("notifications/initialized")

    def call_text(self, tool: str, args: dict) -> str:
        """Call a tool and return its text content. MADB tools return a single
        human-readable text block (e.g. "Stored memory: <id>"), not JSON."""
        result = self._request("tools/call", {"name": tool, "arguments": args})
        if "error" in result:
            raise RuntimeError(f"{tool} failed: {result['error']}")
        return result["result"]["content"][0]["text"]

    def close(self) -> None:
        if not self.proc:
            return
        try:
            if self.proc.stdin:
                self.proc.stdin.close()
            self.proc.terminate()
            self.proc.wait(timeout=5)
        except Exception:  # noqa: BLE001
            self.proc.kill()


def _topo_order(memories: list[dict]) -> list[dict]:
    """Order so every caused_by dependency is written before its dependents."""
    by_id = {m["id"]: m for m in memories}
    ordered: list[dict] = []
    seen: set[str] = set()

    def visit(mem: dict) -> None:
        if mem["id"] in seen:
            return
        for dep in mem.get("caused_by", []):
            if dep in by_id:
                visit(by_id[dep])
        seen.add(mem["id"])
        ordered.append(mem)

    for m in memories:
        visit(m)
    return ordered


def seed(client: McpClient, spec: dict) -> dict[str, str]:
    tenant = spec["tenant_id"]
    shared_tag = spec["shared_tag"]
    logical_to_event: dict[str, str] = {}

    for mem in _topo_order(spec["memories"]):
        caused_by = [logical_to_event[d] for d in mem.get("caused_by", []) if d in logical_to_event]
        out = client.call_text(
            "remember",
            {
                "content": mem["content"],
                "tenant_id": tenant,
                "tags": [shared_tag, *mem.get("tags", [])],
                "importance": mem.get("importance"),
                "caused_by": caused_by or None,
                "idempotency_key": f"onboarding-{mem['id']}",
            },
        )
        match = _UUID_RE.search(out)
        if not match:
            raise RuntimeError(f"could not parse event_id from remember response: {out!r}")
        event_id = match.group(0)
        logical_to_event[mem["id"]] = event_id
        print(f"  seeded {mem['id']:<3} -> {event_id}")
    return logical_to_event


def verify(client: McpClient, spec: dict, ids: dict[str, str]) -> None:
    tour = spec.get("tour", {})
    query = tour.get("suggested_recall_query", "what do you remember")
    print(f"\nrecall: {query!r}")
    # The tools return human-readable text already formatted for display — print it.
    print(
        client.call_text(
            "recall",
            {"query": query, "tenant_id": spec["tenant_id"], "tag_filter": [spec["shared_tag"]], "top_k": 5},
        )
    )

    anchor = ids.get(tour.get("trace_from", ""))
    if anchor:
        print(f"\ntrace_cause backward from {tour['trace_from']} ({anchor}):")
        print(
            client.call_text(
                "trace_cause",
                {"event_id": anchor, "tenant_id": spec["tenant_id"], "direction": "backward"},
            )
        )


def clear(client: McpClient, spec: dict) -> None:
    """Remove every onboarding_demo record so the user's store is left clean."""
    listing = client.call_text(
        "list_recent", {"tenant_id": spec["tenant_id"], "tags": [spec["shared_tag"]], "limit": 100}
    )
    event_ids = list(dict.fromkeys(_UUID_RE.findall(listing)))  # de-dupe, keep order
    for eid in event_ids:
        client.call_text("forget", {"event_id": eid, "tenant_id": spec["tenant_id"]})
    print(f"  cleared {len(event_ids)} onboarding_demo record(s)")


def main() -> int:
    ap = argparse.ArgumentParser(description="MADB first-run seeder (activation wedge)")
    ap.add_argument("--verify", action="store_true", help="after seeding, recall + trace_cause to show the aha")
    ap.add_argument("--clear", action="store_true", help="forget all onboarding_demo records and exit")
    args = ap.parse_args()

    spec = json.loads(SEED_FILE.read_text())
    client = McpClient(MCP_CMD)
    try:
        client.start()
        client.initialize()
    except FileNotFoundError:
        print(f"Could not launch the MADB MCP server: command not found ({MCP_CMD!r}).", file=sys.stderr)
        print("Install it first, e.g. `uvx madb-mcp-server` or `pip install madb-mcp-server`.", file=sys.stderr)
        return 1
    except Exception as e:  # noqa: BLE001
        print(f"Could not reach the MADB MCP server via {MCP_CMD!r}: {e}", file=sys.stderr)
        print("Check the install: `claude mcp add madb -- uvx madb-mcp-server`", file=sys.stderr)
        client.close()
        return 1

    try:
        if args.clear:
            clear(client, spec)
            return 0

        print(f"Seeding guided tour into tenant {spec['tenant_id']!r} ...")
        ids = seed(client, spec)
        if args.verify:
            verify(client, spec, ids)
        print("\nDone. Try asking Claude: " + json.dumps(spec["tour"]["first_prompts_for_user"][0]))
        return 0
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
