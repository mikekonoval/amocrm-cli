# tests/test_commands/test_loss_reasons.py
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from amocrm.commands.loss_reasons import app
from amocrm.exceptions import EntityNotFoundError

runner = CliRunner()
SAMPLE_REASON = {"id": 1, "name": "Too expensive"}

def test_list_command():
    with patch("amocrm.commands.loss_reasons.LossReasonsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.list.return_value = [SAMPLE_REASON]
        with patch("amocrm.commands.loss_reasons.AmoCRMClient"):
            result = runner.invoke(app, ["list", "--output", "json"])
    assert result.exit_code == 0

def test_get_command():
    with patch("amocrm.commands.loss_reasons.LossReasonsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.return_value = SAMPLE_REASON
        with patch("amocrm.commands.loss_reasons.AmoCRMClient"):
            result = runner.invoke(app, ["get", "1", "--output", "json"])
    assert result.exit_code == 0

def test_create_command():
    with patch("amocrm.commands.loss_reasons.LossReasonsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.create.return_value = [SAMPLE_REASON]
        with patch("amocrm.commands.loss_reasons.AmoCRMClient"):
            result = runner.invoke(app, ["create", "--name", "Too expensive"])
    assert result.exit_code == 0

def test_update_command():
    with patch("amocrm.commands.loss_reasons.LossReasonsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.update.return_value = SAMPLE_REASON
        with patch("amocrm.commands.loss_reasons.AmoCRMClient"):
            result = runner.invoke(app, ["update", "1", "--name", "Updated"])
    assert result.exit_code == 0
    mock_resource.update.assert_called_once_with(1, {"name": "Updated"})

def test_delete_command():
    with patch("amocrm.commands.loss_reasons.LossReasonsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.delete.return_value = True
        with patch("amocrm.commands.loss_reasons.AmoCRMClient"):
            result = runner.invoke(app, ["delete", "1"])
    assert result.exit_code == 0

def test_get_not_found_exits_1():
    with patch("amocrm.commands.loss_reasons.LossReasonsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.side_effect = EntityNotFoundError("/leads/loss_reasons/999")
        with patch("amocrm.commands.loss_reasons.AmoCRMClient"):
            result = runner.invoke(app, ["get", "999"])
    assert result.exit_code == 1
