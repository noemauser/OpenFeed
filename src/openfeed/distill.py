"""OpenFeed Distill — public target → Knowledge Packs for agents and builders.

Inputs: GitHub owner/repo, local path, arXiv id.
Outputs: schema-valid packs (overview, surfaces, agent_use, optional architecture).

Use for learning, feeding, rebuild notes, remix — as you need.
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

USER_AGENT = "OpenFeed-Distill/0.3.2 (+https://github.com/noemauser/OpenFeed)"
GITHUB_API = "https://api.github.com"
RAW = "https://raw.githubusercontent.com"

# Hot paths to sample (depth)
HOT_GLOBS = (
    "README.md",
    "LICENSE",
    "LICENSE.md",
    "pyproject.toml",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "requirements.txt",
    "setup.py",
    "Dockerfile",
    "Makefile",
    "docs/",
    "src/",
    "lib/",
    "app/",
    "cmd/",
    "pkg/",
    ".github/workflows/",
)


def _utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _get_json(url: str, *, timeout: float = 45.0) -> Any:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/vnd.github+json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec B310
        return json.loads(resp.read().decode("utf-8"))


def _get_text(url: str, *, timeout: float = 45.0, max_bytes: int = 200_000) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/plain,*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec B310
        data = resp.read(max_bytes)
        return data.decode("utf-8", errors="replace")


def parse_github_target(target: str) -> tuple[str, str]:
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


def _truncate(text: str, max_chars: int) -> str:
    t = (text or "").strip()
    if len(t) <= max_chars:
        return t
    return t[: max_chars - 20] + "\n\n…(truncated)…"


def _read_local_file(root: Path, rel: str, max_chars: int = 4000) -> str | None:
    p = root / rel
    if not p.is_file():
        return None
    try:
        return _truncate(p.read_text(encoding="utf-8", errors="replace"), max_chars)
    except OSError:
        return None


def _walk_local(root: Path, depth: int) -> tuple[list[str], dict[str, str]]:
    """Return relative paths (capped) and sample file contents."""
    paths: list[str] = []
    samples: dict[str, str] = {}
    root = root.resolve()
    if depth < 0:
        depth = 0
    for p in sorted(root.rglob("*")):
        if p.is_dir() and p.name in {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}:
            continue
        try:
            rel = str(p.relative_to(root)).replace("\\", "/")
        except ValueError:
            continue
        if rel.startswith(".git"):
            continue
        level = rel.count("/")
        if level > depth:
            continue
        if p.is_file():
            paths.append(rel)
            if len(paths) > 400:
                break
        elif p.is_dir() and level < depth:
            paths.append(rel + "/")

    for name in (
        "README.md",
        "LICENSE",
        "LICENSE.md",
        "pyproject.toml",
        "package.json",
        "Cargo.toml",
        "go.mod",
        "Makefile",
        "Dockerfile",
    ):
        body = _read_local_file(root, name)
        if body:
            samples[name] = body
    # sample a few docs
    docs = root / "docs"
    if docs.is_dir():
        for p in sorted(docs.glob("*.md"))[:5]:
            rel = str(p.relative_to(root)).replace("\\", "/")
            body = _read_local_file(root, rel, 2500)
            if body:
                samples[rel] = body
    return paths, samples


def fetch_github_repo(owner: str, repo: str, *, depth: int = 2) -> dict[str, Any]:
    meta = _get_json(f"{GITHUB_API}/repos/{owner}/{repo}")
    if meta.get("private"):
        raise PermissionError("GitHub API reports private repository (public API only)")
    default_branch = meta.get("default_branch") or "main"
    readme = ""
    try:
        readme = _get_text(f"{RAW}/{owner}/{repo}/{default_branch}/README.md")
    except Exception:
        try:
            data = _get_json(f"{GITHUB_API}/repos/{owner}/{repo}/readme")
            import base64

            readme = base64.b64decode(data.get("content") or "").decode("utf-8", errors="replace")
        except Exception:
            readme = ""

    tree_paths: list[str] = []
    try:
        recursive = "1" if depth >= 1 else "0"
        tree = _get_json(
            f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/{default_branch}?recursive={recursive}"
        )
        for item in tree.get("tree") or []:
            path = item.get("path") or ""
            if not path:
                continue
            level = path.count("/")
            if level > depth:
                continue
            if item.get("type") == "tree":
                tree_paths.append(path + "/")
            else:
                tree_paths.append(path)
            if len(tree_paths) >= 500:
                break
    except Exception:
        tree_paths = []

    samples: dict[str, str] = {}
    if readme:
        samples["README.md"] = _truncate(readme, 8000)
    # fetch hot files if present in tree
    want = [
        "LICENSE",
        "LICENSE.md",
        "pyproject.toml",
        "package.json",
        "Cargo.toml",
        "go.mod",
        "Makefile",
        "Dockerfile",
        "requirements.txt",
    ]
    tree_set = set(tree_paths)
    for name in want:
        if name in tree_set or any(p.endswith("/" + name) or p == name for p in tree_paths):
            try:
                samples[name] = _truncate(
                    _get_text(f"{RAW}/{owner}/{repo}/{default_branch}/{name}"), 4000
                )
            except Exception:
                pass
    # a few docs/*.md
    doc_files = [p for p in tree_paths if p.startswith("docs/") and p.endswith(".md")][:5]
    for pth in doc_files:
        try:
            samples[pth] = _truncate(
                _get_text(f"{RAW}/{owner}/{repo}/{default_branch}/{pth}"), 2500
            )
        except Exception:
            pass

    lic = meta.get("license") or {}
    license_spdx = lic.get("spdx_id") or lic.get("key") if isinstance(lic, dict) else None
    root = sorted({p.split("/")[0].rstrip("/") for p in tree_paths if p})[:80]

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
        "readme": _truncate(readme, 12000),
        "root_entries": root,
        "tree_paths": tree_paths[:400],
        "file_samples": samples,
        "depth": depth,
        "fetched_at": _utcnow(),
        "api_url": f"{GITHUB_API}/repos/{owner}/{repo}",
    }


def fetch_local_project(path: Path, *, depth: int = 2) -> dict[str, Any]:
    path = path.resolve()
    if not path.is_dir():
        raise NotADirectoryError(path)
    tree_paths, samples = _walk_local(path, depth)
    readme = samples.get("README.md") or ""
    description = ""
    if "pyproject.toml" in samples:
        m = re.search(r'description\s*=\s*"([^"]+)"', samples["pyproject.toml"])
        if m:
            description = m.group(1)
    root = sorted({p.split("/")[0].rstrip("/") for p in tree_paths if p})[:80]
    return {
        "kind": "local_path",
        "path": str(path),
        "name": path.name,
        "repo": path.name,
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
        "tree_paths": tree_paths[:400],
        "file_samples": samples,
        "depth": depth,
        "fetched_at": _utcnow(),
        "api_url": None,
        "owner": "local",
    }


def fetch_arxiv(arxiv_id: str, *, depth: int = 0) -> dict[str, Any]:
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
        "tree_paths": [],
        "file_samples": {"abstract": _truncate(summary, 6000)},
        "topics": ["arxiv", "paper"],
        "language": None,
        "license_spdx": None,
        "depth": depth,
        "fetched_at": _utcnow(),
        "api_url": url,
        "owner": "arxiv",
        "repo": aid,
        "stars": None,
        "forks": None,
        "open_issues": None,
        "default_branch": None,
    }


def _detect_stack(samples: dict[str, str], language: str | None) -> list[str]:
    stack: list[str] = []
    if language:
        stack.append(str(language))
    keys = set(samples)
    if "pyproject.toml" in keys or "requirements.txt" in keys or "setup.py" in keys:
        stack.append("Python packaging")
    if "package.json" in keys:
        stack.append("Node/npm")
        try:
            pkg = json.loads(samples["package.json"])
            deps = list((pkg.get("dependencies") or {}).keys())[:12]
            if deps:
                stack.append("npm deps: " + ", ".join(deps))
        except Exception:
            pass
    if "Cargo.toml" in keys:
        stack.append("Rust/Cargo")
    if "go.mod" in keys:
        stack.append("Go modules")
    if "Dockerfile" in keys:
        stack.append("Docker")
    if "Makefile" in keys:
        stack.append("Make")
    # python project name from pyproject
    if "pyproject.toml" in samples:
        m = re.search(r'name\s*=\s*"([^"]+)"', samples["pyproject.toml"])
        if m:
            stack.append(f"package: {m.group(1)}")
    return list(dict.fromkeys(stack))


def _pack_id(prefix: str, target_slug: str) -> str:
    return f"kp_distill_{target_slug}_{prefix}_001"


def build_packs_from_snapshot(
    snap: dict[str, Any],
    *,
    pack_set: str = "full",
) -> list[dict[str, Any]]:
    """Build packs. pack_set: core (3) | full (4 with architecture)."""
    now = _utcnow()
    kind = snap.get("kind") or "target"
    slug = slugify(str(snap.get("repo") or snap.get("name") or snap.get("full_name") or "target"))
    url = snap.get("html_url") or snap.get("path") or "unknown"
    desc = snap.get("description") or "(no description)"
    readme = _truncate(snap.get("readme") or "", 2500)
    roots = snap.get("root_entries") or []
    roots_md = ", ".join(f"`{r}`" for r in roots[:40]) or "_(none)_"
    tree = snap.get("tree_paths") or []
    tree_preview = "\n".join(f"- `{p}`" for p in tree[:60]) or "_(none)_"
    samples = snap.get("file_samples") or {}
    lic = snap.get("license_spdx") or "unknown"
    topics = ", ".join(snap.get("topics") or []) or "—"
    stack = _detect_stack(samples, snap.get("language"))
    stack_md = ", ".join(stack) if stack else "—"
    depth = snap.get("depth", 1)

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
                "title": "Fetch endpoint used by Distill",
                "accessed_at": snap.get("fetched_at") or now,
                "license": "see-target",
            }
        )

    note = (
        "## About this distill\n\n"
        f"Generated by **OpenFeed Distill** (depth={depth}, set=`{pack_set}`). "
        "Public metadata + sampled files. Use for learning, feeding agents, rebuild notes, remix.\n"
    )

    # LICENSE excerpt
    lic_body = samples.get("LICENSE") or samples.get("LICENSE.md") or ""
    lic_section = _truncate(lic_body, 1200) if lic_body else f"SPDX hint: `{lic}`"

    # manifests section
    man_bits = []
    for key in ("pyproject.toml", "package.json", "Cargo.toml", "go.mod", "Makefile", "Dockerfile"):
        if key in samples:
            man_bits.append(f"### `{key}`\n\n```\n{_truncate(samples[key], 1500)}\n```\n")
    manifests_md = "\n".join(man_bits) if man_bits else "_(no common manifests sampled)_"

    overview_body = f"""# Distill overview — {snap.get('full_name')}

