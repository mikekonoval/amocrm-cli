# AmoCRM CLI — Chats (amojo) API Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `ChatsResource` for the AmoCRM Chats API (`amojo.amocrm.ru`), enabling creating chat channels, sending messages, and connecting conversations to leads/contacts, plus a `chats` CLI command group.

**Architecture:** The Chats API lives at `https://amojo.amocrm.ru` and uses HMAC-SHA256 request signing instead of Bearer token auth. `ChatsResource` makes httpx calls directly (like `oauth.py`), signing each request with the integration's secret key. The `account_chat_id` needed for scoping requests is obtained from the main AmoCRM API (`GET /api/v4/account?with=amojo_id`). No changes to `AmoCRMClient` are required.

**Tech Stack:** Python 3.11+, Typer, httpx (sync), hashlib (HMAC-SHA256), pytest, respx

---

## Reading Before You Start

Read these files before touching code:
- `amocrm/auth/oauth.py` — pattern for direct httpx calls outside AmoCRMClient
- `amocrm/resources/base.py` — do NOT subclass BaseResource (different domain, different auth)
- `amocrm/commands/leads.py` — canonical command pattern
- `amocrm/client.py` — note that `_client_id`, `_client_secret` are accessible on the client
- `amocrm/app.py` — where to register the new `chats` command group
- AmoCRM API docs context: amojo.amocrm.ru uses HMAC-SHA256 with `Content-Type`, `Date`, `Content-MD5`, and `Request-Body-Hash` headers

---

## Background: amojo Authentication

The amojo API uses HMAC-SHA256 signatures. Each request is signed with the integration's client secret. The signature covers the HTTP method, Content-MD5, Content-Type, Date, and request path.

**Required headers on every request:**
```
Date: <RFC2822 date>
Content-Type: application/json
Content-MD5: <md5(body_bytes).hexdigest()>
X-Signature: <hmac-sha256(signing_string, client_secret)>
```
Where `signing_string = "\n".join([method, content_md5, content_type, date, path])`.

**Getting `account_chat_id`:** Call the main AmoCRM API:
```
GET /api/v4/account?with=amojo_id
```
Response includes `amojo_id` field — this is the `account_chat_id` used in all amojo paths.

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `amocrm/resources/chats.py` | Create | `ChatsResource` — amojo API HMAC signing + chat operations |
| `amocrm/commands/chats.py` | Create | Typer CLI: `chats connect`, `chats send`, `chats list`, `chats get` |
| `amocrm/resources/__init__.py` | Modify | Export `ChatsResource` |
| `amocrm/__init__.py` | Modify | Export `ChatsResource` |
| `amocrm/app.py` | Modify | Register `chats` command group |
| `tests/test_resources/test_chats.py` | Create | Resource tests with respx |
| `tests/test_commands/test_chats.py` | Create | Command tests with typer CliRunner |

---

## Task 1: `ChatsResource` — HMAC-signed amojo client

