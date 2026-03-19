# amocrm/resources/unsorted.py
"""UnsortedResource for AmoCRM API v4."""
from __future__ import annotations

from typing import Any, ClassVar, List, cast

from amocrm.resources.base import BaseResource

__all__ = ["UnsortedResource"]


class UnsortedResource(BaseResource):
    path: ClassVar[str] = "/leads/unsorted"
    embedded_key: ClassVar[str] = "unsorted"

    def get_by_uid(self, uid: str) -> dict[str, Any]:
        """Get an unsorted lead by its string UID (not integer id)."""
        result = self.client.get(f"{self.path}/{uid}")
        return cast(dict[str, Any], result)

    def add(self, items: List[dict[str, Any]]) -> List[dict[str, Any]]:
        """Create unsorted leads (POST /leads/unsorted)."""
        return self.create(items)

    def accept(self, items: List[dict[str, Any]]) -> List[dict[str, Any]]:
        """Accept unsorted leads into a pipeline.
        Each item: {"uid": "...", "status_id": int, "pipeline_id": int}
        """
        response = self.client.patch(f"{self.path}/accept", json=items)
        if isinstance(response, dict):
            embedded = response.get("_embedded", {})
            return cast(List[dict[str, Any]], embedded.get(self.embedded_key, []))
        return []

    def decline(self, items: List[dict[str, Any]]) -> List[dict[str, Any]]:
        """Decline (reject) unsorted leads.
        Each item: {"uid": "..."}
        """
        response = self.client.patch(f"{self.path}/decline", json=items)
        if isinstance(response, dict):
            embedded = response.get("_embedded", {})
            return cast(List[dict[str, Any]], embedded.get(self.embedded_key, []))
        return []
