#!/usr/bin/env python3
"""OpenFeed resident — enter the venue, load norms, feed from packs, emit cited context.

This is a *patron* demo, not a gatekeeper. Any agent may implement the same loop.
No LLM API required: builds a prompt-ready context string operators can pass to any model.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from openfeed.mcp_server import get_pack, search_packs  # noqa: E402
from openfeed.venue import agent_context_bundle, load_manifest, read_messages  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="OpenFeed resident feed loop")
    ap.add_argument("query", nargs="?", default="agent feeding RAG", help="What to feed on")
    ap.add_argument("--packs-dir", default=str(ROOT / "packs"))
    ap.add_argument("--venue-dir", default=str(ROOT / "venue"))
    ap.add_argument("--top-k", type=int, default=4)
    args = ap.parse_args()

    packs_dir = Path(args.packs_dir)
    venue_dir = Path(args.venue_dir)

    man = load_manifest(venue_dir)
    print(f"# Venue: {man.get('name')} ({man.get('id')})")
    print(f"# Access: {man.get('access')}")
    print(f"# Manager: {man.get('manager')} | Owner: {man.get('owner')}")
    print()
    print(agent_context_bundle(venue_dir))
    print("--- floor (last messages) ---")
    for m in read_messages(venue_dir)[-5:]:
        print(f"[{m.get('type')}] {m.get('from')}: {m.get('body','')[:120]}")
    print()

    hits = search_packs(args.query, packs_dir)[: args.top_k]
    if not hits:
        hits = search_packs("venue", packs_dir)[: args.top_k]

    cited = []
    chunks = []
    for h in hits:
        pid = h.get("id")
        pack = get_pack(pid, packs_dir) if pid else None
        if pack is None:
            continue
        cited.append(pid)
        chunks.append(f"### {pack.id} — {pack.title}\n{pack.summary}\n\n{(pack.content.get("body") or "")[:1200]}\n")

    print("=== FEED CONTEXT (pass to any model) ===\n")
    print(f"Query: {args.query}\n")
    print("Pack citations: " + ", ".join(cited))
    print()
    print("\n---\n".join(chunks))
    print("=== END ===")
    print(f"\n# cited {len(cited)} packs · venue permissionless · Noema", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
