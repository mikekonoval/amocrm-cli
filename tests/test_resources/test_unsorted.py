# tests/test_resources/test_unsorted.py
import respx
import httpx
import pytest
from amocrm.client import AmoCRMClient
from amocrm.resources.unsorted import UnsortedResource
from amocrm.exceptions import EntityNotFoundError

SAMPLE_UID = "abc123def456"
SAMPLE_UNSORTED = {"uid": SAMPLE_UID, "source_uid": "src1", "pipeline_id": 100}

@pytest.fixture
def client():
    return AmoCRMClient(subdomain="testco", access_token="test-token")

@pytest.fixture
def resource(client):
    return UnsortedResource(client)

@respx.mock
def test_list_returns_unsorted(resource):
    respx.get("https://testco.amocrm.ru/api/v4/leads/unsorted").mock(
        return_value=httpx.Response(200, json={"_embedded": {"unsorted": [SAMPLE_UNSORTED]}})
    )
    result = resource.list()
    assert result == [SAMPLE_UNSORTED]

@respx.mock
def test_get_by_uid(resource):
    respx.get(f"https://testco.amocrm.ru/api/v4/leads/unsorted/{SAMPLE_UID}").mock(
        return_value=httpx.Response(200, json=SAMPLE_UNSORTED)
    )
    result = resource.get_by_uid(SAMPLE_UID)
    assert result["uid"] == SAMPLE_UID

@respx.mock
def test_get_204_raises_not_found(resource):
    respx.get("https://testco.amocrm.ru/api/v4/leads/unsorted/notexist").mock(
        return_value=httpx.Response(204)
    )
    with pytest.raises(EntityNotFoundError):
        resource.get_by_uid("notexist")

@respx.mock
def test_add_unsorted(resource):
    respx.post("https://testco.amocrm.ru/api/v4/leads/unsorted").mock(
        return_value=httpx.Response(200, json={"_embedded": {"unsorted": [SAMPLE_UNSORTED]}})
    )
    result = resource.add([{"source_uid": "src1", "pipeline_id": 100}])
    assert result == [SAMPLE_UNSORTED]

@respx.mock
def test_accept(resource):
    respx.patch("https://testco.amocrm.ru/api/v4/leads/unsorted/accept").mock(
        return_value=httpx.Response(200, json={"_embedded": {"unsorted": [SAMPLE_UNSORTED]}})
    )
    result = resource.accept([{"uid": SAMPLE_UID, "status_id": 10, "pipeline_id": 100}])
    assert result == [SAMPLE_UNSORTED]

@respx.mock
def test_decline(resource):
    respx.patch("https://testco.amocrm.ru/api/v4/leads/unsorted/decline").mock(
        return_value=httpx.Response(200, json={"_embedded": {"unsorted": [SAMPLE_UNSORTED]}})
    )
    result = resource.decline([{"uid": SAMPLE_UID}])
    assert result == [SAMPLE_UNSORTED]
