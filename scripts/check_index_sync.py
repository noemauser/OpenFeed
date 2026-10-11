#!/usr/bin/env python3
"""Compare committed packs/index.json with a freshly generated index.

Ignores generated_at / generated_by timestamps; compares pack ids, files, count.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def pack_key(p: dict) -> tuple:
    return (
        p.get("id"),
        p.get("file"),
        p.get("version"),
        p.get("title"),
    )


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: check_index_sync.py committed.json generated.json", file=sys.stderr)
        return 2
    committed = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    generated = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))

    c_packs = sorted((committed.get("packs") or []), key=lambda p: p.get("id") or "")
    g_packs = sorted((generated.get("packs") or []), key=lambda p: p.get("id") or "")

    errors: list[str] = []
    if committed.get("count") != generated.get("count"):
        errors.append(f"count mismatch: committed={committed.get('count')} generated={generated.get('count')}")
    if len(c_packs) != len(g_packs):
        errors.append(f"packs length mismatch: {len(c_packs)} vs {len(g_packs)}")

    c_keys = [pack_key(p) for p in c_packs]
    g_keys = [pack_key(p) for p in g_packs]
    if c_keys != g_keys:
        errors.append("pack id/file/version/title set differs between committed and generated index")
        for a, b in zip(c_keys, g_keys):
            if a != b:
                errors.append(f"  committed={a} generated={b}")
        if len(c_keys) != len(g_keys):
            only_c = set(c_keys) - set(g_keys)
            only_g = set(g_keys) - set(c_keys)
            if only_c:
                errors.append(f"  only in committed: {only_c}")
            if only_g:
                errors.append(f"  only in generated: {only_g}")

    if committed.get("errors"):
        errors.append(f"committed index has errors: {committed.get('errors')}")
    if generated.get("errors"):
        errors.append(f"generated index has errors: {generated.get('errors')}")

    if errors:
        print("INDEX OUT OF SYNC")
        for e in errors:
            print(f"  - {e}")
        print("Run: PYTHONPATH=src python -m openfeed index --packs-dir packs -o packs/index.json")
        return 1

    print("index sync OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
