"""OAuth 2.0 flow for AmoCRM: browser redirect + token exchange."""
from __future__ import annotations

import time
import urllib.parse
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

import httpx

TOKEN_URL = "https://{subdomain}.amocrm.ru/oauth2/access_token"
AUTH_URL = "https://www.amocrm.ru/oauth"


def build_auth_url(client_id: str, state: str, mode: str = "popup") -> str:
    params = {"client_id": client_id, "state": state, "mode": mode}
    return f"{AUTH_URL}?{urllib.parse.urlencode(params)}"


def exchange_code_for_tokens(
    subdomain: str,
    code: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
) -> dict[str, object]:
    """Exchange authorization code for access + refresh tokens."""
    url = TOKEN_URL.format(subdomain=subdomain)
    response = httpx.post(url, json={
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    })
    response.raise_for_status()
    data = response.json()
    return {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "expires_at": int(time.time()) + data["expires_in"],
    }


def refresh_tokens(
    subdomain: str,
    refresh_token: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
) -> dict[str, object]:
    """Refresh an expired access token. Refresh token is single-use."""
    url = TOKEN_URL.format(subdomain=subdomain)
    response = httpx.post(url, json={
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "redirect_uri": redirect_uri,
    })
    response.raise_for_status()
    data = response.json()
    return {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "expires_at": int(time.time()) + data["expires_in"],
    }


def run_browser_flow(
    subdomain: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str = "http://localhost:8080",
) -> dict[str, object]:
    """Open browser for OAuth consent, capture redirect, return token dict."""
    import secrets
    state = secrets.token_urlsafe(16)
    captured: dict[str, object] = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            captured["code"] = params.get("code", [None])[0]
            captured["state"] = params.get("state", [None])[0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Auth complete. You can close this window.")

        def log_message(self, *args: object) -> None:
            pass  # suppress server logs

    port = int(urllib.parse.urlparse(redirect_uri).port or 8080)
    server = HTTPServer(("localhost", port), Handler)
    thread = threading.Thread(target=server.handle_request)
    thread.start()

    auth_url = build_auth_url(client_id=client_id, state=state)
    webbrowser.open(auth_url)
    thread.join(timeout=120)

    if captured.get("state") != state:
        raise ValueError("OAuth state mismatch — possible CSRF attack")
    if not captured.get("code"):
        raise ValueError("No authorization code received")

    tokens = exchange_code_for_tokens(
        subdomain=subdomain,
        code=str(captured["code"]),
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
    )
    return tokens
