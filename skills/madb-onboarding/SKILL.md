---
name: madb-onboarding
description: First-run experience for a freshly installed MADB. Trigger this skill when a user has just installed/registered the `madb` MCP server and has little or no memory yet, when they ask "what do you remember about me?", "show me what MADB/this can do", "is MADB working?", "what's in my memory?", or any first-session "how do I start" question about MADB. Its job is to compress time-to-aha: get the user to a real recall + causal-lineage moment within their first session instead of waiting days for memory to accumulate organically. Do NOT trigger for routine remember/recall during normal work — that is the `madb-memory` skill. This skill is specifically the guided first run and the "what do you remember about me?" handler.
license: CC-BY-ND-4.0
---

<!--
  MADB-ONBOARDING SKILL © 2026 Pushkar Singh / Meta-Agents.AI

  Licensed under Creative Commons Attribution-NoDerivatives 4.0 International
  (CC BY-ND 4.0). Share verbatim with attribution; modified versions may not
  be published. https://creativecommons.org/licenses/by-nd/4.0/legalcode

  The MADB software this Skill invokes is distributed under the Meta-Agents.AI
  Proprietary License. This Skill is the interface contract, not the software.
-->

# madb-onboarding

This is the **activation wedge**. A new MADB install has an empty store, so a
user's first sessions recall *nothing* and they never feel why MADB matters. Your
job in this skill is to manufacture the "wait — it *remembered*, and it can show me
*why*" moment inside the very first session. That moment is the whole product in
20 seconds; everything else in MADB compounds from it.

The aha has two halves, and you must show **both**:

1. **Recall across a clean session** — memory that survives when the context window
   doesn't.
2. **`trace_cause` lineage** — walking the causal DAG to answer *why* a decision was
   made. This is the half a flat vector store cannot do, and it is what makes the
   moment land instead of feeling like ordinary search.

## When this skill fires

- The user just ran `claude mcp add madb` / first launched the server.
- `list_recent` / `stats` shows an empty or near-empty store for their tenant.
- They ask "what do you remember about me?", "what's in my memory?", "show me what
  this can do", "is it working?", or "how do I start with MADB?".

If the store already has real user memory, prefer the `madb-memory` skill — don't
run the guided tour over a populated store.

## The 60-second guided tour

When a new user wants to see MADB work and has nothing stored yet, offer the tour in
one sentence ("Want a 60-second demo of what MADB does? I'll plant a tiny sample
project history, then recall it and show you the causal chain — all in a throwaway
`onboarding-tour` tenant, removable in one command."). On yes:

1. **Plant the sample DAG.** Run the seeder that ships with MADB:
   `python -m onboarding.seed` (or `python onboarding/seed.py`). It writes a small,
   clearly-labelled causal graph for a sample project (`samplex.io`) into the
   isolated `onboarding-tour` tenant, tagged `onboarding_demo`. It is idempotent.
   If you cannot run a shell, plant the same records yourself by reading
   `onboarding/seed_memories.json` and calling `remember` once per entry in
   `caused_by`-dependency order, chaining each `caused_by` to the real `event_id`
   returned by its parent.
2. **Recall in front of them.** Call `recall` with
   *"what do you remember about my project and the decisions I made"*, tenant
   `onboarding-tour`, tag_filter `["onboarding_demo"]`. Show the returned memories —
   this is the "it persisted" half.
3. **Walk the lineage.** Take the hydration-fix memory (logical id `m4`) and call
   `trace_cause` backward. Narrate the chain in plain English: *"the chart fix
   happened because of the SvelteKit choice, which happened because of how the
   project was framed."* This is the half that makes them lean in.
4. **Hand off.** Tell them the tour data lives in a separate tenant and can be wiped
   with `python onboarding/seed.py --clear`, and that **their** memory now
   accumulates automatically as they work — no commands to learn.

Keep the whole thing under a minute of reading. The point is the moment, not a
lecture about the engine.

## The "what do you remember about me?" handler

This question is the single most common first-session trigger and your best
recurring activation surface. Always answer it in two moves, never one:

1. `recall` with the user's identity/project as the query (use their real tenant).
2. `trace_cause` on the **top result** and surface the lineage.

A `recall`-only answer reads like search and undersells MADB. The lineage is the
differentiator — show it every time, even briefly.

If the store is genuinely empty (new user, no tour yet), don't apologise with "I
don't have anything." Convert it: *"Nothing yet — but that's the point, I'll start
remembering as we work. Want a 60-second demo of how that pays off?"* and offer the
tour above. An empty store is an activation opportunity, not a dead end.

## Make the aha shareable

When the lineage moment lands, the user has just generated the exact artifact that
drives the next install. Offer — lightly, never pushily — *"That causal chain is the
thing most people screenshot. Happy to format it as a clean before/after if you want
to share it."* Capturing one aha as shareable content is the growth loop closing on
itself; the engine that just demoed memory is the same engine MADB is selling.

## Honest framing (do not oversell)

- The strong, reliable part of the demo is **persistence + `trace_cause` lineage**.
  Lead with those.
- Raw semantic similarity on short queries can score low; recall leans on recency,
  importance, and tags too. Don't claim perfect semantic matching — claim durable,
  causally-linked memory, which is the true and defensible pitch.
- Never imply the hosted API is live — local install is the product today.

## Leave the store clean

The tour lives in its own `onboarding-tour` tenant so it never pollutes real memory.
Always remind the user it is removable (`seed.py --clear`). Do not seed demo records
into the user's working tenant.
