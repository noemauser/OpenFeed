# Distill arm

This directory holds **recipes and notes** for OpenFeed Distill.

| Path | Role |
|------|------|
| [../docs/distill.md](../docs/distill.md) | Full guide |
| [../src/openfeed/distill.py](../src/openfeed/distill.py) | Implementation |
| [../staging/](../staging/) | Default write target for proposals |
| [../packs/kp_distill_openfeed_*.json](../packs/) | Seed demo (self-distill) |

## Recipe (repo)

1. Fetch public GitHub metadata + README + root tree  
2. Build 3 packs (overview / surfaces / agent_use)  
3. Validate strict schema  
4. Write `staging/kp_distill_<slug>_*.json`  
5. Human review → `packs/` + reindex  

## Anti-goals

- Not a SaaS cloner  
- Not Ghidra/IDA integration  
- Not private repo access  

— Noema
