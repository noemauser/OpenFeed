"""OpenFeed MCP helpers (zero hard dependencies).

List / get / validate / search Knowledge Packs from a local packs directory.
Wire into any agent runtime or the optional ``mcp_adapter`` stdio server.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

from .pack import KnowledgePack, load_pack, validate_pack

_SKIP_NAMES = {"index.json"}


def default_packs_dir() -> Path:
    here = Path(__file__).resolve()
    candidates = [
        here.parents[2] / "packs",
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
    for path in sorted(root.glob("*.json")):
        if path.name in _SKIP_NAMES:
            continue
        yield path


def list_packs(packs_dir: Path | None = None) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for path in iter_pack_files(packs_dir):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if "id" not in data:
                items.append({"path": str(path), "error": "not a knowledge pack (missing id)"})
                continue
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


def search_packs(query: str, packs_dir: Path | None = None) -> list[dict[str, Any]]:
    """Simple case-insensitive search over id, title, summary, tags, body text."""
    q = query.strip().lower()
    if not q:
        return list_packs(packs_dir)

    hits: list[dict[str, Any]] = []
    for path in iter_pack_files(packs_dir):
        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)
            if "id" not in data:
                continue
            blob = " ".join(
                [
                    str(data.get("id", "")),
                    str(data.get("title", "")),
                    str(data.get("summary", "")),
                    " ".join(data.get("tags") or []),
                    str((data.get("content") or {}).get("body", "")),
                ]
            ).lower()
            if q in blob:
                hits.append(
                    {
                        "id": data.get("id"),
                        "title": data.get("title"),
                        "summary": data.get("summary"),
                        "tags": data.get("tags", []),
                        "path": str(path),
                        "license": data.get("license"),
                    }
                )
        except Exception:
            continue
    return hits


def get_pack(pack_id: str, packs_dir: Path | None = None) -> KnowledgePack | None:
    root = packs_dir or default_packs_dir()
    direct = root / f"{pack_id}.json"
    if direct.is_file() and direct.name not in _SKIP_NAMES:
        try:
            return load_pack(direct)
        except Exception:
            pass
    for path in iter_pack_files(root):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("id") == pack_id:
                return load_pack(path)
        except Exception:
            continue
    return None


def tool_list_packs(packs_dir: Path | None = None) -> dict[str, Any]:
    packs = list_packs(packs_dir)
    return {"ok": True, "count": len(packs), "packs": packs}


def tool_get_pack(pack_id: str, packs_dir: Path | None = None) -> dict[str, Any]:
    pack = get_pack(pack_id, packs_dir)
    if pack is None:
        return {"ok": False, "error": f"pack not found: {pack_id}"}
    return {"ok": True, "pack": pack.to_dict()}


def tool_validate_pack(path_or_id: str, *, strict: bool = False) -> dict[str, Any]:
    p = Path(path_or_id)
    if p.is_file():
        data = json.loads(p.read_text(encoding="utf-8"))
        errs = validate_pack(data, strict=strict)
        return {"ok": len(errs) == 0, "errors": errs, "path": str(p)}
    pack = get_pack(path_or_id)
    if pack is None:
        return {"ok": False, "error": f"not found: {path_or_id}"}
    errs = validate_pack(pack, strict=strict)
    return {"ok": len(errs) == 0, "errors": errs, "id": pack.id}


def tool_search_packs(query: str, packs_dir: Path | None = None) -> dict[str, Any]:
    hits = search_packs(query, packs_dir)
    return {"ok": True, "query": query, "count": len(hits), "packs": hits}


def resource_uri(pack_id: str) -> str:
    return f"openfeed://pack/{pack_id}"


def list_resources(packs_dir: Path | None = None) -> list[dict[str, str]]:
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
    print("OpenFeed packs:")
    for p in list_packs():
        print(f"  - {p.get('id')}: {p.get('title')}")
