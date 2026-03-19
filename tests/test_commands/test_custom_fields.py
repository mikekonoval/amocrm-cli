"""Tests for custom_fields CLI commands."""
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from amocrm.commands.custom_fields import app
from amocrm.exceptions import EntityNotFoundError

runner = CliRunner()
SAMPLE_FIELD = {"id": 1, "name": "Budget"}
SAMPLE_GROUP = {"id": 10, "name": "Finance"}


def test_list_fields():
    with patch("amocrm.commands.custom_fields.CustomFieldsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.list.return_value = [SAMPLE_FIELD]
        with patch("amocrm.commands.custom_fields.AmoCRMClient"):
            result = runner.invoke(app, ["list", "--entity", "leads", "--output", "json"])
    assert result.exit_code == 0


def test_get_field():
    with patch("amocrm.commands.custom_fields.CustomFieldsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.return_value = SAMPLE_FIELD
        with patch("amocrm.commands.custom_fields.AmoCRMClient"):
            result = runner.invoke(app, ["get", "1", "--entity", "leads", "--output", "json"])
    assert result.exit_code == 0


def test_get_field_not_found():
    with patch("amocrm.commands.custom_fields.CustomFieldsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.side_effect = EntityNotFoundError("/leads/custom_fields/999")
        with patch("amocrm.commands.custom_fields.AmoCRMClient"):
            result = runner.invoke(app, ["get", "999", "--entity", "leads"])
    assert result.exit_code == 1


def test_list_groups():
    with patch("amocrm.commands.custom_fields.CustomFieldGroupsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.list.return_value = [SAMPLE_GROUP]
        with patch("amocrm.commands.custom_fields.AmoCRMClient"):
            result = runner.invoke(app, ["groups", "list", "--entity", "leads", "--output", "json"])
    assert result.exit_code == 0
