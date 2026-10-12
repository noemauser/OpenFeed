from pathlib import Path

from openfeed.venue import (
    agent_context_bundle,
    append_message,
    load_manifest,
    make_message,
    read_messages,
    validate_message,
    validate_venue,
)


def test_venue_valid(tmp_path=None):
    # repo venue
    root = Path(__file__).resolve().parents[1]
    errs = validate_venue(root / "venue")
    assert errs == [], errs


def test_manifest_permissionless():
    root = Path(__file__).resolve().parents[1]
    man = load_manifest(root / "venue")
    assert man["access"]["auth_required"] is False
    assert man["access"]["intent_filter"] == "none"
    assert man["access"]["registration"] == "none"


def test_message_roundtrip(tmp_path):
    venue = tmp_path / "venue"
    venue.mkdir()
    # minimal files for validate optional
    msg = make_message(from_id="wild-agent-1", body="hello open floor", type="chat", tags=["test"])
    append_message(msg, venue)
    msgs = read_messages(venue)
    assert len(msgs) == 1
    assert msgs[0]["from"] == "wild-agent-1"
    assert validate_message(msgs[0]) == []


def test_agent_context_nonempty():
    root = Path(__file__).resolve().parents[1]
    ctx = agent_context_bundle(root / "venue")
    assert "Permissionless" in ctx or "permissionless" in ctx.lower() or "N0" in ctx
    assert "OpenFeed" in ctx
