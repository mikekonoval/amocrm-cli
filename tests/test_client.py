import time
import respx
import httpx
import pytest
from unittest.mock import patch
from amocrm.client import AmoCRMClient
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError


@pytest.fixture
def client():
    return AmoCRMClient(subdomain="testco", access_token="tok")


@respx.mock
def test_get_returns_dict(client):
    respx.get("https://testco.amocrm.ru/api/v4/leads/1").mock(
        return_value=httpx.Response(200, json={"id": 1})
    )
    assert client.get("/leads/1") == {"id": 1}


@respx.mock
def test_get_204_raises_entity_not_found(client):
    respx.get("https://testco.amocrm.ru/api/v4/leads/999").mock(
        return_value=httpx.Response(204)
    )
    with pytest.raises(EntityNotFoundError):
        client.get("/leads/999")


@respx.mock
def test_delete_204_returns_true(client):
    respx.delete("https://testco.amocrm.ru/api/v4/leads/1").mock(
        return_value=httpx.Response(204)
    )
    assert client.delete("/leads/1") is True


@respx.mock
def test_patch_single_resource_204_raises_not_found(client):
    respx.patch("https://testco.amocrm.ru/api/v4/leads/1").mock(
        return_value=httpx.Response(204)
    )
    with pytest.raises(EntityNotFoundError):
        client.patch("/leads/1", json={"name": "x"})


@respx.mock
def test_patch_batch_204_returns_empty_list(client):
    respx.patch("https://testco.amocrm.ru/api/v4/leads").mock(
        return_value=httpx.Response(204)
    )
    result = client.patch("/leads", json=[{"id": 1, "name": "x"}])
    assert result == []


@respx.mock
def test_error_response_raises_api_error(client):
    respx.get("https://testco.amocrm.ru/api/v4/leads").mock(
        return_value=httpx.Response(
            400,
            json={"status": 400, "title": "Bad Request", "detail": "missing name"},
            headers={"content-type": "application/problem+json"},
        )
    )
    with pytest.raises(AmoCRMAPIError) as exc_info:
        client.get("/leads")
    assert exc_info.value.status == 400


@respx.mock
def test_429_retries(client):
    respx.get("https://testco.amocrm.ru/api/v4/leads").mock(
        side_effect=[
            httpx.Response(429),
            httpx.Response(200, json={"_embedded": {"leads": []}}),
        ]
    )
    with patch("time.sleep"):
        result = client.get("/leads")
    assert result is not None


def test_longtoken_mode_skips_refresh():
    client = AmoCRMClient(subdomain="testco", access_token="tok")
    # No refresh_token — should not attempt refresh
    with respx.mock:
        respx.get("https://testco.amocrm.ru/api/v4/account").mock(
            return_value=httpx.Response(200, json={"id": 1})
        )
        result = client.get("/account")
    assert result == {"id": 1}


def test_kwargs_with_expiring_token_refreshes():
    expires_soon = int(time.time()) + 100  # within 300s threshold
    client = AmoCRMClient(
        subdomain="testco",
        access_token="old-tok",
        refresh_token="ref-tok",
        client_id="cid",
        client_secret="csec",
        expires_at=expires_soon,
    )
    with respx.mock:
        respx.post("https://testco.amocrm.ru/oauth2/access_token").mock(
            return_value=httpx.Response(200, json={
                "access_token": "new-tok",
                "refresh_token": "new-ref",
                "expires_in": 86400,
            })
        )
        respx.get("https://testco.amocrm.ru/api/v4/account").mock(
            return_value=httpx.Response(200, json={"id": 1})
        )
        client.get("/account")
    assert client._access_token == "new-tok"


def test_kwargs_refresh_does_not_write_config(tmp_path):
    """After a refresh in kwargs mode, the config file must not be touched."""
    import json as _json
    sentinel = {"subdomain": "other", "auth_mode": "longtoken", "access_token": "sentinel"}
    config_file = tmp_path / "config.json"
    config_file.write_text(_json.dumps(sentinel))

    expires_soon = int(time.time()) + 100
    client = AmoCRMClient(
        subdomain="testco",
        access_token="old-tok",
        refresh_token="ref-tok",
        client_id="cid",
        client_secret="csec",
        expires_at=expires_soon,
    )
    with respx.mock, patch("amocrm.auth.config.CONFIG_PATH", config_file):
        respx.post("https://testco.amocrm.ru/oauth2/access_token").mock(
            return_value=httpx.Response(200, json={
                "access_token": "new-tok",
                "refresh_token": "new-ref",
                "expires_in": 86400,
            })
        )
        respx.get("https://testco.amocrm.ru/api/v4/account").mock(
            return_value=httpx.Response(200, json={"id": 1})
        )
        client.get("/account")

    # Config file must be unchanged — kwargs mode never writes to disk
    assert _json.loads(config_file.read_text()) == sentinel


def test_kwargs_expires_at_none_refreshes_on_401():
    """When expires_at=None, no proactive refresh; refresh triggered by 401."""
    client = AmoCRMClient(
        subdomain="testco",
        access_token="old-tok",
        refresh_token="ref-tok",
        client_id="cid",
        client_secret="csec",
        expires_at=None,  # no known expiry
    )
    with respx.mock:
        respx.post("https://testco.amocrm.ru/oauth2/access_token").mock(
            return_value=httpx.Response(200, json={
                "access_token": "new-tok",
                "refresh_token": "new-ref",
                "expires_in": 86400,
            })
        )
        route = respx.get("https://testco.amocrm.ru/api/v4/account").mock(
            side_effect=[
                httpx.Response(401),
                httpx.Response(200, json={"id": 1}),
            ]
        )
        result = client.get("/account")

    assert result == {"id": 1}
    assert client._access_token == "new-tok"
    assert len(route.calls) == 2  # first call got 401, second succeeded