**Files:**
- Create: `amocrm/resources/chats.py`
- Test: `tests/test_resources/test_chats.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_resources/test_chats.py
from __future__ import annotations

from unittest.mock import MagicMock

import httpx
import pytest
import respx

from amocrm.resources.chats import ChatsResource

AMOJO_BASE = "https://amojo.amocrm.ru"
ACCOUNT_CHAT_ID = "test-account-chat-id"

SAMPLE_CHAT = {
    "id": "chat-uuid-1",
    "source_uid": "ext-chat-001",
    "created_at": 1700000000,
}

SAMPLE_MESSAGE = {
    "msgid": "msg-uuid-1",
    "conversation_id": "chat-uuid-1",
    "created_at": 1700000000,
    "body": {"type": "text", "text": "Hello!"},
}


@pytest.fixture
def mock_client() -> MagicMock:
    client = MagicMock()
    client._access_token = "test-token"
    client._client_secret = "test-secret"
    return client


@respx.mock
def test_connect_chat(mock_client: MagicMock) -> None:
    url = f"{AMOJO_BASE}/api/v2/origin/custom/{ACCOUNT_CHAT_ID}/connect"
    respx.post(url).mock(return_value=httpx.Response(200, json={
        "account_id": ACCOUNT_CHAT_ID,
        "title": "My Chat",
        "hook_api_version": "v2",
    }))
    resource = ChatsResource(mock_client)
    result = resource.connect(
        account_chat_id=ACCOUNT_CHAT_ID,
        title="My Chat",
        hook_url="https://example.com/hook",
    )
    assert result["account_id"] == ACCOUNT_CHAT_ID


@respx.mock
def test_send_message(mock_client: MagicMock) -> None:
    chat_id = "chat-uuid-1"
    url = f"{AMOJO_BASE}/api/v2/origin/custom/{ACCOUNT_CHAT_ID}/chats/{chat_id}/messages"
    respx.post(url).mock(return_value=httpx.Response(200, json=SAMPLE_MESSAGE))
    resource = ChatsResource(mock_client)
    result = resource.send_message(
        account_chat_id=ACCOUNT_CHAT_ID,
        chat_id=chat_id,
        text="Hello!",
        sender_id="user-1",
        sender_name="Alice",
    )
    assert result["msgid"] == "msg-uuid-1"


@respx.mock
def test_create_chat(mock_client: MagicMock) -> None:
    url = f"{AMOJO_BASE}/api/v2/origin/custom/{ACCOUNT_CHAT_ID}/chats"
    respx.post(url).mock(return_value=httpx.Response(200, json=SAMPLE_CHAT))
    resource = ChatsResource(mock_client)
    result = resource.create_chat(
        account_chat_id=ACCOUNT_CHAT_ID,
        source_uid="ext-chat-001",
        contact_id=42,
    )
    assert result["id"] == "chat-uuid-1"
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/test_resources/test_chats.py -v
```
Expected: ImportError (module not found)

- [ ] **Step 3: Implement `ChatsResource`**

```python
# amocrm/resources/chats.py
"""AmoCRM Chats API resource — amojo.amocrm.ru.

Authentication uses HMAC-SHA256 request signing with the integration's client_secret.
The account_chat_id is obtained from GET /api/v4/account?with=amojo_id on the main API.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone
from email.utils import formatdate
from typing import TYPE_CHECKING, Any

import httpx

from amocrm.exceptions import AmoCRMAPIError

if TYPE_CHECKING:
    from amocrm.client import AmoCRMClient

__all__ = ["ChatsResource"]

_AMOJO_BASE = "https://amojo.amocrm.ru"


class ChatsResource:
    """Wraps the AmoCRM Chats API (amojo.amocrm.ru).

    Uses HMAC-SHA256 request signing. Each API call requires:
    - account_chat_id: the amojo_id from GET /api/v4/account?with=amojo_id
    - client._client_secret: integration's secret key for signing
    """

    def __init__(self, client: AmoCRMClient) -> None:
        self.client = client

    def _sign_request(
        self,
        method: str,
        path: str,
        body_bytes: bytes,
        content_type: str = "application/json",
    ) -> dict[str, str]:
        """Build HMAC-SHA256 signed headers for an amojo request."""
        date = formatdate(usegmt=True)
        content_md5 = hashlib.md5(body_bytes).hexdigest()

        signing_string = "\n".join([method.upper(), content_md5, content_type, date, path])
        secret = str(self.client._client_secret or "")
        signature = hmac.new(
            secret.encode("utf-8"),
            signing_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        return {
            "Date": date,
            "Content-Type": content_type,
            "Content-MD5": content_md5,
            "X-Signature": signature,
        }

    def _post(self, path: str, data: dict[str, Any]) -> dict[str, Any]:
        if not self.client._client_secret:
            raise AmoCRMAPIError(
                0,
                "Config Error",
                "client_secret is required for the Chats API. Use OAuth login: amocrm auth login --oauth",
            )
        body_bytes = json.dumps(data).encode("utf-8")
        headers = self._sign_request("POST", path, body_bytes)
        response = httpx.post(
            f"{_AMOJO_BASE}{path}",
            content=body_bytes,
            headers=headers,
        )
        if response.status_code >= 400:
            raise AmoCRMAPIError(response.status_code, "Chats API Error", response.text)
        result: dict[str, Any] = response.json()
        return result

    def connect(
        self,
        account_chat_id: str,
        title: str,
        hook_url: str,
    ) -> dict[str, Any]:
        """Connect (register) a new chat origin for this account."""
        path = f"/api/v2/origin/custom/{account_chat_id}/connect"
        return self._post(path, {"title": title, "hook_api_version": "v2", "hook_api_url": hook_url})

    def disconnect(self, account_chat_id: str) -> dict[str, Any]:
        """Disconnect the chat origin."""
        path = f"/api/v2/origin/custom/{account_chat_id}/disconnect"
        return self._post(path, {})

    def create_chat(
        self,
        account_chat_id: str,
        source_uid: str,
        contact_id: int | None = None,
    ) -> dict[str, Any]:
        """Create a new chat conversation and optionally link it to a contact."""
        path = f"/api/v2/origin/custom/{account_chat_id}/chats"
        data: dict[str, Any] = {"source_uid": source_uid}
        if contact_id is not None:
            data["contact_id"] = contact_id
        return self._post(path, data)

    def send_message(
        self,
        account_chat_id: str,
        chat_id: str,
        text: str,
        sender_id: str,
        sender_name: str,
    ) -> dict[str, Any]:
        """Send a text message in a chat conversation."""
        path = f"/api/v2/origin/custom/{account_chat_id}/chats/{chat_id}/messages"
        data = {
            "sender": {"id": sender_id, "name": sender_name},
            "msgid": f"{sender_id}-{int(datetime.now(timezone.utc).timestamp())}",
            "conversation_id": chat_id,
            "created_at": int(datetime.now(timezone.utc).timestamp()),
            "body": {"type": "text", "text": text},
        }
        return self._post(path, data)
```

