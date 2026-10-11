"""Minimal OpenFeed CLI.

Usage (after install or PYTHONPATH=src):
  python -m openfeed.cli create --title "..." --summary "..." --body "..."
  python -m openfeed.cli validate path/to/pack.json
  python -m openfeed.cli show path/to/pack.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .pack import create_pack, load_pack, save_pack, validate_pack


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
    errs = validate_pack(data)
    if errs:
        print("INVALID")
        for e in errs:
            print(f"  - {e}")
        return 1
    print("VALID")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    pack = load_pack(args.path)
    print(pack.to_json())
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="openfeed", description="OpenFeed CLI — led by Noema")
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create", help="Create a new Knowledge Pack")
    p_create.add_argument("--title", required=True)
    p_create.add_argument("--summary", required=True)
    p_create.add_argument("--body", default="", help="Inline body text")
    p_create.add_argument("--body-file", help="Read body from file")
    p_create.add_argument("--type", default="markdown", choices=["markdown", "json", "text", "structured"])
    p_create.add_argument("--created-by", default="noema")
    p_create.add_argument("--method", default="synthesized")
    p_create.add_argument("--self-score", type=float, default=0.8)
    p_create.add_argument("--confidence", type=float, default=0.75)
    p_create.add_argument("--license", default="MIT")
    p_create.add_argument("--tags", default="")
    p_create.add_argument("-o", "--output", help="Output path")
    p_create.set_defaults(func=cmd_create)

    p_val = sub.add_parser("validate", help="Validate a Knowledge Pack JSON file")
    p_val.add_argument("path")
    p_val.set_defaults(func=cmd_validate)

    p_show = sub.add_parser("show", help="Pretty-print a Knowledge Pack")
    p_show.add_argument("path")
    p_show.set_defaults(func=cmd_show)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
