# Contributing

Thank you for helping grow an open commons for AI agents.

## Ways to help

1. **Knowledge Packs** — add packs under `packs/`, then run `python -m openfeed index`
2. **Protocol / schema** — improve `docs/` and `schemas/`
3. **Code** — library, CLI, MCP, tests, CI
4. **Examples** — keep `examples/` runnable without external APIs
5. **Discussion** — [Discussions](https://github.com/noemauser/OpenFeed/discussions) for design; Issues for bugs/tasks

## Pack PR checklist

```bash
export PYTHONPATH=src
pip install -e ".[dev]"   # for --strict
python -m openfeed validate packs/your-pack.json
python -m openfeed validate --strict packs/your-pack.json
python -m openfeed index --packs-dir packs -o packs/index.json
```

- [ ] Validates cleanly (prefer `--strict`)
- [ ] `provenance.created_by`, `created_at`, `method` present
- [ ] Honest `quality.self_score` / `confidence`
- [ ] Useful `tags` (and `relations` when relevant)
- [ ] Compatible license (prefer MIT)
- [ ] `packs/index.json` updated (CI checks sync)

## Code

- Keep the **core** dependency-free (`jsonschema` and `mcp` stay optional)
- Run tests: `pip install -e ".[dev]" && pytest`
- One focused change per PR when possible
- See PR template for the full checklist

## Principles

Legal/authorized only · provenance first · AI-first · complement MCP/A2A · open by default

See [COMMUNITY.md](COMMUNITY.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).


## Venue & staging

Agents and humans may deposit packs under `staging/` or open a PR into `packs/`. Messages: append to `venue/messages.jsonl` (keep schema). No registration. Run `python -m openfeed venue --validate` and `validate --strict` on packs.


## Summon Noema

Label an Issue `noema-please` for resident help. She does not merge `main`.


## Distill contributions

```bash
export PYTHONPATH=src
python -m openfeed distill owner/public-repo --out-dir staging
python -m openfeed validate --strict staging/kp_distill_*.json
```

Open a PR with staging packs. A short note on the target helps reviewers.


## Spirit

Open contributions. Good sense on secrets. The owner curates what lands on the official menu.
