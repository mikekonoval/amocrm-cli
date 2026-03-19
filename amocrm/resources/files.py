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
        # Cannot call builtin list() here — method is also named "list".
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
