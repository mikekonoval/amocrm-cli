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

from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError

__all__ = ["AmoCRMClient"]


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
        raise NotImplementedError

    def get(self, path: str, params: dict | None = None) -> dict | list:
        """GET request. Raises EntityNotFoundError on 204. Raises AmoCRMAPIError on errors."""
        raise NotImplementedError

    def post(self, path: str, json: list | dict | None = None) -> dict | list:
        """POST request. Returns parsed response body."""
        raise NotImplementedError

    def patch(self, path: str, json: list | dict | None = None) -> dict | list:
        """PATCH request.
        Single-resource path (ends with /{id}): 204 raises EntityNotFoundError.
        Batch path (no trailing ID): 204 returns [].
        """
        raise NotImplementedError

    def delete(self, path: str) -> bool:
        """DELETE request. Returns True on 204 success."""
        raise NotImplementedError
