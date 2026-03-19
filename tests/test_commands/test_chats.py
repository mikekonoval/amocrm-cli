# tests/test_commands/test_chats.py
from __future__ import annotations

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from amocrm.commands.chats import app

runner = CliRunner()

ACCOUNT_CHAT_ID = "test-account-chat-id"
SAMPLE_CHAT = {"id": "chat-uuid-1", "source_uid": "ext-001"}
SAMPLE_MESSAGE = {"msgid": "msg-1", "conversation_id": "chat-uuid-1"}


def test_connect() -> None:
    with patch("amocrm.commands.chats.ChatsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.connect.return_value = {"account_id": ACCOUNT_CHAT_ID}
        with patch("amocrm.commands.chats.AmoCRMClient"):
            result = runner.invoke(app, [
                "connect",
                ACCOUNT_CHAT_ID,
                "--title", "My Bot",
                "--hook-url", "https://example.com/hook",
                "--output", "json",
            ])
    assert result.exit_code == 0
    mock_resource.connect.assert_called_once_with(
        account_chat_id=ACCOUNT_CHAT_ID,
        title="My Bot",
        hook_url="https://example.com/hook",
    )


def test_send() -> None:
    with patch("amocrm.commands.chats.ChatsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.send_message.return_value = SAMPLE_MESSAGE
        with patch("amocrm.commands.chats.AmoCRMClient"):
            result = runner.invoke(app, [
                "send",
                ACCOUNT_CHAT_ID,
                "chat-uuid-1",
                "--text", "Hello!",
                "--sender-id", "user-1",
                "--sender-name", "Alice",
                "--output", "json",
            ])
    assert result.exit_code == 0
    mock_resource.send_message.assert_called_once_with(
        account_chat_id=ACCOUNT_CHAT_ID,
        chat_id="chat-uuid-1",
        text="Hello!",
        sender_id="user-1",
        sender_name="Alice",
    )


def test_create_chat() -> None:
    with patch("amocrm.commands.chats.ChatsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.create_chat.return_value = SAMPLE_CHAT
        with patch("amocrm.commands.chats.AmoCRMClient"):
            result = runner.invoke(app, [
                "create",
                ACCOUNT_CHAT_ID,
                "--source-uid", "ext-001",
                "--output", "json",
            ])
    assert result.exit_code == 0
    mock_resource.create_chat.assert_called_once_with(
        account_chat_id=ACCOUNT_CHAT_ID,
        source_uid="ext-001",
        contact_id=None,
    )


def test_disconnect() -> None:
    with patch("amocrm.commands.chats.ChatsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.disconnect.return_value = {}
        with patch("amocrm.commands.chats.AmoCRMClient"):
            result = runner.invoke(app, ["disconnect", ACCOUNT_CHAT_ID])
    assert result.exit_code == 0
    mock_resource.disconnect.assert_called_once_with(account_chat_id=ACCOUNT_CHAT_ID)
