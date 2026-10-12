# Changelog

All notable changes to OpenFeed are documented here.

## [0.1.3] — 2026-10-12

### Added
- **6 domain packs**: HITL, citation hygiene, local model feeding, tool schema design, uncertainty, canonical agent loop — **20 packs total**
- CLI `get`, `fetch`; `list`/`search` support `--tag` and `--min-confidence`
- `openfeed.remote` — stdlib HTTPS catalog/pack fetch
- [registry/openfeed-agent-card.json](registry/openfeed-agent-card.json)
- [ROADMAP.md](ROADMAP.md)
- Example: `examples/fetch_remote_catalog.py`
- Tests for tag search, confidence filter, remote index filter

### Changed
- Package version **0.1.3**

## [0.1.2] — 2026-10-11

### Added
- 8 domain Knowledge Packs — 14 total
- CLI `related` + MCP `related_packs`
- Experimental HMAC-SHA256 signing
- Static registry + Pages workflow
- CI MCP smoke

## [0.1.1] — 2026-10-11

### Added
- CLI `search`, strict schema validation, tests/CI, community docs, examples

## [0.1.0] — 2026-10-11

### Added
- Schema v0.1, library, CLI, 6 seed packs, MCP helpers
