# Examples

Runnable demos of consuming OpenFeed Knowledge Packs.

```bash
cd /path/to/OpenFeed
export PYTHONPATH=src

python examples/load_packs.py
python examples/minimal_feed.py "verification"
python examples/minimal_feed.py "RAG" --limit 2
```

| Script | Purpose |
|--------|---------|
| `load_packs.py` | List local catalog |
| `minimal_feed.py` | Search packs and print grounded excerpts for a query |

These scripts do **not** call external APIs. Wire the printed context into your model host as you prefer.
