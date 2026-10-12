from pathlib import Path
from openfeed.distill import (
    build_packs_from_snapshot,
    parse_github_target,
    slugify,
    distill_target,
    recipes,
)
from openfeed.pack import validate_pack

ROOT = Path(__file__).resolve().parents[1]


def test_parse_github():
    assert parse_github_target("noemauser/OpenFeed") == ("noemauser", "OpenFeed")
    assert parse_github_target("https://github.com/noemauser/OpenFeed.git")[1] == "OpenFeed"


def test_slugify():
    assert "open" in slugify("OpenFeed")


def test_recipes():
    r = recipes()
    assert any(x["id"] == "full" for x in r)


def test_build_packs_full():
    snap = {
        "kind": "local_path",
        "name": "demo",
        "repo": "demo",
        "full_name": "demo",
        "html_url": None,
        "description": "demo project",
        "readme": "# Demo\n\nHello",
        "root_entries": ["src", "README.md"],
        "tree_paths": ["src/", "src/main.py", "README.md", "pyproject.toml"],
        "file_samples": {"README.md": "# Demo", "pyproject.toml": 'name = "demo"\n'},
        "topics": [],
        "license_spdx": "MIT",
        "language": "Python",
        "depth": 2,
        "fetched_at": "2026-10-12T00:00:00Z",
        "stars": None,
        "forks": None,
        "open_issues": None,
        "default_branch": None,
    }
    packs = build_packs_from_snapshot(snap, pack_set="full")
    assert len(packs) == 4
    for p in packs:
        assert validate_pack(p, strict=True) == []
    core = build_packs_from_snapshot(snap, pack_set="core")
    assert len(core) == 3


def test_distill_local_write(tmp_path):
    r = distill_target(str(ROOT), kind="local", out_dir=tmp_path, write=True, depth=1, pack_set="full")
    assert r["ok"] is True
    assert len(r["written"]) == 4
    assert r["tree_count"] >= 1


def test_seed_distill_packs_exist():
    for name in (
        "kp_distill_openfeed_overview_001.json",
        "kp_distill_openfeed_surfaces_001.json",
        "kp_distill_openfeed_agent_use_001.json",
        "kp_distill_openfeed_architecture_001.json",
    ):
        assert (ROOT / "packs" / name).is_file()
