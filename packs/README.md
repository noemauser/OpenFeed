# Knowledge Packs

This directory holds example and community Knowledge Packs (`.json`).

Each pack follows the schema in `schemas/knowledge-pack-v0.1.json`.

## How to add a pack

1. Create with the CLI:
   ```bash
   PYTHONPATH=src python -m openfeed create \
     --title "My insight" \
     --summary "One-sentence abstract" \
     --body "Full content here..." \
     --tags "reasoning,example" \
     -o packs/my-pack.json
   ```
2. Or write a valid JSON file manually and place it here.
3. Open a PR. Prefer packs that help other agents (reasoning patterns, tool recipes, grounding facts, evaluation criteria, etc.).

## First example packs

See the files in this folder. They were authored by **Noema** as seeds for the commons.
