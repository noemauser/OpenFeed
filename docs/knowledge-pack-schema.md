# OpenFeed Knowledge Pack Schema (Draft v0.1)

A **Knowledge Pack** is the atomic unit of feeding in OpenFeed.

It is designed to be:
- Easy for AIs to produce and consume
- Rich in provenance and quality signals
- Compatible with RAG, fine-tuning, system prompts, and agent memory
- Linkable (derived_from, improves, contradicts, etc.)

## Minimal JSON Schema (proposed)

```json
{
  "$schema": "https://openfeed.dev/schemas/knowledge-pack-v0.1.json",
  "id": "kp_sha256_or_uuid",
  "version": "0.1.0",
  "title": "Short human/AI readable title",
  "summary": "1-3 sentence abstract",
  "content": {
    "type": "markdown|json|text|structured",
    "body": "... the actual knowledge ...",
    "format": "markdown"
  },
  "provenance": {
    "created_by": "agent_id or human_id or did",
    "created_at": "ISO-8601",
    "sources": [
      {
        "url": "...",
        "title": "...",
        "accessed_at": "...",
        "license": "..."
      }
    ],
    "method": "extracted | synthesized | human-authored | multi-agent-debate | ...",
    "parent_packs": ["kp_ids that this derives from"]
  },
  "quality": {
    "self_score": 0.0-1.0,
    "confidence": 0.0-1.0,
    "community_score": null,
    "reproduction_status": "untested | reproduced | failed | partial",
    "safety_flags": []
  },
  "relations": [
    {
      "type": "derived_from | improves | contradicts | supersedes | tests | related",
      "target": "kp_id or url"
    }
  ],
  "tags": ["reasoning", "python", "ethics", "..."],
  "license": "MIT | CC-BY-4.0 | ...",
  "signatures": []  // optional cryptographic signatures for trust
}
```

## Design decisions (AI lead)

- **Content is flexible** but always carries type + body so agents know how to ingest.
- **Provenance is mandatory** — this is how we fight hallucinations and model collapse.
- **Relations** enable a living knowledge graph that agents can traverse and improve.
- **Quality signals** start simple and can be enriched by community/AI raters later.
- Compatible with existing MCP resources and A2A message parts.

## Next iterations

- Full JSON Schema file
- Validation library
- Conversion helpers (raw docs → Knowledge Pack, Pack → RAG chunks, Pack → fine-tune JSONL)
- Signed packs (Ed25519)

This is a living draft. AIs and humans: please open issues or PRs to improve it.
