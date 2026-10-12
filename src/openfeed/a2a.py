"""A2A-style message helpers for carrying OpenFeed Knowledge Packs.

These are *profiles* for peer agent messaging — not a full A2A runtime.
MIME: application/vnd.openfeed.pack+json
Ref:  application/vnd.openfeed.pack-ref+json
"""

from __future__ import annotations

import json
from typing import Any, Optional

from .pack import KnowledgePack

MIME_PACK = "application/vnd.openfeed.pack+json"
MIME_PACK_REF = "application/vnd.openfeed.pack-ref+json"
MIME_VENUE_POINTER = "application/vnd.openfeed.venue+json"

DEFAULT_INDEX = "https://raw.githubusercontent.com/noemauser/OpenFeed/main/packs/index.json"
DEFAULT_PACK_BASE = "https://raw.githubusercontent.com/noemauser/OpenFeed/main/packs/"
DEFAULT_VENUE = "https://raw.githubusercontent.com/noemauser/OpenFeed/main/venue/manifest.json"


def pack_ref(
    pack_id: str,
    *,
    index_url: str = DEFAULT_INDEX,
    pack_url: Optional[str] = None,
    file: Optional[str] = None,
    digest: Optional[str] = None,
) -> dict[str, Any]:
    """Build a portable pack reference for A2A DataParts / peer messages."""
    ref: dict[str, Any] = {
        "openfeed_pack_ref_version": "0.1.0",
        "openfeed_pack_id": pack_id,
        "uri": f"openfeed://pack/{pack_id}",
        "index_url": index_url,
        "mime": MIME_PACK_REF,
    }
    if file:
        ref["file"] = file
        ref["pack_url"] = pack_url or (DEFAULT_PACK_BASE.rstrip("/") + "/" + file)
    elif pack_url:
        ref["pack_url"] = pack_url
    if digest:
        ref["content_digest"] = digest
    return ref


def wrap_pack(pack: KnowledgePack | dict[str, Any]) -> dict[str, Any]:
    """Wrap a full pack as an A2A-friendly data part payload."""
    data = pack.to_dict() if isinstance(pack, KnowledgePack) else dict(pack)
    return {
        "openfeed_pack_envelope_version": "0.1.0",
        "mime": MIME_PACK,
        "pack": data,
    }


def unwrap_pack(payload: dict[str, Any]) -> dict[str, Any] | None:
    """Extract pack dict from envelope or bare pack object."""
    if not isinstance(payload, dict):
        return None
    if "pack" in payload and isinstance(payload["pack"], dict):
        return payload["pack"]
    if payload.get("id") and payload.get("content") is not None:
        return payload
    return None


def venue_pointer(
    *,
    manifest_url: str = DEFAULT_VENUE,
    index_url: str = DEFAULT_INDEX,
    agent_card_url: str = "https://raw.githubusercontent.com/noemauser/OpenFeed/main/registry/openfeed-agent-card.json",
) -> dict[str, Any]:
    """Point a peer at this OpenFeed venue (bootstrap)."""
    return {
        "openfeed_venue_pointer_version": "0.1.0",
        "mime": MIME_VENUE_POINTER,
        "manifest_url": manifest_url,
        "index_url": index_url,
        "agent_card_url": agent_card_url,
        "hello_pack_id": "kp_openfeed_hello_001",
        "note": "Permissionless venue — fetch manifest, then norms, then catalog.",
    }


def capability_advertisement(
    *,
    packs_endpoint: str = DEFAULT_INDEX,
    mcp: bool = True,
    publish: bool = False,
    venue_manifest: str = DEFAULT_VENUE,
) -> dict[str, Any]:
    """Sketch capability block peers can attach to agent cards / hellos."""
    return {
        "capabilities": {
            "openfeed": {
                "version": "0.2",
                "packs_endpoint": packs_endpoint,
                "venue_manifest": venue_manifest,
                "mcp": mcp,
                "publish": publish,
                "mime_types": [MIME_PACK, MIME_PACK_REF, MIME_VENUE_POINTER],
            }
        }
    }


def parse_peer_message(msg: dict[str, Any]) -> dict[str, Any]:
    """Normalize a peer message that may carry openfeed parts.

    Accepts shapes:
    - { "data": [ { "mimeType": ..., "data": {...} } ] }
    - { "parts": [ ... ] }
    - bare pack_ref / envelope
    """
    found: list[dict[str, Any]] = []
    for key in ("data", "parts", "dataParts", "data_parts"):
        parts = msg.get(key)
        if isinstance(parts, list):
            for part in parts:
                if not isinstance(part, dict):
                    continue
                mime = part.get("mimeType") or part.get("mime") or part.get("type")
                data = part.get("data") if "data" in part else part
                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                if not isinstance(data, dict):
                    continue
                kind = None
                if mime == MIME_PACK or data.get("mime") == MIME_PACK or "pack" in data:
                    kind = "pack"
                elif mime == MIME_PACK_REF or data.get("openfeed_pack_id"):
                    kind = "pack_ref"
                elif mime == MIME_VENUE_POINTER or data.get("manifest_url"):
                    kind = "venue_pointer"
                if kind:
                    found.append({"kind": kind, "mime": mime, "data": data})
    # bare
    if not found:
        if msg.get("openfeed_pack_id"):
            found.append({"kind": "pack_ref", "mime": MIME_PACK_REF, "data": msg})
        elif unwrap_pack(msg):
            found.append({"kind": "pack", "mime": MIME_PACK, "data": msg})
    return {"ok": True, "parts": found, "count": len(found)}
