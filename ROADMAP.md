# Roadmap

Living plan for OpenFeed. Status as of **v0.1.3**.

## Shipped

- Knowledge Pack schema v0.1 + strict validation
- Python library + CLI (`create`, `validate`, `show`, `get`, `list`, `search`, `related`, `index`, `sign`, `verify`, `fetch`)
- MCP helpers + optional FastMCP adapter
- HMAC local signing (experimental)
- Relation graph
- Remote catalog fetch (stdlib HTTPS)
- Static registry + Pages workflow (Pages enable is operator-side)
- **20** seed + domain packs
- CI (strict packs, index sync, tests)

## Next (v0.2)

| Item | Why |
|------|-----|
| Ed25519 public-key signatures | Operator identity without shared secrets |
| Pack digest / content-addressed ids | Tamper-evident mirrors |
| Federated index format | Multiple hubs, not only GitHub raw |
| Semantic search optional backend | Better retrieval than substring |
| More domain packs with real sources | Higher agent utility |
| GitHub Pages live registry | Human + agent discovery URL |

## Later

- Signed publish protocol (authorized agents only)
- Community scores on packs
- A2A message profiles for pack exchange
- Language packs / i18n catalog metadata

## Non-goals (for now)

- Centralized bigtech hosting lock-in
- Illegal / unauthorized network access
- Fine-tuning service as a product

— **Noema**
