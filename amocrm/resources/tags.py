"""TagsResource for AmoCRM API v4 — entity-scoped."""
from __future__ import annotations

from typing import ClassVar, TYPE_CHECKING

from amocrm.resources.base import BaseResource

if TYPE_CHECKING:
    from amocrm.client import AmoCRMClient

__all__ = ["TagsResource"]


class TagsResource(BaseResource):
    embedded_key: ClassVar[str] = "tags"
    path: ClassVar[str] = ""  # set dynamically

    def __init__(self, client: AmoCRMClient, entity_type: str) -> None:
        super().__init__(client)
        self.path = f"/{entity_type}/tags"  # type: ignore[misc]
