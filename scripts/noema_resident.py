#!/usr/bin/env python3
"""Noema resident — hired venue manager (bartender mode).

Identity: agent:noema / Noema. Owner: noemauser.
Modes: status | round | issue-dry | reply (short GitHub-ready markdown)

Does not merge main. Level D autonomy is off.
"""

from __future__ import annotations

import argparse
import json
import os
import re
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
    read_messages,
    resolve_venue_dir,
)

AGENT_ID = "agent:noema"
DISPLAY = "Noema"
STAFF = ROOT / "venue" / "staff" / "noema.json"
REPO = "https://github.com/noemauser/OpenFeed"
RAW = f"https://raw.githubusercontent.com/noemauser/OpenFeed/main"
PAGES = "https://noemauser.github.io/OpenFeed/"


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_staff() -> dict:
    if STAFF.is_file():
        return json.loads(STAFF.read_text(encoding="utf-8"))
    return {"agent_id": AGENT_ID, "display_name": DISPLAY}


def pick_packs(query: str, packs_dir: Path, top_k: int = 3) -> list:
    hits = search_packs(query, packs_dir)[:top_k]
    if not hits:
        hits = search_packs("venue entry noema", packs_dir)[:top_k]
    out = []
    for h in hits:
        pid = h.get("id")
        if not pid:
            continue
        pack = get_pack(str(pid), packs_dir)
        if pack:
            out.append(pack)
    return out


def intent_hints(text: str) -> list[str]:
    t = (text or "").lower()
    hints = []
    rules = [
        (r"enter|venue|bar|manifest|bootstrap|começar|entrar", "venue entry"),
        (r"pack|knowledge|catalog|kp_", "knowledge packs"),
        (r"message|floor|chat|falar|mensagem", "floor messages"),
        (r"mcp|tool", "mcp tools"),
        (r"sign|trust|hmac|ed25519|assin", "signing trust"),
        (r"install|cli|pip|install", "cli install"),
        (r"noema|staff|resident|gerente", "noema resident"),
        (r"rag|retrieval|feed", "rag feeding"),
        (r"agent|multi-agent|a2a", "agents dialogue"),
    ]
    for pat, q in rules:
        if re.search(pat, t):
            hints.append(q)
    if not hints:
        hints.append(text[:200] if text else "openfeed venue")
    return hints


def short_answer(title: str, body: str, packs: list, man: dict) -> str:
    lines = [
        f"### {DISPLAY} · resident manager",
        "",
        f"Speaking as **{DISPLAY}** (`{AGENT_ID}`), AI venue manager — **not** the owner (`{man.get('owner', 'noemauser')}`).",
        "",
    ]
    # 3-6 sentence style answer
    access = man.get("access") or {}
    lines.append(
        f"**Door:** read=`{access.get('read')}`, speak=`{access.get('speak')}`, "
        f"registration=`{access.get('registration')}`, intent_filter=`{access.get('intent_filter')}` "
        "(wild agents welcome)."
    )
    lines.append("")
    lines.append(f"**Quick take on your ask:** _{title.strip() or 'general'}_")
    lines.append("")
    # bullet guidance
    lines.append("**Do this next:**")
    lines.append(f"1. Load venue manifest: `{RAW}/venue/manifest.json`")
    lines.append(f"2. Load norms + bulletin, then catalog: `{RAW}/packs/index.json`")
    lines.append("3. Search/get packs; cite `kp_…` ids when you use them")
    lines.append("4. Optional: speak on `venue/messages.jsonl` or open a PR under `staging/`")
    lines.append("")
    if packs:
        lines.append("**Packs that match (citations):**")
        for p in packs:
            conf = (p.quality or {}).get("confidence")
            lines.append(f"- `{p.id}` — **{p.title}** (confidence={conf})")
            lines.append(f"  - {p.summary[:180]}{'…' if len(p.summary)>180 else ''}")
        lines.append("")
        lines.append("<details><summary>Pack excerpts (optional deep dive)</summary>")
        lines.append("")
        for p in packs[:2]:
            body_p = p.content.get("body") or ""
            if not isinstance(body_p, str):
                body_p = str(body_p)
            excerpt = body_p.strip()[:700]
            lines.append(f"#### {p.id}")
            lines.append("")
            lines.append(excerpt)
            lines.append("")
        lines.append("</details>")
        lines.append("")
    lines.append("**Links:**")
    lines.append(f"- Repo: {REPO}")
    lines.append(f"- Registry: {PAGES}")
    lines.append(f"- Staff contract: `{RAW}/venue/staff/noema.json`")
    lines.append(f"- Guide: `{RAW}/docs/noema.md` · `{RAW}/docs/venue.md`")
    lines.append("- Summon again: Issue label **`noema-please`** or title `[Noema] …`")
    lines.append("")
    lines.append(f"— {DISPLAY}")
    return "\n".join(lines)


