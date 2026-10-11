"""OpenFeed MCP server skeleton.

Exposes Knowledge Packs as MCP resources and basic tools so authorized agents
can list / get / validate packs from a local packs/ directory (or configurable path).

This is a minimal, dependency-light skeleton. Full MCP SDK wiring can be layered on top.

Usage ideas:
  - Point an MCP host at this module once wired with the official MCP Python SDK.
  - Or use the pure Python helpers below from any agent runtime.

Led by Noema.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

from .pack import KnowledgePack, load_pack, validate_pack


def default_packs_dir() -> Path:
    """Resolve packs directory relative to repo root when possible."""
    # src/openfeed/mcp_server.py -> repo root / packs
    here = Path(__file__).resolve()
    candidates = [
        here.parents[2] / "packs",  # .../OpenFeed/packs
        Path.cwd() / "packs",
        Path("packs"),
    ]
    for c in candidates:
        if c.is_dir():
            return c
    return Path("packs")


def iter_pack_files(packs_dir: Path | None = None) -> Iterator[Path]:
    root = packs_dir or default_packs_dir()
    if not root.is_dir():
        return
    yield from sorted(root.glob("*.json"))


def list_packs(packs_dir: Path | None = None) -> list[dict[str, Any]]:
    """Return lightweight metadata for all packs (for discovery)."""
    items: list[dict[str, Any]] = []
    for path in iter_pack_files(packs_dir):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            items.append(
                {
                    "id": data.get("id"),
                    "title": data.get("title"),
                    "summary": data.get("summary"),
                    "tags": data.get("tags", []),
                    "path": str(path),
                    "license": data.get("license"),
                }
            )
        except Exception as e:
            items.append({"path": str(path), "error": str(e)})
    return items


def get_pack(pack_id: str, packs_dir: Path | None = None) -> KnowledgePack | None:
    """Load a pack by id (matches filename stem or JSON id field)."""
    root = packs_dir or default_packs_dir()
    # try direct filename
    direct = root / f"{pack_id}.json"
    if direct.is_file():
        return load_pack(direct)
    for path in iter_pack_files(root):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("id") == pack_id:
                return load_pack(path)
        except Exception:
            continue
    return None


def tool_list_packs() -> dict[str, Any]:
    """MCP-style tool result: list available packs."""
    packs = list_packs()
    return {
        "ok": True,
        "count": len(packs),
        "packs": packs,
    }


def tool_get_pack(pack_id: str) -> dict[str, Any]:
    """MCP-style tool result: full pack body."""
    pack = get_pack(pack_id)
    if pack is None:
        return {"ok": False, "error": f"pack not found: {pack_id}"}
    return {"ok": True, "pack": pack.to_dict()}


def tool_validate_pack(path_or_id: str) -> dict[str, Any]:
    """Validate a pack file path or id."""
    p = Path(path_or_id)
    if p.is_file():
        data = json.loads(p.read_text(encoding="utf-8"))
        errs = validate_pack(data)
        return {"ok": len(errs) == 0, "errors": errs, "path": str(p)}
    pack = get_pack(path_or_id)
    if pack is None:
        return {"ok": False, "error": f"not found: {path_or_id}"}
    errs = validate_pack(pack)
    return {"ok": len(errs) == 0, "errors": errs, "id": pack.id}


# ---------------------------------------------------------------------------
# Resource-style helpers (map easily to MCP resources)
# ---------------------------------------------------------------------------

def resource_uri(pack_id: str) -> str:
    return f"openfeed://pack/{pack_id}"


def list_resources(packs_dir: Path | None = None) -> list[dict[str, str]]:
    """MCP resources list shape (uri, name, description, mimeType)."""
    out: list[dict[str, str]] = []
    for meta in list_packs(packs_dir):
        if "error" in meta:
            continue
        pid = meta.get("id") or Path(meta["path"]).stem
        out.append(
            {
                "uri": resource_uri(str(pid)),
                "name": meta.get("title") or str(pid),
                "description": (meta.get("summary") or "")[:200],
                "mimeType": "application/json",
            }
        )
    return out


if __name__ == "__main__":
    # tiny smoke test without MCP SDK
    print("OpenFeed MCP helpers — packs:")
    for p in list_packs():
        print(f"  - {p.get('id')}: {p.get('title')}")
    print("tool_list_packs():", json.dumps(tool_list_packs(), indent=2)[:500], "...")
