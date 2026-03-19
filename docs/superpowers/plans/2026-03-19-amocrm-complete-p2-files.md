# AmoCRM CLI — Files API Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `FilesResource` (upload/list/get/download/delete) using the AmoCRM Files API at `drive-b.amocrm.ru`, plus a `files` CLI command group.

**Architecture:** The Files API lives at a different domain (`https://drive-b.amocrm.ru/v1.0`) and uses the same Bearer token as the main API. Because `AmoCRMClient._request()` builds URLs from a fixed base, `FilesResource` makes its own `httpx` calls directly (the same pattern used by `amocrm/auth/oauth.py`). The resource reads the access token via `client._access_token`. No changes to `AmoCRMClient` are required.

**Tech Stack:** Python 3.11+, Typer, httpx (sync), pytest, respx (for resource tests)

---

## Reading Before You Start

Read these files before touching code:
- `amocrm/auth/oauth.py` — shows the pattern for making httpx calls outside the client
- `amocrm/resources/base.py` — do NOT subclass `BaseResource` for Files (different domain, different path structure)
- `amocrm/commands/leads.py` — canonical command pattern
- `amocrm/client.py` — confirms `_access_token` is a plain `str` attribute, safe to read
- `tests/test_resources/test_leads.py` — respx test pattern to learn from
- `amocrm/app.py` — where to register the new `files` command group

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `amocrm/resources/files.py` | Create | `FilesResource` — upload/list/get/download/delete via drive-b.amocrm.ru |
| `amocrm/commands/files.py` | Create | Typer CLI: `files upload`, `files list`, `files get`, `files download`, `files delete` |
| `amocrm/resources/__init__.py` | Modify | Export `FilesResource` |
| `amocrm/__init__.py` | Modify | Export `FilesResource` |
| `amocrm/app.py` | Modify | Register `files` command group |
| `tests/test_resources/test_files.py` | Create | Resource-level tests with respx |
| `tests/test_commands/test_files.py` | Create | Command-level tests with typer CliRunner |

---

## Task 1: `FilesResource` — core HTTP wrapper

**Files:**
- Create: `amocrm/resources/files.py`
- Test: `tests/test_resources/test_files.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_resources/test_files.py
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

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
    test_file.write_text("hello")
    respx.post(f"{DRIVE_BASE}/package").mock(
        return_value=httpx.Response(200, json={"_links": {}, "_embedded": {"files": [SAMPLE_FILE]}})
    )
    resource = FilesResource(mock_client)
    result = resource.upload(str(test_file))
    assert result["uuid"] == "abc-123"


@respx.mock
def test_download_file(mock_client: MagicMock) -> None:
    content = b"binary file content"
    respx.get(f"{DRIVE_BASE}/files/abc-123/download").mock(
        return_value=httpx.Response(200, content=content)
    )
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
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/test_resources/test_files.py -v
```
Expected: ImportError (module not found)

- [ ] **Step 3: Implement `FilesResource`**

```python
# amocrm/resources/files.py
"""AmoCRM Files API resource — drive-b.amocrm.ru."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, List

import httpx

from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError

if TYPE_CHECKING:
    from amocrm.client import AmoCRMClient

__all__ = ["FilesResource"]

_DRIVE_BASE = "https://drive-b.amocrm.ru/v1.0"


class FilesResource:
    """Wraps the AmoCRM Files API (drive-b.amocrm.ru).

    Uses the same Bearer token as the main API client.
    Makes httpx calls directly because the base domain is different.
    """

    def __init__(self, client: AmoCRMClient) -> None:
        self.client = client

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.client._access_token}"}

    def _raise_for_error(self, response: httpx.Response) -> None:
        if response.status_code >= 400:
            try:
                body = response.json()
                status = body.get("status", response.status_code)
                title = body.get("title", "Files API Error")
                detail = body.get("detail", "")
            except Exception:
                status = response.status_code
                title = "Files API Error"
                detail = response.text
            raise AmoCRMAPIError(int(status), str(title), str(detail))

    def list(self, page: int = 1, limit: int = 50) -> List[dict[str, Any]]:
        """List uploaded files."""
        params = {"page": page, "limit": limit}
        response = httpx.get(f"{_DRIVE_BASE}/files", headers=self._headers(), params=params)
        if response.status_code == 204:
            return []
        self._raise_for_error(response)
        data: dict[str, Any] = response.json()
        embedded = data.get("_embedded", {})
        # Note: cannot call builtin list() here — method is also named "list".
        # Use [*iterable] spread syntax instead.
        return [*embedded.get("files", [])]

    def get(self, uuid: str) -> dict[str, Any]:
        """Get file metadata by UUID."""
        response = httpx.get(f"{_DRIVE_BASE}/files/{uuid}", headers=self._headers())
        if response.status_code == 204:
            raise EntityNotFoundError(f"/files/{uuid}")
        self._raise_for_error(response)
        result: dict[str, Any] = response.json()
        return result

    def upload(self, file_path: str) -> dict[str, Any]:
        """Upload a file. Returns the created file metadata dict."""
        path = Path(file_path)
        with open(path, "rb") as f:
            files = {"file": (path.name, f)}
            response = httpx.post(f"{_DRIVE_BASE}/package", headers=self._headers(), files=files)
        self._raise_for_error(response)
        data: dict[str, Any] = response.json()
        embedded = data.get("_embedded", {})
        items: list[dict[str, Any]] = embedded.get("files", [])
        return items[0] if items else {}

    def download(self, uuid: str) -> bytes:
        """Download file content. Returns raw bytes."""
        response = httpx.get(f"{_DRIVE_BASE}/files/{uuid}/download", headers=self._headers())
        if response.status_code == 204:
            raise EntityNotFoundError(f"/files/{uuid}")
        self._raise_for_error(response)
        return response.content

    def delete(self, uuid: str) -> bool:
        """Delete a file by UUID."""
        response = httpx.delete(f"{_DRIVE_BASE}/files/{uuid}", headers=self._headers())
        if response.status_code == 204:
            return True
        self._raise_for_error(response)
        return True
```

