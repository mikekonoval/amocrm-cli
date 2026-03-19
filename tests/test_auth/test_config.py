import json
import pytest
from unittest.mock import patch
from amocrm.auth.config import load_config, save_config


def test_load_config_reads_json(tmp_path):
    config_data = {
        "subdomain": "mycompany",
        "auth_mode": "longtoken",
        "access_token": "tok",
        "refresh_token": None,
        "expires_at": None,
        "client_id": None,
        "client_secret": None,
        "redirect_uri": "http://localhost:8080",
    }
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config_data))
    with patch("amocrm.auth.config.CONFIG_PATH", config_file):
        result = load_config()
    assert result["subdomain"] == "mycompany"
    assert result["auth_mode"] == "longtoken"


def test_load_config_raises_if_missing(tmp_path):
    with patch("amocrm.auth.config.CONFIG_PATH", tmp_path / "missing.json"):
        with pytest.raises(FileNotFoundError):
            load_config()


def test_load_config_raises_on_invalid_auth_mode(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"auth_mode": "invalid", "subdomain": "x", "access_token": "y"}))
    with patch("amocrm.auth.config.CONFIG_PATH", config_file):
        with pytest.raises(ValueError, match="auth_mode"):
            load_config()


def test_save_config_writes_json(tmp_path):
    config_file = tmp_path / "config.json"
    config = {"subdomain": "test", "auth_mode": "longtoken", "access_token": "tok"}
    with patch("amocrm.auth.config.CONFIG_PATH", config_file):
        save_config(config)
    assert json.loads(config_file.read_text())["subdomain"] == "test"
