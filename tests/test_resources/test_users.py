import respx
import httpx
import pytest
from amocrm.client import AmoCRMClient
from amocrm.resources.users import UsersResource, RolesResource
from amocrm.exceptions import EntityNotFoundError

SAMPLE_USER = {"id": 1, "name": "John", "email": "john@example.com"}
SAMPLE_ROLE = {"id": 1, "name": "Admin"}

@pytest.fixture
def client():
    return AmoCRMClient(subdomain="testco", access_token="test-token")

@pytest.fixture
def users_resource(client):
    return UsersResource(client)

@pytest.fixture
def roles_resource(client):
    return RolesResource(client)

# UsersResource Tests
@respx.mock
def test_users_list_returns_users(users_resource):
    respx.get("https://testco.amocrm.ru/api/v4/users").mock(
        return_value=httpx.Response(200, json={"_embedded": {"users": [SAMPLE_USER]}})
    )
    result = users_resource.list()
    assert result == [SAMPLE_USER]

@respx.mock
def test_users_get_returns_user(users_resource):
    respx.get("https://testco.amocrm.ru/api/v4/users/1").mock(
        return_value=httpx.Response(200, json=SAMPLE_USER)
    )
    result = users_resource.get(1)
    assert result["id"] == 1

@respx.mock
def test_users_get_204_raises_not_found(users_resource):
    respx.get("https://testco.amocrm.ru/api/v4/users/999").mock(
        return_value=httpx.Response(204)
    )
    with pytest.raises(EntityNotFoundError):
        users_resource.get(999)

@respx.mock
def test_users_create_returns_users(users_resource):
    respx.post("https://testco.amocrm.ru/api/v4/users").mock(
        return_value=httpx.Response(200, json={"_embedded": {"users": [SAMPLE_USER]}})
    )
    result = users_resource.create([{"name": "John"}])
    assert result == [SAMPLE_USER]

@respx.mock
def test_users_delete_returns_true(users_resource):
    respx.delete("https://testco.amocrm.ru/api/v4/users/1").mock(
        return_value=httpx.Response(204)
    )
    assert users_resource.delete(1) is True

# RolesResource Tests
@respx.mock
def test_roles_list_returns_roles(roles_resource):
    respx.get("https://testco.amocrm.ru/api/v4/roles").mock(
        return_value=httpx.Response(200, json={"_embedded": {"roles": [SAMPLE_ROLE]}})
    )
    result = roles_resource.list()
    assert result == [SAMPLE_ROLE]

@respx.mock
def test_roles_get_returns_role(roles_resource):
    respx.get("https://testco.amocrm.ru/api/v4/roles/1").mock(
        return_value=httpx.Response(200, json=SAMPLE_ROLE)
    )
    result = roles_resource.get(1)
    assert result["id"] == 1

@respx.mock
def test_roles_get_204_raises_not_found(roles_resource):
    respx.get("https://testco.amocrm.ru/api/v4/roles/999").mock(
        return_value=httpx.Response(204)
    )
    with pytest.raises(EntityNotFoundError):
        roles_resource.get(999)
