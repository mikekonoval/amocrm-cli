import respx
import httpx
import pytest
from amocrm.client import AmoCRMClient
from amocrm.resources.events import EventsResource
from amocrm.exceptions import EntityNotFoundError

SAMPLE_EVENT = {"id": 1, "type": "lead_status_changed", "entity_type": "leads"}

@pytest.fixture
def client():
    return AmoCRMClient(subdomain="testco", access_token="test-token")

@pytest.fixture
def resource(client):
    return EventsResource(client)

@respx.mock
def test_list_returns_events(resource):
    respx.get("https://testco.amocrm.ru/api/v4/events").mock(
        return_value=httpx.Response(200, json={"_embedded": {"events": [SAMPLE_EVENT]}})
    )
    result = resource.list()
    assert result == [SAMPLE_EVENT]

@respx.mock
def test_list_clamps_limit_to_100(resource):
    route = respx.get("https://testco.amocrm.ru/api/v4/events").mock(
        return_value=httpx.Response(200, json={"_embedded": {"events": []}})
    )
    resource.list(limit=200)
    assert "limit=100" in str(route.calls[0].request.url)

@respx.mock
def test_list_limit_100_not_exceeded(resource):
    route = respx.get("https://testco.amocrm.ru/api/v4/events").mock(
        return_value=httpx.Response(200, json={"_embedded": {"events": []}})
    )
    resource.list(limit=50)
    assert "limit=50" in str(route.calls[0].request.url)

@respx.mock
def test_get_event(resource):
    respx.get("https://testco.amocrm.ru/api/v4/events/1").mock(
        return_value=httpx.Response(200, json=SAMPLE_EVENT)
    )
    result = resource.get(1)
    assert result["id"] == 1

@respx.mock
def test_get_204_raises_not_found(resource):
    respx.get("https://testco.amocrm.ru/api/v4/events/999").mock(
        return_value=httpx.Response(204)
    )
    with pytest.raises(EntityNotFoundError):
        resource.get(999)
