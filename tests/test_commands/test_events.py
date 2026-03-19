from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from amocrm.commands.events import app
from amocrm.exceptions import EntityNotFoundError

runner = CliRunner()
SAMPLE_EVENT = {"id": 1, "type": "lead_status_changed", "entity_type": "leads"}

def test_list_command():
    with patch("amocrm.commands.events.EventsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.list.return_value = [SAMPLE_EVENT]
        with patch("amocrm.commands.events.AmoCRMClient"):
            result = runner.invoke(app, ["list", "--output", "json"])
    assert result.exit_code == 0
    mock_cls.assert_called_once()

def test_get_command():
    with patch("amocrm.commands.events.EventsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.return_value = SAMPLE_EVENT
        with patch("amocrm.commands.events.AmoCRMClient"):
            result = runner.invoke(app, ["get", "1", "--output", "json"])
    assert result.exit_code == 0

def test_get_not_found_exits_1():
    with patch("amocrm.commands.events.EventsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.side_effect = EntityNotFoundError("/events/999")
        with patch("amocrm.commands.events.AmoCRMClient"):
            result = runner.invoke(app, ["get", "999"])
    assert result.exit_code == 1
