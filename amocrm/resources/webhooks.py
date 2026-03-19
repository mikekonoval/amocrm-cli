"""WebhooksResource — subscribe/unsubscribe webhooks in AmoCRM."""
from __future__ import annotations

from amocrm.exceptions import EntityNotFoundError
from amocrm.resources.base import BaseResource

__all__ = ["WebhooksResource"]


class WebhooksResource(BaseResource):
    path = "/webhooks"
    embedded_key = "hooks"  # AmoCRM uses "hooks" not "webhooks"

    def subscribe(self, destination: str, settings: list[str]) -> dict:
        """POST to /webhooks to register a new webhook."""
        response = self.client.post(self.path, json={"destination": destination, "settings": settings})
        if isinstance(response, dict):
            embedded = response.get("_embedded", {})
            hooks = embedded.get("hooks", [])
            return hooks[0] if hooks else response
        return {}

    def unsubscribe(self, url: str) -> bool:
        """Find webhook by destination URL and delete it."""
        webhooks = self.list()
        for webhook in webhooks:
            if webhook.get("destination") == url:
                return self.delete(webhook["id"])
        raise EntityNotFoundError("/webhooks")
