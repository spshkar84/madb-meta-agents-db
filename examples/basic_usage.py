"""
Basic usage of the MADB Anthropic SDK shim.

This example shows the one-import swap that turns a stock Anthropic
client into one that persists every turn to MADB with causal lineage.

Prerequisite:
    pip install madb-anthropic
    export ANTHROPIC_API_KEY=<your-anthropic-api-key>
    export MADB_TENANT_ID=my-agent        # optional; defaults to "default"
    export MADB_DATA_DIR=~/.madb/data     # optional
"""

from madb_anthropic import Anthropic


def main() -> None:
    # Identical surface to anthropic.Anthropic() — one import change.
    client = Anthropic(tenant_id="quickstart-demo")

    # First turn — no prior memory exists yet, so recall returns nothing
    # and the shim persists this turn as the root of the DAG.
    resp1 = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=256,
        messages=[
            {"role": "user", "content": "Remember that my project uses Rust 2024 edition."},
        ],
    )
    print("Turn 1:", resp1.content[0].text)

    # Second turn — the shim recalls turn 1 automatically, injects it as
    # a memory preface into the system prompt, and chains caused_by.
    resp2 = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=256,
        messages=[
            {"role": "user", "content": "What edition of Rust am I using?"},
        ],
    )
    print("Turn 2:", resp2.content[0].text)

    # Inspect the causal DAG from the most recent memory backward.
    recent = client.madb_recall("Rust edition", top_k=1)
    if recent:
        event_id = recent[0]["event_id"]
        trace = client.madb_trace(event_id, direction="backward", depth=5)
        print(f"\nCausal chain for {event_id}:")
        for hop in trace:
            print(f"  {hop['from']} -> {hop['to']} (depth {hop['depth']})")


if __name__ == "__main__":
    main()
