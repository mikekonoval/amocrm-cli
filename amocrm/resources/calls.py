# amocrm/resources/calls.py
"""CallsResource for AmoCRM API v4 — write-only call log."""
from __future__ import annotations

from typing import Any, List

from amocrm.resources.base import BaseResource

__all__ = ["CallsResource"]


class CallsResource(BaseResource):
    path = "/calls"
    embedded_key = "calls"

    def add(self, items: List[dict[str, Any]]) -> List[dict[str, Any]]:
        """POST call log entries. No GET endpoint exists in AmoCRM v4."""
        return self.create(items)