{note}

## Target

| Field | Value |
|-------|-------|
| Kind | `{kind}` |
| Name | {snap.get('full_name')} |
| URL | {url} |
| Description | {desc} |
| Language | {snap.get('language') or '—'} |
| Stack signals | {stack_md} |
| License | `{lic}` |
| Topics | {topics} |
| Depth | {depth} |
| Fetched | {snap.get('fetched_at')} |

## README excerpt

{readme if readme else '_(no README)_'}

## License signal

{lic_section}

## Takeaway

Orientation pack for agents and builders. Pair with surfaces + architecture packs when present.
"""

    surfaces_body = f"""# Distill surfaces — {snap.get('full_name')}

{note}

## Root layout

{roots_md}

## Tree sample (depth ≤ {depth})

{tree_preview}

## How to dig in

1. Documented entry points: README, docs/, CLI, MCP, OpenAPI  
2. Hot dirs often: `src/`, `lib/`, `app/`, `cmd/`, `docs/`  
3. Stack signals: {stack_md}  
4. OpenFeed-style extras if present: `venue/`, `packs/`, `registry/`  

## Signals

- Stars: {snap.get('stars')} · Forks: {snap.get('forks')} · Issues: {snap.get('open_issues')}
- Branch: {snap.get('default_branch') or '—'}
"""

    agent_body = f"""# Distill agent-use — {snap.get('full_name')}

