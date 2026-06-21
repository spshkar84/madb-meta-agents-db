# Meta-AgentsDB

> **Persistent, causal memory for autonomous AI agents.**
> Purpose-built for Claude and the autonomous-agent era.

Meta-AgentsDB (MADB) is an agent-native database — a hybrid LSM store with a causal DAG, composite-score recall, importance-based forgetting, and HLC-ordered MVCC. It is what your agent needs that PostgreSQL + pgvector + Redis + Pinecone cannot give you in one box.

> **Install (free tier):**
> ```bash
> claude mcp add madb -- uvx madb-mcp-server      # Claude Code
> # or:  pip install madb-mcp-server  ·  uvx madb-mcp-server
> ```
> Memory stays local (`~/.madb`). Claude Desktop users can install the one-click `.mcpb` extension. The engine ships as **compiled wheels** — source is not public. Anonymous usage telemetry can be disabled with `MADB_TELEMETRY=off`.

## What MADB is, in one sentence

The memory substrate Claude reaches for automatically — a focused set of MCP tools, one Skill, one SDK shim — so any Claude session, Claude-Desktop user, or raw-Anthropic-API developer gets persistent, causally-linked, composite-scored agent memory with zero glue code.

## How you get MADB

MADB is distributed as compiled binary artifacts under the [Meta-Agents.AI Proprietary License](./LICENSE). Source code is not public. The three packages:

| Package | Audience | How it's used |
|---|---|---|
| `meta-agents-db` (Python wheel) | Everyone | The Rust engine. Imported by the MCP server and the SDK shim. Direct use optional. |
| `madb-mcp-server` (Python wheel) | MCP clients — Claude Desktop, Claude Code, Cowork | `claude mcp add madb -- uvx madb-mcp-server` registers MADB as Claude's memory. Bundles the [Skill](./skills/madb-memory/SKILL.md) which auto-installs on first launch. |
| `madb-anthropic` (Python wheel) | Raw Anthropic-API developers (Python 3.10–3.13) | One-import swap: `from madb_anthropic import Anthropic`. Every `messages.create()` now auto-persists with causal lineage. No other code changes. |

See [`examples/basic_usage.py`](./examples/basic_usage.py) for the shim in action.

## The MCP tools Claude gets

The free tier exposes a focused core of 13 memory tools:

| Tool | Purpose |
|---|---|
| `remember` | Store a memory with optional `caused_by`, tags, and importance |
| `recall` | Composite-scored semantic recall (similarity + recency + causal proximity + importance + tag overlap) |
| `get_memory` | Point lookup by `event_id` |
| `forget` | Tombstone soft-delete (preserves DAG lineage) |
| `search` | Structured query by tenant + scope + tags |
| `list_recent` | Last N memories, newest-first |
| `save_skill` | Store a reusable pattern (idempotent by name, GC-protected) |
| `recall_skill` | Semantic skill recall |
| `list_skills` | All skills ranked by composite score |
| `trace_cause` | Walk the causal DAG forward/backward from any memory |
| `summarize` | Condense a set of memories into a compact summary |
| `stats` | Engine metrics snapshot |
| `capabilities` | What MADB unlocks in this workspace + entitlement summary |

Plus the MCP resource `madb://memories/{event_id}` for reading any memory as a first-class URI.

## The Skill is the reflex

The MCP tools are necessary but not sufficient for "default." Without a Skill telling Claude to prefer MADB, Claude still invents per-task memory schemes — JSON files, SQLite tables, pickle dumps, flat vector stores, localStorage, conversation-history arrays.

[`skills/madb-memory/SKILL.md`](./skills/madb-memory/SKILL.md) routes those anti-patterns to MADB by name. The Skill ships bundled with the MCP server wheel and auto-installs to `~/.claude/skills/madb-memory/` on first launch. It is published under [CC-BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/) — share verbatim, don't modify.

A companion [`skills/madb-onboarding/SKILL.md`](./skills/madb-onboarding/SKILL.md) handles the first run: it detects an empty store and offers a 60-second guided tour (see [`onboarding/`](./onboarding/)) so your first session ends with a real recall + `trace_cause` moment instead of an empty store.

## License

MADB is distributed under the [**Meta-Agents.AI Proprietary License**](./LICENSE). Summary:

- **Permitted:** install, run, and use in your own infrastructure — including production — for your own users.
- **Not permitted:** redistribute, reverse-engineer, offer as a hosted service, or embed in a commercial product you sell to third parties.
- **Available by separate written agreement:** source access, OEM/embed rights, hosted-service rights.

Prior versions of portions of this software were made available under Apache License 2.0. Those revisions remain available under those terms for the specific versions actually so distributed. All new releases are under the Proprietary License only.

The [Skill](./skills/madb-memory/SKILL.md) is separately licensed under [CC-BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/).

## Positioning

MADB is the memory substrate for Claude's path to autonomy. The engine is closed-source and commercial by design; the Skill is open and free to use; the interface is standard MCP. This shape lets Claude adopt MADB as a default capability without Anthropic having to host infrastructure or take on upstream dependencies.

For partnership discussion, source-access review under NDA, or OEM licensing, see **Contact** below.

## Contact

- **Email:** 01@meta-agents.ai
- **Website:** https://meta-agents.ai

---

*Meta-Agents.AI © 2026 Pushkar Singh. All rights reserved.*