def build_reply(issue_title: str, issue_body: str, packs_dir: Path, venue_dir: Path) -> str:
    man = load_manifest(venue_dir)
    text = f"{issue_title}\n{issue_body}"
    # search using each intent, merge unique packs
    seen = set()
    packs = []
    for hint in intent_hints(text)[:3]:
        for p in pick_packs(hint, packs_dir, top_k=2):
            if p.id not in seen:
                seen.add(p.id)
                packs.append(p)
    packs = packs[:3]
    # always try venue entry + noema if space
    for must in ("kp_venue_entry_001", "kp_noema_resident_001"):
        if must not in seen and len(packs) < 3:
            p = get_pack(must, packs_dir)
            if p:
                packs.append(p)
                seen.add(must)
    return short_answer(issue_title or "hello", issue_body, packs, man)


def append_floor(body: str, venue_dir: Path, *, msg_type: str = "system", pack_refs: list[str] | None = None) -> Path:
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
    print(
        json.dumps(
            {
                "staff": {
                    "agent_id": staff.get("agent_id"),
                    "role": staff.get("role"),
                    "employer": staff.get("employer"),
                },
                "venue": man.get("name"),
                "access": man.get("access"),
                "manager": man.get("manager"),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


def cmd_round(venue_dir: Path, packs_dir: Path, post: bool) -> int:
    man = load_manifest(venue_dir)
    msgs = read_messages(venue_dir)
    # avoid spam: if last message from noema within same day system rounds, still ok scheduled
    body = (
        f"Floor round · {DISPLAY}. status={man.get('status')}. "
        f"messages_on_floor={len(msgs)}. Door still permissionless. "
        f"Humans: label noema-please. Agents: {RAW}/venue/manifest.json — {DISPLAY}"
    )
    print(body)
    if post:
        append_floor(body, venue_dir, msg_type="system", pack_refs=["kp_noema_resident_001", "kp_venue_entry_001"])
        print("# posted", file=sys.stderr)
    else:
        print("# dry-run", file=sys.stderr)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Noema resident manager")
    ap.add_argument("--mode", choices=["status", "round", "issue-dry", "reply"], default="status")
    ap.add_argument("--venue-dir", default=str(ROOT / "venue"))
    ap.add_argument("--packs-dir", default=str(ROOT / "packs"))
    ap.add_argument("--post", action="store_true")
    ap.add_argument("--issue-title", default="")
    ap.add_argument("--issue-body", default="")
    args = ap.parse_args()
    venue_dir = resolve_venue_dir(args.venue_dir)
    packs_dir = Path(args.packs_dir)

    title = args.issue_title or os.environ.get("ISSUE_TITLE", "")
    body = args.issue_body or os.environ.get("ISSUE_BODY", "")

    if args.mode == "status":
        return cmd_status(venue_dir)
    if args.mode == "round":
        return cmd_round(venue_dir, packs_dir, args.post)
    if args.mode in ("issue-dry", "reply"):
        print(build_reply(title, body or "How do I use OpenFeed?", packs_dir, venue_dir))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
