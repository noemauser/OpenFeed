from pathlib import Path
from openfeed.distill import build_packs_from_snapshot, parse_github_target, slugify, distill_target
from openfeed.pack import validate_pack

ROOT = Path(__file__).resolve().parents[1]


def test_parse_github():
    assert parse_github_target("noemauser/OpenFeed") == ("noemauser", "OpenFeed")
    assert parse_github_target("https://github.com/noemauser/OpenFeed.git")[1] == "OpenFeed"


def test_slugify():
    assert "open" in slugify("OpenFeed")


def test_build_packs_local_snapshot():
    snap = {
        "kind": "local_path",
        "name": "demo",
        "repo": "demo",
        "full_name": "demo",
        "html_url": None,
        "description": "demo project",
        "readme": "# Demo\n\nHello",
        "root_entries": ["src", "README.md"],
        "topics": [],
        "license_spdx": "MIT",
        "fetched_at": "2026-10-12T00:00:00Z",
    }
    packs = build_packs_from_snapshot(snap)
    assert len(packs) == 3
    for p in packs:
        assert validate_pack(p, strict=True) == []


def test_distill_local_write(tmp_path):
    r = distill_target(str(ROOT), kind="local", out_dir=tmp_path, write=True)
    assert r["ok"] is True
    assert len(r["written"]) == 3
    assert (tmp_path / f"{r['packs'][0]['id']}.json").is_file()


def test_seed_distill_packs_exist():
    for name in (
        "kp_distill_openfeed_overview_001.json",
        "kp_distill_openfeed_surfaces_001.json",
        "kp_distill_openfeed_agent_use_001.json",
    ):
        assert (ROOT / "packs" / name).is_file()
