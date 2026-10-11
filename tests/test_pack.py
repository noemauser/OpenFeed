"""Core Knowledge Pack tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from openfeed.pack import create_pack, load_pack, save_pack, validate_pack

REPO = Path(__file__).resolve().parents[1]
PACKS = REPO / "packs"


def test_create_and_validate_roundtrip(tmp_path: Path) -> None:
    pack = create_pack(
        title="Test pack",
        summary="A short summary for tests",
        body="# Hello\n\nBody content.",
        tags=["test"],
        created_by="test",
    )
    errs = validate_pack(pack)
    assert errs == []

    path = tmp_path / "pack.json"
    save_pack(pack, path)
    loaded = load_pack(path)
    assert loaded.id == pack.id
    assert loaded.title == "Test pack"
    assert loaded.content["type"] == "markdown"


def test_validate_missing_fields() -> None:
    errs = validate_pack({"id": "x"})
    assert any("missing required field" in e for e in errs)


def test_validate_bad_score() -> None:
    pack = create_pack(title="t", summary="s", body="b")
    d = pack.to_dict()
    d["quality"]["self_score"] = 2.0
    errs = validate_pack(d)
    assert any("self_score" in e for e in errs)


def test_seed_packs_validate() -> None:
    files = sorted(PACKS.glob("kp_*.json"))
    assert len(files) >= 6
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        errs = validate_pack(data)
        assert errs == [], f"{path.name}: {errs}"


def test_index_json_is_not_a_pack() -> None:
    index = PACKS / "index.json"
    assert index.is_file()
    data = json.loads(index.read_text(encoding="utf-8"))
    assert "openfeed_index_version" in data
    assert "packs" in data


@pytest.mark.skipif(
    __import__("importlib").util.find_spec("jsonschema") is None,
    reason="jsonschema not installed",
)
def test_seed_packs_strict_schema() -> None:
    for path in sorted(PACKS.glob("kp_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        # ensure provenance has lists for additionalProperties:false schemas that list them
        errs = validate_pack(data, strict=True)
        # Filter only real schema errors if soft notices appear
        hard = [e for e in errs if not e.startswith("strict validation requires")]
        assert hard == [], f"{path.name}: {hard}"
