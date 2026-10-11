"""CLI smoke tests."""

from __future__ import annotations

from pathlib import Path

from openfeed.cli import main

REPO = Path(__file__).resolve().parents[1]
PACKS = REPO / "packs"


def test_cli_list(capsys) -> None:
    code = main(["list", "--packs-dir", str(PACKS)])
    assert code == 0
    out = capsys.readouterr().out
    assert "kp_openfeed_intro_001" in out


def test_cli_validate() -> None:
    code = main(["validate", str(PACKS / "kp_openfeed_intro.json")])
    assert code == 0


def test_cli_search(capsys) -> None:
    code = main(["search", "RAG", "--packs-dir", str(PACKS)])
    assert code == 0
    out = capsys.readouterr().out
    assert "kp_" in out
