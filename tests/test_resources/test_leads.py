import respx
import httpx
import pytest
from amocrm.client import AmoCRMClient
from amocrm.resources.leads import LeadsResource
from amocrm.exceptions import EntityNotFoundError

SAMPLE_LEAD = {"id": 1, "name": "Big Deal", "price": 50000, "status_id": 142}

@pytest.fixture
def client():
    return AmoCRMClient(subdomain="testco", access_token="test-token")

@pytest.fixture
def resource(client):
    return LeadsResource(client)

@respx.mock
def test_list_returns_leads(resource):
    respx.get("https://testco.amocrm.ru/api/v4/leads").mock(
        return_value=httpx.Response(200, json={"_embedded": {"leads": [SAMPLE_LEAD]}})
    )
    result = resource.list()
    assert result == [SAMPLE_LEAD]

@respx.mock
def test_list_with_filter(resource):
    route = respx.get("https://testco.amocrm.ru/api/v4/leads").mock(
        return_value=httpx.Response(200, json={"_embedded": {"leads": []}})
    )
    resource.list(filters={"pipeline_id": [5]})
    assert "filter%5Bpipeline_id%5D%5B0%5D=5" in str(route.calls[0].request.url)

@respx.mock
def test_list_with_order(resource):
    route = respx.get("https://testco.amocrm.ru/api/v4/leads").mock(
        return_value=httpx.Response(200, json={"_embedded": {"leads": []}})
    )
    resource.list(order="created_at:asc")
    assert "order%5Bcreated_at%5D=asc" in str(route.calls[0].request.url)

@respx.mock
def test_get_returns_lead(resource):
    respx.get("https://testco.amocrm.ru/api/v4/leads/1").mock(
        return_value=httpx.Response(200, json=SAMPLE_LEAD)
    )
    result = resource.get(1)
    assert result["id"] == 1

@respx.mock
def test_get_204_raises_not_found(resource):
    respx.get("https://testco.amocrm.ru/api/v4/leads/999").mock(
        return_value=httpx.Response(204)
    )
    with pytest.raises(EntityNotFoundError):
        resource.get(999)

@respx.mock
def test_create_returns_leads(resource):
    respx.post("https://testco.amocrm.ru/api/v4/leads").mock(
        return_value=httpx.Response(200, json={"_embedded": {"leads": [SAMPLE_LEAD]}})
    )
    result = resource.create([{"name": "Big Deal"}])
    assert result == [SAMPLE_LEAD]

@respx.mock
def test_update_returns_lead(resource):
    respx.patch("https://testco.amocrm.ru/api/v4/leads/1").mock(
        return_value=httpx.Response(200, json=SAMPLE_LEAD)
    )
    result = resource.update(1, {"price": 99000})
    assert result["id"] == 1

@respx.mock
def test_update_batch_204_returns_empty(resource):
    respx.patch("https://testco.amocrm.ru/api/v4/leads").mock(
        return_value=httpx.Response(204)
    )
    result = resource.update_batch([{"id": 1, "price": 99000}])
    assert result == []

@respx.mock
def test_delete_returns_true(resource):
    respx.delete("https://testco.amocrm.ru/api/v4/leads/1").mock(
        return_value=httpx.Response(204)
    )
    assert resource.delete(1) is True

@respx.mock
def test_create_complex(resource):
    respx.post("https://testco.amocrm.ru/api/v4/leads/complex").mock(
        return_value=httpx.Response(200, json={"_embedded": {"leads": [SAMPLE_LEAD]}})
    )
    result = resource.create_complex([{"name": "Big Deal", "contacts": []}])
    assert result == [SAMPLE_LEAD]
