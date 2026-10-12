# Examples

```bash
cd /path/to/OpenFeed
export PYTHONPATH=src

python examples/load_packs.py
python examples/minimal_feed.py "verification"
python examples/fetch_remote_catalog.py rag
```

| Script | Purpose |
|--------|---------|
| `load_packs.py` | List local catalog |
| `minimal_feed.py` | Search packs and print grounded excerpts |
| `fetch_remote_catalog.py` | HTTPS fetch of public `index.json` |

No external API keys required for the default GitHub raw endpoints.
