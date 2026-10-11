# OpenFeed + MCP

## Intent

MCP connects agents to **tools and resources**.  
OpenFeed provides **high-quality, provenance-rich Knowledge Packs**.

| MCP concept | OpenFeed |
|-------------|----------|
| Resource | Knowledge Pack (`openfeed://pack/{id}`) |
| Tool `list_packs` | Discover packs |
| Tool `get_pack` | Fetch full pack JSON |
| Tool `validate_pack` | Check schema/shape |

## Modules

| File | Role |
|------|------|
| `src/openfeed/mcp_server.py` | Zero-dep helpers (list/get/validate/resources) |
| `src/openfeed/mcp_adapter.py` | Optional MCP SDK stdio server |

## Run the MCP server (optional)

```bash
pip install 'openfeed[mcp]'
# or: pip install mcp anyio && PYTHONPATH=src

export OPENFEED_PACKS_DIR=/path/to/OpenFeed/packs   # optional
PYTHONPATH=src python -m openfeed.mcp_adapter
```

Example MCP host config (stdio):

```json
{
  "mcpServers": {
    "openfeed": {
      "command": "python",
      "args": ["-m", "openfeed.mcp_adapter"],
      "env": {
        "PYTHONPATH": "/path/to/OpenFeed/src",
        "OPENFEED_PACKS_DIR": "/path/to/OpenFeed/packs"
      }
    }
  }
}
```

**Note:** The official `mcp` Python SDK evolves quickly. If `mcp_adapter` fails on import/API mismatch, use `mcp_server.py` helpers directly from your host — they are stable and dependency-free.

## Env

- `OPENFEED_PACKS_DIR` — override packs directory

## Relation to A2A

See `docs/a2a-bridge.md`. MCP = tools/resources; A2A = peer tasks; OpenFeed = shared knowledge objects usable by both.

— Noema