- [ ] **Step 4: Run tests to verify they pass**

```
pytest tests/test_resources/test_chats.py -v
```
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add amocrm/resources/chats.py tests/test_resources/test_chats.py
git commit -m "feat: add ChatsResource for amojo.amocrm.ru with HMAC signing"
```

---

## Task 2: `chats` CLI commands

**Files:**
- Create: `amocrm/commands/chats.py`
- Test: `tests/test_commands/test_chats.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_commands/test_chats.py
from __future__ import annotations

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from amocrm.commands.chats import app

runner = CliRunner()

ACCOUNT_CHAT_ID = "test-account-chat-id"
SAMPLE_CHAT = {"id": "chat-uuid-1", "source_uid": "ext-001"}
SAMPLE_MESSAGE = {"msgid": "msg-1", "conversation_id": "chat-uuid-1"}


def test_connect() -> None:
    with patch("amocrm.commands.chats.ChatsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.connect.return_value = {"account_id": ACCOUNT_CHAT_ID}
        with patch("amocrm.commands.chats.AmoCRMClient"):
            result = runner.invoke(app, [
                "connect",
                ACCOUNT_CHAT_ID,
                "--title", "My Bot",
                "--hook-url", "https://example.com/hook",
                "--output", "json",
            ])
    assert result.exit_code == 0
    mock_resource.connect.assert_called_once_with(
        account_chat_id=ACCOUNT_CHAT_ID,
        title="My Bot",
        hook_url="https://example.com/hook",
    )


def test_send() -> None:
    with patch("amocrm.commands.chats.ChatsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.send_message.return_value = SAMPLE_MESSAGE
        with patch("amocrm.commands.chats.AmoCRMClient"):
            result = runner.invoke(app, [
                "send",
                ACCOUNT_CHAT_ID,
                "chat-uuid-1",
                "--text", "Hello!",
                "--sender-id", "user-1",
                "--sender-name", "Alice",
                "--output", "json",
            ])
    assert result.exit_code == 0
    mock_resource.send_message.assert_called_once_with(
        account_chat_id=ACCOUNT_CHAT_ID,
        chat_id="chat-uuid-1",
        text="Hello!",
        sender_id="user-1",
        sender_name="Alice",
    )


def test_create_chat() -> None:
    with patch("amocrm.commands.chats.ChatsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.create_chat.return_value = SAMPLE_CHAT
        with patch("amocrm.commands.chats.AmoCRMClient"):
            result = runner.invoke(app, [
                "create",
                ACCOUNT_CHAT_ID,
                "--source-uid", "ext-001",
                "--output", "json",
            ])
    assert result.exit_code == 0


def test_disconnect() -> None:
    with patch("amocrm.commands.chats.ChatsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.disconnect.return_value = {}
        with patch("amocrm.commands.chats.AmoCRMClient"):
            result = runner.invoke(app, ["disconnect", ACCOUNT_CHAT_ID])
    assert result.exit_code == 0
    mock_resource.disconnect.assert_called_once_with(account_chat_id=ACCOUNT_CHAT_ID)
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/test_commands/test_chats.py -v
```
Expected: ImportError (module not found)

- [ ] **Step 3: Implement `chats` CLI commands**

```python
# amocrm/commands/chats.py
"""CLI commands for the AmoCRM Chats (amojo) API."""
from __future__ import annotations

from typing import Optional

import typer

from amocrm.client import AmoCRMClient
from amocrm.commands.output import render
from amocrm.exceptions import AmoCRMAPIError
from amocrm.resources.chats import ChatsResource

app = typer.Typer(name="chats", help="Manage chats via amojo API")


@app.command("connect")
def connect(
    account_chat_id: str = typer.Argument(..., help="amojo_id from GET /api/v4/account?with=amojo_id"),
    title: str = typer.Option(..., "--title", help="Display name for this chat channel"),
    hook_url: str = typer.Option(..., "--hook-url", help="Webhook URL to receive incoming messages"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Connect (register) a chat channel with AmoCRM."""
    try:
        resource = ChatsResource(AmoCRMClient())
        result = resource.connect(account_chat_id=account_chat_id, title=title, hook_url=hook_url)
        render(result, output=output)
    except AmoCRMAPIError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("disconnect")
def disconnect(
    account_chat_id: str = typer.Argument(...),
) -> None:
    """Disconnect the chat channel."""
    try:
        resource = ChatsResource(AmoCRMClient())
        resource.disconnect(account_chat_id=account_chat_id)
        typer.echo(f"Chat channel {account_chat_id} disconnected.")
    except AmoCRMAPIError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("create")
def create_chat(
    account_chat_id: str = typer.Argument(...),
    source_uid: str = typer.Option(..., "--source-uid", help="Unique ID from your chat system"),
    contact_id: Optional[int] = typer.Option(None, "--contact-id", help="Link to AmoCRM contact"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Create a new chat conversation."""
    try:
        resource = ChatsResource(AmoCRMClient())
        result = resource.create_chat(
            account_chat_id=account_chat_id,
            source_uid=source_uid,
            contact_id=contact_id,
        )
        render(result, output=output)
    except AmoCRMAPIError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("send")
def send_message(
    account_chat_id: str = typer.Argument(...),
    chat_id: str = typer.Argument(...),
    text: str = typer.Option(..., "--text"),
    sender_id: str = typer.Option(..., "--sender-id"),
    sender_name: str = typer.Option(..., "--sender-name"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Send a message in a chat conversation."""
    try:
        resource = ChatsResource(AmoCRMClient())
        result = resource.send_message(
            account_chat_id=account_chat_id,
            chat_id=chat_id,
            text=text,
            sender_id=sender_id,
            sender_name=sender_name,
        )
        render(result, output=output)
    except AmoCRMAPIError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
```

- [ ] **Step 4: Run tests to verify they pass**

```
pytest tests/test_commands/test_chats.py -v
```
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add amocrm/commands/chats.py tests/test_commands/test_chats.py
git commit -m "feat: add chats CLI commands (connect/disconnect/create/send)"
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
from amocrm.commands.chats import app as chats_app
# ...
app.add_typer(chats_app, name="chats")
```

- [ ] **Step 2: Export from `amocrm/resources/__init__.py`**

Add the import and also add `"ChatsResource"` to the `__all__` list:
```python
from amocrm.resources.chats import ChatsResource
# and in __all__:
# "ChatsResource",
```

- [ ] **Step 3: Export from `amocrm/__init__.py`**

Add:
```python
from amocrm.resources.chats import ChatsResource
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
git commit -m "feat: register chats command group and exports"
```

---

## Notes for Implementation

**Getting `account_chat_id`:** Before using any Chats API endpoint, users must find their `account_chat_id`:
```
amocrm account get --with amojo_id
```
The `amojo_id` field in the response is the `account_chat_id`.

**Client secret requirement:** The `chats connect/send` commands require `--client-secret` to be available. In OAuth mode (logged in via `amocrm auth login --oauth`), the client secret is already stored in the config. In long-token mode, the Chats API cannot be used because HMAC signing requires the secret.

**If `client._client_secret` is `None`:** The `_sign_request` method will use an empty string as the secret, which will produce incorrect signatures. Add a guard at the start of any method that signs requests:
```python
if not self.client._client_secret:
    raise AmoCRMAPIError(0, "Config Error", "client_secret required for Chats API. Use OAuth login.")
```
