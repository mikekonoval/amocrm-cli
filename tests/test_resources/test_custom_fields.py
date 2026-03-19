"""Tests for CustomFieldsResource and CustomFieldGroupsResource."""
import respx
import httpx
import pytest
from amocrm.client import AmoCRMClient
from amocrm.resources.custom_fields import CustomFieldsResource, CustomFieldGroupsResource
from amocrm.exceptions import EntityNotFoundError

SAMPLE_FIELD = {"id": 1, "name": "Budget", "type": "numeric"}
SAMPLE_GROUP = {"id": 10, "name": "Finance"}


@pytest.fixture
def client():
    return AmoCRMClient(subdomain="testco", access_token="test-token")


@pytest.fixture
def field_resource(client):
    return CustomFieldsResource(client, entity="leads")


@pytest.fixture
def group_resource(client):
    return CustomFieldGroupsResource(client, entity="leads")


def test_field_path(field_resource):
    assert field_resource.path == "/leads/custom_fields"


def test_group_path(group_resource):
    assert group_resource.path == "/leads/custom_fields/groups"


@respx.mock
def test_list_fields(field_resource):
    respx.get("https://testco.amocrm.ru/api/v4/leads/custom_fields").mock(
        return_value=httpx.Response(200, json={"_embedded": {"custom_fields": [SAMPLE_FIELD]}})
    )
    result = field_resource.list()
    assert result == [SAMPLE_FIELD]


@respx.mock
def test_get_field(field_resource):
    respx.get("https://testco.amocrm.ru/api/v4/leads/custom_fields/1").mock(
        return_value=httpx.Response(200, json=SAMPLE_FIELD)
    )
    result = field_resource.get(1)
    assert result["id"] == 1


@respx.mock
def test_get_field_204_raises(field_resource):
    respx.get("https://testco.amocrm.ru/api/v4/leads/custom_fields/999").mock(
        return_value=httpx.Response(204)
    )
    with pytest.raises(EntityNotFoundError):
        field_resource.get(999)


@respx.mock
def test_list_groups(group_resource):
    respx.get("https://testco.amocrm.ru/api/v4/leads/custom_fields/groups").mock(
        return_value=httpx.Response(200, json={"_embedded": {"custom_field_groups": [SAMPLE_GROUP]}})
    )
    result = group_resource.list()
    assert result == [SAMPLE_GROUP]


@respx.mock
def test_create_field(field_resource):
    respx.post("https://testco.amocrm.ru/api/v4/leads/custom_fields").mock(
        return_value=httpx.Response(200, json={"_embedded": {"custom_fields": [SAMPLE_FIELD]}})
    )
    result = field_resource.create([{"name": "Budget", "type": "numeric"}])
    assert result == [SAMPLE_FIELD]


@respx.mock
def test_delete_field(field_resource):
    respx.delete("https://testco.amocrm.ru/api/v4/leads/custom_fields/1").mock(
        return_value=httpx.Response(204)
    )
    assert field_resource.delete(1) is True
