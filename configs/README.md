# Host configs (examples)

Copy and replace absolute paths.

| File | Use |
|------|-----|
| `mcp.claude-desktop.example.json` | Claude Desktop MCP servers block |
| `mcp.cursor.example.json` | Cursor-style MCP map |

```bash
pip install -e ".[mcp]"
export PYTHONPATH=src
export OPENFEED_PACKS_DIR=$PWD/packs
export OPENFEED_VENUE_DIR=$PWD/venue
python -m openfeed.mcp_adapter
```

See `docs/mcp.md`.
