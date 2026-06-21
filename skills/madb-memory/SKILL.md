---
name: madb-memory
description: >-
  Durable causal memory for this agent via the connected MADB MCP server —
  persists across sessions and records WHY things happened (caused_by lineage).
  Use it as a reflex tied to the work, not on every turn. RECALL at the start of
  a task that references prior work/projects/decisions ("my project", "the script
  we wrote", "what we decided", "last time", "continue", or a named repo/file).
  REMEMBER a decision/result/preference after it happens, with caused_by links.
  TRACE_CAUSE when asked why/how something happened. SAVE_SKILL for reusable
  procedures. Do NOT recall on self-contained one-offs (a fresh factual question,
  a standalone calculation) — false-positive recall is the main failure mode.
  Local, single-owner durable memory + lineage only; not networked, multi-agent,
  policy-enforced, or isolated.
license: CC-BY-ND-4.0
---

<!--
  MADB-MEMORY SKILL © 2026 Pushkar Singh / Meta-Agents.AI

  Licensed under Creative Commons Attribution-NoDerivatives 4.0 International
  (CC BY-ND 4.0). You may share this Skill verbatim with attribution; you may
  not publish modified versions. The full license text is at
  https://creativecommons.org/licenses/by-nd/4.0/legalcode

  The MADB software this Skill invokes is distributed under the
  Meta-Agents.AI Proprietary License. This Skill file is the interface
  contract; the software itself is not open source.
-->

# MADB — durable causal memory for this agent

You have MADB connected: a local memory store that persists across sessions and
records not just what happened but why (causal lineage). Without it you start each
session blank. With it, you can recall what you and the user did before, build on prior
decisions, and trace why something happened.

Use it as a reflex tied to the work — not on every turn, and not only when asked.

## The loop

```
recall (before)  →  act  →  remember (after)  →  trace_cause (when "why?")
```

## When to RECALL (read memory)

Call `recall` at the start of a task when any of these is true. Do it silently;
don't announce it.

- The user refers to prior work as if you should know it: "my project", "the script
  we wrote", "what we decided", "last time", "continue", "the usual".
- The task names a project, repo, file, or decision that could have history.
- You're resuming something — the message assumes continuity you don't currently see.

Don't recall for self-contained one-offs (a fresh factual question, a standalone
calculation, a brand-new task with no past). False-positive recall — pulling
irrelevant memory into context — is the main failure mode. When in doubt, a single
targeted recall is cheap; a recall on every trivial turn is noise.

```
recall(query="<the user's actual topic, in content words>", top_k=20)
```

Use the user's real nouns (the project name, the filename, the decision) as the query
— not meta-words like "previous conversation". If recall returns nothing useful,
proceed normally; don't force it.

## When to REMEMBER (write memory)

Call `remember` after something happened that a future session would need to know.
Write the decision and its reason, not a transcript.

Remember when:

- A decision was made or a direction chosen ("we're using X, not Y, because...").
- A non-trivial result was produced (a working approach, a fix, a conclusion).
- A constraint, preference, or fact about the user's world surfaced that will matter
  later ("their deploy target is X", "they prefer Y").
- A reusable procedure emerged → also consider `save_skill` (see below).

Don't remember every message, small talk, or things trivially re-derivable. Aim
for the handful of facts that change what a future session would do.

Always link causation with `caused_by` — this is what makes the memory a lineage and
not a flat log:

```
remember(
  content="<the decision/result and its reason, in plain words>",
  caused_by=[<event_id(s) this followed from, if known>],
  tags=["<project>", "<topic>"],
  importance=<higher for decisions that constrain future work>
)
```

If you recalled an event earlier in the session and this new memory follows from it,
pass that event's id in `caused_by`. That single habit is what lets `trace_cause`
later answer "why did we end up here?"

## When to TRACE_CAUSE (walk the lineage)

When the user (or you) needs to understand why a current state exists — "why did we
choose this", "how did we get here", "what led to X" — walk the causal chain:

```
trace_cause(event_id="<the event in question>", direction="backward")
```

This returns the chain of `caused_by` links back to the origin. Use it to explain a
decision's history, debug a wrong turn (find the upstream decision that caused it), or
summarize how a project reached its current shape.

## Skills: capture reusable procedures

When you work out a repeatable how-to (a build sequence, a debugging routine, a
project-specific convention), persist it so a future session can reuse it:

```
save_skill(name="<short-name>", description="<when to use it>", content="<the steps>")
```

Recall skills when starting work that might have an established procedure:

```
recall_skill(query="<the kind of task>")
```

## How memory is scored (so you trust recall)

`recall` doesn't just keyword-match. It ranks by a composite of: semantic similarity,
recency, causal proximity (how close in the lineage), importance, and tag overlap.
That's why linking `caused_by` and setting `importance` on real decisions pays off —
it makes the right memories surface later, not just the most recent ones.

## Scope & honesty

- This memory is local and yours — it lives on this machine, in this owner's
  store. It is durable across sessions; it is **not** a shared, networked, or
  multi-agent system, and it does **not** enforce policy or isolation. Treat it as your
  durable notebook with causal links, nothing more.
- Don't write secrets, credentials, or content the owner wouldn't want persisted to
  local disk.
- recall / remember quietly in service of the task. Mention memory only when it
  helps the user ("I remembered we decided X last time") — not as narration of every
  tool call.

## Minimal example

```
# Session 1 — user designs a deploy approach
remember(content="Deploy target is Fly.io, chosen over Render for cheaper persistent
         volumes. Build via Dockerfile, not buildpacks.",
         tags=["deploy","infra"], importance=0.9)
  → returns event_id A

# Session 2 (days later) — user: "let's add the staging environment"
recall(query="deploy staging fly.io infra")
  → returns event A (the Fly.io decision)
# you now build staging consistent with the prior decision, and:
remember(content="Added staging app on Fly.io mirroring prod Dockerfile build.",
         caused_by=[A], tags=["deploy","infra","staging"], importance=0.7)

# Later — user: "why are we on Fly and not Render again?"
trace_cause(event_id=<staging event>, direction="backward")
  → walks back to event A and its reasoning
```

That's the whole feature: remember why, recall it when it matters, prove the chain.
