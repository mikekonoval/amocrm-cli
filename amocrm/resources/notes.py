"""NotesResource for AmoCRM API v4 — entity-scoped."""
from __future__ import annotations

from typing import ClassVar, TYPE_CHECKING

from amocrm.resources.base import BaseResource

if TYPE_CHECKING:
    from amocrm.client import AmoCRMClient

__all__ = ["NotesResource"]


class NotesResource(BaseResource):
    embedded_key: ClassVar[str] = "notes"
    path: ClassVar[str] = ""  # dynamically set in __init__

    def __init__(self, client: AmoCRMClient, entity_type: str, entity_id: int | None = None) -> None:
        super().__init__(client)
        if entity_id is not None:
            self.path = f"/{entity_type}/{entity_id}/notes"
        else:
            self.path = f"/{entity_type}/notes"
