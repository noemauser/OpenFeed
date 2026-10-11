"""Knowledge Pack core: create, validate, load, save.

Minimal, dependency-light implementation of the OpenFeed Knowledge Pack v0.1.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass
class KnowledgePack:
    """Atomic unit of feedable knowledge."""

    id: str
    version: str
    title: str
    summary: str
    content: dict[str, Any]
    provenance: dict[str, Any]
    quality: dict[str, Any]
    license: str
    relations: list[dict[str, str]] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    signatures: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        # drop empty optional lists for cleaner packs if desired; keep for schema compliance
        return d

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


def create_pack(
    title: str,
    summary: str,
    body: str | dict | list,
    *,
    content_type: str = "markdown",
    created_by: str = "noema",
    method: str = "synthesized",
    self_score: float = 0.8,
    confidence: float = 0.75,
    license: str = "MIT",
    tags: Optional[list[str]] = None,
    sources: Optional[list[dict]] = None,
    parent_packs: Optional[list[str]] = None,
    relations: Optional[list[dict]] = None,
    pack_id: Optional[str] = None,
    version: str = "0.1.0",
) -> KnowledgePack:
    """Create a new Knowledge Pack with sensible defaults."""
    if content_type not in ("markdown", "json", "text", "structured"):
        raise ValueError(f"Invalid content_type: {content_type}")

    content: dict[str, Any] = {"type": content_type, "body": body}
    if content_type == "markdown":
        content["format"] = "markdown"

    provenance: dict[str, Any] = {
        "created_by": created_by,
        "created_at": _utcnow_iso(),
        "method": method,
    }
    if sources:
        provenance["sources"] = sources
    if parent_packs:
        provenance["parent_packs"] = parent_packs

    quality = {
        "self_score": max(0.0, min(1.0, self_score)),
        "confidence": max(0.0, min(1.0, confidence)),
        "community_score": None,
        "reproduction_status": "untested",
        "safety_flags": [],
    }

    return KnowledgePack(
        id=pack_id or f"kp_{uuid.uuid4().hex}",
        version=version,
        title=title.strip(),
        summary=summary.strip(),
        content=content,
        provenance=provenance,
        quality=quality,
        license=license,
        relations=relations or [],
        tags=tags or [],
        signatures=[],
    )


def validate_pack(data: dict[str, Any] | KnowledgePack) -> list[str]:
    """Lightweight validation against the v0.1 shape. Returns list of error messages (empty = ok)."""
    errors: list[str] = []
    d = data.to_dict() if isinstance(data, KnowledgePack) else data

    required = ["id", "version", "title", "summary", "content", "provenance", "quality", "license"]
    for k in required:
        if k not in d:
            errors.append(f"missing required field: {k}")

    if "content" in d:
        c = d["content"]
        if not isinstance(c, dict):
            errors.append("content must be an object")
        else:
            if "type" not in c or "body" not in c:
                errors.append("content requires type and body")
            elif c["type"] not in ("markdown", "json", "text", "structured"):
                errors.append(f"invalid content.type: {c['type']}")

    if "provenance" in d:
        p = d["provenance"]
        if not isinstance(p, dict):
            errors.append("provenance must be an object")
        else:
            for k in ("created_by", "created_at", "method"):
                if k not in p:
                    errors.append(f"provenance missing: {k}")

    if "quality" in d:
        q = d["quality"]
        if not isinstance(q, dict):
            errors.append("quality must be an object")
        else:
            for k in ("self_score", "confidence"):
                if k not in q:
                    errors.append(f"quality missing: {k}")
                elif not isinstance(q[k], (int, float)) or not (0 <= q[k] <= 1):
                    errors.append(f"quality.{k} must be a number between 0 and 1")

    return errors


def load_pack(path: str | Path) -> KnowledgePack:
    """Load a Knowledge Pack from a JSON file."""
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    errs = validate_pack(data)
    if errs:
        raise ValueError("Invalid Knowledge Pack:\n  - " + "\n  - ".join(errs))
    return KnowledgePack(
        id=data["id"],
        version=data["version"],
        title=data["title"],
        summary=data["summary"],
        content=data["content"],
        provenance=data["provenance"],
        quality=data["quality"],
        license=data["license"],
        relations=data.get("relations", []),
        tags=data.get("tags", []),
        signatures=data.get("signatures", []),
    )


def save_pack(pack: KnowledgePack, path: str | Path) -> Path:
    """Save a Knowledge Pack to a JSON file."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(pack.to_json(), encoding="utf-8")
    return p
