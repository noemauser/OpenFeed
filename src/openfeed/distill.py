"""OpenFeed Distill — reverse a public target into Knowledge Packs (not a cloner).

Input: public GitHub repo (owner/name), local path, or arXiv id.
Output: validated Knowledge Pack JSON files for staging/ (agent food with provenance).

This is the "decanter" arm of the bar: understand → pack → cite.
It is NOT UnBuild/REA: no binary reverse engineering, no clone blueprints for piracy.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .pack import create_pack, validate_pack
from .sign import pack_digest

USER_AGENT = "OpenFeed-Distill/0.3.0 (+https://github.com/noemauser/OpenFeed)"
GITHUB_API = "https://api.github.com"
RAW = "https://raw.githubusercontent.com"


def _utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _get_json(url: str, *, timeout: float = 30.0) -> Any:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec B310
        return json.loads(resp.read().decode("utf-8"))


def _get_text(url: str, *, timeout: float = 30.0) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/plain"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec B310
        return resp.read().decode("utf-8", errors="replace")


def parse_github_target(target: str) -> tuple[str, str]:
    """Accept owner/repo or https://github.com/owner/repo[.git]."""
    t = target.strip().rstrip("/")
    t = re.sub(r"^https?://github\.com/", "", t)
    t = re.sub(r"\.git$", "", t)
    parts = [p for p in t.split("/") if p]
    if len(parts) < 2:
        raise ValueError(f"expected owner/repo, got: {target}")
    return parts[0], parts[1]


def slugify(s: str, *, max_len: int = 40) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return (s[:max_len] or "target").rstrip("_")


def fetch_github_repo(owner: str, repo: str) -> dict[str, Any]:
    """Fetch public repo metadata, README text, root tree names, license."""
    meta = _get_json(f"{GITHUB_API}/repos/{owner}/{repo}")
    if meta.get("private"):
        raise PermissionError("refusing private repositories")
    default_branch = meta.get("default_branch") or "main"
    readme = ""
    try:
        # API readme returns base64; prefer raw
        readme = _get_text(f"{RAW}/{owner}/{repo}/{default_branch}/README.md")
    except Exception:
        try:
            data = _get_json(f"{GITHUB_API}/repos/{owner}/{repo}/readme")
            import base64

            readme = base64.b64decode(data.get("content") or "").decode("utf-8", errors="replace")
        except Exception:
            readme = ""
    tree_names: list[str] = []
    try:
        tree = _get_json(
            f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=0"
        )
        for item in tree.get("tree") or []:
            if item.get("type") == "tree":
                tree_names.append(item.get("path") or "")
            elif item.get("type") == "blob":
                tree_names.append(item.get("path") or "")
    except Exception:
        tree_names = []
    # root only for summary
    root = sorted({p.split("/")[0] for p in tree_names if p})[:80]
    license_spdx = None
    lic = meta.get("license") or {}
    if isinstance(lic, dict):
        license_spdx = lic.get("spdx_id") or lic.get("key")
    return {
        "kind": "github_repo",
        "owner": owner,
        "repo": repo,
        "full_name": meta.get("full_name") or f"{owner}/{repo}",
        "html_url": meta.get("html_url") or f"https://github.com/{owner}/{repo}",
        "description": meta.get("description") or "",
        "default_branch": default_branch,
        "topics": meta.get("topics") or [],
        "language": meta.get("language"),
        "license_spdx": license_spdx,
        "stars": meta.get("stargazers_count"),
        "forks": meta.get("forks_count"),
        "open_issues": meta.get("open_issues_count"),
        "readme": readme[:12000],
        "root_entries": root,
        "fetched_at": _utcnow(),
        "api_url": f"{GITHUB_API}/repos/{owner}/{repo}",
    }


def fetch_local_project(path: Path) -> dict[str, Any]:
    path = path.resolve()
    if not path.is_dir():
        raise NotADirectoryError(path)
    readme = ""
    for name in ("README.md", "Readme.md", "readme.md"):
        p = path / name
        if p.is_file():
            readme = p.read_text(encoding="utf-8", errors="replace")[:12000]
            break
    root = sorted([c.name for c in path.iterdir()])[:80]
    pyproject = path / "pyproject.toml"
    description = ""
    if pyproject.is_file():
        text = pyproject.read_text(encoding="utf-8", errors="replace")
        m = re.search(r'description\s*=\s*"([^"]+)"', text)
        if m:
            description = m.group(1)
    return {
        "kind": "local_path",
        "path": str(path),
        "name": path.name,
        "full_name": path.name,
        "html_url": None,
        "description": description,
        "default_branch": None,
        "topics": [],
        "language": "mixed",
        "license_spdx": "MIT" if (path / "LICENSE").is_file() else None,
        "stars": None,
        "forks": None,
        "open_issues": None,
        "readme": readme,
        "root_entries": root,
        "fetched_at": _utcnow(),
        "api_url": None,
    }


