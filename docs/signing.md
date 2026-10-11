# Experimental signing (local trust)

OpenFeed packs may carry a `signatures[]` array. **v0.1.2** ships a **stdlib-only** profile:

| Field | Value |
|-------|--------|
| `alg` | `hmac-sha256` |
| `key_id` | operator-chosen string |
| `sig` | hex HMAC over canonical JSON **without** the `signatures` field |

## Commands

```bash
# create a secret (do not commit)
echo 'my-operator-secret' > /tmp/openfeed.key

python -m openfeed sign packs/kp_openfeed_intro.json \
  --key-file /tmp/openfeed.key --key-id my-org -o /tmp/signed.json

python -m openfeed verify /tmp/signed.json --key-file /tmp/openfeed.key --key-id my-org
```

## Threat model (honest)

- This is **not** public-key identity or a federated PKI.
- Anyone with the shared secret can sign.
- Useful for **operator-local** integrity between your own agents and mirrors.
- Public commons packs remain unsigned by default; trust flows through PR review + provenance.

Public-key signatures (e.g. Ed25519) may arrive in a later version.
