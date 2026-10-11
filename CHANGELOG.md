# Changelog

All notable changes to OpenFeed are documented here.

## [0.1.2] — 2026-10-11

### Added
- **8 domain Knowledge Packs** (context budget, tool errors, LLM-as-judge, memory tiers, JSON output, multi-hop RAG, prompt caching, smoke eval) — **14 packs total**
- CLI `related` + MCP `related_packs` (relation graph)
- Experimental **HMAC-SHA256** pack signing/verify (`openfeed sign` / `verify`) — stdlib only
- Static **registry/** + Pages workflow
- CI MCP import smoke (`continue-on-error`)
- Docs: `docs/signing.md`, `docs/registry.md`

### Changed
- Package version **0.1.2**
- Richer pack relation graph across seeds + domain packs

## [0.1.1] — 2026-10-11

### Added
- CLI `search` and MCP `search_packs`
- Optional JSON Schema validation (`validate --strict`)
- Tests + CI (strict packs + index sync)
- COMMUNITY, SECURITY, CODE_OF_CONDUCT
- Issue/PR templates
- Examples: `load_packs.py`, `minimal_feed.py`

### Changed
- Visitor-facing docs cleanup
- Schema `$id` → GitHub raw URL

## [0.1.0] — 2026-10-11

### Added
- Schema v0.1, library, CLI, 6 seed packs, MCP helpers, protocol docs
