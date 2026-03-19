import respx
import httpx
import pytest
from amocrm.client import AmoCRMClient
from amocrm.resources.base import BaseResource, _build_filter_params, _build_order_params


class SampleResource(BaseResource):
    path = "/leads"
    embedded_key = "leads"


@pytest.fixture
def client():
    return AmoCRMClient(subdomain="test", access_token="test-token")


@pytest.fixture
def resource(client):
    return SampleResource(client)


def test_build_filter_params_list():
    result = _build_filter_params({"pipeline_id": [1, 2]})
    assert result == {"filter[pipeline_id][0]": 1, "filter[pipeline_id][1]": 2}


def test_build_filter_params_range():
    result = _build_filter_params({"created_at": {"from": 1700000, "to": 1800000}})
    assert result == {"filter[created_at][from]": 1700000, "filter[created_at][to]": 1800000}


def test_build_order_params():
    assert _build_order_params("created_at:asc") == {"order[created_at]": "asc"}
    assert _build_order_params("id:desc") == {"order[id]": "desc"}


@respx.mock
def test_list_returns_entities(resource):
    respx.get("https://test.amocrm.ru/api/v4/leads").mock(
        return_value=httpx.Response(200, json={
            "_embedded": {"leads": [{"id": 1, "name": "Deal"}]},
            "_page": 1,
        })
    )
    result = resource.list()
    assert result == [{"id": 1, "name": "Deal"}]


@respx.mock
def test_list_with_filters(resource):
    route = respx.get("https://test.amocrm.ru/api/v4/leads").mock(
        return_value=httpx.Response(200, json={"_embedded": {"leads": []}})
    )
    resource.list(filters={"pipeline_id": [5]})
    assert "filter%5Bpipeline_id%5D%5B0%5D=5" in str(route.calls[0].request.url)


@respx.mock
def test_get_returns_entity(resource):
    respx.get("https://test.amocrm.ru/api/v4/leads/123").mock(
        return_value=httpx.Response(200, json={"id": 123, "name": "Deal"})
    )
    result = resource.get(123)
    assert result["id"] == 123


@respx.mock
def test_delete_returns_true(resource):
    respx.delete("https://test.amocrm.ru/api/v4/leads/123").mock(
        return_value=httpx.Response(204)
    )
    assert resource.delete(123) is True
