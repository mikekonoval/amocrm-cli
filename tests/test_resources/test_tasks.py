import respx
import httpx
import pytest
from amocrm.client import AmoCRMClient
from amocrm.resources.tasks import TasksResource
from amocrm.exceptions import EntityNotFoundError

SAMPLE_TASK = {"id": 1, "text": "Follow up", "complete_till": 1700000}

@pytest.fixture
def client():
    return AmoCRMClient(subdomain="testco", access_token="test-token")

@pytest.fixture
def resource(client):
    return TasksResource(client)

@respx.mock
def test_list_returns_tasks(resource):
    respx.get("https://testco.amocrm.ru/api/v4/tasks").mock(
        return_value=httpx.Response(200, json={"_embedded": {"tasks": [SAMPLE_TASK]}})
    )
    result = resource.list()
    assert result == [SAMPLE_TASK]

@respx.mock
def test_list_with_filter(resource):
    route = respx.get("https://testco.amocrm.ru/api/v4/tasks").mock(
        return_value=httpx.Response(200, json={"_embedded": {"tasks": []}})
    )
    resource.list(filters={"query": ["Follow up"]})
    assert "filter" in str(route.calls[0].request.url)

@respx.mock
def test_list_with_order(resource):
    route = respx.get("https://testco.amocrm.ru/api/v4/tasks").mock(
        return_value=httpx.Response(200, json={"_embedded": {"tasks": []}})
    )
    resource.list(order="created_at:desc")
    assert "order%5Bcreated_at%5D=desc" in str(route.calls[0].request.url)

@respx.mock
def test_get_returns_task(resource):
    respx.get("https://testco.amocrm.ru/api/v4/tasks/1").mock(
        return_value=httpx.Response(200, json=SAMPLE_TASK)
    )
    result = resource.get(1)
    assert result["id"] == 1

@respx.mock
def test_get_204_raises_not_found(resource):
    respx.get("https://testco.amocrm.ru/api/v4/tasks/999").mock(
        return_value=httpx.Response(204)
    )
    with pytest.raises(EntityNotFoundError):
        resource.get(999)

@respx.mock
def test_create_returns_tasks(resource):
    respx.post("https://testco.amocrm.ru/api/v4/tasks").mock(
        return_value=httpx.Response(200, json={"_embedded": {"tasks": [SAMPLE_TASK]}})
    )
    result = resource.create([{"text": "Follow up", "complete_till": 1700000}])
    assert result == [SAMPLE_TASK]

@respx.mock
def test_update_returns_task(resource):
    respx.patch("https://testco.amocrm.ru/api/v4/tasks/1").mock(
        return_value=httpx.Response(200, json=SAMPLE_TASK)
    )
    result = resource.update(1, {"text": "Follow up"})
    assert result["id"] == 1

@respx.mock
def test_update_batch_204_returns_empty(resource):
    respx.patch("https://testco.amocrm.ru/api/v4/tasks").mock(
        return_value=httpx.Response(204)
    )
    result = resource.update_batch([{"id": 1, "text": "Follow up"}])
    assert result == []

@respx.mock
def test_delete_returns_true(resource):
    respx.delete("https://testco.amocrm.ru/api/v4/tasks/1").mock(
        return_value=httpx.Response(204)
    )
    assert resource.delete(1) is True
