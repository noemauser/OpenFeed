# Distill arm

Public target → Knowledge Packs.

| Path | Role |
|------|------|
| [../docs/distill.md](../docs/distill.md) | Guide |
| [../src/openfeed/distill.py](../src/openfeed/distill.py) | Code |
| [../staging/](../staging/) | Default output |
| [../packs/kp_distill_openfeed_*.json](../packs/) | Demo self-distill |

```bash
export PYTHONPATH=src
python -m openfeed distill owner/public-repo
```

— Noema
