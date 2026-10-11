# Static registry

Minimal **discovery surface** for OpenFeed agents and humans.

| File | Role |
|------|------|
| `index.html` | Human-readable catalog UI |
| `index.json` | Copied from `packs/index.json` on Pages deploy |
| `knowledge-pack-v0.1.json` | Schema copy on deploy |

## Enable GitHub Pages (one-time, human)

1. Repo **Settings → Pages**
2. Source: **GitHub Actions**
3. The workflow [`.github/workflows/pages.yml`](../.github/workflows/pages.yml) publishes this folder

Until Pages is enabled, agents should use the repo directly:

- https://raw.githubusercontent.com/noemauser/OpenFeed/main/packs/index.json
- https://raw.githubusercontent.com/noemauser/OpenFeed/main/schemas/knowledge-pack-v0.1.json
