# tests/test_commands/test_unsorted.py
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from amocrm.commands.unsorted import app
from amocrm.exceptions import EntityNotFoundError

runner = CliRunner()
SAMPLE_UNSORTED = {"uid": "abc123", "source_uid": "src1", "pipeline_id": 100}

def test_list_command():
    with patch("amocrm.commands.unsorted.UnsortedResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.list.return_value = [SAMPLE_UNSORTED]
        with patch("amocrm.commands.unsorted.AmoCRMClient"):
            result = runner.invoke(app, ["list", "--output", "json"])
    assert result.exit_code == 0

def test_get_command():
    with patch("amocrm.commands.unsorted.UnsortedResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get_by_uid.return_value = SAMPLE_UNSORTED
        with patch("amocrm.commands.unsorted.AmoCRMClient"):
            result = runner.invoke(app, ["get", "abc123", "--output", "json"])
    assert result.exit_code == 0
    mock_resource.get_by_uid.assert_called_once_with("abc123")

def test_accept_command():
    with patch("amocrm.commands.unsorted.UnsortedResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.accept.return_value = [SAMPLE_UNSORTED]
        with patch("amocrm.commands.unsorted.AmoCRMClient"):
            result = runner.invoke(app, ["accept", "abc123", "--pipeline-id", "100", "--status-id", "10"])
    assert result.exit_code == 0
    mock_resource.accept.assert_called_once_with([{"uid": "abc123", "pipeline_id": 100, "status_id": 10}])

def test_decline_command():
    with patch("amocrm.commands.unsorted.UnsortedResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.decline.return_value = [SAMPLE_UNSORTED]
        with patch("amocrm.commands.unsorted.AmoCRMClient"):
            result = runner.invoke(app, ["decline", "abc123"])
    assert result.exit_code == 0
    mock_resource.decline.assert_called_once_with([{"uid": "abc123"}])

def test_get_not_found():
    with patch("amocrm.commands.unsorted.UnsortedResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get_by_uid.side_effect = EntityNotFoundError("/leads/unsorted/nope")
        with patch("amocrm.commands.unsorted.AmoCRMClient"):
            result = runner.invoke(app, ["get", "nope"])
    assert result.exit_code == 1
