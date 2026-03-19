"""AmoCRM API client — synchronous httpx wrapper.

Construction modes:
    # Config-file mode (CLI): reads ~/.amocrm/config.json
    client = AmoCRMClient()

    # Kwargs mode (library): skips config file
    client = AmoCRMClient(subdomain="mycompany", access_token="xxx")
    client = AmoCRMClient(
        subdomain="mycompany",
        access_token="xxx",
        refresh_token="yyy",
        client_id="zzz",
        client_secret="aaa",
        expires_at=1234567890,  # None = refresh on 401 only
    )
"""
from __future__ import annotations

import random
import time
from typing import Any

import httpx

from amocrm.auth.config import load_config, save_config
from amocrm.auth.oauth import refresh_tokens
from amocrm.auth.token import is_token_expiring
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError

__all__ = ["AmoCRMClient"]

_MIN_INTERVAL = 1 / 7  # 7 req/s throttle


def _is_single_resource_path(path: str) -> bool:
    """True if path ends with a numeric ID (single-resource, not batch)."""
    return path.rstrip("/").split("/")[-1].isdigit()


class AmoCRMClient:
    def __init__(
        self,
        subdomain: str | None = None,
        access_token: str | None = None,
        refresh_token: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        expires_at: int | None = None,
    ) -> None:
        """Initialize client from config file (no args) or from kwargs (library use)."""
        self._last_request_time: float = 0.0

        if subdomain is not None:
            # Kwargs mode: library use, skip config file
            self._subdomain = subdomain
            self._access_token = access_token or ""
            self._refresh_token = refresh_token
            self._client_id = client_id
            self._client_secret = client_secret
            self._expires_at = expires_at
            self._auth_mode = "oauth" if refresh_token else "longtoken"
            self._config_mode = False  # do not write to config file
            self._redirect_uri = "http://localhost:8080"
        else:
            # Config-file mode: CLI use
            config = load_config()
            self._subdomain = str(config["subdomain"])
            self._access_token = str(config["access_token"])
            self._refresh_token = str(config["refresh_token"]) if config.get("refresh_token") else None
            self._client_id = str(config["client_id"]) if config.get("client_id") else None
            self._client_secret = str(config["client_secret"]) if config.get("client_secret") else None
            expires = config.get("expires_at")
            self._expires_at = int(expires) if isinstance(expires, (int, float)) else None
            self._auth_mode = str(config.get("auth_mode", "longtoken"))
            self._redirect_uri = str(config.get("redirect_uri", "http://localhost:8080"))
            self._config_mode = True  # write refreshed tokens back to config

            # Proactive refresh in config-file mode
            if self._auth_mode == "oauth" and is_token_expiring(self._expires_at):
                self._do_refresh(write_config=True)

        self._base_url = f"https://{self._subdomain}.amocrm.ru/api/v4"

        # Kwargs mode proactive refresh is deferred to first request to allow
        # test mocks to be set up after client construction.

    def _do_refresh(self, write_config: bool) -> None:
        """Refresh access token using refresh_token."""
        if not (self._refresh_token and self._client_id and self._client_secret):
            return
        result = refresh_tokens(
            subdomain=self._subdomain,
            refresh_token=str(self._refresh_token),
            client_id=str(self._client_id),
            client_secret=str(self._client_secret),
            redirect_uri=self._redirect_uri,
        )
        self._access_token = str(result["access_token"])
        self._refresh_token = str(result["refresh_token"])
        self._expires_at = int(result["expires_at"])  # type: ignore[call-overload]

        if write_config:
            config = load_config()
            config["access_token"] = self._access_token
            config["refresh_token"] = self._refresh_token
            config["expires_at"] = self._expires_at
            save_config(config)

    def _throttle(self) -> None:
        """Sleep to maintain 7 req/s rate limit."""
        elapsed = time.monotonic() - self._last_request_time
        wait = _MIN_INTERVAL - elapsed
        if wait > 0:
            time.sleep(wait)
        self._last_request_time = time.monotonic()

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._access_token}"}

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Raise AmoCRMAPIError if response indicates an error."""
        ct = response.headers.get("content-type", "")
        is_error_status = response.status_code >= 400
        is_problem_json = "application/problem+json" in ct

        if is_problem_json or is_error_status:
            try:
                body = response.json()
                status = body.get("status", response.status_code)
                title = body.get("title", "API Error")
                detail = body.get("detail", "")
            except Exception:
                status = response.status_code
                title = "API Error"
                detail = response.text
            raise AmoCRMAPIError(int(status), str(title), str(detail))

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: list[Any] | dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Execute HTTP request with throttling and retry logic."""
        url = f"{self._base_url}{path}"
        max_retries = 3
        delay = 1.0
        response: httpx.Response | None = None

        for attempt in range(max_retries + 1):
            self._throttle()
            response = httpx.request(
                method,
                url,
                headers=self._headers(),
                params=params,
                json=json,
            )

            if response.status_code in (429, 503, 504):
                if attempt < max_retries:
                    jitter = random.uniform(0, 0.5)
                    time.sleep(delay + jitter)
                    delay *= 2
                    continue
                # Exhausted retries — fall through
                break

            return response

        assert response is not None
        return response

    def _can_reactive_refresh(self) -> bool:
        """True if client is in kwargs mode with full refresh credentials and no known expiry."""
        return (
            not self._config_mode
            and bool(self._refresh_token)
            and bool(self._client_id)
            and bool(self._client_secret)
            and self._expires_at is None
        )

    def _maybe_proactive_refresh(self) -> None:
        """In kwargs mode, proactively refresh if token is expiring (deferred from __init__)."""
        if (
            not self._config_mode
            and self._refresh_token
            and self._expires_at is not None
            and is_token_expiring(self._expires_at)
        ):
            self._do_refresh(write_config=False)

    def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any] | list[Any]:
        """GET request. Raises EntityNotFoundError on 204. Raises AmoCRMAPIError on errors."""
        self._maybe_proactive_refresh()
        if self._can_reactive_refresh():
            response = self._request("GET", path, params=params)
            if response.status_code == 401:
                self._do_refresh(write_config=False)
                response = self._request("GET", path, params=params)
        else:
            response = self._request("GET", path, params=params)

        if response.status_code == 204:
            raise EntityNotFoundError(path)
        self._handle_error_response(response)
        result: dict[str, Any] | list[Any] = response.json()
        return result

    def post(self, path: str, json: list[Any] | dict[str, Any] | None = None) -> dict[str, Any] | list[Any]:
        """POST request. Returns parsed response body."""
        self._maybe_proactive_refresh()
        if self._can_reactive_refresh():
            response = self._request("POST", path, json=json)
            if response.status_code == 401:
                self._do_refresh(write_config=False)
                response = self._request("POST", path, json=json)
        else:
            response = self._request("POST", path, json=json)

        self._handle_error_response(response)
        result: dict[str, Any] | list[Any] = response.json()
        return result

    def patch(self, path: str, json: list[Any] | dict[str, Any] | None = None) -> dict[str, Any] | list[Any]:
        """PATCH request.

        Single-resource path (ends with /{id}): 204 raises EntityNotFoundError.
        Batch path (no trailing ID): 204 returns [].
        """
        self._maybe_proactive_refresh()
        if self._can_reactive_refresh():
            response = self._request("PATCH", path, json=json)
            if response.status_code == 401:
                self._do_refresh(write_config=False)
                response = self._request("PATCH", path, json=json)
        else:
            response = self._request("PATCH", path, json=json)

        if response.status_code == 204:
            if _is_single_resource_path(path):
                raise EntityNotFoundError(path)
            return []
        self._handle_error_response(response)
        result: dict[str, Any] | list[Any] = response.json()
        return result

    def delete(self, path: str) -> bool:
        """DELETE request. Returns True on 204 success."""
        self._maybe_proactive_refresh()
        if self._can_reactive_refresh():
            response = self._request("DELETE", path)
            if response.status_code == 401:
                self._do_refresh(write_config=False)
                response = self._request("DELETE", path)
        else:
            response = self._request("DELETE", path)

        if response.status_code == 204:
            return True
        self._handle_error_response(response)
        return True