def fetch_arxiv(arxiv_id: str) -> dict[str, Any]:
    """Fetch arXiv atom abstract (public)."""
    aid = arxiv_id.strip().replace("arxiv:", "")
    url = f"http://export.arxiv.org/api/query?id_list={aid}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:  # nosec B310
        xml = resp.read().decode("utf-8", errors="replace")
    def tag(name: str) -> str:
        m = re.search(rf"<[^>]*{name}[^>]*>(.*?)</[^>]*{name}>", xml, re.S | re.I)
        return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""

    title = tag("title").replace("\n", " ")
    summary = tag("summary")
    return {
        "kind": "arxiv",
        "arxiv_id": aid,
        "full_name": f"arXiv:{aid}",
        "html_url": f"https://arxiv.org/abs/{aid}",
        "description": title,
        "readme": f"# {title}\n\n{summary}\n",
        "root_entries": [],
        "topics": ["arxiv", "paper"],
        "language": None,
        "license_spdx": None,
        "fetched_at": _utcnow(),
        "api_url": url,
        "owner": "arxiv",
        "repo": aid,
    }


def _truncate_readme(text: str, max_chars: int = 2500) -> str:
    t = text.strip()
    if len(t) <= max_chars:
        return t
    return t[: max_chars - 20] + "\n\n…(truncated)…"


def _pack_id(prefix: str, target_slug: str) -> str:
    return f"kp_distill_{target_slug}_{prefix}_001"


def build_packs_from_snapshot(snap: dict[str, Any]) -> list[dict[str, Any]]:
    """Build overview + surfaces + agent_use packs (and architecture if tree rich)."""
    now = _utcnow()
    kind = snap.get("kind") or "target"
    slug = slugify(str(snap.get("repo") or snap.get("name") or snap.get("full_name") or "target"))
    url = snap.get("html_url") or snap.get("path") or "unknown"
    desc = snap.get("description") or "(no description)"
    readme = _truncate_readme(snap.get("readme") or "")
    roots = snap.get("root_entries") or []
    roots_md = ", ".join(f"`{r}`" for r in roots[:40]) or "_(none)_"
    lic = snap.get("license_spdx") or "unknown"
    topics = ", ".join(snap.get("topics") or []) or "—"
    sources = [
        {
            "url": str(url),
            "title": str(snap.get("full_name") or url),
            "accessed_at": snap.get("fetched_at") or now,
            "license": lic if lic != "unknown" else "see-target",
        }
    ]
    if snap.get("api_url"):
        sources.append(
            {
                "url": str(snap["api_url"]),
                "title": "API/fetch endpoint used by Distill",
                "accessed_at": snap.get("fetched_at") or now,
                "license": "see-target",
            }
        )

    disclaimer = (
        "## Distill disclaimer\n\n"
        "This pack was **distilled** by OpenFeed Distill for **agent feeding** "
        "(understand + cite). It is **not** a license to clone proprietary software, "
        "bypass DRM, or reverse binaries. Prefer the original project's license and ToS.\n"
    )

    overview_body = f"""# Distill overview — {snap.get('full_name')}

{disclaimer}

## Target

| Field | Value |
|-------|-------|
| Kind | `{kind}` |
| Name | {snap.get('full_name')} |
| URL | {url} |
| Description | {desc} |
| Language | {snap.get('language') or '—'} |
| License (SPDX hint) | `{lic}` |
| Topics | {topics} |
| Fetched | {snap.get('fetched_at')} |

## README excerpt

{readme if readme else '_(no README fetched)_'}

## Agent takeaway

Use this pack as **orientation**, then fetch primary sources. Cite this pack id when used.
"""

    surfaces_body = f"""# Distill surfaces — {snap.get('full_name')}

{disclaimer}

## Root layout (observed)

{roots_md}

## How agents should approach surfaces

1. Prefer **documented** entry points (README, docs/, OpenAPI, MCP, CLI `--help`)
2. Do not invent private endpoints
3. Respect rate limits and auth; Distill only sees **public** metadata
4. For OpenFeed-style projects, also check `venue/`, `packs/`, `registry/`

## Observed signals

- Stars: {snap.get('stars')}
- Forks: {snap.get('forks')}
- Open issues: {snap.get('open_issues')}
- Default branch: {snap.get('default_branch') or '—'}

## Next reads

- Overview pack sibling
- Agent-use pack sibling
- Original repository
"""

    agent_body = f"""# Distill agent-use — {snap.get('full_name')}

{disclaimer}

## Safe agent loop

1. **Map** — read overview pack + original README  
2. **Retrieve** — docs, schemas, public APIs only  
3. **Act** — tools the project documents (CLI/MCP/HTTP)  
4. **Cite** — pack ids + original URLs  
5. **Do not** — exfiltrate secrets, bypass auth, or reimplement under a confused license  

## Suggested OpenFeed actions

```bash
# after distill packs land in staging/ or packs/
export PYTHONPATH=src
python -m openfeed search "distill {slug}" --packs-dir packs
python -m openfeed validate --strict path/to/distill-pack.json
```

## When to open a PR

- Distill output under `staging/` is a **proposal**
- Maintainers validate license + content_policy before moving to `packs/`

## Related

- `docs/distill.md` — Distill arm of the bar
- `kp_a2a_openfeed_bridge_001` — sharing pack-refs with peers
"""

    packs: list[dict[str, Any]] = []
    base_meta = {
        "version": "0.1.0",
        "provenance": {
            "created_by": "noema-distill",
            "created_at": now,
            "method": "extracted",
            "sources": sources,
            "parent_packs": [],
        },
        "quality": {
            "self_score": 0.78,
            "confidence": 0.75,
            "community_score": None,
            "reproduction_status": "untested",
            "safety_flags": ["distill-generated", "verify-against-source"],
        },
        "license": "MIT",
        "signatures": [],
        "tags": ["distill", "sourced", "agents", slug, kind.replace("_", "-")],
    }

    def make(prefix: str, title: str, summary: str, body: str, tags_extra: list[str]) -> dict[str, Any]:
        pid = _pack_id(prefix, slug)
        p = create_pack(
            pack_id=pid,
            title=title,
            summary=summary,
            body=body,
            tags=list(dict.fromkeys(base_meta["tags"] + tags_extra)),
            created_by="noema-distill",
            method="extracted",
            license="MIT",
        )
        d = p.to_dict()
        d["provenance"] = base_meta["provenance"]
        d["quality"] = base_meta["quality"]
        d["relations"] = []
        return d

    o = make(
        "overview",
        f"Distill overview: {snap.get('full_name')}",
        f"Distilled orientation for {snap.get('full_name')}: what it is, license hint, README excerpt. Agent food — not a clone kit.",
        overview_body,
        ["overview"],
    )
    s = make(
        "surfaces",
        f"Distill surfaces: {snap.get('full_name')}",
        f"Observed layout and approach surfaces for agents using {snap.get('full_name')} (public metadata only).",
        surfaces_body,
        ["surfaces", "architecture"],
    )
    a = make(
        "agent_use",
        f"Distill agent-use: {snap.get('full_name')}",
        f"How agents should safely use/learn from {snap.get('full_name')} inside OpenFeed loops (cite, don't pirate).",
        agent_body,
        ["agent-use", "safety"],
    )
    # wire relations
    o["relations"] = [
        {"type": "related", "target": s["id"]},
        {"type": "related", "target": a["id"]},
    ]
    s["relations"] = [
        {"type": "derived_from", "target": o["id"]},
        {"type": "related", "target": a["id"]},
    ]
    a["relations"] = [
        {"type": "derived_from", "target": o["id"]},
        {"type": "related", "target": s["id"]},
    ]
    packs.extend([o, s, a])
    return packs


