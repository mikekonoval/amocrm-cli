from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from amocrm.commands.pipelines import app
from amocrm.exceptions import EntityNotFoundError

runner = CliRunner()
SAMPLE_PIPELINE = {"id": 100, "name": "Main Pipeline"}
SAMPLE_STAGE = {"id": 1000, "name": "New Lead"}

def test_list_pipelines():
    with patch("amocrm.commands.pipelines.PipelinesResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.list.return_value = [SAMPLE_PIPELINE]
        with patch("amocrm.commands.pipelines.AmoCRMClient"):
            result = runner.invoke(app, ["list", "--output", "json"])
    assert result.exit_code == 0

def test_get_pipeline():
    with patch("amocrm.commands.pipelines.PipelinesResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.return_value = SAMPLE_PIPELINE
        with patch("amocrm.commands.pipelines.AmoCRMClient"):
            result = runner.invoke(app, ["get", "100", "--output", "json"])
    assert result.exit_code == 0

def test_get_pipeline_not_found():
    with patch("amocrm.commands.pipelines.PipelinesResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.side_effect = EntityNotFoundError("/leads/pipelines/999")
        with patch("amocrm.commands.pipelines.AmoCRMClient"):
            result = runner.invoke(app, ["get", "999"])
    assert result.exit_code == 1

def test_stages_list():
    with patch("amocrm.commands.pipelines.StagesResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.list.return_value = [SAMPLE_STAGE]
        with patch("amocrm.commands.pipelines.AmoCRMClient"):
            result = runner.invoke(app, ["stages", "list", "100", "--output", "json"])
    assert result.exit_code == 0

def test_stages_get():
    with patch("amocrm.commands.pipelines.StagesResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.return_value = SAMPLE_STAGE
        with patch("amocrm.commands.pipelines.AmoCRMClient"):
            result = runner.invoke(app, ["stages", "get", "100", "1000", "--output", "json"])
    assert result.exit_code == 0

def test_create_pipeline():
    with patch("amocrm.commands.pipelines.PipelinesResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.create.return_value = [SAMPLE_PIPELINE]
        with patch("amocrm.commands.pipelines.AmoCRMClient"):
            result = runner.invoke(app, ["create", "--name", "New Pipeline", "--output", "json"])
    assert result.exit_code == 0
    call_args = mock_resource.create.call_args[0][0][0]
    assert call_args["name"] == "New Pipeline"
    assert "_embedded" in call_args  # required by AmoCRM API

def test_delete_pipeline():
    with patch("amocrm.commands.pipelines.PipelinesResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.delete.return_value = True
        with patch("amocrm.commands.pipelines.AmoCRMClient"):
            result = runner.invoke(app, ["delete", "100"])
    assert result.exit_code == 0

def test_delete_pipeline_not_found():
    with patch("amocrm.commands.pipelines.PipelinesResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.delete.side_effect = EntityNotFoundError("/leads/pipelines/999")
        with patch("amocrm.commands.pipelines.AmoCRMClient"):
            result = runner.invoke(app, ["delete", "999"])
    assert result.exit_code == 1

def test_stages_create():
    with patch("amocrm.commands.pipelines.StagesResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.create.return_value = [SAMPLE_STAGE]
        with patch("amocrm.commands.pipelines.AmoCRMClient"):
            result = runner.invoke(app, ["stages", "create", "100", "--name", "New Stage", "--output", "json"])
    assert result.exit_code == 0
    call_args = mock_resource.create.call_args[0][0][0]
    assert call_args["name"] == "New Stage"

def test_stages_update():
    with patch("amocrm.commands.pipelines.StagesResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.update.return_value = SAMPLE_STAGE
        with patch("amocrm.commands.pipelines.AmoCRMClient"):
            result = runner.invoke(app, ["stages", "update", "100", "1000", "--name", "Renamed", "--output", "json"])
    assert result.exit_code == 0
    mock_resource.update.assert_called_once_with(1000, {"name": "Renamed"})

def test_stages_delete():
    with patch("amocrm.commands.pipelines.StagesResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.delete.return_value = True
        with patch("amocrm.commands.pipelines.AmoCRMClient"):
            result = runner.invoke(app, ["stages", "delete", "100", "1000"])
    assert result.exit_code == 0
