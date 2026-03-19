"""TasksResource for AmoCRM API v4."""
from __future__ import annotations

from amocrm.resources.base import BaseResource

__all__ = ["TasksResource"]


class TasksResource(BaseResource):
    path = "/tasks"
    embedded_key = "tasks"
