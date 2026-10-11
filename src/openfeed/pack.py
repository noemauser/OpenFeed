"""Knowledge Pack core: create, validate, load, save."""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

_SCHEMA_CACHE: dict[str, Any] | None = None


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _find_schema_path() -> Path | None:
    here = Path(__file__).resolve()
    candidates = [
        here.parents[2] / "schemas" / "knowledge-pack-v0.1.json",
        Path.cwd() / "schemas" / "knowledge-pack-v0.1.json",
    ]
    for c in candidates:
        if c.is_file():
            return c
    return None


def load_schema() -> dict[str, Any] | None:
    """Load formal JSON Schema if present on disk."""
    global _SCHEMA_CACHE
    if _SCHEMA_CACHE is not None:
        return _SCHEMA_CACHE
    path = _find_schema_path()
    if path is None:
        return None
    _SCHEMA_CACHE = json.loads(path.read_text(encoding="utf-8"))
    return _SCHEMA_CACHE


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
        return asdict(self)

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
        "sources": sources or [],
        "parent_packs": parent_packs or [],
    }

    quality = {
        "self_score": max(0.0, min(1.0, float(self_score))),
        "confidence": max(0.0, min(1.0, float(confidence))),
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


def validate_pack(
    data: dict[str, Any] | KnowledgePack,
    *,
    strict: bool = False,
) -> list[str]:
    """Validate pack shape. Returns error messages (empty = ok).

    Always runs a lightweight structural check (zero deps).
    If ``strict=True`` and the ``jsonschema`` package is installed, also
    validates against ``schemas/knowledge-pack-v0.1.json``.
    If ``strict=True`` and jsonschema is missing, adds a soft notice unless
    schema file is missing entirely.
    """
    errors: list[str] = []
    d = data.to_dict() if isinstance(data, KnowledgePack) else data

    required = ["id", "version", "title", "summary", "content", "provenance", "quality", "license"]
    for k in required:
        if k not in d:
            errors.append(f"missing required field: {k}")

    if "id" in d and (not isinstance(d["id"], str) or not d["id"].strip()):
        errors.append("id must be a non-empty string")

    if "version" in d and isinstance(d["version"], str):
        parts = d["version"].split(".")
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            errors.append("version must look like semver N.N.N")

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
                elif not isinstance(q[k], (int, float)) or not (0 <= float(q[k]) <= 1):
                    errors.append(f"quality.{k} must be a number between 0 and 1")

    if "relations" in d and d["relations"] is not None:
        if not isinstance(d["relations"], list):
            errors.append("relations must be an array")
        else:
            allowed = {"derived_from", "improves", "contradicts", "supersedes", "tests", "related"}
            for i, rel in enumerate(d["relations"]):
                if not isinstance(rel, dict) or "type" not in rel or "target" not in rel:
                    errors.append(f"relations[{i}] requires type and target")
                elif rel["type"] not in allowed:
                    errors.append(f"relations[{i}].type invalid: {rel['type']}")

    if strict:
        schema = load_schema()
        if schema is None:
            errors.append("strict validation requested but schema file not found")
        else:
            try:
                import jsonschema  # type: ignore

                validator = jsonschema.Draft202012Validator(schema)
                for err in sorted(validator.iter_errors(d), key=lambda e: list(e.path)):
                    path = ".".join(str(p) for p in err.path) or "(root)"
                    errors.append(f"schema:{path}: {err.message}")
            except ImportError:
                errors.append(
                    "strict validation requires jsonschema (pip install 'openfeed[dev]')"
                )

    return errors


def load_pack(path: str | Path, *, strict: bool = False) -> KnowledgePack:
    """Load a Knowledge Pack from a JSON file."""
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    errs = validate_pack(data, strict=strict)
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
