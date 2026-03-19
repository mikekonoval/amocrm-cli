"""ContactsResource for AmoCRM API v4."""
from __future__ import annotations

from amocrm.resources.base import BaseResource

__all__ = ["ContactsResource"]


class ContactsResource(BaseResource):
    path = "/contacts"
    embedded_key = "contacts"
