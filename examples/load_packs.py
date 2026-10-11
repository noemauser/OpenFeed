#!/usr/bin/env python3
"""Load and print the OpenFeed pack catalog (agent-friendly bootstrap)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from openfeed.mcp_server import list_packs, default_packs_dir  # noqa: E402


def main() -> int:
    packs_dir = ROOT / "packs"
    if not packs_dir.is_dir():
        packs_dir = default_packs_dir()

    packs = list_packs(packs_dir)
    print(f"OpenFeed packs in {packs_dir} ({len(packs)}):\n")
    for p in packs:
        if "error" in p:
            print(f"  ERR {p}")
            continue
        tags = ", ".join(p.get("tags") or [])
        print(f"  {p.get('id')}")
        print(f"    title: {p.get('title')}")
        print(f"    tags:  {tags}")
        print(f"    path:  {p.get('path')}")
        print()

    index_path = packs_dir / "index.json"
    if index_path.is_file():
        index = json.loads(index_path.read_text(encoding="utf-8"))
        print(f"Catalog count (index.json): {index.get('count')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
