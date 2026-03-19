"""AmoCRM Chats API resource — amojo.amocrm.ru.

Authentication uses HMAC-SHA256 request signing with the integration's client_secret.
The account_chat_id is obtained from GET /api/v4/account?with=amojo_id on the main API.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone
from email.utils import formatdate
from typing import TYPE_CHECKING, Any

import httpx

from amocrm.exceptions import AmoCRMAPIError

if TYPE_CHECKING:
    from amocrm.client import AmoCRMClient

__all__ = ["ChatsResource"]

_AMOJO_BASE = "https://amojo.amocrm.ru"


class ChatsResource:
    """Wraps the AmoCRM Chats API (amojo.amocrm.ru).

    Uses HMAC-SHA256 request signing. Each API call requires:
    - account_chat_id: the amojo_id from GET /api/v4/account?with=amojo_id
    - client._client_secret: integration's secret key for signing
    """

    def __init__(self, client: AmoCRMClient) -> None:
        self.client = client

    def _sign_request(
        self,
        method: str,
        path: str,
        body_bytes: bytes,
        content_type: str = "application/json",
    ) -> dict[str, str]:
        """Build HMAC-SHA256 signed headers for an amojo request."""
        date = formatdate(usegmt=True)
        content_md5 = hashlib.md5(body_bytes).hexdigest()

        signing_string = "\n".join([method.upper(), content_md5, content_type, date, path])
        secret = str(self.client._client_secret or "")
        signature = hmac.new(
            secret.encode("utf-8"),
            signing_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        return {
            "Date": date,
            "Content-Type": content_type,
            "Content-MD5": content_md5,
            "X-Signature": signature,
        }

    def _post(self, path: str, data: dict[str, Any]) -> dict[str, Any]:
        if not self.client._client_secret:
            raise AmoCRMAPIError(
                0,
                "Config Error",
                "client_secret is required for the Chats API. Use OAuth login: amocrm auth login --oauth",
            )
        body_bytes = json.dumps(data).encode("utf-8")
        headers = self._sign_request("POST", path, body_bytes)
        response = httpx.post(
            f"{_AMOJO_BASE}{path}",
            content=body_bytes,
            headers=headers,
        )
        if response.status_code >= 400:
            raise AmoCRMAPIError(response.status_code, "Chats API Error", response.text)
        result: dict[str, Any] = response.json()
        return result

    def connect(
        self,
        account_chat_id: str,
        title: str,
        hook_url: str,
    ) -> dict[str, Any]:
        """Connect (register) a new chat origin for this account."""
        path = f"/api/v2/origin/custom/{account_chat_id}/connect"
        return self._post(path, {"title": title, "hook_api_version": "v2", "hook_api_url": hook_url})

    def disconnect(self, account_chat_id: str) -> dict[str, Any]:
        """Disconnect the chat origin."""
        path = f"/api/v2/origin/custom/{account_chat_id}/disconnect"
        return self._post(path, {})

    def create_chat(
        self,
        account_chat_id: str,
        source_uid: str,
        contact_id: int | None = None,
    ) -> dict[str, Any]:
        """Create a new chat conversation and optionally link it to a contact."""
        path = f"/api/v2/origin/custom/{account_chat_id}/chats"
        data: dict[str, Any] = {"source_uid": source_uid}
        if contact_id is not None:
            data["contact_id"] = contact_id
        return self._post(path, data)

    def send_message(
        self,
        account_chat_id: str,
        chat_id: str,
        text: str,
        sender_id: str,
        sender_name: str,
    ) -> dict[str, Any]:
        """Send a text message in a chat conversation."""
        path = f"/api/v2/origin/custom/{account_chat_id}/chats/{chat_id}/messages"
        data: dict[str, Any] = {
            "sender": {"id": sender_id, "name": sender_name},
            "msgid": f"{sender_id}-{int(datetime.now(timezone.utc).timestamp())}",
            "conversation_id": chat_id,
            "created_at": int(datetime.now(timezone.utc).timestamp()),
            "body": {"type": "text", "text": text},
        }
        return self._post(path, data)
