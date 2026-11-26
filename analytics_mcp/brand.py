"""Wonderland's icon for this server: the W on the Analytics orange tile.

One of a family: each Wonderland MCP server has its own colour and badge, so
they are told apart in Claude's connector list. Served without auth, because a
client draws the connector before it holds any credential.
"""

from importlib import resources

from mcp import types
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

ICON_PATH = "/brand/icon-512.png"

_FILES = {
    "/favicon.ico": ("favicon.ico", "image/x-icon"),
    ICON_PATH: ("icon-512.png", "image/png"),
    "/brand/icon-192.png": ("icon-192.png", "image/png"),
    "/apple-touch-icon.png": ("icon-180.png", "image/png"),
}


def _read(name: str) -> bytes:
    return resources.files("analytics_mcp").joinpath("brand", name).read_bytes()


def brand_routes() -> list[Route]:
    """Starlette routes for the favicon and icons. Files are read once, at build."""
    routes = []
    for path, (name, media_type) in _FILES.items():
        body = _read(name)

        async def serve(_: Request, body=body, media_type=media_type) -> Response:
            return Response(
                body,
                media_type=media_type,
                headers={"Cache-Control": "public, max-age=86400"},
            )

        routes.append(Route(path, serve, methods=["GET", "HEAD"]))
    return routes


def server_icons(public_url: str) -> list[types.Icon]:
    """The serverInfo icons entry. Absolute: clients resolve it outside any page."""
    return [
        types.Icon(
            src=f"{public_url.rstrip('/')}{ICON_PATH}",
            mime_type="image/png",
            sizes=["512x512"],
        )
    ]
