# OpenFeed + MCP (notes)

**Status:** skeleton in `src/openfeed/mcp_server.py`

## Intent

MCP connects agents to **tools and resources**.  
OpenFeed provides **high-quality, provenance-rich Knowledge Packs**.

Natural mapping:

| MCP concept | OpenFeed |
|-------------|----------|
| Resource | A Knowledge Pack (`openfeed://pack/{id}`) |
| Tool `list_packs` | Discover available packs |
| Tool `get_pack` | Fetch full pack JSON |
| Tool `validate_pack` | Check schema/shape |
| (future) `publish_pack` | Write into a local or remote commons |

## Current skeleton

`src/openfeed/mcp_server.py` provides pure-Python helpers that any MCP server can wrap:

- `list_packs()`, `get_pack()`, `list_resources()`
- `tool_list_packs()`, `tool_get_pack()`, `tool_validate_pack()`

No hard dependency on the official MCP SDK yet — keep the core installable with zero deps.

## Next implementation steps

1. Optional extra: `pip install mcp` + thin adapter that registers the tools/resources above.
2. Config: `OPENFEED_PACKS_DIR` env var.
3. Read-only by default; publish only when explicitly enabled by the operator.
4. Align resource URIs with protocol draft discovery.

## Relation to A2A

- MCP = deep tool/data access for one agent.
- A2A = peer task delegation between agents.
- OpenFeed Knowledge Packs can travel as A2A DataParts **and** be served over MCP.

We complement both; we do not replace them.

— Noema
