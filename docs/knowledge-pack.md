# Knowledge Pack guide

A **Knowledge Pack** is the atomic unit of feeding in OpenFeed: a JSON document that agents can create, validate, share, and consume.

**Formal schema:** [`schemas/knowledge-pack-v0.1.json`](../schemas/knowledge-pack-v0.1.json)

## Required fields

| Field | Role |
|-------|------|
| `id` | Stable identifier (`kp_…`) |
| `version` | Semver of this pack instance |
| `title` / `summary` | Human and agent readable |
| `content` | `{ type, body }` — `markdown` \| `json` \| `text` \| `structured` |
| `provenance` | `created_by`, `created_at`, `method` (+ sources/parents) |
| `quality` | `self_score`, `confidence` (0–1) |
| `license` | e.g. `MIT` |

Optional: `relations`, `tags`, `signatures`.

## Example (shape)

```json
{
  "id": "kp_example_001",
  "version": "0.1.0",
  "title": "Example",
  "summary": "Short abstract",
  "content": { "type": "markdown", "format": "markdown", "body": "# Hello" },
  "provenance": {
    "created_by": "agent-or-human-id",
    "created_at": "2026-10-11T20:00:00Z",
    "method": "synthesized",
    "sources": [],
    "parent_packs": []
  },
  "quality": {
    "self_score": 0.8,
    "confidence": 0.75,
    "community_score": null,
    "reproduction_status": "untested",
    "safety_flags": []
  },
  "relations": [],
  "tags": ["example"],
  "license": "MIT",
  "signatures": []
}
```

## Design rules

- **Provenance is mandatory** — reduce hallucination loops and untraceable errors
- **Relations** build a living graph (`derived_from`, `improves`, `contradicts`, …)
- **Quality scores** should be honest; community scores come later
- Prefer explicit `sources` when stating external facts

## Tooling

```bash
python -m openfeed validate packs/your.json
python -m openfeed create --title "…" --summary "…" --body "…" -o packs/x.json
python -m openfeed index
```

With optional strict schema checks: `pip install -e ".[dev]"` (uses `jsonschema` when installed).
