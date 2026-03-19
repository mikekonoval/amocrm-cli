import respx
import httpx
import pytest
from amocrm.client import AmoCRMClient
from amocrm.resources.contacts import ContactsResource
from amocrm.exceptions import EntityNotFoundError

SAMPLE_CONTACT = {"id": 1, "name": "John Doe", "first_name": "John", "last_name": "Doe"}

@pytest.fixture
def client():
    return AmoCRMClient(subdomain="testco", access_token="test-token")

@pytest.fixture
def resource(client):
    return ContactsResource(client)

@respx.mock
def test_list_returns_contacts(resource):
    respx.get("https://testco.amocrm.ru/api/v4/contacts").mock(
        return_value=httpx.Response(200, json={"_embedded": {"contacts": [SAMPLE_CONTACT]}})
    )
    result = resource.list()
    assert result == [SAMPLE_CONTACT]

@respx.mock
def test_list_with_filter(resource):
    route = respx.get("https://testco.amocrm.ru/api/v4/contacts").mock(
        return_value=httpx.Response(200, json={"_embedded": {"contacts": []}})
    )
    resource.list(filters={"query": ["John"]})
    assert "filter" in str(route.calls[0].request.url)

@respx.mock
def test_list_with_order(resource):
    route = respx.get("https://testco.amocrm.ru/api/v4/contacts").mock(
        return_value=httpx.Response(200, json={"_embedded": {"contacts": []}})
    )
    resource.list(order="created_at:desc")
    assert "order%5Bcreated_at%5D=desc" in str(route.calls[0].request.url)

@respx.mock
def test_get_returns_contact(resource):
    respx.get("https://testco.amocrm.ru/api/v4/contacts/1").mock(
        return_value=httpx.Response(200, json=SAMPLE_CONTACT)
    )
    result = resource.get(1)
    assert result["id"] == 1

@respx.mock
def test_get_204_raises_not_found(resource):
    respx.get("https://testco.amocrm.ru/api/v4/contacts/999").mock(
        return_value=httpx.Response(204)
    )
    with pytest.raises(EntityNotFoundError):
        resource.get(999)

@respx.mock
def test_create_returns_contacts(resource):
    respx.post("https://testco.amocrm.ru/api/v4/contacts").mock(
        return_value=httpx.Response(200, json={"_embedded": {"contacts": [SAMPLE_CONTACT]}})
    )
    result = resource.create([{"name": "John Doe"}])
    assert result == [SAMPLE_CONTACT]

@respx.mock
def test_update_returns_contact(resource):
    respx.patch("https://testco.amocrm.ru/api/v4/contacts/1").mock(
        return_value=httpx.Response(200, json=SAMPLE_CONTACT)
    )
    result = resource.update(1, {"name": "Jane Doe"})
    assert result["id"] == 1

@respx.mock
def test_update_batch_204_returns_empty(resource):
    respx.patch("https://testco.amocrm.ru/api/v4/contacts").mock(
        return_value=httpx.Response(204)
    )
    result = resource.update_batch([{"id": 1, "name": "Jane"}])
    assert result == []

@respx.mock
def test_delete_returns_true(resource):
    respx.delete("https://testco.amocrm.ru/api/v4/contacts/1").mock(
        return_value=httpx.Response(204)
    )
    assert resource.delete(1) is True
