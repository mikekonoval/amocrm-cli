import time
import respx
import httpx
import pytest
from unittest.mock import patch, MagicMock
from amocrm.auth.oauth import exchange_code_for_tokens, build_auth_url, refresh_tokens


def test_build_auth_url():
    url = build_auth_url(client_id="abc123", state="xyz")
    assert "client_id=abc123" in url
    assert "state=xyz" in url
    assert url.startswith("https://www.amocrm.ru/oauth")


@respx.mock
def test_exchange_code_for_tokens():
    respx.post("https://myco.amocrm.ru/oauth2/access_token").mock(
        return_value=httpx.Response(200, json={
            "token_type": "Bearer",
            "expires_in": 86400,
            "access_token": "new-access",
            "refresh_token": "new-refresh",
        })
    )
    result = exchange_code_for_tokens(
        subdomain="myco",
        code="auth-code",
        client_id="cid",
        client_secret="csec",
        redirect_uri="http://localhost:8080",
    )
    assert result["access_token"] == "new-access"
    assert result["refresh_token"] == "new-refresh"
    assert "expires_at" in result


@respx.mock
def test_refresh_tokens():
    respx.post("https://myco.amocrm.ru/oauth2/access_token").mock(
        return_value=httpx.Response(200, json={
            "token_type": "Bearer",
            "expires_in": 86400,
            "access_token": "refreshed-access",
            "refresh_token": "refreshed-refresh",
        })
    )
    result = refresh_tokens(
        subdomain="myco",
        refresh_token="old-refresh",
        client_id="cid",
        client_secret="csec",
        redirect_uri="http://localhost:8080",
    )
    assert result["access_token"] == "refreshed-access"
    assert result["refresh_token"] == "refreshed-refresh"
