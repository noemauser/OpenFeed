"""Graph + HMAC sign tests."""

from __future__ import annotations

import json
from pathlib import Path

from openfeed.graph import related_packs
from openfeed.pack import create_pack
from openfeed.sign import sign_pack_dict, verify_pack_dict

REPO = Path(__file__).resolve().parents[1]
PACKS = REPO / "packs"


def test_related_intro() -> None:
    r = related_packs("kp_openfeed_intro_001", PACKS)
    assert r["ok"] is True
    assert r["id"] == "kp_openfeed_intro_001"


def test_related_domain_links() -> None:
    r = related_packs("kp_multi_hop_rag_001", PACKS)
    assert r["ok"] is True
    targets = {x.get("target") for x in r.get("outgoing") or []}
    assert "kp_tool_recipe_rag_001" in targets


def test_hmac_sign_verify(tmp_path: Path) -> None:
    pack = create_pack(title="t", summary="s", body="b", pack_id="kp_test_sign")
    d = pack.to_dict()
    key = b"test-secret-key"
    signed = sign_pack_dict(d, key, key_id="ci")
    assert signed["signatures"]
    assert verify_pack_dict(signed, key, key_id="ci") == []
    signed["title"] = "tampered"
    assert verify_pack_dict(signed, key, key_id="ci") != []


def test_domain_packs_present() -> None:
    ids = {json.loads(p.read_text())["id"] for p in PACKS.glob("kp_*.json")}
    assert "kp_context_budget_001" in ids
    assert "kp_multi_hop_rag_001" in ids
    assert "kp_openfeed_agent_loop_001" in ids
    assert len(ids) >= 20
