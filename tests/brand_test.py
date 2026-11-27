"""The Wonderland icon: public routes, and serverInfo pointing at the public URL."""

import unittest
from unittest.mock import patch

from analytics_mcp import server
from starlette.testclient import TestClient

ISSUER = "https://analytics.mcp.wonderland.marketing"


class TestBrand(unittest.TestCase):
    def _app(self):
        args = server.parse_args(
            ["--transport", "http", "--host", "0.0.0.0", "--port", "9000",
             "--stateless-http", "--oauth", "--issuer-url", ISSUER]
        )
        with patch.dict(
            "os.environ",
            {"GOOGLE_OAUTH_CLIENT_ID": "test-id", "GOOGLE_OAUTH_CLIENT_SECRET": "test-secret"},
        ):
            return server.build_http_app(args)

    def test_icons_served_without_auth(self):
        with TestClient(self._app()) as c:
            for path, media in [
                ("/favicon.ico", "image/x-icon"),
                ("/brand/icon-512.png", "image/png"),
                ("/apple-touch-icon.png", "image/png"),
            ]:
                r = c.get(path)
                self.assertEqual(r.status_code, 200, path)
                self.assertEqual(r.headers["content-type"], media)
                self.assertGreater(len(r.content), 100)
            # The home page names the icon, so Google indexes this host's favicon for Claude.
            home = c.get("/")
            self.assertEqual(home.status_code, 200)
            self.assertIn('href="/brand/icon-512.png"', home.text)
            # The MCP endpoint itself still demands a token.
            self.assertEqual(c.post("/mcp", json={}).status_code, 401)

    def test_server_info_icon_uses_public_url(self):
        made = []
        real = server.coordinator.create_server

        def capture(*a, **k):
            made.append(real(*a, **k))
            return made[-1]

        with patch.object(server.coordinator, "create_server", side_effect=capture):
            self._app()
        icon = made[0].icons[0]
        self.assertEqual(str(icon.src), f"{ISSUER}/brand/icon-512.png")
        self.assertEqual(icon.sizes, ["512x512"])
        self.assertEqual(made[0].title, "Wonderland Google Analytics")


if __name__ == "__main__":
    unittest.main()
