# Changelog

All notable changes to the public MADB distribution (the `madb-mcp-server` and
`meta-agents-db` wheels) are documented here. The engine is distributed as
compiled binary wheels under the
[Meta-Agents.AI Proprietary License](./LICENSE); source is not public.

## [0.2.6] — 2026-06-20

Maintenance + distribution release. Supersedes 0.2.5 (which stays on PyPI; `pip`/`uvx` resolve to 0.2.6).

### Changed
- Unified all packages at **0.2.6** (engine `meta-agents-db`, `madb-mcp-server`, `madb-anthropic`).
- Public home is the new, source-free repository **`madb-meta-agents-db`**.
- `madb-mcp-server` now bundles the **`madb-onboarding`** first-run skill + guided tour, so a fresh install produces a real recall + `trace_cause` moment on session #1.

### Notes
- `madb-anthropic` is available for **Python 3.10–3.13**.
- No new engine features in this release — packaging, docs, and distribution only.

## [0.2.5] — 2026-06-19

The first public free-tier release of the MADB MCP server.

### Added
- **`madb-memory` reflex Skill** — bundled with the server wheel; teaches Claude
  to use MADB as a reflex: recall prior context before related work, remember
  decisions (with `caused_by` lineage) after they happen, and `trace_cause` to
  answer "why did we do X?". Auto-installs on first launch.
- **Working keyword recall with no embedder** — `recall(query=...)` now returns
  results out of the box on a local install: when no semantic index is present,
  recall falls back to lexical scoring (query-term overlap + recency +
  importance), so memory is useful from the first session.
- **Guided first-run tour** (`onboarding/`) — an optional seed that plants a
  small, clearly-labelled causal DAG so a brand-new install produces a real
  recall + `trace_cause` moment on session #1 instead of an empty store.
- **One-click Claude Desktop extension** (`.mcpb`) and `uvx`/`pip` install paths.
- **Anonymous, count-only usage telemetry** — measures how much, never what (no
  content, queries, file paths, or username/hostname). Opt out with
  `MADB_TELEMETRY=off`.

### Changed
- **Free-tier tool surface focused to 13 core memory tools** — `remember`,
  `recall`, `get_memory`, `search`, `list_recent`, `forget`, `trace_cause`,
  `save_skill`, `recall_skill`, `list_skills`, `summarize`, `stats`,
  `capabilities`.
- **Honest capability copy** — documentation describes MADB as local,
  single-owner durable causal memory + lineage. Policy enforcement, tenant
  isolation, and multi-agent governance are on the roadmap, not delivered in
  this release.

### Fixed
- Multiple data-integrity and concurrency fixes in the storage engine
  (restart/recovery and concurrent-write paths), with regression coverage.
- Read-path tenant scoping on `get_memory` and `trace_cause`.

### Security
- The shipped build embeds **no license signing key**, so no license can be
  forged against this release; paid-tier keys are minted offline.
- Hardened input validation (tenant-ID charset, payload/tag/vector bounds),
  `0o700`/`0o600` file permissions on Unix, optional WAL HMAC, and exclusive
  data-directory locking.

### Free tier
- Up to **50,000 events** and **5 tenant namespaces** on the local free tier; a
  gentle heads-up around 30,000 causal lineages; writes pause only at the
  50,000-event hard cap. For higher limits or a hosted/team tier, email
  **01@meta-agents.ai** or see <https://meta-agents.ai/upgrade>.

[0.2.6]: https://github.com/spshkar84/madb-meta-agents-db
[0.2.5]: https://github.com/spshkar84/madb-meta-agents-db
