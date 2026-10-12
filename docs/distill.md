# OpenFeed Distill

Public target → **Knowledge Packs** for agents and builders.

## CLI

```bash
export PYTHONPATH=src
python -m openfeed distill recipes
python -m openfeed distill noemauser/OpenFeed --depth 2 --set full
python -m openfeed distill . --kind local --depth 2
python -m openfeed distill 2309.15217 --kind arxiv --set full
python -m openfeed distill owner/repo --preview
```

| Flag | Meaning |
|------|---------|
| `--depth 0-4` | Tree depth (default 2) |
| `--set core` | overview + surfaces + agent_use |
| `--set full` | core + **architecture** (manifests, rebuild notes) |
| `--preview` | no write |
| `--out-dir` | default `staging/` |

## Outputs

1. overview  
2. surfaces  
3. agent_use  
4. architecture (full set)

Samples: README, LICENSE, pyproject/package.json/Cargo/go.mod, docs/*.md when present.

## Noema

Issue label **`distill-please`** or title `[Distill] owner/repo` → Distill desk preview (packs + digests + command).

## Demo packs

- `kp_distill_openfeed_*` (self-distill, full)  
- `kp_distill_2309_15217_*` (Ragas paper arXiv showcase)

— Noema
