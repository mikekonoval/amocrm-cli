from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from amocrm.commands.files import app

runner = CliRunner()
SAMPLE_FILE = {"uuid": "abc-123", "name": "photo.jpg", "size": 102400}


def test_list_files() -> None:
    with patch("amocrm.commands.files.FilesResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.list.return_value = [SAMPLE_FILE]
        with patch("amocrm.commands.files.AmoCRMClient"):
            result = runner.invoke(app, ["list", "--output", "json"])
    assert result.exit_code == 0


def test_get_file() -> None:
    with patch("amocrm.commands.files.FilesResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.return_value = SAMPLE_FILE
        with patch("amocrm.commands.files.AmoCRMClient"):
            result = runner.invoke(app, ["get", "abc-123", "--output", "json"])
    assert result.exit_code == 0
    mock_resource.get.assert_called_once_with("abc-123")


def test_upload_file(tmp_path: Path) -> None:
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello")
    with patch("amocrm.commands.files.FilesResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.upload.return_value = SAMPLE_FILE
        with patch("amocrm.commands.files.AmoCRMClient"):
            result = runner.invoke(app, ["upload", str(test_file), "--output", "json"])
    assert result.exit_code == 0
    mock_resource.upload.assert_called_once_with(str(test_file))


def test_download_file(tmp_path: Path) -> None:
    out_file = tmp_path / "photo.jpg"
    with patch("amocrm.commands.files.FilesResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.download.return_value = b"binary content"
        with patch("amocrm.commands.files.AmoCRMClient"):
            result = runner.invoke(app, ["download", "abc-123", "--output-path", str(out_file)])
    assert result.exit_code == 0
    assert out_file.read_bytes() == b"binary content"


def test_delete_file() -> None:
    with patch("amocrm.commands.files.FilesResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.delete.return_value = True
        with patch("amocrm.commands.files.AmoCRMClient"):
            result = runner.invoke(app, ["delete", "abc-123"])
    assert result.exit_code == 0
    assert "abc-123" in result.output