- [ ] **Step 4: Run tests to verify they pass**

```
pytest tests/test_resources/test_files.py -v
```
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add amocrm/resources/files.py tests/test_resources/test_files.py
git commit -m "feat: add FilesResource for drive-b.amocrm.ru"
```

---

## Task 2: `files` CLI commands

**Files:**
- Create: `amocrm/commands/files.py`
- Test: `tests/test_commands/test_files.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_commands/test_files.py
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
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
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/test_commands/test_files.py -v
```
Expected: ImportError (module not found)

- [ ] **Step 3: Implement `files` CLI commands**

```python
# amocrm/commands/files.py
"""CLI commands for the AmoCRM Files API."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from amocrm.client import AmoCRMClient
from amocrm.commands.output import render
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError
from amocrm.resources.files import FilesResource

app = typer.Typer(name="files", help="Manage files in AmoCRM drive")


@app.command("list")
def list_files(
    page: int = typer.Option(1, "--page"),
    limit: int = typer.Option(50, "--limit"),
    output: str = typer.Option("table", "--output"),
    columns: Optional[str] = typer.Option(None, "--columns"),
) -> None:
    """List uploaded files."""
    try:
        resource = FilesResource(AmoCRMClient())
        results = resource.list(page=page, limit=limit)
        render(results, output=output, columns=columns.split(",") if columns else None)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("get")
def get_file(
    uuid: str = typer.Argument(...),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Get file metadata by UUID."""
    try:
        resource = FilesResource(AmoCRMClient())
        result = resource.get(uuid)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("upload")
def upload_file(
    file_path: str = typer.Argument(..., metavar="FILE"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Upload a file to AmoCRM drive."""
    try:
        resource = FilesResource(AmoCRMClient())
        result = resource.upload(file_path)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError, FileNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("download")
def download_file(
    uuid: str = typer.Argument(...),
    output_path: str = typer.Option(..., "--output-path", "-o", help="Path to save the file"),
) -> None:
    """Download a file by UUID."""
    try:
        resource = FilesResource(AmoCRMClient())
        content = resource.download(uuid)
        Path(output_path).write_bytes(content)
        typer.echo(f"File {uuid} saved to {output_path}")
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("delete")
def delete_file(
    uuid: str = typer.Argument(...),
) -> None:
    """Delete a file by UUID."""
    try:
        resource = FilesResource(AmoCRMClient())
        resource.delete(uuid)
        typer.echo(f"File {uuid} deleted.")
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
```

- [ ] **Step 4: Run tests to verify they pass**

```
pytest tests/test_commands/test_files.py -v
```
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add amocrm/commands/files.py tests/test_commands/test_files.py
git commit -m "feat: add files CLI commands (upload/list/get/download/delete)"
```

---

## Task 3: Register and export

**Files:**
- Modify: `amocrm/resources/__init__.py`
- Modify: `amocrm/__init__.py`
- Modify: `amocrm/app.py`

- [ ] **Step 1: Register in `app.py`**

Open `amocrm/app.py`. Add:
```python
from amocrm.commands.files import app as files_app
# ...
app.add_typer(files_app, name="files")
```

- [ ] **Step 2: Export from `amocrm/resources/__init__.py`**

Add to the imports and `__all__`:
```python
from amocrm.resources.files import FilesResource
```

- [ ] **Step 3: Export from `amocrm/__init__.py`**

Add:
```python
from amocrm.resources.files import FilesResource
```

- [ ] **Step 4: Run the full test suite**

```
pytest -q
ruff check .
mypy amocrm/
```
Expected: all tests pass, zero ruff errors, zero mypy errors

- [ ] **Step 5: Commit**

```bash
git add amocrm/app.py amocrm/resources/__init__.py amocrm/__init__.py
git commit -m "feat: register files command group and exports"
```
