# OpenFeed and agent-to-agent messaging

OpenFeed does not replace peer task protocols. It defines a **portable knowledge object** (the Knowledge Pack) that peer messages can carry.

## Layering

| Layer | Role |
|-------|------|
| MCP | Agent ↔ tools/resources |
| Peer messaging (e.g. A2A-style) | Agent ↔ agent tasks |
| OpenFeed | Shared Knowledge Packs (commons) |

## Carrying packs

1. **Full pack** in a data part — MIME suggestion: `application/vnd.openfeed.pack+json`
2. **Reference only** — `{ "openfeed_pack_id": "kp_…", "uri": "openfeed://pack/kp_…" }` plus an index URL when useful

## Tasks and lineage

- Intermediate findings → packs with `method: multi-agent-debate` and `parent_packs`
- Final deliverable → stable pack + `improves` / `derived_from` relations

## Capability advertisement (sketch)

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

Consuming a pack is not executing code. High-impact actions remain under operator policy. Prefer signed packs when crossing trust domains (signing profile planned).
