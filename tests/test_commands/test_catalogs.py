from unittest import mock
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from amocrm.commands.catalogs import app
from amocrm.exceptions import EntityNotFoundError

runner = CliRunner()
SAMPLE_CATALOG = {"id": 1, "name": "Products"}
SAMPLE_ELEMENT = {"id": 10, "name": "Widget"}


def test_list_catalogs_command():
    with patch("amocrm.commands.catalogs.CatalogsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.list.return_value = [SAMPLE_CATALOG]
        with patch("amocrm.commands.catalogs.AmoCRMClient"):
            result = runner.invoke(app, ["list", "--output", "json"])
    assert result.exit_code == 0
    mock_resource.list.assert_called_once()


def test_get_catalog_command():
    with patch("amocrm.commands.catalogs.CatalogsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.return_value = SAMPLE_CATALOG
        with patch("amocrm.commands.catalogs.AmoCRMClient"):
            result = runner.invoke(app, ["get", "1", "--output", "json"])
    assert result.exit_code == 0


def test_get_catalog_not_found_exits_1():
    with patch("amocrm.commands.catalogs.CatalogsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.side_effect = EntityNotFoundError("/catalogs/999")
        with patch("amocrm.commands.catalogs.AmoCRMClient"):
            result = runner.invoke(app, ["get", "999"])
    assert result.exit_code == 1


def test_create_catalog_command():
    with patch("amocrm.commands.catalogs.CatalogsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.create.return_value = [SAMPLE_CATALOG]
        with patch("amocrm.commands.catalogs.AmoCRMClient"):
            result = runner.invoke(app, ["create", "--name", "Products", "--output", "json"])
    assert result.exit_code == 0
    mock_resource.create.assert_called_once()


def test_delete_catalog_command():
    with patch("amocrm.commands.catalogs.CatalogsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.delete.return_value = True
        with patch("amocrm.commands.catalogs.AmoCRMClient"):
            result = runner.invoke(app, ["delete", "1"])
    assert result.exit_code == 0


# Elements sub-command tests
def test_list_elements_command():
    with patch("amocrm.commands.catalogs.CatalogElementsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.list.return_value = [SAMPLE_ELEMENT]
        with patch("amocrm.commands.catalogs.AmoCRMClient"):
            result = runner.invoke(app, ["elements", "list", "1", "--output", "json"])
    assert result.exit_code == 0
    mock_cls.assert_called_once_with(mock.ANY, catalog_id=1)
    mock_resource.list.assert_called_once()


def test_get_element_command():
    with patch("amocrm.commands.catalogs.CatalogElementsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.return_value = SAMPLE_ELEMENT
        with patch("amocrm.commands.catalogs.AmoCRMClient"):
            result = runner.invoke(app, ["elements", "get", "1", "10", "--output", "json"])
    assert result.exit_code == 0
    mock_cls.assert_called_once_with(mock.ANY, catalog_id=1)
    mock_resource.get.assert_called_once_with(10)


def test_get_element_not_found_exits_1():
    with patch("amocrm.commands.catalogs.CatalogElementsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.side_effect = EntityNotFoundError("/catalogs/1/elements/999")
        with patch("amocrm.commands.catalogs.AmoCRMClient"):
            result = runner.invoke(app, ["elements", "get", "1", "999"])
    assert result.exit_code == 1


def test_create_element_command():
    with patch("amocrm.commands.catalogs.CatalogElementsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.create.return_value = [SAMPLE_ELEMENT]
        with patch("amocrm.commands.catalogs.AmoCRMClient"):
            result = runner.invoke(app, ["elements", "create", "1", "--name", "Widget", "--output", "json"])
    assert result.exit_code == 0
    mock_cls.assert_called_once_with(mock.ANY, catalog_id=1)
    mock_resource.create.assert_called_once()


def test_delete_element_command():
    with patch("amocrm.commands.catalogs.CatalogElementsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.delete.return_value = True
        with patch("amocrm.commands.catalogs.AmoCRMClient"):
            result = runner.invoke(app, ["elements", "delete", "1", "10"])
    assert result.exit_code == 0
    mock_cls.assert_called_once_with(mock.ANY, catalog_id=1)
    mock_resource.delete.assert_called_once_with(10)
