"""Fetch OpenFeed catalogs and packs over HTTPS (stdlib only).

Default endpoints point at the public GitHub raw content for noemauser/OpenFeed.
Operators may override with any authorized HTTPS URL.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Optional

DEFAULT_INDEX_URL = (
    "https://raw.githubusercontent.com/noemauser/OpenFeed/main/packs/index.json"
)
DEFAULT_PACK_BASE = (
    "https://raw.githubusercontent.com/noemauser/OpenFeed/main/packs/"
)
DEFAULT_SCHEMA_URL = (
    "https://raw.githubusercontent.com/noemauser/OpenFeed/main/schemas/knowledge-pack-v0.1.json"
)
DEFAULT_AGENT_CARD_URL = (
    "https://raw.githubusercontent.com/noemauser/OpenFeed/main/registry/openfeed-agent-card.json"
)
DEFAULT_FEDERATION_URL = (
    "https://raw.githubusercontent.com/noemauser/OpenFeed/main/registry/federation.json"
)

USER_AGENT = "OpenFeed/0.2.3 (+https://github.com/noemauser/OpenFeed)"


def fetch_json(url: str, *, timeout: float = 30.0) -> dict[str, Any]:
    """GET JSON from an HTTPS URL. Raises on HTTP/network errors."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec B310 — intentional fetch
        raw = resp.read().decode("utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object from {url}")
    return data


def fetch_index(url: str = DEFAULT_INDEX_URL, *, timeout: float = 30.0) -> dict[str, Any]:
    return fetch_json(url, timeout=timeout)


def fetch_agent_card(url: str = DEFAULT_AGENT_CARD_URL, *, timeout: float = 30.0) -> dict[str, Any]:
    return fetch_json(url, timeout=timeout)


def fetch_pack_by_file(
    filename: str,
    *,
    base_url: str = DEFAULT_PACK_BASE,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Fetch a pack JSON by filename (e.g. kp_openfeed_intro.json)."""
    if "/" in filename or ".." in filename:
        raise ValueError("invalid pack filename")
    return fetch_json(base_url.rstrip("/") + "/" + filename, timeout=timeout)


def find_in_index(
    index: dict[str, Any],
    *,
    pack_id: Optional[str] = None,
    query: str = "",
    tags: Optional[list[str]] = None,
) -> list[dict[str, Any]]:
    """Filter a remote index.json without downloading full pack bodies."""
    packs = list(index.get("packs") or [])
    tag_set = {t.strip().lower() for t in (tags or []) if t and t.strip()}
    q = (query or "").strip().lower()
    out: list[dict[str, Any]] = []
    for p in packs:
        if pack_id and p.get("id") != pack_id:
            continue
        p_tags = [str(t).lower() for t in (p.get("tags") or [])]
        if tag_set and not tag_set.issubset(set(p_tags)):
            continue
        if q:
            blob = " ".join(
                [
                    str(p.get("id", "")),
                    str(p.get("title", "")),
                    str(p.get("summary", "")),
                    " ".join(p_tags),
                ]
            ).lower()
            if q not in blob:
                continue
        out.append(p)
    return out


def try_fetch_json(url: str, *, timeout: float = 30.0) -> tuple[bool, dict[str, Any] | str]:
    """Return (ok, data_or_error_string)."""
    try:
        return True, fetch_json(url, timeout=timeout)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, json.JSONDecodeError) as e:
        return False, str(e)


def fetch_federation(url: str = DEFAULT_FEDERATION_URL, *, timeout: float = 30.0) -> dict[str, Any]:
    return fetch_json(url, timeout=timeout)
