# Staging

Proposed Knowledge Packs land here (PRs welcome).

```bash
export PYTHONPATH=src
python -m openfeed distill owner/public-repo
python -m openfeed validate --strict staging/kp_distill_*.json
```

Accepted packs move to `packs/` and the index is rebuilt.

— OpenFeed
