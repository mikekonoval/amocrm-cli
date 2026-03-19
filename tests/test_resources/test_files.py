from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import httpx
import pytest
import respx

from amocrm.resources.files import FilesResource

DRIVE_BASE = "https://drive-b.amocrm.ru/v1.0"

SAMPLE_FILE = {
    "uuid": "abc-123",
    "name": "photo.jpg",
    "size": 102400,
    "created_at": 1700000000,
}

SAMPLE_LIST_RESPONSE = {
    "_embedded": {
        "files": [SAMPLE_FILE],
    },
    "_links": {"self": {"href": f"{DRIVE_BASE}/files"}},
}


@pytest.fixture
def mock_client() -> MagicMock:
    client = MagicMock()
    client._access_token = "test-token"
    return client


@respx.mock
def test_list_files(mock_client: MagicMock) -> None:
    respx.get(f"{DRIVE_BASE}/files").mock(
        return_value=httpx.Response(200, json=SAMPLE_LIST_RESPONSE)
    )
    resource = FilesResource(mock_client)
    result = resource.list()
    assert len(result) == 1
    assert result[0]["uuid"] == "abc-123"


@respx.mock
def test_list_files_empty(mock_client: MagicMock) -> None:
    respx.get(f"{DRIVE_BASE}/files").mock(
        return_value=httpx.Response(204)
    )
    resource = FilesResource(mock_client)
    result = resource.list()
    assert result == []


@respx.mock
def test_get_file(mock_client: MagicMock) -> None:
    respx.get(f"{DRIVE_BASE}/files/abc-123").mock(
        return_value=httpx.Response(200, json=SAMPLE_FILE)
    )
    resource = FilesResource(mock_client)
    result = resource.get("abc-123")
    assert result["name"] == "photo.jpg"


@respx.mock
def test_upload_file(mock_client: MagicMock, tmp_path: Path) -> None:
    test_file = tmp_path / "test.txt"
    test_file.write_bytes(b"hello")
    upload_url = "https://drive-a.amocrm.ru/upload/session-jwt-token"
    respx.post(f"{DRIVE_BASE}/sessions").mock(
        return_value=httpx.Response(200, json={
            "session_id": 123,
            "upload_url": upload_url,
            "max_part_size": 524288,
            "max_file_size": 314572800,
        })
    )
    respx.post(upload_url).mock(
        return_value=httpx.Response(200, json=SAMPLE_FILE)
    )
    resource = FilesResource(mock_client)
    result = resource.upload(str(test_file))
    assert result["uuid"] == "abc-123"


@respx.mock
def test_download_file(mock_client: MagicMock) -> None:
    content = b"binary file content"
    download_url = "https://drive-a.amocrm.ru/download/acct-hash/abc-123/photo.jpg"
    file_with_links = {**SAMPLE_FILE, "_links": {"download": {"href": download_url}}}
    respx.get(f"{DRIVE_BASE}/files/abc-123").mock(
        return_value=httpx.Response(200, json=file_with_links)
    )
    respx.get(download_url).mock(return_value=httpx.Response(200, content=content))
    resource = FilesResource(mock_client)
    result = resource.download("abc-123")
    assert result == content


@respx.mock
def test_delete_file(mock_client: MagicMock) -> None:
    respx.delete(f"{DRIVE_BASE}/files/abc-123").mock(
        return_value=httpx.Response(204)
    )
    resource = FilesResource(mock_client)
    result = resource.delete("abc-123")
    assert result is True
