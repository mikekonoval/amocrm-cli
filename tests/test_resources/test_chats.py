from __future__ import annotations

from unittest.mock import MagicMock

import httpx
import pytest
import respx

from amocrm.resources.chats import ChatsResource

AMOJO_BASE = "https://amojo.amocrm.ru"
ACCOUNT_CHAT_ID = "test-account-chat-id"

SAMPLE_CHAT = {
    "id": "chat-uuid-1",
    "source_uid": "ext-chat-001",
    "created_at": 1700000000,
}

SAMPLE_MESSAGE = {
    "msgid": "msg-uuid-1",
    "conversation_id": "chat-uuid-1",
    "created_at": 1700000000,
    "body": {"type": "text", "text": "Hello!"},
}


@pytest.fixture
def mock_client() -> MagicMock:
    client = MagicMock()
    client._access_token = "test-token"
    client._client_secret = "test-secret"
    return client


@respx.mock
def test_connect_chat(mock_client: MagicMock) -> None:
    url = f"{AMOJO_BASE}/api/v2/origin/custom/{ACCOUNT_CHAT_ID}/connect"
    respx.post(url).mock(return_value=httpx.Response(200, json={
        "account_id": ACCOUNT_CHAT_ID,
        "title": "My Chat",
        "hook_api_version": "v2",
    }))
    resource = ChatsResource(mock_client)
    result = resource.connect(
        account_chat_id=ACCOUNT_CHAT_ID,
        title="My Chat",
        hook_url="https://example.com/hook",
    )
    assert result["account_id"] == ACCOUNT_CHAT_ID


@respx.mock
def test_send_message(mock_client: MagicMock) -> None:
    chat_id = "chat-uuid-1"
    url = f"{AMOJO_BASE}/api/v2/origin/custom/{ACCOUNT_CHAT_ID}/chats/{chat_id}/messages"
    respx.post(url).mock(return_value=httpx.Response(200, json=SAMPLE_MESSAGE))
    resource = ChatsResource(mock_client)
    result = resource.send_message(
        account_chat_id=ACCOUNT_CHAT_ID,
        chat_id=chat_id,
        text="Hello!",
        sender_id="user-1",
        sender_name="Alice",
    )
    assert result["msgid"] == "msg-uuid-1"


@respx.mock
def test_create_chat(mock_client: MagicMock) -> None:
    url = f"{AMOJO_BASE}/api/v2/origin/custom/{ACCOUNT_CHAT_ID}/chats"
    respx.post(url).mock(return_value=httpx.Response(200, json=SAMPLE_CHAT))
    resource = ChatsResource(mock_client)
    result = resource.create_chat(
        account_chat_id=ACCOUNT_CHAT_ID,
        source_uid="ext-chat-001",
        contact_id=42,
    )
    assert result["id"] == "chat-uuid-1"
