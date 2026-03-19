# tests/test_resources/test_calls.py
import respx
import httpx
import pytest
from amocrm.client import AmoCRMClient
from amocrm.resources.calls import CallsResource

SAMPLE_CALL = {"id": 1, "duration": 60, "direction": "inbound"}

@pytest.fixture
def client():
    return AmoCRMClient(subdomain="testco", access_token="test-token")

@pytest.fixture
def resource(client):
    return CallsResource(client)

@respx.mock
def test_add_call(resource):
    respx.post("https://testco.amocrm.ru/api/v4/calls").mock(
        return_value=httpx.Response(200, json={"_embedded": {"calls": [SAMPLE_CALL]}})
    )
    result = resource.add([{
        "direction": "inbound", "duration": 60, "source": "Telephony",
        "phone": "+79001234567", "call_status": 4, "responsible_user_id": 1,
    }])
    assert result == [SAMPLE_CALL]
