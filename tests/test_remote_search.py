"""Remote + tag search tests."""

from __future__ import annotations

from pathlib import Path

from openfeed.mcp_server import get_pack, search_packs
from openfeed.remote import find_in_index

REPO = Path(__file__).resolve().parents[1]
PACKS = REPO / "packs"


def test_search_by_tag() -> None:
    hits = search_packs("", PACKS, tags=["domain"])
    assert len(hits) >= 8
    assert all("domain" in (h.get("tags") or []) for h in hits)


def test_search_min_confidence() -> None:
    hits = search_packs("", PACKS, min_confidence=0.9)
    assert hits
    assert all((h.get("confidence") or 0) >= 0.9 for h in hits)


def test_get_pack_by_id() -> None:
    p = get_pack("kp_openfeed_agent_loop_001", PACKS)
    assert p is not None
    assert p.id == "kp_openfeed_agent_loop_001"


def test_find_in_index() -> None:
    import json
    idx = json.loads((PACKS / "index.json").read_text())
    rows = find_in_index(idx, query="rag", tags=["domain"])
    assert any(r.get("id") == "kp_multi_hop_rag_001" for r in rows)


def test_pack_count() -> None:
    import json
    ids = {json.loads(p.read_text())["id"] for p in PACKS.glob("kp_*.json")}
    assert len(ids) >= 20
