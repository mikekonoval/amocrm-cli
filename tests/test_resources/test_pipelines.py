import respx
import httpx
import pytest
from amocrm.client import AmoCRMClient
from amocrm.resources.pipelines import PipelinesResource, StagesResource, WON_STATUS_ID, LOST_STATUS_ID
from amocrm.exceptions import EntityNotFoundError

SAMPLE_PIPELINE = {"id": 100, "name": "Main Pipeline"}
SAMPLE_STAGE = {"id": 1000, "name": "New Lead", "pipeline_id": 100}

@pytest.fixture
def client():
    return AmoCRMClient(subdomain="testco", access_token="test-token")

@pytest.fixture
def pipeline_resource(client):
    return PipelinesResource(client)

@pytest.fixture
def stage_resource(client):
    return StagesResource(client, pipeline_id=100)

def test_constants():
    assert WON_STATUS_ID == 142
    assert LOST_STATUS_ID == 143

def test_stages_path(stage_resource):
    assert stage_resource.path == "/leads/pipelines/100/statuses"

@respx.mock
def test_list_pipelines(pipeline_resource):
    respx.get("https://testco.amocrm.ru/api/v4/leads/pipelines").mock(
        return_value=httpx.Response(200, json={"_embedded": {"pipelines": [SAMPLE_PIPELINE]}})
    )
    result = pipeline_resource.list()
    assert result == [SAMPLE_PIPELINE]

@respx.mock
def test_get_pipeline(pipeline_resource):
    respx.get("https://testco.amocrm.ru/api/v4/leads/pipelines/100").mock(
        return_value=httpx.Response(200, json=SAMPLE_PIPELINE)
    )
    result = pipeline_resource.get(100)
    assert result["id"] == 100

@respx.mock
def test_get_pipeline_204_raises_not_found(pipeline_resource):
    respx.get("https://testco.amocrm.ru/api/v4/leads/pipelines/999").mock(
        return_value=httpx.Response(204)
    )
    with pytest.raises(EntityNotFoundError):
        pipeline_resource.get(999)

@respx.mock
def test_list_stages(stage_resource):
    respx.get("https://testco.amocrm.ru/api/v4/leads/pipelines/100/statuses").mock(
        return_value=httpx.Response(200, json={"_embedded": {"statuses": [SAMPLE_STAGE]}})
    )
    result = stage_resource.list()
    assert result == [SAMPLE_STAGE]

@respx.mock
def test_create_pipeline(pipeline_resource):
    respx.post("https://testco.amocrm.ru/api/v4/leads/pipelines").mock(
        return_value=httpx.Response(200, json={"_embedded": {"pipelines": [SAMPLE_PIPELINE]}})
    )
    result = pipeline_resource.create([{"name": "Main Pipeline"}])
    assert result == [SAMPLE_PIPELINE]

@respx.mock
def test_delete_pipeline(pipeline_resource):
    respx.delete("https://testco.amocrm.ru/api/v4/leads/pipelines/100").mock(
        return_value=httpx.Response(204)
    )
    assert pipeline_resource.delete(100) is True
