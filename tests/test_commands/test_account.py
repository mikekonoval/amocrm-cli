from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from amocrm.commands.account import app

runner = CliRunner()
SAMPLE_ACCOUNT = {"id": 123456, "name": "My Company"}


def test_info_command():
    with patch("amocrm.commands.account.AccountResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.return_value = SAMPLE_ACCOUNT
        with patch("amocrm.commands.account.AmoCRMClient"):
            result = runner.invoke(app, ["--output", "json"])
    assert result.exit_code == 0


def test_info_with_params():
    with patch("amocrm.commands.account.AccountResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.return_value = SAMPLE_ACCOUNT
        with patch("amocrm.commands.account.AmoCRMClient"):
            result = runner.invoke(app, ["--with", "users_groups,task_types", "--output", "json"])
    assert result.exit_code == 0
    call_kwargs = mock_resource.get.call_args[1]
    assert "users_groups" in call_kwargs.get("with_", [])
