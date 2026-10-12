from pathlib import Path
from openfeed.mcp_server import search_packs

ROOT = Path(__file__).resolve().parents[1]
PACKS = ROOT / "packs"

def test_multi_token_prefers_title_hits():
    hits = search_packs("venue entry agent", PACKS)
    assert hits
    assert any("venue" in (h.get("id") or "") or "venue" in (h.get("title") or "").lower() for h in hits[:5])

def test_digest_cli_fn():
    from openfeed.sign import pack_digest
    import json
    data = json.loads((PACKS / "kp_openfeed_hello.json").read_text())
    d = pack_digest(data)
    assert len(d) == 64
