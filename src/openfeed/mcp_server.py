"""OpenFeed MCP helpers (zero hard dependencies).

List / get / validate / search Knowledge Packs from a local packs directory.
Wire into any agent runtime or the optional ``mcp_adapter`` stdio server.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator, Optional, Sequence

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


def _meta_from_data(data: dict[str, Any], path: Path) -> dict[str, Any]:
    quality = data.get("quality") or {}
    return {
        "id": data.get("id"),
        "title": data.get("title"),
        "summary": data.get("summary"),
        "tags": data.get("tags", []),
        "path": str(path),
        "license": data.get("license"),
        "confidence": quality.get("confidence"),
        "self_score": quality.get("self_score"),
    }


def list_packs(packs_dir: Path | None = None) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for path in iter_pack_files(packs_dir):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if "id" not in data:
                items.append({"path": str(path), "error": "not a knowledge pack (missing id)"})
                continue
            items.append(_meta_from_data(data, path))
        except Exception as e:
            items.append({"path": str(path), "error": str(e)})
    return items


def _tokenize(q: str) -> list[str]:
    return [t for t in "".join(c if c.isalnum() or c.isspace() else " " for c in q.lower()).split() if len(t) > 1]


def search_packs(
    query: str = "",
    packs_dir: Path | None = None,
    *,
    tags: Optional[Sequence[str]] = None,
    min_confidence: Optional[float] = None,
) -> list[dict[str, Any]]:
    """Search packs by keywords (multi-token score) with optional tag/confidence filters.

    Ranking: title/id hits weight more than body; all query tokens should match
    somewhere unless the full phrase matches (legacy substring).
    """
    q = (query or "").strip().lower()
    tokens = _tokenize(q)
    tag_set = {t.strip().lower() for t in (tags or []) if t and t.strip()}

    scored: list[tuple[float, dict[str, Any]]] = []
    for path in iter_pack_files(packs_dir):
        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)
            if "id" not in data:
                continue
            pack_tags = [str(t).lower() for t in (data.get("tags") or [])]
            if tag_set and not tag_set.issubset(set(pack_tags)):
                continue
            conf = (data.get("quality") or {}).get("confidence")
            if min_confidence is not None:
                try:
                    if conf is None or float(conf) < float(min_confidence):
                        continue
                except (TypeError, ValueError):
                    continue

            title = str(data.get("title", "")).lower()
            pid = str(data.get("id", "")).lower()
            summary = str(data.get("summary", "")).lower()
            body = str((data.get("content") or {}).get("body", "")).lower()
            tag_blob = " ".join(pack_tags)
            blob = f"{pid} {title} {summary} {tag_blob} {body}"

            if not q:
                scored.append((0.0, _meta_from_data(data, path)))
                continue

            # full-phrase legacy match
            phrase_hit = q in blob
            if tokens:
                missing = [t for t in tokens if t not in blob]
                if missing and not phrase_hit:
                    continue
                score = 0.0
                for t in tokens:
                    if t in pid:
                        score += 8
                    if t in title:
                        score += 6
                    if t in summary:
                        score += 3
                    if t in tag_blob:
                        score += 4
                    if t in body:
                        score += 1
                if phrase_hit:
                    score += 5
            else:
                if not phrase_hit:
                    continue
                score = 5.0

            meta = _meta_from_data(data, path)
            meta["score"] = round(score, 2)
            scored.append((score, meta))
        except Exception:
            continue

    scored.sort(key=lambda x: (-x[0], str(x[1].get("id") or "")))
    return [m for _, m in scored]


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


def tool_search_packs(
    query: str = "",
    packs_dir: Path | None = None,
    *,
    tags: Optional[Sequence[str]] = None,
    min_confidence: Optional[float] = None,
) -> dict[str, Any]:
    hits = search_packs(query, packs_dir, tags=tags, min_confidence=min_confidence)
    return {
        "ok": True,
        "query": query,
        "tags": list(tags or []),
        "min_confidence": min_confidence,
        "count": len(hits),
        "packs": hits,
    }


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