{note}

## Suggested loop

1. **Map** — overview + README  
2. **Retrieve** — docs, schemas, tree sample, architecture pack  
3. **Act** — tools/CLI the project documents; rebuild or extend as you need  
4. **Cite** — `kp_…` + original URL  
5. **Iterate** — deeper distill (`--depth`), more file samples, human notes  

## OpenFeed commands

```bash
export PYTHONPATH=src
python -m openfeed search "distill {slug}" --packs-dir packs
python -m openfeed validate --strict path/to/distill-pack.json
python -m openfeed distill {snap.get('full_name') or snap.get('path') or 'owner/repo'} --depth {depth}
```

## Staging → menu

Default write is `staging/`. Promote to `packs/` when the house wants it on the official menu.
"""

    arch_body = f"""# Distill architecture — {snap.get('full_name')}

{note}

## Stack

{stack_md}

## Layout (compressed)

{tree_preview}

## Manifests / config samples

{manifests_md}

## Rebuild / explore notes

These are **working notes** from public files, not a full formal architecture review.

1. Identify entrypoints from README and package manifests  
2. Map modules under the hottest top-level dirs  
3. Note license (`{lic}`) before redistribution  
4. Prefer tests and CI under `.github/workflows/` if present for how the project validates itself  
5. For agent feeding: promote stable facts into Knowledge Packs with provenance  

