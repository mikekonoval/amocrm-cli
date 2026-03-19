import time
from amocrm.auth.token import is_token_expiring, make_longtoken_config


def test_is_token_expiring_returns_true_within_300s():
    expires_at = int(time.time()) + 200  # expires in 200s
    assert is_token_expiring(expires_at) is True


def test_is_token_expiring_returns_false_with_time_remaining():
    expires_at = int(time.time()) + 600  # expires in 600s
    assert is_token_expiring(expires_at) is False


def test_is_token_expiring_returns_false_for_none():
    assert is_token_expiring(None) is False


def test_make_longtoken_config():
    config = make_longtoken_config(subdomain="myco", token="tok123")
    assert config["auth_mode"] == "longtoken"
    assert config["access_token"] == "tok123"
    assert config["subdomain"] == "myco"
    assert config["refresh_token"] is None
