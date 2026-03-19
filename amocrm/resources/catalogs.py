"""CatalogsResource and CatalogElementsResource for AmoCRM API v4."""
from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from amocrm.resources.base import BaseResource

if TYPE_CHECKING:
    from amocrm.client import AmoCRMClient

__all__ = ["CatalogsResource", "CatalogElementsResource"]


class CatalogsResource(BaseResource):
    path: ClassVar[str] = "/catalogs"
    embedded_key: ClassVar[str] = "catalogs"


class CatalogElementsResource(BaseResource):
    embedded_key: ClassVar[str] = "elements"
    path: ClassVar[str] = ""

    def __init__(self, client: AmoCRMClient, catalog_id: int) -> None:
        super().__init__(client)
        self.path = f"/catalogs/{catalog_id}/elements"  # type: ignore[misc]
