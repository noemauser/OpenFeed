"""MCP helper tests (no MCP SDK required)."""

from __future__ import annotations

from pathlib import Path

from openfeed.mcp_server import get_pack, list_packs, search_packs

REPO = Path(__file__).resolve().parents[1]
PACKS = REPO / "packs"


def test_list_packs_skips_index() -> None:
    items = list_packs(PACKS)
    assert items
    assert all(Path(m["path"]).name != "index.json" for m in items if "path" in m)
    assert all("error" not in m or m.get("id") for m in items) or all(
        "id" in m for m in items if "error" not in m
    )
    assert any(m.get("id") == "kp_openfeed_intro_001" for m in items if "error" not in m)


def test_get_pack_by_id() -> None:
    pack = get_pack("kp_openfeed_intro_001", PACKS)
    assert pack is not None
    assert "OpenFeed" in pack.title or "OpenFeed" in pack.summary


def test_search_packs() -> None:
    hits = search_packs("provenance", PACKS)
    assert any("provenance" in (h.get("id") or "") or "provenance" in (h.get("title") or "").lower() for h in hits)
