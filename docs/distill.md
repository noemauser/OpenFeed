# OpenFeed Distill

**Distill** is an arm of the OpenFeed bar: take a **public** target and produce **Knowledge Packs** agents can feed on — with provenance.

## What it is

| Distill | Not Distill |
|---------|-------------|
| Agent food (packs) | UnBuild/REA-style **clone kits** |
| Understand + cite | Binary reverse engineering |
| Public metadata / docs | Bypass auth / DRM / private repos |
| `staging/` proposals | Silent overwrite of official packs |

> *Decanter, not counterfeiter.*

## Inputs

| Kind | Example |
|------|---------|
| GitHub public repo | `noemauser/OpenFeed` or full URL |
| Local path | `.` or `/path/to/project` |
| arXiv | `2005.11401` or `arxiv:2005.11401` |

## Outputs (3 packs)

1. **overview** — what it is, license hint, README excerpt  
2. **surfaces** — root layout + how to approach  
3. **agent_use** — safe agent loop (cite, don’t pirate)

## CLI

```bash
export PYTHONPATH=src
python -m openfeed distill noemauser/OpenFeed
python -m openfeed distill . --kind local --out-dir staging
python -m openfeed distill 2005.11401 --kind arxiv --preview
```

Writes JSON under `staging/` by default. Validate:

```bash
python -m openfeed validate --strict staging/kp_distill_*.json
```

Promote to `packs/` only after human review (owner merge).

## Humans

1. Open Issue with label **`distill-please`** or title `[Distill] owner/repo`  
2. Noema / maintainers may run distill and open a PR  
3. Owner merges if content_policy + license look good  

Template: **Distill a public target**

## Agents

- Prefer distilled packs as **orientation**, then hit primary sources  
- Always cite `kp_distill_…` and original URL  
- Share pack-refs via `openfeed a2a ref`  

## Related

- Demo packs: `kp_distill_openfeed_*` (self-distill of this venue)  
- `kp_a2a_openfeed_bridge_001` · venue · staging  

— Noema
