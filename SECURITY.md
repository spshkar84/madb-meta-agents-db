# Security Policy

Copyright 2025-2026 Pushkar Singh / Meta-Agents.AI

## Reporting a Vulnerability

If you discover a security vulnerability in Meta-AgentsDB, please report it
responsibly:

**Contact**: [01@meta-agents.ai](mailto:01@meta-agents.ai)

- **48-hour acknowledgement**: We will confirm receipt within 48 hours.
- **7-day response**: We aim to provide a substantive response (triage,
  severity assessment, fix timeline) within 7 calendar days.
- **Coordinated disclosure**: Please allow us reasonable time to develop and
  release a fix before public disclosure.

Do **not** open a public GitHub issue for security vulnerabilities.

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.2.x   | Yes       |

## Licensing & Deployment

This open-source release of Meta-AgentsDB is licensed for **development
purposes only**. Claude Code users may use MADB freely during development
and experimentation.

For **production deployments** — where autonomous AI agents use MADB as
their runtime memory layer — a paid runtime license and cloud deployment
are required. Contact [01@meta-agents.ai](mailto:01@meta-agents.ai) for
production licensing, managed cloud deployment, and enterprise support.

## Security Controls

Meta-AgentsDB implements the following security controls:

- **Tenant ID validation**: All tenant identifiers are restricted to
  `[a-zA-Z0-9_-]` (1-128 chars), preventing path traversal and injection.
- **Input validation**: Record payload size, tag count/length, vector
  dimensions, and causal parent count are bounded by `SecurityConfig`.
- **File permissions**: Data directories are created with `0o700` and data
  files with `0o600` on Unix systems.
- **WAL integrity**: Write-ahead log entries are protected with
  HMAC-SHA256 (when `MADB_WAL_HMAC_KEY` is set) in addition to CRC32.
- **MCP server authentication**: Optional API key authentication via
  `MADB_API_KEY` environment variable.
- **Vector validation**: NaN/Inf values are rejected from vector indexes.
- **Causal parent validation**: Parent event IDs are verified to exist
  before accepting causal links.
- **Data directory locking**: Exclusive `flock` prevents concurrent
  processes from corrupting the same data directory.
- **MVCC snapshot reads**: Reads see a consistent point-in-time snapshot
  via Hybrid Logical Clock timestamps.

## Threat Model

Meta-AgentsDB is a **local, single-owner** store. It is designed to run on
the owner's machine inside a trusted perimeter, not as a multi-tenant
network service. The current controls assume:

- The filesystem is the primary trust boundary; memory stays on local disk.
- Network-level authentication/encryption (TLS, mTLS) — if MADB is ever
  fronted by a service — is handled by the deployment infrastructure.
- Tenant IDs are a **namespacing** mechanism, not a security boundary. MADB
  does not enforce policy or cross-tenant authorization at the engine; any
  such authorization must be enforced at the application layer. Storage-layer
  policy enforcement and tenant isolation are on the roadmap, not delivered
  in this release.
