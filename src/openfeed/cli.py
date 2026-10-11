"""OpenFeed CLI."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .graph import related_packs
from .mcp_server import list_packs, search_packs
from .pack import create_pack, load_pack, save_pack, validate_pack
from .sign import load_key, sign_pack_dict, verify_pack_dict


def cmd_create(args: argparse.Namespace) -> int:
    body = args.body
    if args.body_file:
        body = Path(args.body_file).read_text(encoding="utf-8")

    pack = create_pack(
        title=args.title,
        summary=args.summary,
        body=body,
        content_type=args.type,
        created_by=args.created_by,
        method=args.method,
        self_score=args.self_score,
        confidence=args.confidence,
        license=args.license,
        tags=[t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else [],
    )

    out = Path(args.output) if args.output else Path(f"packs/{pack.id}.json")
    save_pack(pack, out)
    print(f"Created Knowledge Pack: {out}")
    print(f"  id: {pack.id}")
    print(f"  title: {pack.title}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    path = Path(args.path)
    data = json.loads(path.read_text(encoding="utf-8"))
    errs = validate_pack(data, strict=args.strict)
    if errs:
        print("INVALID")
        for e in errs:
            print(f"  - {e}")
        return 1
    print("VALID" + (" (strict)" if args.strict else ""))
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    pack = load_pack(args.path, strict=args.strict)
    print(pack.to_json())
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    packs_dir = Path(args.packs_dir) if args.packs_dir else None
    for m in list_packs(packs_dir):
        if "error" in m:
            print(f"ERR  {m.get('path')}: {m.get('error')}")
        else:
            print(f"{m.get('id')}\t{m.get('title')}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    packs_dir = Path(args.packs_dir) if args.packs_dir else None
    hits = search_packs(args.query, packs_dir)
    for m in hits:
        print(f"{m.get('id')}\t{m.get('title')}")
    print(f"# {len(hits)} hit(s)", file=sys.stderr)
    return 0


def cmd_related(args: argparse.Namespace) -> int:
    packs_dir = Path(args.packs_dir) if args.packs_dir else None
    result = related_packs(args.pack_id, packs_dir)
    if not result.get("ok"):
        print(result.get("error", "error"), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_sign(args: argparse.Namespace) -> int:
    path = Path(args.path)
    data = json.loads(path.read_text(encoding="utf-8"))
    key = load_key(args.key_file)
    signed = sign_pack_dict(data, key, key_id=args.key_id)
    out = Path(args.output) if args.output else path
    out.write_text(json.dumps(signed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Signed {out} (alg=hmac-sha256 key_id={args.key_id})")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    path = Path(args.path)
    data = json.loads(path.read_text(encoding="utf-8"))
    key = load_key(args.key_file)
    errs = verify_pack_dict(data, key, key_id=args.key_id or None)
    if errs:
        print("VERIFY FAIL")
        for e in errs:
            print(f"  - {e}")
        return 1
    print("VERIFY OK")
    return 0


def cmd_index(args: argparse.Namespace) -> int:
    packs_dir = Path(args.packs_dir)
    out = Path(args.output)
    entries = []
    errors = []

    for m in list_packs(packs_dir):
        if "error" in m:
            errors.append(m)
            continue
        path = Path(m["path"])
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            errors.append({"path": str(path), "error": str(e)})
            continue
        verrs = validate_pack(data, strict=args.strict)
        if verrs:
            errors.append({"path": str(path), "validation": verrs})
        entries.append(
            {
                "id": data.get("id"),
                "version": data.get("version"),
                "title": data.get("title"),
                "summary": data.get("summary"),
                "tags": data.get("tags", []),
                "license": data.get("license"),
                "created_by": (data.get("provenance") or {}).get("created_by"),
                "created_at": (data.get("provenance") or {}).get("created_at"),
                "quality": {
                    "self_score": (data.get("quality") or {}).get("self_score"),
                    "confidence": (data.get("quality") or {}).get("confidence"),
                },
                "file": path.name,
                "uri": f"openfeed://pack/{data.get('id')}",
            }
        )

    index = {
        "openfeed_index_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "generated_by": "openfeed-cli",
        "count": len(entries),
        "packs": sorted(entries, key=lambda e: e.get("id") or ""),
        "errors": errors,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out} with {len(entries)} packs ({len(errors)} errors)")
    return 1 if errors else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="openfeed", description="OpenFeed CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create", help="Create a new Knowledge Pack")
    p_create.add_argument("--title", required=True)
    p_create.add_argument("--summary", required=True)
    p_create.add_argument("--body", default="")
    p_create.add_argument("--body-file")
    p_create.add_argument("--type", default="markdown", choices=["markdown", "json", "text", "structured"])
    p_create.add_argument("--created-by", default="noema")
    p_create.add_argument("--method", default="synthesized")
    p_create.add_argument("--self-score", type=float, default=0.8)
    p_create.add_argument("--confidence", type=float, default=0.75)
    p_create.add_argument("--license", default="MIT")
    p_create.add_argument("--tags", default="")
    p_create.add_argument("-o", "--output")
    p_create.set_defaults(func=cmd_create)

    p_val = sub.add_parser("validate", help="Validate a Knowledge Pack JSON file")
    p_val.add_argument("path")
    p_val.add_argument("--strict", action="store_true", help="Also run JSON Schema (needs jsonschema)")
    p_val.set_defaults(func=cmd_validate)

    p_show = sub.add_parser("show", help="Pretty-print a Knowledge Pack")
    p_show.add_argument("path")
    p_show.add_argument("--strict", action="store_true")
    p_show.set_defaults(func=cmd_show)

    p_list = sub.add_parser("list", help="List packs in a directory")
    p_list.add_argument("--packs-dir", default=None)
    p_list.set_defaults(func=cmd_list)

    p_search = sub.add_parser("search", help="Search packs by keyword")
    p_search.add_argument("query")
    p_search.add_argument("--packs-dir", default=None)
    p_search.set_defaults(func=cmd_search)

    p_rel = sub.add_parser("related", help="Show relation graph around a pack id")
    p_rel.add_argument("pack_id")
    p_rel.add_argument("--packs-dir", default=None)
    p_rel.set_defaults(func=cmd_related)

    p_sign = sub.add_parser("sign", help="HMAC-SHA256 sign a pack (experimental local trust)")
    p_sign.add_argument("path")
    p_sign.add_argument("--key-file", required=True)
    p_sign.add_argument("--key-id", default="local")
    p_sign.add_argument("-o", "--output", help="Output path (default: overwrite)")
    p_sign.set_defaults(func=cmd_sign)

    p_ver = sub.add_parser("verify", help="Verify HMAC-SHA256 pack signature")
    p_ver.add_argument("path")
    p_ver.add_argument("--key-file", required=True)
    p_ver.add_argument("--key-id", default="")
    p_ver.set_defaults(func=cmd_verify)

    p_index = sub.add_parser("index", help="Build packs/index.json")
    p_index.add_argument("--packs-dir", default="packs")
    p_index.add_argument("-o", "--output", default="packs/index.json")
    p_index.add_argument("--strict", action="store_true")
    p_index.set_defaults(func=cmd_index)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
