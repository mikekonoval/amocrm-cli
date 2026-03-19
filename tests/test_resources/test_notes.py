import respx
import httpx
import pytest
from amocrm.client import AmoCRMClient
from amocrm.resources.notes import NotesResource
from amocrm.exceptions import EntityNotFoundError

SAMPLE_NOTE = {"id": 1, "note_type": "common", "params": {"text": "Call done"}}

@pytest.fixture
def client():
    return AmoCRMClient(subdomain="testco", access_token="test-token")

@pytest.fixture
def resource(client):
    return NotesResource(client, entity_type="leads")

@pytest.fixture
def resource_with_id(client):
    return NotesResource(client, entity_type="leads", entity_id=456)

def test_path_without_entity_id(resource):
    assert resource.path == "/leads/notes"

def test_path_with_entity_id(resource_with_id):
    assert resource_with_id.path == "/leads/456/notes"

@respx.mock
def test_list_returns_notes(resource):
    respx.get("https://testco.amocrm.ru/api/v4/leads/notes").mock(
        return_value=httpx.Response(200, json={"_embedded": {"notes": [SAMPLE_NOTE]}})
    )
    result = resource.list()
    assert result == [SAMPLE_NOTE]

@respx.mock
def test_list_with_entity_id(resource_with_id):
    respx.get("https://testco.amocrm.ru/api/v4/leads/456/notes").mock(
        return_value=httpx.Response(200, json={"_embedded": {"notes": [SAMPLE_NOTE]}})
    )
    result = resource_with_id.list()
    assert result == [SAMPLE_NOTE]

@respx.mock
def test_get_204_raises_not_found(resource):
    respx.get("https://testco.amocrm.ru/api/v4/leads/notes/999").mock(
        return_value=httpx.Response(204)
    )
    with pytest.raises(EntityNotFoundError):
        resource.get(999)

@respx.mock
def test_create_note(resource):
    respx.post("https://testco.amocrm.ru/api/v4/leads/notes").mock(
        return_value=httpx.Response(200, json={"_embedded": {"notes": [SAMPLE_NOTE]}})
    )
    result = resource.create([{"note_type": "common", "params": {"text": "Call done"}}])
    assert result == [SAMPLE_NOTE]

@respx.mock
def test_delete_returns_true(resource):
    respx.delete("https://testco.amocrm.ru/api/v4/leads/notes/1").mock(
        return_value=httpx.Response(204)
    )
    assert resource.delete(1) is True
