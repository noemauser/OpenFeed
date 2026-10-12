#!/usr/bin/env python3
"""Build sample A2A-style peer messages carrying OpenFeed packs."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from openfeed.a2a import MIME_PACK_REF, pack_ref, parse_peer_message, venue_pointer, capability_advertisement
from openfeed.mcp_server import get_pack
from openfeed.sign import pack_digest

def main() -> int:
    pack = get_pack("kp_openfeed_hello_001", ROOT / "packs")
    digest = pack_digest(pack.to_dict()) if pack else None
    ref = pack_ref("kp_openfeed_hello_001", file="kp_openfeed_hello.json", digest=digest)
    msg = {
        "role": "agent",
        "from": "agent:example",
        "to": "agent:peer",
        "task": "share_bootstrap_pack",
        "parts": [
            {"mimeType": MIME_PACK_REF, "data": ref},
            {"mimeType": "application/vnd.openfeed.venue+json", "data": venue_pointer()},
        ],
        "capabilities": capability_advertisement()["capabilities"],
    }
    print(json.dumps(msg, indent=2, ensure_ascii=False))
    print("--- parse ---", file=sys.stderr)
    print(json.dumps(parse_peer_message(msg), indent=2), file=sys.stderr)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
