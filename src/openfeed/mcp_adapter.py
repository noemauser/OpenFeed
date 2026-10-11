"""Optional MCP SDK adapter for OpenFeed.

Install:
  pip install 'openfeed[mcp]'   # or: pip install mcp

Run (stdio server):
  PYTHONPATH=src python -m openfeed.mcp_adapter

Or configure your MCP host to launch this module.

If the `mcp` package is not installed, importing this module still works for
documentation; `main()` will print install instructions.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .mcp_server import (
    get_pack,
    list_packs,
    list_resources,
    tool_get_pack,
    tool_list_packs,
    tool_validate_pack,
)


def _packs_dir() -> Path | None:
    env = os.environ.get("OPENFEED_PACKS_DIR")
    return Path(env) if env else None


def build_server():
    """Create an MCP Server instance if SDK is available."""
    try:
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import (
            Resource,
            TextContent,
            Tool,
        )
    except ImportError as e:
        raise ImportError(
            "MCP SDK not installed. Run: pip install mcp\n"
            "Or: pip install 'openfeed[mcp]'"
        ) from e

    server = Server("openfeed")

    @server.list_tools()
    async def _list_tools() -> list[Tool]:
        return [
            Tool(
                name="list_packs",
                description="List OpenFeed Knowledge Packs (id, title, summary, tags).",
                inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
            ),
            Tool(
                name="get_pack",
                description="Get a full Knowledge Pack by id.",
                inputSchema={
                    "type": "object",
                    "required": ["pack_id"],
                    "properties": {"pack_id": {"type": "string"}},
                    "additionalProperties": False,
                },
            ),
            Tool(
                name="validate_pack",
                description="Validate a pack by file path or pack id.",
                inputSchema={
                    "type": "object",
                    "required": ["path_or_id"],
                    "properties": {"path_or_id": {"type": "string"}},
                    "additionalProperties": False,
                },
            ),
        ]

    @server.call_tool()
    async def _call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        if name == "list_packs":
            result = tool_list_packs()
            # re-list with env dir if set
            if _packs_dir():
                result = {
                    "ok": True,
                    "count": len(list_packs(_packs_dir())),
                    "packs": list_packs(_packs_dir()),
                }
        elif name == "get_pack":
            pid = arguments.get("pack_id", "")
            pack = get_pack(pid, _packs_dir())
            result = (
                {"ok": True, "pack": pack.to_dict()}
                if pack
                else {"ok": False, "error": f"pack not found: {pid}"}
            )
        elif name == "validate_pack":
            result = tool_validate_pack(arguments.get("path_or_id", ""))
        else:
            result = {"ok": False, "error": f"unknown tool: {name}"}
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

    @server.list_resources()
    async def _list_resources() -> list[Resource]:
        out: list[Resource] = []
        for r in list_resources(_packs_dir()):
            out.append(
                Resource(
                    uri=r["uri"],
                    name=r["name"],
                    description=r.get("description"),
                    mimeType=r.get("mimeType", "application/json"),
                )
            )
        return out

    @server.read_resource()
    async def _read_resource(uri: str) -> str:
        # openfeed://pack/{id}
        prefix = "openfeed://pack/"
        if not str(uri).startswith(prefix):
            raise ValueError(f"unsupported uri: {uri}")
        pid = str(uri)[len(prefix) :]
        pack = get_pack(pid, _packs_dir())
        if pack is None:
            raise ValueError(f"pack not found: {pid}")
        return pack.to_json()

    return server, stdio_server


def main() -> None:
    try:
        server, stdio_server = build_server()
    except ImportError as e:
        print(str(e))
        raise SystemExit(1) from e

    import anyio
    from mcp.server.models import InitializationOptions
    from mcp.server.lowlevel import NotificationOptions

    async def _run() -> None:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="openfeed",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

    anyio.run(_run)


if __name__ == "__main__":
    main()
