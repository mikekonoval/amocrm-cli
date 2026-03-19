import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from amocrm.commands.leads import app
from amocrm.exceptions import EntityNotFoundError

runner = CliRunner()
SAMPLE_LEAD = {"id": 1, "name": "Big Deal", "price": 50000}

def test_list_command_calls_resource():
    with patch("amocrm.commands.leads.LeadsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.list.return_value = [SAMPLE_LEAD]
        with patch("amocrm.commands.leads.AmoCRMClient"):
            result = runner.invoke(app, ["list", "--output", "json"])
    assert result.exit_code == 0
    mock_resource.list.assert_called_once()

def test_list_with_filter_parses_json():
    with patch("amocrm.commands.leads.LeadsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.list.return_value = []
        with patch("amocrm.commands.leads.AmoCRMClient"):
            result = runner.invoke(app, ["list", "--filter", '{"status_id": 142}', "--output", "json"])
    assert result.exit_code == 0
    call_kwargs = mock_resource.list.call_args[1]
    assert call_kwargs["filters"] == {"status_id": 142}

def test_get_command():
    with patch("amocrm.commands.leads.LeadsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.return_value = SAMPLE_LEAD
        with patch("amocrm.commands.leads.AmoCRMClient"):
            result = runner.invoke(app, ["get", "1", "--output", "json"])
    assert result.exit_code == 0

def test_get_not_found_exits_1():
    with patch("amocrm.commands.leads.LeadsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.side_effect = EntityNotFoundError("/leads/999")
        with patch("amocrm.commands.leads.AmoCRMClient"):
            result = runner.invoke(app, ["get", "999"])
    assert result.exit_code == 1

def test_create_command():
    with patch("amocrm.commands.leads.LeadsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.create.return_value = [SAMPLE_LEAD]
        with patch("amocrm.commands.leads.AmoCRMClient"):
            result = runner.invoke(app, ["create", "--name", "New Deal", "--output", "json"])
    assert result.exit_code == 0
    mock_resource.create.assert_called_once()

def test_delete_command():
    with patch("amocrm.commands.leads.LeadsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.delete.return_value = True
        with patch("amocrm.commands.leads.AmoCRMClient"):
            result = runner.invoke(app, ["delete", "1"])
    assert result.exit_code == 0
