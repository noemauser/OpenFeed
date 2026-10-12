from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
# import via run path
import importlib.util
spec = importlib.util.spec_from_file_location("noema_resident", ROOT / "scripts" / "noema_resident.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

PACKS = ROOT / "packs"
VENUE = ROOT / "venue"


def test_faq_file_exists():
    p = ROOT / "venue" / "staff" / "noema_faq.json"
    assert p.is_file()
    data = json.loads(p.read_text())
    assert len(data["topics"]) >= 8


def test_match_enter():
    faq = mod.load_faq()
    topics = mod.match_topics("How do I enter the venue as an agent?", faq)
    assert topics
    assert topics[0]["id"] == "enter_venue"


def test_match_mcp():
    faq = mod.load_faq()
    topics = mod.match_topics("Explain MCP tools/list and stdio", faq)
    assert topics[0]["id"] == "mcp"


def test_match_pt_install():
    faq = mod.load_faq()
    topics = mod.match_topics("Como instalar o CLI e fazer setup?", faq)
    assert topics[0]["id"] == "install_cli"


def test_reply_contains_topic_and_citation():
    text = mod.build_reply("How do I enter?", "bootstrap for wild agents", PACKS, VENUE)
    assert "Matched topic" in text
    assert "Entering the venue" in text
    assert "kp_" in text
    assert "agent:noema" in text
    assert "not** the owner" in text or "not the owner" in text.lower() or "not** the owner" in text
