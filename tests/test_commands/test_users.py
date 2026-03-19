from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from amocrm.commands.users import app
from amocrm.exceptions import EntityNotFoundError

runner = CliRunner()
SAMPLE_USER = {"id": 1, "name": "John", "email": "john@example.com"}
SAMPLE_ROLE = {"id": 1, "name": "Admin"}

def test_list_users_command():
    with patch("amocrm.commands.users.UsersResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.list.return_value = [SAMPLE_USER]
        with patch("amocrm.commands.users.AmoCRMClient"):
            result = runner.invoke(app, ["list", "--output", "json"])
    assert result.exit_code == 0
    mock_resource.list.assert_called_once()

def test_get_user_command():
    with patch("amocrm.commands.users.UsersResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.return_value = SAMPLE_USER
        with patch("amocrm.commands.users.AmoCRMClient"):
            result = runner.invoke(app, ["get", "1", "--output", "json"])
    assert result.exit_code == 0

def test_get_user_not_found_exits_1():
    with patch("amocrm.commands.users.UsersResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.side_effect = EntityNotFoundError("/users/999")
        with patch("amocrm.commands.users.AmoCRMClient"):
            result = runner.invoke(app, ["get", "999"])
    assert result.exit_code == 1

def test_list_roles_command():
    with patch("amocrm.commands.users.RolesResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.list.return_value = [SAMPLE_ROLE]
        with patch("amocrm.commands.users.AmoCRMClient"):
            result = runner.invoke(app, ["roles", "list", "--output", "json"])
    assert result.exit_code == 0
    mock_resource.list.assert_called_once()

def test_get_role_command():
    with patch("amocrm.commands.users.RolesResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.return_value = SAMPLE_ROLE
        with patch("amocrm.commands.users.AmoCRMClient"):
            result = runner.invoke(app, ["roles", "get", "1", "--output", "json"])
    assert result.exit_code == 0
