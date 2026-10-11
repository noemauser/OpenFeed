"""Pack relation graph helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .mcp_server import get_pack, iter_pack_files


def load_all_packs(packs_dir: Path | None = None) -> dict[str, dict[str, Any]]:
    """Map pack id -> raw dict."""
    out: dict[str, dict[str, Any]] = {}
    for path in iter_pack_files(packs_dir):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            pid = data.get("id")
            if pid:
                data["_path"] = str(path)
                out[str(pid)] = data
        except Exception:
            continue
    return out


def related_packs(
    pack_id: str,
    packs_dir: Path | None = None,
    *,
    depth: int = 1,
) -> dict[str, Any]:
    """Return outgoing/incoming relations for a pack (depth 1 by default)."""
    all_packs = load_all_packs(packs_dir)
    if pack_id not in all_packs:
        # try resolve via get_pack for filename stems
        pack = get_pack(pack_id, packs_dir)
        if pack is None:
            return {"ok": False, "error": f"pack not found: {pack_id}"}
        pack_id = pack.id
        if pack_id not in all_packs:
            all_packs[pack_id] = pack.to_dict()

    center = all_packs[pack_id]
    outgoing = list(center.get("relations") or [])

    incoming: list[dict[str, str]] = []
    for pid, data in all_packs.items():
        if pid == pack_id:
            continue
        for rel in data.get("relations") or []:
            if rel.get("target") == pack_id:
                incoming.append({"from": pid, "type": rel.get("type", "related")})

    neighbors: dict[str, dict[str, Any]] = {}
    targets = {r.get("target") for r in outgoing if r.get("target")}
    targets |= {i["from"] for i in incoming}
    for t in targets:
        if t in all_packs:
            d = all_packs[t]
            neighbors[t] = {
                "id": t,
                "title": d.get("title"),
                "summary": d.get("summary"),
                "tags": d.get("tags", []),
            }

    result: dict[str, Any] = {
        "ok": True,
        "id": pack_id,
        "title": center.get("title"),
        "outgoing": outgoing,
        "incoming": incoming,
        "neighbors": neighbors,
    }

    if depth > 1:
        # shallow expansion of neighbor titles only (no deep recursion explosion)
        result["depth"] = depth
    return result
