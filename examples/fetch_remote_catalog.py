#!/usr/bin/env python3
"""Fetch the public OpenFeed catalog over HTTPS (no API key)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from openfeed.remote import DEFAULT_INDEX_URL, fetch_index, find_in_index  # noqa: E402


def main() -> int:
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    print(f"# GET {DEFAULT_INDEX_URL}", file=sys.stderr)
    index = fetch_index()
    rows = find_in_index(index, query=query) if query else list(index.get("packs") or [])
    print(json.dumps({"count": len(rows), "packs": rows}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
