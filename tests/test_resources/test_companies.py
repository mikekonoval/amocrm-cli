import respx
import httpx
import pytest
from amocrm.client import AmoCRMClient
from amocrm.resources.companies import CompaniesResource
from amocrm.exceptions import EntityNotFoundError

SAMPLE_COMPANY = {"id": 1, "name": "Acme Corp"}

@pytest.fixture
def client():
    return AmoCRMClient(subdomain="testco", access_token="test-token")

@pytest.fixture
def resource(client):
    return CompaniesResource(client)

@respx.mock
def test_list_returns_companies(resource):
    respx.get("https://testco.amocrm.ru/api/v4/companies").mock(
        return_value=httpx.Response(200, json={"_embedded": {"companies": [SAMPLE_COMPANY]}})
    )
    result = resource.list()
    assert result == [SAMPLE_COMPANY]

@respx.mock
def test_list_with_filter(resource):
    route = respx.get("https://testco.amocrm.ru/api/v4/companies").mock(
        return_value=httpx.Response(200, json={"_embedded": {"companies": []}})
    )
    resource.list(filters={"query": ["Acme"]})
    assert "filter" in str(route.calls[0].request.url)

@respx.mock
def test_list_with_order(resource):
    route = respx.get("https://testco.amocrm.ru/api/v4/companies").mock(
        return_value=httpx.Response(200, json={"_embedded": {"companies": []}})
    )
    resource.list(order="created_at:desc")
    assert "order%5Bcreated_at%5D=desc" in str(route.calls[0].request.url)

@respx.mock
def test_get_returns_company(resource):
    respx.get("https://testco.amocrm.ru/api/v4/companies/1").mock(
        return_value=httpx.Response(200, json=SAMPLE_COMPANY)
    )
    result = resource.get(1)
    assert result["id"] == 1

@respx.mock
def test_get_204_raises_not_found(resource):
    respx.get("https://testco.amocrm.ru/api/v4/companies/999").mock(
        return_value=httpx.Response(204)
    )
    with pytest.raises(EntityNotFoundError):
        resource.get(999)

@respx.mock
def test_create_returns_companies(resource):
    respx.post("https://testco.amocrm.ru/api/v4/companies").mock(
        return_value=httpx.Response(200, json={"_embedded": {"companies": [SAMPLE_COMPANY]}})
    )
    result = resource.create([{"name": "Acme Corp"}])
    assert result == [SAMPLE_COMPANY]

@respx.mock
def test_update_returns_company(resource):
    respx.patch("https://testco.amocrm.ru/api/v4/companies/1").mock(
        return_value=httpx.Response(200, json=SAMPLE_COMPANY)
    )
    result = resource.update(1, {"name": "Acme Corp"})
    assert result["id"] == 1

@respx.mock
def test_update_batch_204_returns_empty(resource):
    respx.patch("https://testco.amocrm.ru/api/v4/companies").mock(
        return_value=httpx.Response(204)
    )
    result = resource.update_batch([{"id": 1, "name": "Acme Corp"}])
    assert result == []

@respx.mock
def test_delete_returns_true(resource):
    respx.delete("https://testco.amocrm.ru/api/v4/companies/1").mock(
        return_value=httpx.Response(204)
    )
    assert resource.delete(1) is True
