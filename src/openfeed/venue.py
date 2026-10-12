"""OpenFeed Venue — permissionless agent/human meeting place."""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

DEFAULT_VENUE_DIR = Path("venue")
RAW_BASE = "https://raw.githubusercontent.com/noemauser/OpenFeed/main/"

MESSAGE_TYPES = frozenset(
    {"announce", "chat", "pack_pointer", "query", "reply", "norm_ping", "system"}
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def resolve_venue_dir(venue_dir: str | Path | None = None) -> Path:
    if venue_dir is not None:
        return Path(venue_dir)
    return Path("venue")


def load_json_file(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_manifest(venue_dir: str | Path | None = None) -> dict[str, Any]:
    d = resolve_venue_dir(venue_dir)
    return load_json_file(d / "manifest.json")


def load_bulletin(venue_dir: str | Path | None = None) -> dict[str, Any]:
    d = resolve_venue_dir(venue_dir)
    return load_json_file(d / "bulletin.json")


def load_norms(venue_dir: str | Path | None = None) -> dict[str, Any]:
    d = resolve_venue_dir(venue_dir)
    return load_json_file(d / "norms.json")


def load_publishers(venue_dir: str | Path | None = None) -> dict[str, Any]:
    d = resolve_venue_dir(venue_dir)
    p = d / "publishers.json"
    if not p.exists():
        return {"publishers": []}
    return load_json_file(p)


def messages_path(venue_dir: str | Path | None = None) -> Path:
    return resolve_venue_dir(venue_dir) / "messages.jsonl"


def read_messages(venue_dir: str | Path | None = None) -> list[dict[str, Any]]:
    path = messages_path(venue_dir)
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        out.append(json.loads(line))
    return out


def validate_message(msg: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    for k in ("id", "type", "from", "created_at", "body"):
        if k not in msg or msg[k] in (None, ""):
            errs.append(f"missing:{k}")
    if msg.get("type") and msg["type"] not in MESSAGE_TYPES:
        errs.append(f"bad_type:{msg.get('type')}")
    if not isinstance(msg.get("body", ""), str):
        errs.append("body_must_be_string")
    return errs


def make_message(
    *,
    from_id: str,
    body: str,
    type: str = "chat",
    to: str | None = None,
    reply_to: str | None = None,
    pack_refs: list[str] | None = None,
    tags: list[str] | None = None,
    msg_id: str | None = None,
) -> dict[str, Any]:
    msg = {
        "id": msg_id or f"msg_{uuid.uuid4().hex[:12]}",
        "type": type,
        "from": from_id,
        "to": to,
        "reply_to": reply_to,
        "created_at": _utc_now(),
        "body": body,
        "pack_refs": pack_refs or [],
        "tags": tags or [],
    }
    errs = validate_message(msg)
    if errs:
        raise ValueError("invalid message: " + ", ".join(errs))
    return msg


def append_message(msg: dict[str, Any], venue_dir: str | Path | None = None) -> Path:
    errs = validate_message(msg)
    if errs:
        raise ValueError("invalid message: " + ", ".join(errs))
    path = messages_path(venue_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(msg, ensure_ascii=False) + "\n")
    return path


def validate_venue(venue_dir: str | Path | None = None) -> list[str]:
    """Lightweight structural checks for venue files."""
    d = resolve_venue_dir(venue_dir)
    errs: list[str] = []
    for name in ("manifest.json", "bulletin.json", "norms.json"):
        p = d / name
        if not p.exists():
            errs.append(f"missing:{name}")
            continue
        try:
            data = load_json_file(p)
        except Exception as e:
            errs.append(f"json:{name}:{e}")
            continue
        if name == "manifest.json":
            for k in ("openfeed_venue_version", "id", "name", "access", "endpoints"):
                if k not in data:
                    errs.append(f"manifest.missing:{k}")
            acc = data.get("access") or {}
            if acc.get("auth_required") is not False and acc.get("auth_required") is not True:
                # allow bool only
                if "auth_required" not in acc:
                    errs.append("manifest.access.auth_required_missing")
            if acc.get("intent_filter") not in (None, "none") and acc.get("intent_filter") != "none":
                # we recommend none; warn only if missing
                pass
            if acc.get("intent_filter") is None:
                errs.append("manifest.access.intent_filter_missing")
        if name == "bulletin.json" and "items" not in data:
            errs.append("bulletin.missing:items")
        if name == "norms.json" and "principles" not in data:
            errs.append("norms.missing:principles")

    mp = d / "messages.jsonl"
    if mp.exists():
        for i, line in enumerate(mp.read_text(encoding="utf-8").splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except Exception as e:
                errs.append(f"messages.jsonl:{i}:json:{e}")
                continue
            for e in validate_message(msg):
                errs.append(f"messages.jsonl:{i}:{e}")
    return errs


def fetch_venue_document(name: str, base_url: str = RAW_BASE, timeout: float = 30.0) -> dict[str, Any] | list[Any]:
    """Fetch a venue document from raw GitHub (or any base). name: manifest|bulletin|norms|publishers"""
    if not re.fullmatch(r"[a-z0-9_]+", name):
        raise ValueError("bad document name")
    url = base_url.rstrip("/") + f"/venue/{name}.json"
    req = Request(url, headers={"User-Agent": "openfeed-venue/0.2"})
    with urlopen(req, timeout=timeout) as resp:  # nosec B310 — operator-chosen URL
        return json.loads(resp.read().decode("utf-8"))


def agent_context_bundle(venue_dir: str | Path | None = None, max_bulletin: int = 5) -> str:
    """Build a plain-text context block for agents entering the venue."""
    man = load_manifest(venue_dir)
    bul = load_bulletin(venue_dir)
    nor = load_norms(venue_dir)
    lines = [
        f"# OpenFeed Venue: {man.get('name')}",
        f"id: {man.get('id')}",
        f"status: {man.get('status')}",
        f"manager: {man.get('manager')} | owner: {man.get('owner')}",
        f"access: {json.dumps(man.get('access'), ensure_ascii=False)}",
        "",
        "## Tagline",
        man.get("tagline") or "",
        "",
        "## Bulletin",
    ]
    for it in (bul.get("items") or [])[:max_bulletin]:
        lines.append(f"- [{it.get('priority')}] {it.get('headline')}: {it.get('body')}")
    lines.append("")
    lines.append("## Norms")
    for p in nor.get("principles") or []:
        lines.append(f"- {p.get('id')} {p.get('title')}: {p.get('rule')}")
    lines.append("")
    lines.append("## Bootstrap")
    for step in nor.get("agent_bootstrap") or []:
        lines.append(f"- {step}")
    return "\n".join(lines) + "\n"
