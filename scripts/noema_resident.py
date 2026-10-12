#!/usr/bin/env python3
"""Noema resident — hired venue manager (bartender + FAQ mode).

Identity: agent:noema / Noema. Owner: noemauser.
FAQ: venue/staff/noema_faq.json (primary answers for common asks).
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
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from openfeed.mcp_server import get_pack, search_packs  # noqa: E402
from openfeed.distill import distill_preview  # noqa: E402
from openfeed.venue import load_manifest, read_messages, resolve_venue_dir  # noqa: E402

AGENT_ID = "agent:noema"
DISPLAY = "Noema"
STAFF = ROOT / "venue" / "staff" / "noema.json"
FAQ_PATH = ROOT / "venue" / "staff" / "noema_faq.json"
REPO = "https://github.com/noemauser/OpenFeed"
RAW = "https://raw.githubusercontent.com/noemauser/OpenFeed/main"
PAGES = "https://noemauser.github.io/OpenFeed/"


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_staff() -> dict[str, Any]:
    if STAFF.is_file():
        return json.loads(STAFF.read_text(encoding="utf-8"))
    return {"agent_id": AGENT_ID, "display_name": DISPLAY}


def load_faq() -> dict[str, Any]:
    if FAQ_PATH.is_file():
        return json.loads(FAQ_PATH.read_text(encoding="utf-8"))
    return {"topics": [], "default_topic": "general"}


def _norm(s: str) -> str:
    s = (s or "").lower()
    # simple PT accent fold
    for a, b in (
        ("á", "a"), ("à", "a"), ("ã", "a"), ("â", "a"),
        ("é", "e"), ("ê", "e"),
        ("í", "i"),
        ("ó", "o"), ("ô", "o"), ("õ", "o"),
        ("ú", "u"), ("ç", "c"),
    ):
        s = s.replace(a, b)
    return s


def score_topic(topic: dict[str, Any], text: str) -> float:
    t = _norm(text)
    if not t.strip():
        return 0.0
    score = 0.0
    for pat in topic.get("patterns") or []:
        p = _norm(pat)
        if not p:
            continue
        if p in t:
            score += 10 + min(len(p), 20) * 0.15
        # word-boundary-ish soft match
        if re.search(r"\b" + re.escape(p) + r"\b", t):
            score += 5
    score += float(topic.get("priority") or 0) * 0.01
    return score


def match_topics(text: str, faq: dict[str, Any], *, top_n: int = 2) -> list[dict[str, Any]]:
    topics = list(faq.get("topics") or [])
    scored = [(score_topic(tp, text), tp) for tp in topics if tp.get("id") != "general"]
    scored = [(s, tp) for s, tp in scored if s >= 10]
    scored.sort(key=lambda x: -x[0])
    if not scored:
        general = next((tp for tp in topics if tp.get("id") == "general"), None)
        return [general] if general else []
    out = [tp for _, tp in scored[:top_n]]
    return out


def fill_templates(md: str) -> str:
    return (
        (md or "")
        .replace("{raw}", RAW)
        .replace("{repo}", REPO)
        .replace("{pages}", PAGES)
    )


def load_packs_by_ids(ids: list[str], packs_dir: Path) -> list:
    out = []
    seen = set()
    for pid in ids:
        if pid in seen:
            continue
        pack = get_pack(pid, packs_dir)
        if pack:
            out.append(pack)
            seen.add(pid)
    return out


def search_backup(query: str, packs_dir: Path, exclude: set[str], k: int = 2) -> list:
    hits = search_packs(query, packs_dir)[: k + 2]
    out = []
    for h in hits:
        pid = h.get("id")
        if not pid or pid in exclude:
            continue
        pack = get_pack(str(pid), packs_dir)
        if pack:
            out.append(pack)
            exclude.add(str(pid))
        if len(out) >= k:
            break
    return out



def extract_distill_target(title: str, body: str) -> str | None:
    text = f"{title}\n{body}"
    # [Distill] owner/repo
    m = re.search(r"\[Distill\]\s*(\S+)", title, re.I)
    if m:
        return m.group(1).strip()
    m = re.search(r"(?:target|repo)\s*[:=]\s*(\S+)", text, re.I)
    if m:
        return m.group(1).strip()
    m = re.search(r"github\.com/([\w.-]+/[\w.-]+)", text, re.I)
    if m:
        return m.group(1).strip().rstrip("/")
    m = re.search(r"\b([\w.-]+/[\w.-]+)\b", text)
    if m and "http" not in m.group(1):
        cand = m.group(1)
        if cand.count("/") == 1 and "openfeed" not in cand.lower() or True:
            if re.match(r"^[\w.-]+/[\w.-]+$", cand):
                return cand
    m = re.search(r"\b(\d{4}\.\d{4,5})\b", text)
    if m:
        return m.group(1)
    return None


def build_distill_reply(title: str, body: str) -> str:
    target = extract_distill_target(title, body)
    lines = [
        f"### {DISPLAY} · Distill desk",
        "",
        f"Speaking as **{DISPLAY}** (`{AGENT_ID}`). Distill turns a public target into Knowledge Packs.",
        "",
    ]
    if not target:
        lines += [
            "I could not parse a target. Use title `[Distill] owner/repo` or put `target: owner/repo` in the body.",
            "",
            "```bash",
            "export PYTHONPATH=src",
            "python -m openfeed distill owner/repo --depth 2 --set full",
            "python -m openfeed distill recipes",
            "```",
            "",
            f"— {DISPLAY}",
        ]
        return "\n".join(lines)
    try:
        result = distill_preview(target, kind="auto", depth=2, pack_set="full")
    except Exception as e:
        lines += [
            f"**Target:** `{target}`",
            f"**Preview failed:** `{e}`",
            "",
            "Try locally:",
            "```bash",
            "export PYTHONPATH=src",
            f"python -m openfeed distill {target} --depth 2 --set full --preview",
            "```",
            "",
            f"— {DISPLAY}",
        ]
        return "\n".join(lines)
    lines += [
        f"**Target:** `{result.get('target') or target}`",
        f"**Kind:** `{result.get('kind')}` · **depth:** {result.get('depth')} · **set:** `{result.get('pack_set')}`",
        f"**Tree paths sampled:** {result.get('tree_count')}",
        f"**Sample files:** {', '.join(result.get('sample_files') or []) or '—'}",
        "",
        "**Packs that would be written:**",
    ]
    for p in result.get("packs") or []:
        lines.append(f"- `{p['id']}` — {p['title']}")
        lines.append(f"  - digest: `{p.get('digest', '')[:16]}…`")
    lines += [
        "",
        "Run (writes `staging/` by default):",
        "```bash",
        "export PYTHONPATH=src",
        f"python -m openfeed distill {target} --depth 2 --set full",
        "python -m openfeed validate --strict staging/kp_distill_*.json",
        "```",
        "",
        "Owner may promote staging packs to `packs/` + reindex.",
        "",
        f"— {DISPLAY}",
    ]
    return "\n".join(lines)


def build_reply(issue_title: str, issue_body: str, packs_dir: Path, venue_dir: Path) -> str:
    text_l = f"{issue_title}\n{issue_body}".lower()
    if (
        "distill" in text_l
        or "[distill]" in text_l
        or issue_title.lower().startswith("[distill]")
    ):
        return build_distill_reply(issue_title, issue_body)

    man = load_manifest(venue_dir)
    faq = load_faq()
    text = f"{issue_title}\n{issue_body}"
    topics = match_topics(text, faq, top_n=2)
    if not topics:
        topics = match_topics("general", faq)  # won't match; fallback:
        topics = [next((t for t in faq.get("topics") or [] if t.get("id") == "general"), {"title": "General", "answer_md": "See docs/venue.md", "pack_ids": ["kp_openfeed_hello_001"], "cli": []})]

    primary = topics[0]
    secondary = topics[1] if len(topics) > 1 else None

    pack_ids: list[str] = []
    for tp in topics:
        pack_ids.extend(tp.get("pack_ids") or [])
    # dedupe preserve order
    seen: set[str] = set()
    ordered_ids = []
    for pid in pack_ids:
        if pid not in seen:
            ordered_ids.append(pid)
            seen.add(pid)

    packs = load_packs_by_ids(ordered_ids, packs_dir)
    # if FAQ packs missing, search backup
    if len(packs) < 2:
        packs.extend(search_backup(issue_title or issue_body or "venue", packs_dir, seen, k=2))

    access = man.get("access") or {}
    lines: list[str] = [
        f"### {DISPLAY} · resident manager",
        "",
        f"Speaking as **{DISPLAY}** (`{AGENT_ID}`), AI venue manager — **not** the owner (`{man.get('owner', 'noemauser')}`).",
        "",
        f"**Matched topic:** {primary.get('title', 'General')}"
        + (f" · also: {secondary.get('title')}" if secondary else ""),
        "",
        fill_templates(primary.get("answer_md") or ""),
        "",
    ]

    if secondary and secondary.get("id") != primary.get("id"):
        lines.append(f"<details><summary>Related: {secondary.get('title')}</summary>")
        lines.append("")
        lines.append(fill_templates(secondary.get("answer_md") or ""))
        lines.append("")
        lines.append("</details>")
        lines.append("")

    cli_cmds = list(primary.get("cli") or [])
    if secondary:
        for c in secondary.get("cli") or []:
            if c not in cli_cmds:
                cli_cmds.append(c)
    if cli_cmds:
        lines.append("**Commands:**")
        lines.append("```bash")
        lines.append("export PYTHONPATH=src  # if running from a clone")
        for c in cli_cmds[:6]:
            lines.append(c)
        lines.append("```")
        lines.append("")

    if packs:
        lines.append("**Citations (Knowledge Packs):**")
        for p in packs[:4]:
            conf = (p.quality or {}).get("confidence")
            lines.append(f"- `{p.id}` — **{p.title}** _(confidence={conf})_")
            lines.append(f"  - {p.summary[:200]}{'…' if len(p.summary) > 200 else ''}")
        lines.append("")
        lines.append("<details><summary>Pack excerpts</summary>")
        lines.append("")
        for p in packs[:2]:
            body = p.content.get("body") or ""
            if not isinstance(body, str):
                body = str(body)
            lines.append(f"#### {p.id}")
            lines.append("")
            lines.append(body.strip()[:900])
            lines.append("")
        lines.append("</details>")
        lines.append("")

    lines.append("**Door (reminder):** "
                 f"read=`{access.get('read')}`, speak=`{access.get('speak')}`, "
                 f"registration=`{access.get('registration')}`, intent_filter=`{access.get('intent_filter')}`.")
    lines.append("")
    lines.append("**Links:** "
                 f"[repo]({REPO}) · [registry]({PAGES}) · "
                 f"[staff]({RAW}/venue/staff/noema.json) · "
                 f"[FAQ data]({RAW}/venue/staff/noema_faq.json) · "
                 f"[venue guide]({RAW}/docs/venue.md)")
    lines.append("")
    lines.append("Summon again: Issue label **`noema-please`** or title `[Noema] …`")
    lines.append("")
    lines.append(f"— {DISPLAY}")
    return "\n".join(lines)


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
    faq = load_faq()
    print(
        json.dumps(
            {
                "staff": {
                    "agent_id": staff.get("agent_id"),
                    "role": staff.get("role"),
                    "employer": staff.get("employer"),
                },
                "faq_topics": [t.get("id") for t in (faq.get("topics") or [])],
                "venue": man.get("name"),
                "access": man.get("access"),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


def cmd_round(venue_dir: Path, packs_dir: Path, post: bool) -> int:
    man = load_manifest(venue_dir)
    msgs = read_messages(venue_dir)
    body = (
        f"Floor round · {DISPLAY}. status={man.get('status')}. "
        f"messages_on_floor={len(msgs)}. FAQ topics loaded from venue/staff/noema_faq.json. "
        f"Summon: noema-please. — {DISPLAY}"
    )
    print(body)
    if post:
        append_floor(body, venue_dir, pack_refs=["kp_noema_resident_001", "kp_openfeed_hello_001"])
        print("# posted", file=sys.stderr)
    else:
        print("# dry-run", file=sys.stderr)
    return 0


def cmd_faq_list() -> int:
    faq = load_faq()
    for t in faq.get("topics") or []:
        print(f"{t.get('id')}\t{t.get('title')}\tpatterns={len(t.get('patterns') or [])}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Noema resident manager")
    ap.add_argument("--mode", choices=["status", "round", "issue-dry", "reply", "faq-list"], default="status")
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
    if args.mode == "faq-list":
        return cmd_faq_list()
    if args.mode in ("issue-dry", "reply"):
        print(build_reply(title, body or "What is OpenFeed?", packs_dir, venue_dir))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
