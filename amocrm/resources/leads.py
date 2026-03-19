"""LeadsResource for AmoCRM API v4."""
from __future__ import annotations

from typing import Any

from amocrm.resources.base import BaseResource

__all__ = ["LeadsResource"]


class LeadsResource(BaseResource):
    path = "/leads"
    embedded_key = "leads"

    def create_complex(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """POST to /leads/complex. Atomically creates lead + contacts + companies. Max 50 per call."""
        response = self.client.post("/leads/complex", json=items)
        if isinstance(response, dict):
            embedded = response.get("_embedded", {})
            return list(embedded.get("leads", []))
        return []
