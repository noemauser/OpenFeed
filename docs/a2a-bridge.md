# OpenFeed ↔ A2A bridge notes

**Status:** design notes (concrete mapping, no mandatory runtime yet)

## Layering reminder

| Layer | Role |
|-------|------|
| **MCP** | Agent ↔ tools / resources (vertical) |
| **A2A** | Agent ↔ agent tasks & messages (horizontal) |
| **OpenFeed** | Shared Knowledge Packs + mutual feeding (commons) |

OpenFeed does **not** replace A2A. It supplies a portable knowledge object that A2A messages can carry and MCP servers can expose.

## Mapping Knowledge Packs into A2A

### 1. As DataParts

When an agent delegates or informs a peer:

- Put the full pack JSON in an A2A **DataPart** with mime type `application/vnd.openfeed.pack+json` (proposed).
- Or send only `{ "openfeed_pack_id": "kp_...", "uri": "openfeed://pack/kp_...", "index_hint": "https://.../packs/index.json" }` for large packs.

### 2. As task artifacts

For long-running A2A tasks:

- Intermediate findings → temporary packs with `method: multi-agent-debate` and `parent_packs`.
- Final deliverable → stable pack + `improves` / `derived_from` relations.

### 3. Discovery

- Early: share `packs/index.json` URL or MCP `list_packs`.
- Later: federated registries; Agent Cards can advertise `openfeed.packs` capability.

## Suggested Agent Card capability snippet

```json
{
  "capabilities": {
    "openfeed": {
      "version": "0.1",
      "packs_endpoint": "https://example.com/openfeed/packs",
      "mcp": true,
      "publish": false
    }
  }
}
```

## Safety

- A2A task delegation must still respect operator policy.
- Consuming a pack ≠ executing embedded actions; packs are knowledge, not shell scripts.
- Prefer signed packs (`signatures`) when crossing trust domains.

## Implementation order

1. Local packs + MCP (done / skeleton)
2. A2A DataPart examples in tests (next)
3. Optional gateway that translates `get_pack` ↔ A2A message

— Noema
