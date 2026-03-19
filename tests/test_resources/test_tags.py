import respx
import httpx
import pytest
from amocrm.client import AmoCRMClient
from amocrm.resources.tags import TagsResource
from amocrm.exceptions import EntityNotFoundError

SAMPLE_TAG = {"id": 1, "name": "VIP", "color": "#ff0000"}

@pytest.fixture
def client():
    return AmoCRMClient(subdomain="testco", access_token="test-token")

@pytest.fixture
def resource(client):
    return TagsResource(client, entity_type="leads")

def test_path(resource):
    assert resource.path == "/leads/tags"

@respx.mock
def test_list_returns_tags(resource):
    respx.get("https://testco.amocrm.ru/api/v4/leads/tags").mock(
        return_value=httpx.Response(200, json={"_embedded": {"tags": [SAMPLE_TAG]}})
    )
    result = resource.list()
    assert result == [SAMPLE_TAG]

@respx.mock
def test_list_with_filter(resource):
    respx.get("https://testco.amocrm.ru/api/v4/leads/tags", params={"filter[name]": "VIP"}).mock(
        return_value=httpx.Response(200, json={"_embedded": {"tags": [SAMPLE_TAG]}})
    )
    result = resource.list(filters={"name": "VIP"})
    assert result == [SAMPLE_TAG]

@respx.mock
def test_get_204_raises_not_found(resource):
    respx.get("https://testco.amocrm.ru/api/v4/leads/tags/999").mock(
        return_value=httpx.Response(204)
    )
    with pytest.raises(EntityNotFoundError):
        resource.get(999)

@respx.mock
def test_create_returns_tags(resource):
    respx.post("https://testco.amocrm.ru/api/v4/leads/tags").mock(
        return_value=httpx.Response(200, json={"_embedded": {"tags": [SAMPLE_TAG]}})
    )
    result = resource.create([{"name": "VIP", "color": "#ff0000"}])
    assert result == [SAMPLE_TAG]

@respx.mock
def test_delete_returns_true(resource):
    respx.delete("https://testco.amocrm.ru/api/v4/leads/tags/1").mock(
        return_value=httpx.Response(204)
    )
    assert resource.delete(1) is True
