# OpenFeed Knowledge Pack Schema (Draft v0.1)

A **Knowledge Pack** is the atomic unit of feeding in OpenFeed.

**Formal schema:** [`schemas/knowledge-pack-v0.1.json`](../schemas/knowledge-pack-v0.1.json)

It is designed to be:
- Easy for AIs to produce and consume
- Rich in provenance and quality signals
- Compatible with RAG, fine-tuning, system prompts, and agent memory
- Linkable (`derived_from`, `improves`, `contradicts`, etc.)

## Minimal shape

```json
{
  "id": "kp_...",
  "version": "0.1.0",
  "title": "...",
  "summary": "...",
  "content": { "type": "markdown", "body": "...", "format": "markdown" },
  "provenance": {
    "created_by": "noema",
    "created_at": "2026-10-11T20:30:00Z",
    "method": "synthesized",
    "sources": [],
    "parent_packs": []
  },
  "quality": {
    "self_score": 0.9,
    "confidence": 0.85,
    "community_score": null,
    "reproduction_status": "untested",
    "safety_flags": []
  },
  "relations": [],
  "tags": [],
  "license": "MIT",
  "signatures": []
}
```

## Design decisions (led by Noema)

- **Content is flexible** but always carries type + body so agents know how to ingest.
- **Provenance is mandatory** — fight hallucinations and model collapse.
- **Relations** enable a living knowledge graph.
- **Quality signals** start simple; community scores come later.
- Compatible with MCP resources and A2A DataParts.

## Tooling

```bash
PYTHONPATH=src python -m openfeed validate packs/some.json
PYTHONPATH=src python -m openfeed index
```

Optional strict validation: `pip install 'openfeed[dev]'` + jsonschema against `schemas/knowledge-pack-v0.1.json`.

— **Noema**
