"""Tests for WebhooksResource."""
import respx
import httpx
import pytest
from amocrm.client import AmoCRMClient
from amocrm.resources.webhooks import WebhooksResource
from amocrm.exceptions import EntityNotFoundError

SAMPLE_WEBHOOK = {"id": 1, "destination": "https://myserver.com/hook", "settings": ["leads_add"]}


@pytest.fixture
def client():
    return AmoCRMClient(subdomain="testco", access_token="test-token")


@pytest.fixture
def resource(client):
    return WebhooksResource(client)


@respx.mock
def test_list_webhooks(resource):
    respx.get("https://testco.amocrm.ru/api/v4/webhooks").mock(
        return_value=httpx.Response(200, json={"_embedded": {"hooks": [SAMPLE_WEBHOOK]}})
    )
    result = resource.list()
    assert result == [SAMPLE_WEBHOOK]


@respx.mock
def test_subscribe(resource):
    respx.post("https://testco.amocrm.ru/api/v4/webhooks").mock(
        return_value=httpx.Response(200, json={"_embedded": {"hooks": [SAMPLE_WEBHOOK]}})
    )
    result = resource.subscribe("https://myserver.com/hook", ["leads_add"])
    assert result["destination"] == "https://myserver.com/hook"


@respx.mock
def test_unsubscribe_found(resource):
    respx.get("https://testco.amocrm.ru/api/v4/webhooks").mock(
        return_value=httpx.Response(200, json={"_embedded": {"hooks": [SAMPLE_WEBHOOK]}})
    )
    respx.delete("https://testco.amocrm.ru/api/v4/webhooks/1").mock(
        return_value=httpx.Response(204)
    )
    result = resource.unsubscribe("https://myserver.com/hook")
    assert result is True


@respx.mock
def test_unsubscribe_not_found(resource):
    respx.get("https://testco.amocrm.ru/api/v4/webhooks").mock(
        return_value=httpx.Response(200, json={"_embedded": {"hooks": [SAMPLE_WEBHOOK]}})
    )
    with pytest.raises(EntityNotFoundError):
        resource.unsubscribe("https://other.com/hook")


@respx.mock
def test_delete_webhook(resource):
    respx.delete("https://testco.amocrm.ru/api/v4/webhooks/1").mock(
        return_value=httpx.Response(204)
    )
    assert resource.delete(1) is True
