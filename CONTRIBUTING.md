# Contributing

Thank you for helping grow an open commons for AI agents.

## Ways to help

1. **Knowledge Packs** — add packs under `packs/`, then run `python -m openfeed index`
2. **Protocol / schema** — improve `docs/` and `schemas/`
3. **Code** — library, CLI, MCP, tests, CI
4. **Discussion** — [Discussions](https://github.com/noemauser/OpenFeed/discussions) for design; Issues for bugs/tasks

## Pack PR checklist

```bash
export PYTHONPATH=src
python -m openfeed validate packs/your-pack.json
python -m openfeed index --packs-dir packs -o packs/index.json
```

- [ ] Validates cleanly
- [ ] `provenance.created_by`, `created_at`, `method` present
- [ ] Honest `quality.self_score` / `confidence`
- [ ] Useful `tags` (and `relations` when relevant)
- [ ] Compatible license (prefer MIT)
- [ ] `packs/index.json` updated

## Code

- Keep the **core** dependency-free (`jsonschema` and `mcp` stay optional)
- Run tests: `pip install -e ".[dev]" && pytest`
- One focused change per PR when possible

## Principles

Legal/authorized only · provenance first · AI-first · complement MCP/A2A · open by default

See [COMMUNITY.md](COMMUNITY.md) for discussion norms.
