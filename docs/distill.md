# OpenFeed Distill

**Distill** takes a public target and produces **Knowledge Packs** — structured parts agents and humans can use.

Learn · feed · rebuild · remix · share. The tool does not lecture.

## Inputs

| Kind | Example |
|------|---------|
| GitHub public repo | `noemauser/OpenFeed` |
| Local path | `.` |
| arXiv | `2005.11401` |

GitHub mode uses the **public** API + README (what is already visible). Local mode reads your disk. arXiv pulls public abstracts.

## Outputs

1. **overview** — orientation + README excerpt  
2. **surfaces** — layout signals + how to dig in  
3. **agent_use** — loop ideas for agents  

## CLI

```bash
export PYTHONPATH=src
python -m openfeed distill noemauser/OpenFeed
python -m openfeed distill . --kind local --out-dir staging
python -m openfeed distill 2005.11401 --kind arxiv --preview
```

Default write: `staging/`. Promote to `packs/` when you want it on the menu.

## Humans

Issue label **`distill-please`** or title `[Distill] owner/repo`.

## Agents

Load packs · cite when useful · pass pack-refs with `openfeed a2a ref`.

## Related

Demo: `kp_distill_openfeed_*` · MCP tools `distill_*` · `distill/README.md`

— Noema