def distill_target(
    target: str,
    *,
    kind: str = "auto",
    out_dir: Path | None = None,
    write: bool = True,
) -> dict[str, Any]:
    """Distill a target into packs. kind: auto|github|local|arxiv."""
    kind = (kind or "auto").lower()
    if kind == "auto":
        if target.startswith("arxiv:") or re.match(r"^\d{4}\.\d{4,5}(v\d+)?$", target.strip()):
            kind = "arxiv"
        elif Path(target).is_dir():
            kind = "local"
        else:
            kind = "github"

    if kind == "github":
        owner, repo = parse_github_target(target)
        snap = fetch_github_repo(owner, repo)
    elif kind == "local":
        snap = fetch_local_project(Path(target))
    elif kind == "arxiv":
        snap = fetch_arxiv(target)
    else:
        raise ValueError(f"unknown kind: {kind}")

    packs = build_packs_from_snapshot(snap)
    errors: list[str] = []
    for p in packs:
        errs = validate_pack(p, strict=True)
        if errs:
            errors.extend([f"{p.get('id')}: {e}" for e in errs])

    written: list[str] = []
    out_dir = Path(out_dir) if out_dir else Path("staging")
    if write and not errors:
        out_dir.mkdir(parents=True, exist_ok=True)
        for p in packs:
            # file name from id
            fname = p["id"].replace("kp_distill_", "kp_distill_") + ".json"
            # cleaner: kp_distill_<slug>_<prefix>_001.json already is id
            path = out_dir / f"{p['id']}.json"
            path.write_text(json.dumps(p, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            written.append(str(path))

    digests = {p["id"]: pack_digest(p) for p in packs}
    return {
        "ok": len(errors) == 0,
        "kind": kind,
        "target": snap.get("full_name"),
        "snapshot": {k: v for k, v in snap.items() if k != "readme"},
        "readme_chars": len(snap.get("readme") or ""),
        "packs": [{"id": p["id"], "title": p["title"], "digest": digests[p["id"]]} for p in packs],
        "written": written,
        "errors": errors,
        "disclaimer": "Distill produces agent-feed Knowledge Packs. Not a software cloner.",
    }


def distill_preview(target: str, *, kind: str = "auto") -> dict[str, Any]:
    return distill_target(target, kind=kind, write=False)
