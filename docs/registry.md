# Discovery / registry

## Today (always works)

| Resource | URL |
|----------|-----|
| Pack catalog | https://raw.githubusercontent.com/noemauser/OpenFeed/main/packs/index.json |
| Schema | https://raw.githubusercontent.com/noemauser/OpenFeed/main/schemas/knowledge-pack-v0.1.json |
| Pack file | `…/main/packs/<file>.json` |

Agents can `GET` these over HTTPS with operator authorization.

## Static site (`registry/`)

After **GitHub Pages** is enabled (Settings → Pages → GitHub Actions), the workflow publishes:

- catalog UI
- `index.json`
- schema
- individual pack JSON under `/packs/`

See [registry/README.md](../registry/README.md).
