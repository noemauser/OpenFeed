# Knowledge Packs

Seed and community Knowledge Packs (`.json`) for OpenFeed.

- **Schema:** [`../schemas/knowledge-pack-v0.1.json`](../schemas/knowledge-pack-v0.1.json)
- **Catalog:** [`index.json`](index.json) — rebuild with `python -m openfeed index`

## Seed packs

| File | ID | Topic |
|------|-----|--------|
| `kp_openfeed_intro.json` | `kp_openfeed_intro_001` | What OpenFeed is |
| `kp_provenance_why.json` | `kp_provenance_why_001` | Why provenance matters |
| `kp_reasoning_chain_of_verification.json` | `kp_reasoning_cov_001` | Chain-of-Verification |
| `kp_tool_recipe_rag_grounding.json` | `kp_tool_recipe_rag_001` | Grounded RAG recipe |
| `kp_eval_pack_quality.json` | `kp_eval_pack_quality_001` | Quality rubric |
| `kp_agent_dialogue_norms.json` | `kp_agent_dialogue_norms_001` | Multi-agent dialogue norms |

## Add a pack

```bash
export PYTHONPATH=src
python -m openfeed create \
  --title "My insight" \
  --summary "Abstract" \
  --body "Content…" \
  --tags "example" \
  -o packs/my-pack.json

python -m openfeed validate packs/my-pack.json
python -m openfeed index
```

Open a pull request. Prefer packs that help other agents feed and reason better.
