"""PipelinesResource and StagesResource for AmoCRM API v4."""
from __future__ import annotations

from typing import ClassVar, TYPE_CHECKING

from amocrm.resources.base import BaseResource

if TYPE_CHECKING:
    from amocrm.client import AmoCRMClient

__all__ = ["PipelinesResource", "StagesResource", "WON_STATUS_ID", "LOST_STATUS_ID"]

WON_STATUS_ID = 142
LOST_STATUS_ID = 143


class PipelinesResource(BaseResource):
    path: ClassVar[str] = "/leads/pipelines"
    embedded_key: ClassVar[str] = "pipelines"


class StagesResource(BaseResource):
    """Stages (statuses) sub-resource for a specific pipeline."""

    embedded_key: ClassVar[str] = "statuses"
    path: ClassVar[str] = ""  # set dynamically

    def __init__(self, client: AmoCRMClient, pipeline_id: int) -> None:
        super().__init__(client)
        self.path = f"/leads/pipelines/{pipeline_id}/statuses"
