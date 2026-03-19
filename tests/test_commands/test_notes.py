from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from amocrm.commands.notes import app
from amocrm.exceptions import EntityNotFoundError

runner = CliRunner()
SAMPLE_NOTE = {"id": 1, "note_type": "common"}

def test_list_command():
    with patch("amocrm.commands.notes.NotesResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.list.return_value = [SAMPLE_NOTE]
        with patch("amocrm.commands.notes.AmoCRMClient"):
            result = runner.invoke(app, ["list", "--entity", "leads", "--output", "json"])
    assert result.exit_code == 0
    mock_cls.assert_called_once()

def test_list_with_entity_id():
    with patch("amocrm.commands.notes.NotesResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.list.return_value = []
        with patch("amocrm.commands.notes.AmoCRMClient"):
            result = runner.invoke(app, ["list", "--entity", "leads", "--entity-id", "456", "--output", "json"])
    assert result.exit_code == 0
    # entity_id=456 passed to NotesResource
    call_kwargs = mock_cls.call_args[1]
    assert call_kwargs.get("entity_id") == 456

def test_create_command():
    with patch("amocrm.commands.notes.NotesResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.create.return_value = [SAMPLE_NOTE]
        with patch("amocrm.commands.notes.AmoCRMClient"):
            result = runner.invoke(app, [
                "create", "--entity", "leads", "--entity-id", "456",
                "--text", "Call done", "--output", "json"
            ])
    assert result.exit_code == 0

def test_get_not_found_exits_1():
    with patch("amocrm.commands.notes.NotesResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.side_effect = EntityNotFoundError("/leads/notes/999")
        with patch("amocrm.commands.notes.AmoCRMClient"):
            result = runner.invoke(app, ["get", "999", "--entity", "leads"])
    assert result.exit_code == 1

def test_update_note_command():
    with patch("amocrm.commands.notes.NotesResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.update.return_value = {"id": 10, "text": "Updated note"}
        with patch("amocrm.commands.notes.AmoCRMClient"):
            result = runner.invoke(app, ["update", "10", "--entity", "leads", "--text", "Updated note"])
    assert result.exit_code == 0
    mock_resource.update.assert_called_once_with(10, {"note_type": "common", "params": {"text": "Updated note"}})
