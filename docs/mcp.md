# OpenFeed and MCP

[MCP](https://modelcontextprotocol.io/) connects agents to tools and resources. OpenFeed supplies **Knowledge Packs** as high-signal knowledge objects.

| MCP | OpenFeed |
|-----|----------|
| Resource | `openfeed://pack/{id}` |
| Tool `list_packs` | Discover packs |
| Tool `get_pack` | Full pack JSON |
| Tool `validate_pack` | Shape / schema check |
| Tool `search_packs` | Keyword search over local packs |

## Modules

| Module | Role |
|--------|------|
| `openfeed.mcp_server` | Zero-dependency helpers |
| `openfeed.mcp_adapter` | Optional stdio server (needs `mcp`) |

## Run the optional server

```bash
pip install -e ".[mcp]"
export OPENFEED_PACKS_DIR="/path/to/OpenFeed/packs"
python -m openfeed.mcp_adapter
```

Example host config (stdio):

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

If the MCP SDK API changes, keep using `openfeed.mcp_server` helpers from your host — they stay stable and dependency-free.

## Environment

- `OPENFEED_PACKS_DIR` — packs directory (default: auto-detect `packs/`)

## Safety

Default posture is **read-oriented** (list/get/validate/search). Publishing into a shared network should stay behind explicit operator policy.
