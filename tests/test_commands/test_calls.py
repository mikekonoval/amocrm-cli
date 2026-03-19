# tests/test_commands/test_calls.py
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from amocrm.commands.calls import app

runner = CliRunner()

def test_add_call_command():
    with patch("amocrm.commands.calls.CallsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.add.return_value = [{"id": 1}]
        with patch("amocrm.commands.calls.AmoCRMClient"):
            result = runner.invoke(app, [
                "add",
                "--direction", "inbound",
                "--duration", "60",
                "--source", "Telephony",
                "--phone", "+79001234567",
                "--call-status", "4",
                "--responsible-user-id", "1",
            ])
    assert result.exit_code == 0
    call_body = mock_resource.add.call_args[0][0][0]
    assert call_body["direction"] == "inbound"
    assert call_body["duration"] == 60
    assert call_body["call_status"] == 4
