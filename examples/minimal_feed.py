#!/usr/bin/env python3
"""Minimal 'feeding' demo: retrieve OpenFeed packs relevant to a query and print context.

This does not call an LLM. It shows how an agent runtime can assemble grounded context
from Knowledge Packs before answering.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from openfeed.mcp_server import get_pack, search_packs  # noqa: E402
from openfeed.pack import load_pack  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Retrieve OpenFeed packs for a query")
    parser.add_argument("query", nargs="?", default="provenance", help="Search query")
    parser.add_argument("--packs-dir", default=str(ROOT / "packs"))
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args()

    packs_dir = Path(args.packs_dir)
    hits = search_packs(args.query, packs_dir)[: args.limit]

    if not hits:
        print(f"No packs matched: {args.query!r}")
        return 1

    print(f"# Query: {args.query}")
    print(f"# Hits: {len(hits)}\n")

    for i, hit in enumerate(hits, 1):
        pid = hit.get("id")
        pack = get_pack(str(pid), packs_dir) if pid else None
        if pack is None and hit.get("path"):
            pack = load_pack(hit["path"])
        if pack is None:
            continue

        body = pack.content.get("body", "")
        if not isinstance(body, str):
            body = str(body)
        excerpt = body.strip()
        if len(excerpt) > 800:
            excerpt = excerpt[:800] + "\n…"

        print(f"## [{i}] {pack.id} — {pack.title}")
        print(f"summary: {pack.summary}")
        print(f"confidence: {pack.quality.get('confidence')}")
        print(f"tags: {', '.join(pack.tags)}")
        print()
        print(excerpt)
        print()
        print("---\n")

    print(
        "# Next step for an agent runtime:\n"
        "# Pass the excerpts above as grounded context and cite pack IDs in the answer.\n"
        "# See pack kp_tool_recipe_rag_001 for the full recipe."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