## Doc samples

"""
    doc_bits = []
    for k, v in samples.items():
        if k.startswith("docs/") or k in ("README.md",):
            continue
        if k.endswith(".md") and k not in ("LICENSE.md",):
            doc_bits.append(f"### `{k}`\n\n{_truncate(v, 800)}\n")
    for k, v in samples.items():
        if k.startswith("docs/"):
            doc_bits.append(f"### `{k}`\n\n{_truncate(v, 800)}\n")
    arch_body += "\n".join(doc_bits[:6]) if doc_bits else "_(no extra docs sampled)_"
    arch_body += "\n"

    packs: list[dict[str, Any]] = []
    base_tags = ["distill", "sourced", "agents", slug, kind.replace("_", "-"), f"depth-{depth}"]

    def make(prefix: str, title: str, summary: str, body: str, tags_extra: list[str]) -> dict[str, Any]:
        pid = _pack_id(prefix, slug)
        p = create_pack(
            pack_id=pid,
            title=title,
            summary=summary,
            body=body,
            tags=list(dict.fromkeys(base_tags + tags_extra)),
            created_by="noema-distill",
            method="extracted",
            license="MIT",
        )
        d = p.to_dict()
        d["provenance"] = {
            "created_by": "noema-distill",
            "created_at": now,
            "method": "extracted",
            "sources": sources,
            "parent_packs": [],
        }
        d["quality"] = {
            "self_score": 0.82 if pack_set == "full" else 0.78,
            "confidence": 0.8 if depth >= 2 else 0.72,
            "community_score": None,
            "reproduction_status": "untested",
            "safety_flags": ["distill-generated"],
        }
        d["relations"] = []
        return d

    o = make(
        "overview",
        f"Distill overview: {snap.get('full_name')}",
        f"Orientation for {snap.get('full_name')}: description, stack, license, README excerpt.",
        overview_body,
        ["overview"],
    )
    s = make(
        "surfaces",
        f"Distill surfaces: {snap.get('full_name')}",
        f"Layout and tree sample (depth {depth}) for {snap.get('full_name')}.",
        surfaces_body,
        ["surfaces"],
    )
    a = make(
        "agent_use",
        f"Distill agent-use: {snap.get('full_name')}",
        f"Agent loop and OpenFeed commands for working with {snap.get('full_name')}.",
        agent_body,
        ["agent-use"],
    )
    packs_core = [o, s, a]
    if pack_set == "full":
        ar = make(
            "architecture",
            f"Distill architecture: {snap.get('full_name')}",
            f"Stack, tree, manifests, rebuild/explore notes for {snap.get('full_name')}.",
            arch_body,
            ["architecture", "rebuild"],
        )
        packs_core.append(ar)

    # wire relations
    ids = [p["id"] for p in packs_core]
    for p in packs_core:
        p["relations"] = [
            {"type": "related", "target": tid} for tid in ids if tid != p["id"]
        ][:4]
        if p["id"] != o["id"]:
            p["relations"].insert(0, {"type": "derived_from", "target": o["id"]})

    return packs_core


def distill_target(
    target: str,
    *,
    kind: str = "auto",
    out_dir: Path | None = None,
    write: bool = True,
    depth: int = 2,
    pack_set: str = "full",
) -> dict[str, Any]:
    kind = (kind or "auto").lower()
    pack_set = (pack_set or "full").lower()
    if pack_set not in ("core", "full"):
        raise ValueError("pack_set must be core|full")
    depth = max(0, min(int(depth), 4))

    if kind == "auto":
        if target.startswith("arxiv:") or re.match(r"^\d{4}\.\d{4,5}(v\d+)?$", target.strip()):
            kind = "arxiv"
        elif Path(target).is_dir():
            kind = "local"
        else:
            kind = "github"

    if kind == "github":
        owner, repo = parse_github_target(target)
        snap = fetch_github_repo(owner, repo, depth=depth)
    elif kind == "local":
        snap = fetch_local_project(Path(target), depth=depth)
    elif kind == "arxiv":
        snap = fetch_arxiv(target, depth=depth)
    else:
        raise ValueError(f"unknown kind: {kind}")

    packs = build_packs_from_snapshot(snap, pack_set=pack_set)
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
            path = out_dir / f"{p['id']}.json"
            path.write_text(json.dumps(p, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            written.append(str(path))

    digests = {p["id"]: pack_digest(p) for p in packs}
    return {
        "ok": len(errors) == 0,
        "kind": kind,
        "target": snap.get("full_name"),
        "depth": depth,
        "pack_set": pack_set,
        "snapshot": {
            k: v
            for k, v in snap.items()
            if k not in ("readme", "file_samples")
        },
        "sample_files": list((snap.get("file_samples") or {}).keys()),
        "tree_count": len(snap.get("tree_paths") or []),
        "packs": [{"id": p["id"], "title": p["title"], "digest": digests[p["id"]]} for p in packs],
        "written": written,
        "errors": errors,
        "note": "Distill turns public targets into Knowledge Packs for agents and builders.",
    }


def distill_preview(
    target: str,
    *,
    kind: str = "auto",
    depth: int = 2,
    pack_set: str = "full",
) -> dict[str, Any]:
    return distill_target(
        target, kind=kind, write=False, depth=depth, pack_set=pack_set
    )


def recipes() -> list[dict[str, str]]:
    return [
        {"id": "github", "usage": "openfeed distill owner/repo --depth 2 --set full"},
        {"id": "local", "usage": "openfeed distill . --kind local --depth 2"},
        {"id": "arxiv", "usage": "openfeed distill 2005.11401 --kind arxiv --set core"},
        {"id": "core", "usage": "3 packs: overview, surfaces, agent_use"},
        {"id": "full", "usage": "4 packs: core + architecture"},
    ]
