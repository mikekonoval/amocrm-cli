"""Tests for webhooks CLI commands."""
import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from amocrm.commands.webhooks import app
from amocrm.exceptions import EntityNotFoundError

runner = CliRunner()
SAMPLE_WEBHOOK = {"id": 1, "destination": "https://myserver.com/hook"}


def test_list_webhooks():
    with patch("amocrm.commands.webhooks.WebhooksResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.list.return_value = [SAMPLE_WEBHOOK]
        with patch("amocrm.commands.webhooks.AmoCRMClient"):
            result = runner.invoke(app, ["list", "--output", "json"])
    assert result.exit_code == 0


def test_subscribe():
    with patch("amocrm.commands.webhooks.WebhooksResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.subscribe.return_value = SAMPLE_WEBHOOK
        with patch("amocrm.commands.webhooks.AmoCRMClient"):
            result = runner.invoke(app, ["subscribe", "--url", "https://myserver.com/hook", "--events", "leads_add,task_add"])
    assert result.exit_code == 0


def test_unsubscribe():
    with patch("amocrm.commands.webhooks.WebhooksResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.unsubscribe.return_value = True
        with patch("amocrm.commands.webhooks.AmoCRMClient"):
            result = runner.invoke(app, ["unsubscribe", "--url", "https://myserver.com/hook"])
    assert result.exit_code == 0


def test_unsubscribe_not_found():
    with patch("amocrm.commands.webhooks.WebhooksResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.unsubscribe.side_effect = EntityNotFoundError("/webhooks")
        with patch("amocrm.commands.webhooks.AmoCRMClient"):
            result = runner.invoke(app, ["unsubscribe", "--url", "https://other.com/hook"])
    assert result.exit_code == 1
