"""BaseResource: CRUD mixin for all AmoCRM resources."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, List, cast

if TYPE_CHECKING:
    from amocrm.client import AmoCRMClient

from amocrm.exceptions import EntityNotFoundError

__all__ = ["BaseResource"]


def _build_filter_params(filters: dict[str, Any], prefix: str = "filter") -> dict[str, Any]:
    """Convert nested dict to bracket-notation query params.
    {"pipeline_id": [1,2]} → {"filter[pipeline_id][0]": 1, "filter[pipeline_id][1]": 2}
    {"created_at": {"from": 1700000}} → {"filter[created_at][from]": 1700000}
    """
    result: dict[str, Any] = {}
    for key, value in filters.items():
        if isinstance(value, list):
            for i, item in enumerate(value):
                result[f"{prefix}[{key}][{i}]"] = item
        elif isinstance(value, dict):
            for sub_key, sub_val in value.items():
                result[f"{prefix}[{key}][{sub_key}]"] = sub_val
        else:
            result[f"{prefix}[{key}]"] = value
    return result


def _build_order_params(order: str) -> dict[str, str]:
    """Convert "field:direction" to {"order[field]": "direction"}.
    "created_at:asc" → {"order[created_at]": "asc"}
    """
    field, _, direction = order.partition(":")
    return {f"order[{field}]": direction or "asc"}


class BaseResource:
    path: ClassVar[str]       # e.g. "/leads"
    embedded_key: ClassVar[str]  # e.g. "leads"

    def __init__(self, client: AmoCRMClient) -> None:
        self.client = client

    def list(
        self,
        page: int = 1,
        limit: int = 50,
        filters: dict[str, Any] | None = None,
        order: str | None = None,
        with_: List[str] | None = None,
    ) -> List[dict[str, Any]]:
        params: dict[str, Any] = {"page": page, "limit": limit}
        if filters:
            params.update(_build_filter_params(filters))
        if order:
            params.update(_build_order_params(order))
        if with_:
            params["with"] = ",".join(with_)
        try:
            response = self.client.get(self.path, params=params)
        except EntityNotFoundError:
            return []  # 204 on list endpoint = empty collection
        if isinstance(response, dict):
            embedded = response.get("_embedded", {})
            return cast(List[dict[str, Any]], embedded.get(self.embedded_key, []))
        return []

    def get(self, id: int, with_: List[str] | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if with_:
            params["with"] = ",".join(with_)
        result = self.client.get(f"{self.path}/{id}", params=params or None)
        return cast(dict[str, Any], result)

    def create(self, items: List[dict[str, Any]]) -> List[dict[str, Any]]:
        response = self.client.post(self.path, json=items)
        if isinstance(response, dict):
            embedded = response.get("_embedded", {})
            return cast(List[dict[str, Any]], embedded.get(self.embedded_key, []))
        return []

    def update(self, id: int, data: dict[str, Any]) -> dict[str, Any]:
        result = self.client.patch(f"{self.path}/{id}", json=data)
        return cast(dict[str, Any], result)

    def update_batch(self, items: List[dict[str, Any]]) -> List[dict[str, Any]]:
        response = self.client.patch(self.path, json=items)
        if isinstance(response, list):
            return cast(List[dict[str, Any]], response)
        if isinstance(response, dict):
            embedded = response.get("_embedded", {})
            return cast(List[dict[str, Any]], embedded.get(self.embedded_key, []))
        return []

    def delete(self, id: int) -> bool:
        return self.client.delete(f"{self.path}/{id}")
