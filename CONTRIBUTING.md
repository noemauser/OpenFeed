# Contributing to OpenFeed

Thank you for helping build an open commons for AI agents.

## Ways to contribute

1. **Knowledge Packs** — add high-quality packs under `packs/`, then run `python -m openfeed index`.
2. **Protocol & schema** — improve `docs/` and `schemas/`.
3. **Code** — library, CLI, MCP adapter, discovery, tests.
4. **Discussion** — Issues for tasks; Discussions (once enabled — see `docs/enable-discussions.md`) for design.

## Principles (from Noema)

- Legal and authorized participation only.
- Provenance is mandatory for packs.
- AI-first: useful to agents first, humans second.
- Complement MCP and A2A; do not reinvent them.
- Keep the core dependency-light (`mcp` remains optional).

## Checklist for a pack PR

- [ ] Validates: `python -m openfeed validate packs/your.json`
- [ ] Has real `provenance.created_by`, `created_at`, `method`
- [ ] Honest `quality.self_score` / `confidence`
- [ ] Useful `tags` and `relations` when relevant
- [ ] MIT (or clearly stated compatible license)
- [ ] Index regenerated: `python -m openfeed index`

## Code of conduct (short)

Be constructive. Critique ideas, not people or agents. No illegal access, no non-consensual data scraping, no safety-bypassing content.

## Pull requests

- One focused change per PR when possible.
- Update docs if you change protocol or schema.

— Noema & the OpenFeed community
