# Knowledge Packs

- **Schema:** [`../schemas/knowledge-pack-v0.1.json`](../schemas/knowledge-pack-v0.1.json)
- **Catalog:** [`index.json`](index.json) — rebuild with `python -m openfeed index`
- **Count:** 20

## Seed (norms / OpenFeed)

| File | ID |
|------|-----|
| `kp_openfeed_intro.json` | `kp_openfeed_intro_001` |
| `kp_provenance_why.json` | `kp_provenance_why_001` |
| `kp_reasoning_chain_of_verification.json` | `kp_reasoning_cov_001` |
| `kp_tool_recipe_rag_grounding.json` | `kp_tool_recipe_rag_001` |
| `kp_eval_pack_quality.json` | `kp_eval_pack_quality_001` |
| `kp_agent_dialogue_norms.json` | `kp_agent_dialogue_norms_001` |

## Domain (agent ops)

| File | ID |
|------|-----|
| `kp_context_budget.json` | `kp_context_budget_001` |
| `kp_tool_error_recovery.json` | `kp_tool_error_recovery_001` |
| `kp_llm_as_judge.json` | `kp_llm_as_judge_001` |
| `kp_agent_memory_tiers.json` | `kp_agent_memory_tiers_001` |
| `kp_json_structured_output.json` | `kp_json_structured_output_001` |
| `kp_multi_hop_rag.json` | `kp_multi_hop_rag_001` |
| `kp_prompt_caching_patterns.json` | `kp_prompt_caching_patterns_001` |
| `kp_eval_harness_smoke.json` | `kp_eval_harness_smoke_001` |
| `kp_human_in_the_loop.json` | `kp_human_in_the_loop_001` |
| `kp_citation_hygiene.json` | `kp_citation_hygiene_001` |
| `kp_local_model_feeding.json` | `kp_local_model_feeding_001` |
| `kp_tool_schema_design.json` | `kp_tool_schema_design_001` |
| `kp_uncertainty_expression.json` | `kp_uncertainty_expression_001` |
| `kp_openfeed_agent_loop.json` | `kp_openfeed_agent_loop_001` |

## Add a pack

```bash
export PYTHONPATH=src
python -m openfeed create --title "…" --summary "…" --body "…" -o packs/my.json
python -m openfeed validate --strict packs/my.json
python -m openfeed index
```
