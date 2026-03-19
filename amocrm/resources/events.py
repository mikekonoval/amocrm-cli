"""EventsResource for AmoCRM API v4 — read-only, limit clamped to 100."""
from __future__ import annotations

from typing import ClassVar

from amocrm.resources.base import BaseResource

__all__ = ["EventsResource"]

MAX_EVENTS_LIMIT = 100


class EventsResource(BaseResource):
    path: ClassVar[str] = "/events"
    embedded_key: ClassVar[str] = "events"

    def list(
        self,
        page: int = 1,
        limit: int = 50,
        filters: dict | None = None,
        order: str | None = None,
        with_: list[str] | None = None,
    ) -> list[dict]:
        """List events. Limit is silently clamped to max 100."""
        limit = min(limit, MAX_EVENTS_LIMIT)
        return super().list(page=page, limit=limit, filters=filters, order=order, with_=with_)
