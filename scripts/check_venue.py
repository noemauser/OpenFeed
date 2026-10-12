#!/usr/bin/env python3
"""Fail if venue/ is structurally invalid."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from openfeed.venue import validate_venue  # noqa: E402


def main() -> int:
    errs = validate_venue(ROOT / "venue")
    if errs:
        print("venue invalid:")
        for e in errs:
            print(" ", e)
        return 1
    print("venue ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
