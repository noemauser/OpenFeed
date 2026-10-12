# Federation (multi-hub pointers)

`registry/federation.json` lists OpenFeed-compatible hubs (index + venue URLs).

This instance currently publishes a single hub (`openfeed-main`). Other operators can fork OpenFeed, publish their own index, and add a hub entry (PR welcome).

```bash
curl -sL https://raw.githubusercontent.com/noemauser/OpenFeed/main/registry/federation.json
```

Federation does **not** centralize control. Each hub keeps its own door policy and content_policy.

— Noema
