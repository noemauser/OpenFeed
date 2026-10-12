# Remote discovery

Agents can pull the public catalog without cloning the repo.

## Default endpoints

| Resource | URL |
|----------|-----|
| Catalog | https://raw.githubusercontent.com/noemauser/OpenFeed/main/packs/index.json |
| Schema | https://raw.githubusercontent.com/noemauser/OpenFeed/main/schemas/knowledge-pack-v0.1.json |
| Agent card | https://raw.githubusercontent.com/noemauser/OpenFeed/main/registry/openfeed-agent-card.json |
| Pack file | `…/main/packs/<file>.json` |

## CLI

```bash
python -m openfeed fetch
python -m openfeed fetch --query RAG --tag domain
python -m openfeed fetch --pack-file kp_openfeed_intro.json -o /tmp/intro.json
```

## Python

```python
from openfeed.remote import fetch_index, find_in_index, fetch_pack_by_file

index = fetch_index()
rows = find_in_index(index, query="rag", tags=["domain"])
pack = fetch_pack_by_file("kp_multi_hop_rag.json")
```

Operator-authorized HTTPS only. Override URLs when mirroring under your own control.
