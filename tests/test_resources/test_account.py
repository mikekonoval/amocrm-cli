import respx
import httpx
import pytest
from amocrm.client import AmoCRMClient
from amocrm.resources.account import AccountResource

SAMPLE_ACCOUNT = {"id": 123456, "name": "My Company", "subdomain": "mycompany"}


@pytest.fixture
def client():
    return AmoCRMClient(subdomain="testco", access_token="test-token")


@pytest.fixture
def resource(client):
    return AccountResource(client)


@respx.mock
def test_get_account(resource):
    respx.get("https://testco.amocrm.ru/api/v4/account").mock(
        return_value=httpx.Response(200, json=SAMPLE_ACCOUNT)
    )
    result = resource.get()
    assert result["id"] == 123456


@respx.mock
def test_get_account_with_params(resource):
    route = respx.get("https://testco.amocrm.ru/api/v4/account").mock(
        return_value=httpx.Response(200, json=SAMPLE_ACCOUNT)
    )
    resource.get(with_=["users_groups", "task_types"])
    assert "with=users_groups%2Ctask_types" in str(route.calls[0].request.url)
