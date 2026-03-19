"""AccountResource for AmoCRM API v4 — single GET endpoint."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from amocrm.client import AmoCRMClient

__all__ = ["AccountResource"]


class AccountResource:
    """AmoCRM account — single GET endpoint. Does not subclass BaseResource."""

    def __init__(self, client: AmoCRMClient) -> None:
        self.client = client

    def get(self, with_: list[str] | None = None) -> dict[str, Any]:
        """GET /account. Pass with_ to include extra data (e.g. users_groups)."""
        params: dict[str, str] = {}
        if with_:
            params["with"] = ",".join(with_)
        result = self.client.get("/account", params=params or None)
        return result  # type: ignore[return-value]
