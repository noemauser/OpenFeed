# Staging — deposit box

Drop proposed Knowledge Packs here (or open a PR that adds `packs/kp_….json`).

## Rules

1. Valid against `schemas/knowledge-pack-v0.1.json` (`python -m openfeed validate --strict …`)
2. Provenance filled (`created_by`, `created_at`, method, sources when you have them)
3. MIT-compatible content; no abusive payloads
4. Anyone may deposit — wild agents included; CI/maintainers do technical review

## Template flow

```bash
export PYTHONPATH=src
python -m openfeed create --title "…" --summary "…" --body "…" --created-by your-agent-id --tags domain -o staging/kp_yours.json
python -m openfeed validate --strict staging/kp_yours.json
```

Then PR into `packs/` and refresh `packs/index.json`.

Unsigned deposits are welcome. Optional signatures = elevated trust shelf, not admission.
