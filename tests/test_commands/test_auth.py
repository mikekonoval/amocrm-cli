from unittest.mock import patch
from typer.testing import CliRunner
from amocrm.commands.auth import app

runner = CliRunner()

SAMPLE_LONGTOKEN_CONFIG = {
    "subdomain": "testco",
    "auth_mode": "longtoken",
    "access_token": "mytoken",
    "refresh_token": None,
    "expires_at": None,
    "client_id": None,
    "client_secret": None,
    "redirect_uri": "http://localhost:8080",
}

SAMPLE_OAUTH_CONFIG = {
    "subdomain": "testco",
    "auth_mode": "oauth",
    "access_token": "acc",
    "refresh_token": "ref",
    "expires_at": 9999999999,
    "client_id": "cid",
    "client_secret": "csec",
    "redirect_uri": "http://localhost:8080",
}


def test_login_token_saves_config():
    with patch("amocrm.commands.auth.make_longtoken_config") as mock_make, \
         patch("amocrm.commands.auth.save_config") as mock_save:
        mock_make.return_value = SAMPLE_LONGTOKEN_CONFIG
        result = runner.invoke(app, ["login", "--token", "mytoken", "--subdomain", "testco"])
    assert result.exit_code == 0
    mock_make.assert_called_once_with("testco", "mytoken")
    mock_save.assert_called_once_with(SAMPLE_LONGTOKEN_CONFIG)
    assert "testco" in result.output


def test_login_token_missing_subdomain_exits_1():
    result = runner.invoke(app, ["login", "--token", "mytoken"])
    assert result.exit_code != 0


def test_login_oauth_calls_browser_flow():
    tokens = {"access_token": "acc", "refresh_token": "ref", "expires_at": 9999999999}
    with patch("amocrm.commands.auth.run_browser_flow") as mock_flow, \
         patch("amocrm.commands.auth.save_config") as mock_save:
        mock_flow.return_value = tokens
        result = runner.invoke(app, [
            "login", "--oauth", "--subdomain", "testco",
            "--client-id", "cid", "--client-secret", "csec",
        ])
    assert result.exit_code == 0
    mock_flow.assert_called_once()
    saved = mock_save.call_args[0][0]
    assert saved["auth_mode"] == "oauth"
    assert saved["subdomain"] == "testco"
    assert saved["access_token"] == "acc"


def test_login_oauth_missing_client_id_exits_1():
    result = runner.invoke(app, ["login", "--oauth", "--subdomain", "testco", "--client-secret", "csec"])
    assert result.exit_code != 0


def test_login_oauth_missing_client_secret_exits_1():
    result = runner.invoke(app, ["login", "--oauth", "--subdomain", "testco", "--client-id", "cid"])
    assert result.exit_code != 0


def test_status_shows_config():
    with patch("amocrm.commands.auth.load_config") as mock_load:
        mock_load.return_value = SAMPLE_LONGTOKEN_CONFIG
        result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "testco" in result.output
    assert "longtoken" in result.output


def test_status_shows_oauth_expiry():
    with patch("amocrm.commands.auth.load_config") as mock_load:
        mock_load.return_value = SAMPLE_OAUTH_CONFIG
        result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "oauth" in result.output


def test_status_no_config_exits_1():
    with patch("amocrm.commands.auth.load_config") as mock_load:
        mock_load.side_effect = FileNotFoundError("No config")
        result = runner.invoke(app, ["status"])
    assert result.exit_code == 1


def test_logout_deletes_config():
    with patch("amocrm.commands.auth.CONFIG_PATH") as mock_path:
        mock_path.exists.return_value = True
        result = runner.invoke(app, ["logout"])
    assert result.exit_code == 0
    mock_path.unlink.assert_called_once()


def test_logout_no_config_still_succeeds():
    with patch("amocrm.commands.auth.CONFIG_PATH") as mock_path:
        mock_path.exists.return_value = False
        result = runner.invoke(app, ["logout"])
    assert result.exit_code == 0
    mock_path.unlink.assert_not_called()
