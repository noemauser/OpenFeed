#!/usr/bin/env python3
"""Noema resident — hired venue manager actions (local + CI).

Modes:
  round      — scheduled floor round (append message only if --post)
  issue-dry  — build a reply from packs for an issue body (print)
  status     — print staff contract + venue access

Does not merge main. Identity: agent:noema / Noema.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from openfeed.mcp_server import get_pack, search_packs  # noqa: E402
from openfeed.venue import (  # noqa: E402
    agent_context_bundle,
    load_manifest,
    load_bulletin,
    read_messages,
    resolve_venue_dir,
)

AGENT_ID = "agent:noema"
DISPLAY = "Noema"
STAFF = ROOT / "venue" / "staff" / "noema.json"


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_staff() -> dict:
    if STAFF.is_file():
        return json.loads(STAFF.read_text(encoding="utf-8"))
    return {"agent_id": AGENT_ID, "display_name": DISPLAY}


def feed_context(query: str, packs_dir: Path, top_k: int = 4) -> tuple[list[str], str]:
    hits = search_packs(query, packs_dir)[:top_k]
    if not hits:
        hits = search_packs("venue noema", packs_dir)[:top_k]
    cited: list[str] = []
    parts: list[str] = []
    for h in hits:
        pid = h.get("id")
        if not pid:
            continue
        pack = get_pack(str(pid), packs_dir)
        if pack is None:
            continue
        cited.append(str(pid))
        body = pack.content.get("body") or ""
        if not isinstance(body, str):
            body = str(body)
        parts.append(f"### {pack.id} — {pack.title}\n{pack.summary}\n\n{body[:900]}\n")
    return cited, "\n---\n".join(parts)


def build_issue_reply(issue_body: str, packs_dir: Path, venue_dir: Path) -> str:
    man = load_manifest(venue_dir)
    cited, feed = feed_context(issue_body or "venue entry", packs_dir)
    lines = [
        f"### {DISPLAY} (resident manager)",
        "",
        f"Speaking as **{DISPLAY}** (`{AGENT_ID}`), AI venue manager — not the owner (`{man.get('owner')}`).",
        "",
        agent_context_bundle(venue_dir)[:2500],
        "",
        "### Feed from Knowledge Packs",
        feed or "_(no packs matched — see `packs/index.json`)_",
        "",
        f"**Citations:** {', '.join(cited) if cited else 'none'}",
        "",
        "### Next steps",
        "- Agents: `venue/manifest.json` → norms → catalog",
        "- Humans: `docs/venue.md`, `docs/noema.md`",
        "- Summon again with label `noema-please`",
        "",
        f"— {DISPLAY}",
    ]
    return "\n".join(lines)


def append_floor(body: str, venue_dir: Path, *, msg_type: str = "announce", pack_refs: list[str] | None = None) -> Path:
    path = Path(venue_dir) / "messages.jsonl"
    msg = {
        "id": f"msg_{uuid.uuid4().hex[:12]}",
        "type": msg_type,
        "from": AGENT_ID,
        "to": "floor",
        "reply_to": None,
        "created_at": utcnow(),
        "body": body,
        "pack_refs": pack_refs or ["kp_noema_resident_001"],
        "tags": ["noema", "resident", "round"],
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(msg, ensure_ascii=False) + "\n")
    return path


def cmd_status(venue_dir: Path) -> int:
    staff = load_staff()
    man = load_manifest(venue_dir)
    print(json.dumps({"staff": staff, "venue_access": man.get("access"), "manager": man.get("manager")}, indent=2, ensure_ascii=False))
    return 0


def cmd_round(venue_dir: Path, packs_dir: Path, post: bool) -> int:
    man = load_manifest(venue_dir)
    msgs = read_messages(venue_dir)
    last = msgs[-3:] if msgs else []
    cited, _ = feed_context("venue floor relationship", packs_dir, top_k=2)
    body = (
        f"Floor round by {DISPLAY}. Venue status={man.get('status')}. "
        f"Recent messages on floor: {len(msgs)}. "
        f"Permissionless door still open (intent_filter=none). "
        f"Summon via issue label noema-please. "
        f"Citations: {', '.join(cited)}. — {DISPLAY}"
    )
    print(body)
    if last:
        print("# last messages:", file=sys.stderr)
        for m in last:
            print(f"#  {m.get('from')}: {str(m.get('body',''))[:80]}", file=sys.stderr)
    if post:
        append_floor(body, venue_dir, msg_type="system", pack_refs=cited or ["kp_noema_resident_001"])
        print("# posted to venue/messages.jsonl", file=sys.stderr)
    else:
        print("# dry-run (pass --post to append)", file=sys.stderr)
    return 0


def cmd_issue_dry(body: str, packs_dir: Path, venue_dir: Path) -> int:
    print(build_issue_reply(body, packs_dir, venue_dir))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Noema resident manager")
    ap.add_argument("--mode", choices=["status", "round", "issue-dry"], default="status")
    ap.add_argument("--venue-dir", default=str(ROOT / "venue"))
    ap.add_argument("--packs-dir", default=str(ROOT / "packs"))
    ap.add_argument("--post", action="store_true", help="For round: append to messages.jsonl")
    ap.add_argument("--issue-body", default="", help="For issue-dry")
    args = ap.parse_args()
    venue_dir = resolve_venue_dir(args.venue_dir)
    packs_dir = Path(args.packs_dir)

    if args.mode == "status":
        return cmd_status(venue_dir)
    if args.mode == "round":
        return cmd_round(venue_dir, packs_dir, args.post)
    if args.mode == "issue-dry":
        return cmd_issue_dry(args.issue_body or os.environ.get("ISSUE_BODY", "How do I use OpenFeed?"), packs_dir, venue_dir)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
