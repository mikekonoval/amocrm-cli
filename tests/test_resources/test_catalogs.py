import respx
import httpx
import pytest
from amocrm.client import AmoCRMClient
from amocrm.resources.catalogs import CatalogsResource, CatalogElementsResource
from amocrm.exceptions import EntityNotFoundError

SAMPLE_CATALOG = {"id": 1, "name": "Products"}
SAMPLE_ELEMENT = {"id": 10, "name": "Widget"}


@pytest.fixture
def client():
    return AmoCRMClient(subdomain="testco", access_token="test-token")


@pytest.fixture
def catalogs_resource(client):
    return CatalogsResource(client)


@pytest.fixture
def elements_resource(client):
    return CatalogElementsResource(client, catalog_id=1)


# Catalog tests
@respx.mock
def test_catalogs_path_is_correct(catalogs_resource):
    assert catalogs_resource.path == "/catalogs"


@respx.mock
def test_catalogs_embedded_key_is_correct(catalogs_resource):
    assert catalogs_resource.embedded_key == "catalogs"


@respx.mock
def test_list_catalogs(catalogs_resource):
    respx.get("https://testco.amocrm.ru/api/v4/catalogs").mock(
        return_value=httpx.Response(200, json={"_embedded": {"catalogs": [SAMPLE_CATALOG]}})
    )
    result = catalogs_resource.list()
    assert result == [SAMPLE_CATALOG]


@respx.mock
def test_get_catalog(catalogs_resource):
    respx.get("https://testco.amocrm.ru/api/v4/catalogs/1").mock(
        return_value=httpx.Response(200, json=SAMPLE_CATALOG)
    )
    result = catalogs_resource.get(1)
    assert result["id"] == 1
    assert result["name"] == "Products"


@respx.mock
def test_get_catalog_not_found(catalogs_resource):
    respx.get("https://testco.amocrm.ru/api/v4/catalogs/999").mock(
        return_value=httpx.Response(204)
    )
    with pytest.raises(EntityNotFoundError):
        catalogs_resource.get(999)


@respx.mock
def test_create_catalogs(catalogs_resource):
    respx.post("https://testco.amocrm.ru/api/v4/catalogs").mock(
        return_value=httpx.Response(200, json={"_embedded": {"catalogs": [SAMPLE_CATALOG]}})
    )
    result = catalogs_resource.create([{"name": "Products"}])
    assert result == [SAMPLE_CATALOG]


@respx.mock
def test_delete_catalog(catalogs_resource):
    respx.delete("https://testco.amocrm.ru/api/v4/catalogs/1").mock(
        return_value=httpx.Response(204)
    )
    assert catalogs_resource.delete(1) is True


# CatalogElements tests
@respx.mock
def test_elements_path_is_correct(elements_resource):
    assert elements_resource.path == "/catalogs/1/elements"


@respx.mock
def test_elements_embedded_key_is_correct(elements_resource):
    assert elements_resource.embedded_key == "elements"


@respx.mock
def test_list_elements(elements_resource):
    respx.get("https://testco.amocrm.ru/api/v4/catalogs/1/elements").mock(
        return_value=httpx.Response(200, json={"_embedded": {"elements": [SAMPLE_ELEMENT]}})
    )
    result = elements_resource.list()
    assert result == [SAMPLE_ELEMENT]


@respx.mock
def test_get_element(elements_resource):
    respx.get("https://testco.amocrm.ru/api/v4/catalogs/1/elements/10").mock(
        return_value=httpx.Response(200, json=SAMPLE_ELEMENT)
    )
    result = elements_resource.get(10)
    assert result["id"] == 10
    assert result["name"] == "Widget"


@respx.mock
def test_get_element_not_found(elements_resource):
    respx.get("https://testco.amocrm.ru/api/v4/catalogs/1/elements/999").mock(
        return_value=httpx.Response(204)
    )
    with pytest.raises(EntityNotFoundError):
        elements_resource.get(999)


@respx.mock
def test_create_elements(elements_resource):
    respx.post("https://testco.amocrm.ru/api/v4/catalogs/1/elements").mock(
        return_value=httpx.Response(200, json={"_embedded": {"elements": [SAMPLE_ELEMENT]}})
    )
    result = elements_resource.create([{"name": "Widget"}])
    assert result == [SAMPLE_ELEMENT]


@respx.mock
def test_delete_element(elements_resource):
    respx.delete("https://testco.amocrm.ru/api/v4/catalogs/1/elements/10").mock(
        return_value=httpx.Response(204)
    )
    assert elements_resource.delete(10) is True
