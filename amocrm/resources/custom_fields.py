"""CustomFieldsResource and CustomFieldGroupsResource for AmoCRM API v4."""
from __future__ import annotations

from typing import ClassVar, TYPE_CHECKING

from amocrm.resources.base import BaseResource

if TYPE_CHECKING:
    from amocrm.client import AmoCRMClient

__all__ = ["CustomFieldsResource", "CustomFieldGroupsResource"]


class CustomFieldsResource(BaseResource):
    embedded_key: ClassVar[str] = "custom_fields"
    path: ClassVar[str] = ""  # set dynamically

    def __init__(self, client: AmoCRMClient, entity: str) -> None:
        super().__init__(client)
        self.path = f"/{entity}/custom_fields"  # type: ignore[misc]


class CustomFieldGroupsResource(BaseResource):
    embedded_key: ClassVar[str] = "custom_field_groups"
    path: ClassVar[str] = ""  # set dynamically

    def __init__(self, client: AmoCRMClient, entity: str) -> None:
        super().__init__(client)
        self.path = f"/{entity}/custom_fields/groups"  # type: ignore[misc]
