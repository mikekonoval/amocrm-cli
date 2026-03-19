from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from amocrm.commands.tags import app
from amocrm.exceptions import EntityNotFoundError

runner = CliRunner()
SAMPLE_TAG = {"id": 1, "name": "VIP", "color": "#ff0000"}

def test_list_command():
    with patch("amocrm.commands.tags.TagsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.list.return_value = [SAMPLE_TAG]
        with patch("amocrm.commands.tags.AmoCRMClient"):
            result = runner.invoke(app, ["list", "--entity", "leads", "--output", "json"])
    assert result.exit_code == 0
    mock_cls.assert_called_once()

def test_get_command():
    with patch("amocrm.commands.tags.TagsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.return_value = SAMPLE_TAG
        with patch("amocrm.commands.tags.AmoCRMClient"):
            result = runner.invoke(app, ["get", "1", "--entity", "leads", "--output", "json"])
    assert result.exit_code == 0

def test_get_not_found_exits_1():
    with patch("amocrm.commands.tags.TagsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.side_effect = EntityNotFoundError("/leads/tags/999")
        with patch("amocrm.commands.tags.AmoCRMClient"):
            result = runner.invoke(app, ["get", "999", "--entity", "leads"])
    assert result.exit_code == 1

def test_create_command():
    with patch("amocrm.commands.tags.TagsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.create.return_value = [SAMPLE_TAG]
        with patch("amocrm.commands.tags.AmoCRMClient"):
            result = runner.invoke(app, [
                "create", "--entity", "leads",
                "--name", "VIP", "--color", "#ff0000", "--output", "json"
            ])
    assert result.exit_code == 0

def test_delete_command():
    with patch("amocrm.commands.tags.TagsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.delete.return_value = True
        with patch("amocrm.commands.tags.AmoCRMClient"):
            result = runner.invoke(app, ["delete", "1", "--entity", "leads"])
    assert result.exit_code == 0

def test_update_tag_command():
    with patch("amocrm.commands.tags.TagsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.update.return_value = {"id": 5, "name": "VIP"}
        with patch("amocrm.commands.tags.AmoCRMClient"):
            result = runner.invoke(app, ["update", "5", "--entity", "leads", "--name", "VIP"])
    assert result.exit_code == 0
    mock_resource.update.assert_called_once_with(5, {"name": "VIP"})

def test_delete_tag_command():
    with patch("amocrm.commands.tags.TagsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.delete.return_value = True
        with patch("amocrm.commands.tags.AmoCRMClient"):
            result = runner.invoke(app, ["delete", "5", "--entity", "leads"])
    assert result.exit_code == 0
