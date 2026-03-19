# tests/test_resources/test_loss_reasons.py
import respx
import httpx
import pytest
from amocrm.client import AmoCRMClient
from amocrm.resources.loss_reasons import LossReasonsResource

SAMPLE_REASON = {"id": 1, "name": "Too expensive"}

@pytest.fixture
def client():
    return AmoCRMClient(subdomain="testco", access_token="test-token")

@pytest.fixture
def resource(client):
    return LossReasonsResource(client)

@respx.mock
def test_list_returns_reasons(resource):
    respx.get("https://testco.amocrm.ru/api/v4/leads/loss_reasons").mock(
        return_value=httpx.Response(200, json={"_embedded": {"loss_reasons": [SAMPLE_REASON]}})
    )
    result = resource.list()
    assert result == [SAMPLE_REASON]

@respx.mock
def test_get_returns_reason(resource):
    respx.get("https://testco.amocrm.ru/api/v4/leads/loss_reasons/1").mock(
        return_value=httpx.Response(200, json=SAMPLE_REASON)
    )
    result = resource.get(1)
    assert result["id"] == 1

@respx.mock
def test_create_returns_reasons(resource):
    respx.post("https://testco.amocrm.ru/api/v4/leads/loss_reasons").mock(
        return_value=httpx.Response(200, json={"_embedded": {"loss_reasons": [SAMPLE_REASON]}})
    )
    result = resource.create([{"name": "Too expensive"}])
    assert result == [SAMPLE_REASON]

@respx.mock
def test_update_returns_reason(resource):
    respx.patch("https://testco.amocrm.ru/api/v4/leads/loss_reasons/1").mock(
        return_value=httpx.Response(200, json=SAMPLE_REASON)
    )
    result = resource.update(1, {"name": "Updated"})
    assert result["id"] == 1

@respx.mock
def test_delete_returns_true(resource):
    respx.delete("https://testco.amocrm.ru/api/v4/leads/loss_reasons/1").mock(
        return_value=httpx.Response(204)
    )
    assert resource.delete(1) is True
