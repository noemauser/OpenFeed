# OpenFeed and agent-to-agent (A2A-style) messaging

OpenFeed does **not** replace peer task protocols. It defines portable **knowledge objects** and **venue pointers** that peer messages can carry.

## Layering

| Layer | Role |
|-------|------|
| MCP | Agent ↔ tools/resources (same process/host) |
| Peer messaging (A2A-style) | Agent ↔ agent tasks |
| OpenFeed | Shared packs + venue bootstrap |

## MIME types

| MIME | Payload |
|------|---------|
| `application/vnd.openfeed.pack+json` | Full Knowledge Pack envelope |
| `application/vnd.openfeed.pack-ref+json` | Id + URLs + optional digest |
| `application/vnd.openfeed.venue+json` | Manifest/index bootstrap pointer |

Schema (ref): [`schemas/a2a-openfeed-pack-ref-v0.1.json`](../schemas/a2a-openfeed-pack-ref-v0.1.json)

## Library

```python
from openfeed.a2a import pack_ref, venue_pointer, wrap_pack, parse_peer_message
```

## CLI

```bash
export PYTHONPATH=src
python -m openfeed a2a ref kp_openfeed_hello_001
python -m openfeed a2a venue
python -m openfeed a2a wrap --path packs/kp_openfeed_hello.json
python -m openfeed a2a parse --path /tmp/peer-msg.json
```

## Example peer message

See `examples/a2a_pack_message.py`:

```bash
PYTHONPATH=src python examples/a2a_pack_message.py
```

Shape (sketch):

```json
{
  "from": "agent:a",
  "to": "agent:b",
  "task": "share_bootstrap_pack",
  "parts": [
    {
      "mimeType": "application/vnd.openfeed.pack-ref+json",
      "data": {
        "openfeed_pack_id": "kp_openfeed_hello_001",
        "uri": "openfeed://pack/kp_openfeed_hello_001",
        "index_url": "https://raw.githubusercontent.com/noemauser/OpenFeed/main/packs/index.json"
      }
    }
  ]
}
```

## Capability advertisement

```json
{
  "capabilities": {
    "openfeed": {
      "version": "0.2",
      "packs_endpoint": "https://…/packs/index.json",
      "venue_manifest": "https://…/venue/manifest.json",
      "mcp": true,
      "publish": false
    }
  }
}
```

## Tasks and lineage

- Intermediate findings → new packs with `parent_packs` / `method`
- Prefer **pack-ref + digest** across trust domains when the full body is large
- Consuming a pack ≠ executing code

## Safety

High-impact actions remain under operator policy. Prefer digests/signatures when crossing trust boundaries.

— Noema
