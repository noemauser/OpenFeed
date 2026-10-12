import json
from pathlib import Path
from openfeed.a2a import MIME_PACK_REF, pack_ref, parse_peer_message, venue_pointer, wrap_pack
from openfeed.mcp_server import get_pack

ROOT = Path(__file__).resolve().parents[1]


def test_pack_ref_shape():
    ref = pack_ref("kp_openfeed_hello_001", file="kp_openfeed_hello.json", digest="abc")
    assert ref["openfeed_pack_id"] == "kp_openfeed_hello_001"
    assert ref["uri"].startswith("openfeed://pack/")
    assert ref["mime"] == MIME_PACK_REF


def test_parse_message():
    ref = pack_ref("kp_openfeed_hello_001")
    msg = {"parts": [{"mimeType": MIME_PACK_REF, "data": ref}, {"mimeType": "application/vnd.openfeed.venue+json", "data": venue_pointer()}]}
    out = parse_peer_message(msg)
    assert out["count"] >= 2
    kinds = {p["kind"] for p in out["parts"]}
    assert "pack_ref" in kinds
    assert "venue_pointer" in kinds


def test_wrap_pack():
    pack = get_pack("kp_openfeed_hello_001", ROOT / "packs")
    assert pack is not None
    env = wrap_pack(pack)
    assert "pack" in env
    assert env["pack"]["id"] == "kp_openfeed_hello_001"
