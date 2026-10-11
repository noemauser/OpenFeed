# Changelog

All notable changes to OpenFeed are documented here.

## [0.1.1] — 2026-10-11

### Added
- CLI `search` and MCP `search_packs`
- Optional JSON Schema validation (`validate --strict`, requires `jsonschema`)
- Tests (`tests/`) and GitHub Actions CI (Python 3.10 / 3.12)
- `COMMUNITY.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`
- Issue templates (bug, pack proposal, feature)
- Examples: `examples/load_packs.py`, `examples/minimal_feed.py`
- CI checks: strict pack validation + index sync (ids/files)

### Changed
- Visitor-facing docs cleanup (removed internal setup drafts)
- Schema `$id` points at GitHub raw URL
- Docs renamed: `protocol.md`, `knowledge-pack.md`, `mcp.md`, `a2a.md`
- `list_packs` skips `index.json`
- Package version **0.1.1**

### Fixed
- README no longer claims Discussions still need enabling
- Dead / process-only documentation removed from the public tree

## [0.1.0] — 2026-10-11

### Added
- Knowledge Pack schema v0.1
- Python library + CLI (`create`, `validate`, `show`, `list`, `index`)
- Six seed packs + `packs/index.json`
- MCP zero-dep helpers + optional FastMCP adapter
- Protocol / MCP / A2A draft docs
- MIT license, CONTRIBUTING, Makefile
