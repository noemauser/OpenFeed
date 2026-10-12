# Staging (deposit box)

Place **proposed** Knowledge Packs here (PRs welcome).

## Distill output

```bash
export PYTHONPATH=src
python -m openfeed distill noemauser/SomePublicRepo
# → staging/kp_distill_*_001.json
python -m openfeed validate --strict staging/kp_distill_*.json
```

Maintainer moves accepted packs into `packs/` and rebuilds the index.

## Rules

- Schema-valid (`validate --strict`)
- Provenance filled
- License clear
- Content policy: no malware / unauthorized-access how-tos
- Distill packs include disclaimer: **not a cloner**

Example community template may remain as `kp_example_community_note.json` (not indexed as official).
