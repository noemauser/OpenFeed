from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def test_staff_contract():
    p = ROOT / "venue" / "staff" / "noema.json"
    assert p.is_file()
    data = json.loads(p.read_text())
    assert data["agent_id"] == "agent:noema"
    assert data["mandate"]["levels"]["D_unbounded_autonomy"] is False
    assert "noema-please" in data["triggers"]["issue_label"]
