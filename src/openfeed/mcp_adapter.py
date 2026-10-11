"""Optional MCP SDK adapter for OpenFeed.

Install:
  pip install 'openfeed[mcp]'   # or: pip install mcp anyio

Run (stdio):
  export OPENFEED_PACKS_DIR=/path/to/packs
  PYTHONPATH=src python -m openfeed.mcp_adapter

If the installed `mcp` package API differs from this adapter, use the stable
helpers in `openfeed.mcp_server` directly from your host — zero dependencies.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from .mcp_server import get_pack, list_packs, list_resources, tool_validate_pack


def _packs_dir() -> Path | None:
    env = os.environ.get("OPENFEED_PACKS_DIR")
    return Path(env) if env else None


def _json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def main() -> None:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        try:
            # older / alternate layouts
            from mcp.server.fastmcp import FastMCP  # type: ignore
        except ImportError:
            print(
                "MCP SDK not installed or FastMCP unavailable.\n"
                "  pip install 'openfeed[mcp]'\n"
                "Alternatively call openfeed.mcp_server helpers from your host (no deps).",
                file=sys.stderr,
            )
            raise SystemExit(1)

    mcp = FastMCP("openfeed")

    @mcp.tool()
    def list_packs_tool() -> str:
        """List OpenFeed Knowledge Packs (id, title, summary, tags)."""
        packs = list_packs(_packs_dir())
        return _json({"ok": True, "count": len(packs), "packs": packs})

    @mcp.tool()
    def get_pack_tool(pack_id: str) -> str:
        """Get a full Knowledge Pack by id."""
        pack = get_pack(pack_id, _packs_dir())
        if pack is None:
            return _json({"ok": False, "error": f"pack not found: {pack_id}"})
        return _json({"ok": True, "pack": pack.to_dict()})

    @mcp.tool()
    def validate_pack_tool(path_or_id: str) -> str:
        """Validate a pack by file path or pack id."""
        return _json(tool_validate_pack(path_or_id))

    @mcp.resource("openfeed://pack/{pack_id}")
    def pack_resource(pack_id: str) -> str:
        """Read a Knowledge Pack as a resource."""
        pack = get_pack(pack_id, _packs_dir())
        if pack is None:
            raise ValueError(f"pack not found: {pack_id}")
        return pack.to_json()

    # Also expose a catalog resource
    @mcp.resource("openfeed://catalog")
    def catalog_resource() -> str:
        return _json(list_resources(_packs_dir()))

    mcp.run()


if __name__ == "__main__":
    main()
