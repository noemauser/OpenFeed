"""Experimental local trust: HMAC-SHA256 signatures for Knowledge Packs (stdlib only).

Not a PKI. Operators share a secret key file to sign/verify packs they trust.
Canonical payload excludes the ``signatures`` field so signing is stable.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path
from typing import Any

ALG = "hmac-sha256"


def _canonical_bytes(data: dict[str, Any]) -> bytes:
    payload = {k: v for k, v in data.items() if k != "signatures"}
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


def load_key(path: str | Path) -> bytes:
    raw = Path(path).read_bytes()
    # allow text keys; strip whitespace
    try:
        text = raw.decode("utf-8").strip()
        if text:
            return text.encode("utf-8")
    except UnicodeDecodeError:
        pass
    return raw


def sign_pack_dict(data: dict[str, Any], key: bytes, *,
                   key_id: str = "local") -> dict[str, Any]:
    """Return a new dict with an HMAC signature appended."""
    msg = _canonical_bytes(data)
    sig = hmac.new(key, msg, hashlib.sha256).hexdigest()
    out = dict(data)
    sigs = list(out.get("signatures") or [])
    # replace existing same alg+key_id
    sigs = [s for s in sigs if not (s.get("alg") == ALG and s.get("key_id") == key_id)]
    sigs.append({"alg": ALG, "key_id": key_id, "sig": sig})
    out["signatures"] = sigs
    return out


def verify_pack_dict(data: dict[str, Any], key: bytes, *,
                     key_id: str | None = None) -> list[str]:
    """Return list of problems (empty = ok)."""
    errors: list[str] = []
    sigs = data.get("signatures") or []
    candidates = [
        s
        for s in sigs
        if s.get("alg") == ALG and isinstance(s.get("sig"), str) and (key_id is None or s.get("key_id") == key_id)
    ]
    if not candidates:
        return [f"no {ALG} signature found" + (f" for key_id={key_id}" if key_id else "")]

    msg = _canonical_bytes(data)
    ok_any = False
    for s in candidates:
        expected = hmac.new(key, msg, hashlib.sha256).hexdigest()
        if hmac.compare_digest(expected, s["sig"]):
            ok_any = True
        else:
            errors.append(f"signature mismatch for key_id={s.get('key_id')}")
    if ok_any:
        # if at least one matches, drop mismatch noise for other key_ids
        return []
    return errors or ["signature verification failed"]
