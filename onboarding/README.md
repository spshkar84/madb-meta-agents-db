# MADB guided tour (optional first-run seed)

A brand-new MADB install is empty, so your very first `recall` returns nothing —
which makes it hard to *feel* what MADB does. This optional seed plants a small,
clearly-labelled causal DAG (a fictional `samplex.io` project and the decisions
behind it) so your **first session** produces a real recall + `trace_cause`
moment instead of an empty store.

Everything here is demo data. It lives in its own tenant (`onboarding-tour`) and
every record is tagged `onboarding_demo`, so you can remove it cleanly when
you're done.

## Take the tour

**Fastest path — one command.** With the `madb` MCP server running, the bundled
seeder plants the whole DAG (idempotently) and can show the aha in the same run:

```bash
python seed.py --verify     # plant + recall + trace_cause in one shot
python seed.py --clear      # remove every onboarding_demo record afterwards
```

**Conversational path.** Or, with the `madb` MCP server connected in Claude Code,
load the seed and ask Claude the tour prompts. You can just ask Claude directly:

> "Load `onboarding/seed_memories.json` into MADB under tenant `onboarding-tour`
>  (each entry via `remember`, preserving the `caused_by` links), then recall my
>  project and trace how I ended up deferring the chart render."

Then try the first prompts (also listed in the seed's `tour` block):

- **"What do you remember about my project?"** → `recall` surfaces the project
  context across what looks like a fresh session.
- **"Why did I pick SvelteKit?"** → recall pulls the specific decision, not just
  the most recent note.
- **"Walk me back through how I ended up deferring the chart render to onMount."**
  → `trace_cause` walks the lineage back through the SvelteKit decision to the
  project root — the causal chain a flat vector store cannot produce.

That round trip — recall the right memory, then prove *why* it exists by walking
the DAG — is the whole point of MADB.

## Remove the demo data when you're done

The tour data lives in its own tenant namespace and tag, so cleanup is trivial. Ask
Claude:

> "Forget every MADB memory tagged `onboarding_demo` in tenant `onboarding-tour`."

Or, since it's a dedicated tenant, simply stop using `onboarding-tour` and point
`MADB_TENANT_ID` at your real project namespace — the demo data never mixes with
your own memories.

## Notes

- `samplex.io` and its decisions are **fictional sample content**, included only
  to demonstrate recall and lineage. None of it is real.
- Your own memories live under whatever `MADB_TENANT_ID` you configure (default:
  a built-in namespace), never under `onboarding-tour`.

---

## For maintainers: this is the activation wedge (MAGE Phase 0)

The hardest step in MADB adoption is not awareness and not install — it is the
**aha**: the first time a user sees recall survive a clean session *and* sees
`trace_cause` explain *why* a decision was made. It normally only happens after days
of accumulated memory, so a fresh install churns before it ever lands. Driving
campaign traffic to an install that can't produce the aha wastes the install. This
directory compresses time-to-aha to the first sixty seconds, which is why it ships
before any growth push.

The companion `madb-onboarding` skill (`../skills/madb-onboarding/SKILL.md`)
choreographs the first run: detect an empty store, offer the tour, and answer
"what do you remember about me?" with recall **plus** lineage every time.

### How it ships (install bundling)

The `madb-mcp-server` wheel already bundles skills and auto-installs them to
`~/.claude/skills/` on first launch. Ship the wedge the same way:

1. Bundle `skills/madb-onboarding/` next to `skills/madb-memory/` in the wheel.
2. Bundle this `onboarding/` directory so `python -m onboarding.seed` works
   post-install.
3. On first launch the skill detects the empty store and offers the tour — nothing
   for the user to discover.

### North-star metric — instrument before launch

> **% of installs where Claude calls `remember`/`recall` *unprompted* within 7 days.**

That is Cohort 1's stated success signal (Claude reflexively reaching for MADB) and
the leading indicator for retention, referral, and ultimately the OEM conversation.
Measure it locally, opt-in only:

1. **Activation event.** The first unprompted `recall`/`remember` in a session writes
   one local marker tagged `madb_activation`. Extend the `analytics` tool to expose
   `days_to_first_unprompted_call` per tenant.
2. **Tour-to-activation funnel.** Compare 7-day activation for tour-takers
   (`onboarding_demo` present) vs. non-takers. The delta is the wedge's ROI — a clean
   number to publish.
3. **Telemetry hygiene.** Honour `MADB_TELEMETRY=off`; aggregate only, never per-user
   content. Anything else poisons the trust the OEM relationship depends on.

Supporting metrics: tour acceptance rate, time-to-first-non-empty-recall, and
aha-share rate (tours where the user accepted "format it to share") — the last feeds
straight back into MAGE's content loop.

### Honest caveats (from live verification, server `madb` v1.27.0)

- The demo-grade half of the aha is **persistence + `trace_cause` lineage** — lead
  with those.
- Raw semantic similarity on short cold queries scored low (`similarity` 0.008–0.03,
  `causal_proximity` 0.0); recall is carried by recency, importance, and tag overlap.
  Pitch *durable, causally-linked memory* — true and defensible — not best-in-class
  vector search. Improving cold-query scoring is self-tuning-loop work, tracked
  separately.
