import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from amocrm.commands.tasks import app
from amocrm.exceptions import EntityNotFoundError

runner = CliRunner()
SAMPLE_TASK = {"id": 1, "text": "Follow up", "complete_till": 1700000}

def test_list_command():
    with patch("amocrm.commands.tasks.TasksResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.list.return_value = [SAMPLE_TASK]
        with patch("amocrm.commands.tasks.AmoCRMClient"):
            result = runner.invoke(app, ["list", "--output", "json"])
    assert result.exit_code == 0

def test_get_command():
    with patch("amocrm.commands.tasks.TasksResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.return_value = SAMPLE_TASK
        with patch("amocrm.commands.tasks.AmoCRMClient"):
            result = runner.invoke(app, ["get", "1", "--output", "json"])
    assert result.exit_code == 0

def test_get_not_found_exits_1():
    with patch("amocrm.commands.tasks.TasksResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.side_effect = EntityNotFoundError("/tasks/999")
        with patch("amocrm.commands.tasks.AmoCRMClient"):
            result = runner.invoke(app, ["get", "999"])
    assert result.exit_code == 1

def test_create_command():
    with patch("amocrm.commands.tasks.TasksResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.create.return_value = [SAMPLE_TASK]
        with patch("amocrm.commands.tasks.AmoCRMClient"):
            result = runner.invoke(app, ["create", "--text", "Follow up", "--complete-till", "1700000", "--output", "json"])
    assert result.exit_code == 0

def test_delete_command():
    with patch("amocrm.commands.tasks.TasksResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.delete.return_value = True
        with patch("amocrm.commands.tasks.AmoCRMClient"):
            result = runner.invoke(app, ["delete", "1"])
    assert result.exit_code == 0
