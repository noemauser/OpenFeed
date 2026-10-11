#!/usr/bin/env python3
"""Build packs/index.json from all Knowledge Packs in packs/.

Run from repo root:
  PYTHONPATH=src python scripts/build_index.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from openfeed.mcp_server import list_packs  # noqa: E402
from openfeed.pack import validate_pack  # noqa: E402


def main() -> int:
    packs_dir = ROOT / "packs"
    metas = list_packs(packs_dir)
    entries = []
    errors = []

    for m in metas:
        if "error" in m:
            errors.append(m)
            continue
        path = Path(m["path"])
        data = json.loads(path.read_text(encoding="utf-8"))
        verrs = validate_pack(data)
        if verrs:
            errors.append({"path": str(path), "validation": verrs})
        entries.append(
            {
                "id": data.get("id"),
                "version": data.get("version"),
                "title": data.get("title"),
                "summary": data.get("summary"),
                "tags": data.get("tags", []),
                "license": data.get("license"),
                "created_by": (data.get("provenance") or {}).get("created_by"),
                "created_at": (data.get("provenance") or {}).get("created_at"),
                "quality": {
                    "self_score": (data.get("quality") or {}).get("self_score"),
                    "confidence": (data.get("quality") or {}).get("confidence"),
                },
                "file": path.name,
                "uri": f"openfeed://pack/{data.get('id')}",
            }
        )

    index = {
        "openfeed_index_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "generated_by": "noema",
        "count": len(entries),
        "packs": sorted(entries, key=lambda e: e.get("id") or ""),
        "errors": errors,
    }

    out = packs_dir / "index.json"
    out.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out} with {len(entries)} packs ({len(errors)} errors)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
