# AmoCRM CLI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python package that is both a CLI tool (`amocrm leads list`) and an importable library (`from amocrm import AmoCRMClient, LeadsResource`) for the AmoCRM API v4.

**Architecture:** Three strict layers — `resources/` (pure API, no CLI), `commands/` (CLI only, no HTTP), `client.py` (only place that touches httpx). Exceptions live in `exceptions.py`. Built in 5 waves of parallel agents, each wave completing before the next starts.

**Tech Stack:** Python 3.11+, Typer, httpx (sync), rich, pytest, respx

---

## File Map

| File | Responsibility | Wave |
|---|---|---|
| `pyproject.toml` | Package metadata, dependencies, entrypoint | 0 |
| `amocrm/exceptions.py` | `AmoCRMAPIError`, `EntityNotFoundError` | 0 |
| `amocrm/__init__.py` | Public exports (stub → filled Wave 5) | 0 → 5 |
| `amocrm/py.typed` | PEP 561 marker | 0 |
| `amocrm/app.py` | Typer root app (stub → filled Wave 5) | 0 → 5 |
| `amocrm/client.py` | httpx session, auth, retry, HAL unpacker | 0 (stub) → 1C |
| `amocrm/resources/base.py` | BaseResource CRUD mixin | 0 |
| `amocrm/auth/config.py` | Read/write `~/.amocrm/config.json` | 1A |
| `amocrm/auth/token.py` | Long-lived token storage, expiry check | 1A |
| `amocrm/auth/oauth.py` | Browser OAuth flow, local callback server | 1B |
| `amocrm/resources/leads.py` | LeadsResource + create_complex | 2A |
| `amocrm/commands/leads.py` | CLI: leads list/get/create/update/delete | 2A |
| `amocrm/resources/contacts.py` | ContactsResource | 2B |
| `amocrm/commands/contacts.py` | CLI: contacts commands | 2B |
| `amocrm/resources/companies.py` | CompaniesResource | 2C |
| `amocrm/commands/companies.py` | CLI: companies commands | 2C |
| `amocrm/resources/tasks.py` | TasksResource | 2D |
| `amocrm/commands/tasks.py` | CLI: tasks commands | 2D |
| `amocrm/resources/notes.py` | NotesResource (entity-scoped) | 2E |
| `amocrm/commands/notes.py` | CLI: notes commands | 2E |
| `amocrm/resources/pipelines.py` | PipelinesResource + StagesResource | 3A |
| `amocrm/commands/pipelines.py` | CLI: pipelines + stages commands | 3A |
| `amocrm/resources/users.py` | UsersResource + RolesResource | 3B |
| `amocrm/commands/users.py` | CLI: users + roles commands | 3B |
| `amocrm/resources/tags.py` | TagsResource (entity-scoped) | 3C |
| `amocrm/commands/tags.py` | CLI: tags commands | 3C |
| `amocrm/resources/custom_fields.py` | CustomFieldsResource + CustomFieldGroupsResource | 3D |
| `amocrm/commands/custom_fields.py` | CLI: custom-fields commands | 3D |
| `amocrm/resources/catalogs.py` | CatalogsResource + CatalogElementsResource | 4A |
| `amocrm/commands/catalogs.py` | CLI: catalogs commands | 4A |
| `amocrm/resources/events.py` | EventsResource (read-only, limit≤100) | 4B |
| `amocrm/commands/events.py` | CLI: events commands | 4B |
| `amocrm/resources/webhooks.py` | WebhooksResource (subscribe/unsubscribe) | 4C |
| `amocrm/commands/webhooks.py` | CLI: webhooks commands | 4C |
| `amocrm/resources/account.py` | AccountResource (single GET) | 4D |
| `amocrm/commands/account.py` | CLI: account commands | 4D |
| `amocrm/commands/output.py` | render() → table/json/csv | 0 |
| `amocrm/resources/__init__.py` | All resource exports | 5A |
| `skills/amocrm-cli.md` | Claude skill document | 5B |
| `CLAUDE.md` | Project guidance for agents | 0 |

---

## Task 0: Wave 0 — Scaffold

> **1 agent, sequential. All other waves depend on this.**

**Files:**
- Create: `pyproject.toml`
- Create: `amocrm/__init__.py`
- Create: `amocrm/py.typed`
- Create: `amocrm/app.py`
- Create: `amocrm/client.py` (typed stub)
- Create: `amocrm/exceptions.py`
- Create: `amocrm/resources/__init__.py` (placeholder)
- Create: `amocrm/resources/base.py` (full implementation)
- Create: `amocrm/commands/output.py` (full implementation)
- Create: `amocrm/auth/__init__.py`
- Create: `amocrm/commands/__init__.py`
- Create: `tests/conftest.py`
- Create: `CLAUDE.md`

---

- [ ] **Step 1: Create project layout**

```bash
mkdir -p amocrm/auth amocrm/resources amocrm/commands
mkdir -p tests/test_auth tests/test_resources tests/test_commands
mkdir -p skills docs/superpowers/plans docs/superpowers/specs
touch amocrm/__init__.py amocrm/py.typed
touch amocrm/auth/__init__.py amocrm/resources/__init__.py amocrm/commands/__init__.py
touch tests/__init__.py tests/test_auth/__init__.py tests/test_resources/__init__.py tests/test_commands/__init__.py
```

- [ ] **Step 2: Write `pyproject.toml`**

```toml
[project]
name = "amocrm-cli"
version = "0.1.0"
description = "AmoCRM API v4 — CLI tool and Python library"
requires-python = ">=3.11"
dependencies = [
    "typer>=0.12",
    "httpx>=0.27",
    "rich>=13",
]

[project.optional-dependencies]
dev = [
    "pytest>=8",
    "respx>=0.21",
    "mypy>=1.9",
    "ruff>=0.4",
]

[project.scripts]
amocrm = "amocrm.app:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100

[tool.mypy]
strict = true
```

- [ ] **Step 3: Install dev dependencies**

```bash
pip install -e ".[dev]"
```

Expected: installs without errors.

- [ ] **Step 4: Write `amocrm/exceptions.py`**

```python
class AmoCRMAPIError(Exception):
    def __init__(self, status: int, title: str, detail: str) -> None:
        self.status = status
        self.title = title
        self.detail = detail
        super().__init__(f"[{status}] {title}: {detail}")


class EntityNotFoundError(AmoCRMAPIError):
    """Raised when the API returns 204 on a GET or single-resource PATCH."""

    def __init__(self, path: str) -> None:
        super().__init__(404, "Not Found", f"Entity not found at {path}")
        self.path = path
```

- [ ] **Step 5: Write `amocrm/client.py` — typed stub**

This is a stub only — no implementation logic. Wave 1 Agent C fills it in. The stub locks the interface for all downstream agents.

```python
"""AmoCRM API client — synchronous httpx wrapper.

Construction modes:
    # Config-file mode (CLI): reads ~/.amocrm/config.json
    client = AmoCRMClient()

    # Kwargs mode (library): skips config file
    client = AmoCRMClient(subdomain="mycompany", access_token="xxx")
    client = AmoCRMClient(
        subdomain="mycompany",
        access_token="xxx",
        refresh_token="yyy",
        client_id="zzz",
        client_secret="aaa",
        expires_at=1234567890,  # None = refresh on 401 only
    )
"""
from __future__ import annotations

from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError

__all__ = ["AmoCRMClient"]


class AmoCRMClient:
    def __init__(
        self,
        subdomain: str | None = None,
        access_token: str | None = None,
        refresh_token: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        expires_at: int | None = None,
    ) -> None:
        """Initialize client from config file (no args) or from kwargs (library use)."""
        raise NotImplementedError

    def get(self, path: str, params: dict | None = None) -> dict | list:
        """GET request. Raises EntityNotFoundError on 204. Raises AmoCRMAPIError on errors."""
        raise NotImplementedError

    def post(self, path: str, json: list | dict | None = None) -> dict | list:
        """POST request. Returns parsed response body."""
        raise NotImplementedError

    def patch(self, path: str, json: list | dict | None = None) -> dict | list:
        """PATCH request.
        Single-resource path (ends with /{id}): 204 raises EntityNotFoundError.
        Batch path (no trailing ID): 204 returns [].
        """
        raise NotImplementedError

    def delete(self, path: str) -> bool:
        """DELETE request. Returns True on 204 success."""
        raise NotImplementedError
```

- [ ] **Step 6: Write `amocrm/resources/base.py` — full implementation**

```python
"""BaseResource: CRUD mixin for all AmoCRM resources."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amocrm.client import AmoCRMClient

__all__ = ["BaseResource"]


def _build_filter_params(filters: dict, prefix: str = "filter") -> dict:
    """Convert nested dict to bracket-notation query params.
    {"pipeline_id": [1,2]} → {"filter[pipeline_id][0]": 1, "filter[pipeline_id][1]": 2}
    {"created_at": {"from": 1700000}} → {"filter[created_at][from]": 1700000}
    """
    result: dict = {}
    for key, value in filters.items():
        if isinstance(value, list):
            for i, item in enumerate(value):
                result[f"{prefix}[{key}][{i}]"] = item
        elif isinstance(value, dict):
            for sub_key, sub_val in value.items():
                result[f"{prefix}[{key}][{sub_key}]"] = sub_val
        else:
            result[f"{prefix}[{key}]"] = value
    return result


def _build_order_params(order: str) -> dict:
    """Convert "field:direction" to {"order[field]": "direction"}.
    "created_at:asc" → {"order[created_at]": "asc"}
    """
    field, _, direction = order.partition(":")
    return {f"order[{field}]": direction or "asc"}


class BaseResource:
    path: str       # e.g. "/leads"
    embedded_key: str  # e.g. "leads"

    def __init__(self, client: AmoCRMClient) -> None:
        self.client = client

    def list(
        self,
        page: int = 1,
        limit: int = 50,
        filters: dict | None = None,
        order: str | None = None,
        with_: list[str] | None = None,
    ) -> list[dict]:
        params: dict = {"page": page, "limit": limit}
        if filters:
            params.update(_build_filter_params(filters))
        if order:
            params.update(_build_order_params(order))
        if with_:
            params["with"] = ",".join(with_)
        response = self.client.get(self.path, params=params)
        if isinstance(response, dict):
            embedded = response.get("_embedded", {})
            return embedded.get(self.embedded_key, [])
        return []

    def get(self, id: int, with_: list[str] | None = None) -> dict:
        params: dict = {}
        if with_:
            params["with"] = ",".join(with_)
        result = self.client.get(f"{self.path}/{id}", params=params or None)
        return result  # type: ignore[return-value]

    def create(self, items: list[dict]) -> list[dict]:
        response = self.client.post(self.path, json=items)
        if isinstance(response, dict):
            embedded = response.get("_embedded", {})
            return embedded.get(self.embedded_key, [])
        return []

    def update(self, id: int, data: dict) -> dict:
        result = self.client.patch(f"{self.path}/{id}", json=data)
        return result  # type: ignore[return-value]

    def update_batch(self, items: list[dict]) -> list[dict]:
        response = self.client.patch(self.path, json=items)
        if isinstance(response, list):
            return response
        if isinstance(response, dict):
            embedded = response.get("_embedded", {})
            return embedded.get(self.embedded_key, [])
        return []

    def delete(self, id: int) -> bool:
        return self.client.delete(f"{self.path}/{id}")
```

- [ ] **Step 7: Write tests for `base.py`**

Create `tests/test_resources/test_base.py`:

```python
import respx
import httpx
import pytest
from amocrm.client import AmoCRMClient
from amocrm.resources.base import BaseResource, _build_filter_params, _build_order_params
from amocrm.exceptions import EntityNotFoundError


class SampleResource(BaseResource):
    path = "/leads"
    embedded_key = "leads"


@pytest.fixture
def client():
    return AmoCRMClient(subdomain="test", access_token="test-token")


@pytest.fixture
def resource(client):
    return SampleResource(client)


def test_build_filter_params_list():
    result = _build_filter_params({"pipeline_id": [1, 2]})
    assert result == {"filter[pipeline_id][0]": 1, "filter[pipeline_id][1]": 2}


def test_build_filter_params_range():
    result = _build_filter_params({"created_at": {"from": 1700000, "to": 1800000}})
    assert result == {"filter[created_at][from]": 1700000, "filter[created_at][to]": 1800000}


def test_build_order_params():
    assert _build_order_params("created_at:asc") == {"order[created_at]": "asc"}
    assert _build_order_params("id:desc") == {"order[id]": "desc"}


@respx.mock
def test_list_returns_entities(resource):
    respx.get("https://test.amocrm.ru/api/v4/leads").mock(
        return_value=httpx.Response(200, json={
            "_embedded": {"leads": [{"id": 1, "name": "Deal"}]},
            "_page": 1,
        })
    )
    result = resource.list()
    assert result == [{"id": 1, "name": "Deal"}]


@respx.mock
def test_list_with_filters(resource):
    route = respx.get("https://test.amocrm.ru/api/v4/leads").mock(
        return_value=httpx.Response(200, json={"_embedded": {"leads": []}})
    )
    resource.list(filters={"pipeline_id": [5]})
    assert "filter%5Bpipeline_id%5D%5B0%5D=5" in str(route.calls[0].request.url)


@respx.mock
def test_get_returns_entity(resource):
    respx.get("https://test.amocrm.ru/api/v4/leads/123").mock(
        return_value=httpx.Response(200, json={"id": 123, "name": "Deal"})
    )
    result = resource.get(123)
    assert result["id"] == 123


@respx.mock
def test_delete_returns_true(resource):
    respx.delete("https://test.amocrm.ru/api/v4/leads/123").mock(
        return_value=httpx.Response(204)
    )
    assert resource.delete(123) is True
```

- [ ] **Step 8: Run base tests — expect failures (client not implemented)**

```bash
pytest tests/test_resources/test_base.py -v
```

Expected: FAIL — `NotImplementedError` from client stub. This is correct — TDD red phase.

- [ ] **Step 9: Write `amocrm/app.py` stub**

```python
"""AmoCRM CLI root application."""
import typer

app = typer.Typer(
    name="amocrm",
    help="AmoCRM API CLI tool",
    no_args_is_help=True,
)

# Command groups registered here by Wave 5 Agent A
# Example: app.add_typer(leads_app, name="leads")

if __name__ == "__main__":
    app()
```

- [ ] **Step 10: Write `amocrm/__init__.py` stub**

```python
"""AmoCRM CLI — Python library and CLI tool for AmoCRM API v4.

Library usage:
    from amocrm import AmoCRMClient, LeadsResource
    client = AmoCRMClient(subdomain="mycompany", access_token="xxx")
    leads = LeadsResource(client)
    results = leads.list(filters={"pipeline_id": [1]})
"""
from amocrm.client import AmoCRMClient
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError

# Resource classes added by Wave 5 Agent A after all resources are implemented
# from amocrm.resources import (LeadsResource, ContactsResource, ...)

__all__ = [
    "AmoCRMClient",
    "AmoCRMAPIError",
    "EntityNotFoundError",
]
```

- [ ] **Step 11: Write `amocrm/resources/__init__.py` placeholder**

```python
# Populated by Wave 5 Agent A after all resource classes are implemented.
# Each resource file exports one class: LeadsResource, ContactsResource, etc.
```

- [ ] **Step 12: Write `amocrm/commands/output.py`** (in Wave 0 so all Wave 2+ command agents can import it)

```python
"""Render data as table, json, or csv."""
from __future__ import annotations

import csv
import json
import sys

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def render(
    data: list[dict] | dict,
    output: str = "table",
    columns: list[str] | None = None,
) -> None:
    if isinstance(data, dict):
        data = [data]
    if not data:
        typer.echo("(no results)")
        return
    if output == "json":
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif output == "csv":
        cols = columns or list(data[0].keys())
        writer = csv.DictWriter(sys.stdout, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)
    else:  # table
        cols = columns or list(data[0].keys())
        table = Table(*cols)
        for row in data:
            table.add_row(*[str(row.get(c, "")) for c in cols])
        console.print(table)
```

- [ ] **Step 13: Write `tests/conftest.py`**

```python
"""Shared test fixtures. Add ONLY base fixtures here.
Resource-specific sample data belongs in each test file.
"""
import pytest
import typer.testing
from amocrm.client import AmoCRMClient


@pytest.fixture
def mock_config() -> dict:
    return {
        "subdomain": "testcompany",
        "auth_mode": "longtoken",
        "access_token": "test-access-token",
        "refresh_token": None,
        "expires_at": None,
        "client_id": None,
        "client_secret": None,
        "redirect_uri": "http://localhost:8080",
    }


@pytest.fixture
def mock_client() -> AmoCRMClient:
    return AmoCRMClient(subdomain="testcompany", access_token="test-access-token")


@pytest.fixture
def cli_runner() -> typer.testing.CliRunner:
    return typer.testing.CliRunner()
```

- [ ] **Step 14: Write `CLAUDE.md`**

```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Python package for the AmoCRM API v4. Works as both a **CLI tool** (`amocrm leads list`) and an **importable library** (`from amocrm import AmoCRMClient, LeadsResource`).

## Commands

```bash
pip install -e ".[dev]"          # install with dev dependencies
pytest                            # run all tests
pytest tests/test_resources/test_leads.py::test_leads_list  # single test
ruff check .                      # lint
mypy amocrm/                      # type check
```

## Architecture — Three Strict Layers

- `amocrm/resources/` — pure Python API functions. No CLI, no Typer. Each file has one `{Name}Resource` class subclassing `BaseResource`.
- `amocrm/commands/` — Typer CLI commands. Calls resource methods, formats output via `output.py`. No HTTP here.
- `amocrm/client.py` — the only file that uses httpx. Handles auth, retry, rate limiting, HAL response unpacking.
- `amocrm/exceptions.py` — `AmoCRMAPIError` and `EntityNotFoundError`. Import from here everywhere.

## TDD Workflow

For every new resource or command:
1. Write test in `tests/test_resources/test_{resource}.py` using `respx` — RED
2. Implement `amocrm/resources/{resource}.py` — GREEN
3. Write test in `tests/test_commands/test_{resource}.py` — RED
4. Implement `amocrm/commands/{resource}.py` — GREEN

## Adding a New Resource

1. Create `amocrm/resources/{name}.py`, class `{TitleCase}Resource(BaseResource)`, set `path` and `embedded_key`
2. Create `amocrm/commands/{name}.py`, create Typer app, call resource methods
3. Register command group in `amocrm/app.py`
4. Add class to `amocrm/resources/__init__.py` and `amocrm/__init__.py`
5. Write tests in `tests/test_resources/test_{name}.py` and `tests/test_commands/test_{name}.py`

## CLI Command Structure

Noun-verb: `amocrm <resource> <action>`

Global flags on list commands: `--page`, `--limit`, `--filter` (JSON string), `--order` (field:asc), `--with`, `--output table|json|csv`, `--columns`

## Library Usage

```python
from amocrm import AmoCRMClient, AmoCRMAPIError, EntityNotFoundError
from amocrm.resources import LeadsResource

# Minimal — no auto-refresh
client = AmoCRMClient(subdomain="mycompany", access_token="xxx")

# Full OAuth with refresh
client = AmoCRMClient(
    subdomain="mycompany", access_token="xxx", refresh_token="yyy",
    client_id="zzz", client_secret="aaa", expires_at=1234567890,
)

leads = LeadsResource(client)
results = leads.list(filters={"pipeline_id": [1]}, order="created_at:desc")
```

## API Gotchas

- 204 on GET = not found (`EntityNotFoundError`); 204 on DELETE = `True`; 204 on batch PATCH = `[]`
- Refresh tokens are single-use — save new pair immediately on every refresh
- Tags, notes, custom_fields are entity-scoped (constructor takes `entity_type`)
- All timestamps are Unix integers
- Pipelines stages path: `/leads/pipelines/{id}/statuses` (not `/stages/`)
```

- [ ] **Step 15: Commit Wave 0**

```bash
git init
git add .
git commit -m "feat: Wave 0 scaffold — exceptions, client stub, base resource, project structure"
```

---

## Task 1A: Wave 1 — Auth Config + Token

> **Parallel with 1B and 1C. No dependency on client implementation.**

**Files:**
- Create: `amocrm/auth/config.py`
- Create: `amocrm/auth/token.py`
- Create: `tests/test_auth/test_config.py`
- Create: `tests/test_auth/test_token.py`

---

- [ ] **Step 1: Write failing tests for `config.py`**

Create `tests/test_auth/test_config.py`:

```python
import json
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
from amocrm.auth.config import load_config, save_config, CONFIG_PATH


def test_load_config_reads_json(tmp_path):
    config_data = {
        "subdomain": "mycompany",
        "auth_mode": "longtoken",
        "access_token": "tok",
        "refresh_token": None,
        "expires_at": None,
        "client_id": None,
        "client_secret": None,
        "redirect_uri": "http://localhost:8080",
    }
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config_data))
    with patch("amocrm.auth.config.CONFIG_PATH", config_file):
        result = load_config()
    assert result["subdomain"] == "mycompany"
    assert result["auth_mode"] == "longtoken"


def test_load_config_raises_if_missing(tmp_path):
    with patch("amocrm.auth.config.CONFIG_PATH", tmp_path / "missing.json"):
        with pytest.raises(FileNotFoundError):
            load_config()


def test_load_config_raises_on_invalid_auth_mode(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"auth_mode": "invalid", "subdomain": "x", "access_token": "y"}))
    with patch("amocrm.auth.config.CONFIG_PATH", config_file):
        with pytest.raises(ValueError, match="auth_mode"):
            load_config()


def test_save_config_writes_json(tmp_path):
    config_file = tmp_path / "config.json"
    config = {"subdomain": "test", "auth_mode": "longtoken", "access_token": "tok"}
    with patch("amocrm.auth.config.CONFIG_PATH", config_file):
        save_config(config)
    assert json.loads(config_file.read_text())["subdomain"] == "test"
```

- [ ] **Step 2: Run — expect FAIL**

```bash
pytest tests/test_auth/test_config.py -v
```

Expected: `ModuleNotFoundError: amocrm.auth.config`

- [ ] **Step 3: Implement `amocrm/auth/config.py`**

```python
"""Read and write ~/.amocrm/config.json."""
from __future__ import annotations

import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".amocrm" / "config.json"
VALID_AUTH_MODES = {"longtoken", "oauth"}

_DEFAULTS: dict = {
    "refresh_token": None,
    "expires_at": None,
    "client_id": None,
    "client_secret": None,
    "redirect_uri": "http://localhost:8080",
}


def load_config() -> dict:
    """Load config from disk. Raises FileNotFoundError if missing, ValueError if invalid."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"No config found at {CONFIG_PATH}. Run: amocrm auth login"
        )
    data = json.loads(CONFIG_PATH.read_text())
    mode = data.get("auth_mode")
    if mode not in VALID_AUTH_MODES:
        raise ValueError(
            f"Invalid auth_mode {mode!r} in config. Must be one of: {VALID_AUTH_MODES}"
        )
    return {**_DEFAULTS, **data}


def save_config(config: dict) -> None:
    """Write config to disk. Creates parent directory if needed."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2))
```

- [ ] **Step 4: Run — expect PASS**

```bash
pytest tests/test_auth/test_config.py -v
```

Expected: all PASS

- [ ] **Step 5: Write failing tests for `token.py`**

Create `tests/test_auth/test_token.py`:

```python
import time
import pytest
from amocrm.auth.token import is_token_expiring, make_longtoken_config


def test_is_token_expiring_returns_true_within_300s():
    expires_at = int(time.time()) + 200  # expires in 200s
    assert is_token_expiring(expires_at) is True


def test_is_token_expiring_returns_false_with_time_remaining():
    expires_at = int(time.time()) + 600  # expires in 600s
    assert is_token_expiring(expires_at) is False


def test_is_token_expiring_returns_false_for_none():
    assert is_token_expiring(None) is False


def test_make_longtoken_config():
    config = make_longtoken_config(subdomain="myco", token="tok123")
    assert config["auth_mode"] == "longtoken"
    assert config["access_token"] == "tok123"
    assert config["subdomain"] == "myco"
    assert config["refresh_token"] is None
```

- [ ] **Step 6: Run — expect FAIL**

```bash
pytest tests/test_auth/test_token.py -v
```

Expected: `ModuleNotFoundError: amocrm.auth.token`

- [ ] **Step 7: Implement `amocrm/auth/token.py`**

```python
"""Long-lived token helpers."""
from __future__ import annotations

import time

REFRESH_THRESHOLD_SECONDS = 300


def is_token_expiring(expires_at: int | None) -> bool:
    """True if token expires within 300 seconds. False if None (long-lived token)."""
    if expires_at is None:
        return False
    return (expires_at - int(time.time())) < REFRESH_THRESHOLD_SECONDS


def make_longtoken_config(subdomain: str, token: str) -> dict:
    """Build a config dict for long-lived token auth mode."""
    return {
        "subdomain": subdomain,
        "auth_mode": "longtoken",
        "access_token": token,
        "refresh_token": None,
        "expires_at": None,
        "client_id": None,
        "client_secret": None,
        "redirect_uri": "http://localhost:8080",
    }
```

- [ ] **Step 8: Run — expect PASS**

```bash
pytest tests/test_auth/ -v
```

- [ ] **Step 9: Commit**

```bash
git add amocrm/auth/config.py amocrm/auth/token.py tests/test_auth/
git commit -m "feat: auth config and token helpers"
```

---

## Task 1B: Wave 1 — OAuth Flow

> **Parallel with 1A and 1C. Calls httpx directly — no AmoCRMClient dependency.**

**Files:**
- Create: `amocrm/auth/oauth.py`
- Create: `tests/test_auth/test_oauth.py`

---

- [ ] **Step 1: Write failing tests**

Create `tests/test_auth/test_oauth.py`:

```python
import time
import respx
import httpx
import pytest
from unittest.mock import patch, MagicMock
from amocrm.auth.oauth import exchange_code_for_tokens, build_auth_url, refresh_tokens


def test_build_auth_url():
    url = build_auth_url(client_id="abc123", state="xyz")
    assert "client_id=abc123" in url
    assert "state=xyz" in url
    assert url.startswith("https://www.amocrm.ru/oauth")


@respx.mock
def test_exchange_code_for_tokens():
    respx.post("https://myco.amocrm.ru/oauth2/access_token").mock(
        return_value=httpx.Response(200, json={
            "token_type": "Bearer",
            "expires_in": 86400,
            "access_token": "new-access",
            "refresh_token": "new-refresh",
        })
    )
    result = exchange_code_for_tokens(
        subdomain="myco",
        code="auth-code",
        client_id="cid",
        client_secret="csec",
        redirect_uri="http://localhost:8080",
    )
    assert result["access_token"] == "new-access"
    assert result["refresh_token"] == "new-refresh"
    assert "expires_at" in result


@respx.mock
def test_refresh_tokens():
    respx.post("https://myco.amocrm.ru/oauth2/access_token").mock(
        return_value=httpx.Response(200, json={
            "token_type": "Bearer",
            "expires_in": 86400,
            "access_token": "refreshed-access",
            "refresh_token": "refreshed-refresh",
        })
    )
    result = refresh_tokens(
        subdomain="myco",
        refresh_token="old-refresh",
        client_id="cid",
        client_secret="csec",
        redirect_uri="http://localhost:8080",
    )
    assert result["access_token"] == "refreshed-access"
    assert result["refresh_token"] == "refreshed-refresh"
```

- [ ] **Step 2: Run — expect FAIL**

```bash
pytest tests/test_auth/test_oauth.py -v
```

- [ ] **Step 3: Implement `amocrm/auth/oauth.py`**

```python
"""OAuth 2.0 flow for AmoCRM: browser redirect + token exchange."""
from __future__ import annotations

import time
import urllib.parse
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

import httpx

TOKEN_URL = "https://{subdomain}.amocrm.ru/oauth2/access_token"
AUTH_URL = "https://www.amocrm.ru/oauth"


def build_auth_url(client_id: str, state: str, mode: str = "popup") -> str:
    params = {"client_id": client_id, "state": state, "mode": mode}
    return f"{AUTH_URL}?{urllib.parse.urlencode(params)}"


def exchange_code_for_tokens(
    subdomain: str,
    code: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
) -> dict:
    """Exchange authorization code for access + refresh tokens."""
    url = TOKEN_URL.format(subdomain=subdomain)
    response = httpx.post(url, json={
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    })
    response.raise_for_status()
    data = response.json()
    return {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "expires_at": int(time.time()) + data["expires_in"],
    }


def refresh_tokens(
    subdomain: str,
    refresh_token: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
) -> dict:
    """Refresh an expired access token. Refresh token is single-use."""
    url = TOKEN_URL.format(subdomain=subdomain)
    response = httpx.post(url, json={
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "redirect_uri": redirect_uri,
    })
    response.raise_for_status()
    data = response.json()
    return {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "expires_at": int(time.time()) + data["expires_in"],
    }


def run_browser_flow(
    subdomain: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str = "http://localhost:8080",
) -> dict:
    """Open browser for OAuth consent, capture redirect, return token dict."""
    import secrets
    state = secrets.token_urlsafe(16)
    captured: dict = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            captured["code"] = params.get("code", [None])[0]
            captured["state"] = params.get("state", [None])[0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Auth complete. You can close this window.")

        def log_message(self, *args: object) -> None:
            pass  # suppress server logs

    port = int(urllib.parse.urlparse(redirect_uri).port or 8080)
    server = HTTPServer(("localhost", port), Handler)
    thread = threading.Thread(target=server.handle_request)
    thread.start()

    auth_url = build_auth_url(client_id=client_id, state=state)
    webbrowser.open(auth_url)
    thread.join(timeout=120)

    if captured.get("state") != state:
        raise ValueError("OAuth state mismatch — possible CSRF attack")
    if not captured.get("code"):
        raise ValueError("No authorization code received")

    tokens = exchange_code_for_tokens(
        subdomain=subdomain,
        code=captured["code"],
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
    )
    return tokens
```

- [ ] **Step 4: Run — expect PASS**

```bash
pytest tests/test_auth/test_oauth.py -v
```

- [ ] **Step 5: Commit**

```bash
git add amocrm/auth/oauth.py tests/test_auth/test_oauth.py
git commit -m "feat: OAuth 2.0 flow — browser redirect and token exchange"
```

---

## Task 1C: Wave 1 — API Client

> **Parallel with 1A and 1B. Implements the stub from Wave 0.**

**Files:**
- Modify: `amocrm/client.py` (replace stub with full implementation)
- Create: `tests/test_client.py`

---

- [ ] **Step 1: Write failing tests**

Create `tests/test_client.py`:

```python
import time
import respx
import httpx
import pytest
from unittest.mock import patch
from amocrm.client import AmoCRMClient
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError


@pytest.fixture
def client():
    return AmoCRMClient(subdomain="testco", access_token="tok")


@respx.mock
def test_get_returns_dict(client):
    respx.get("https://testco.amocrm.ru/api/v4/leads/1").mock(
        return_value=httpx.Response(200, json={"id": 1})
    )
    assert client.get("/leads/1") == {"id": 1}


@respx.mock
def test_get_204_raises_entity_not_found(client):
    respx.get("https://testco.amocrm.ru/api/v4/leads/999").mock(
        return_value=httpx.Response(204)
    )
    with pytest.raises(EntityNotFoundError):
        client.get("/leads/999")


@respx.mock
def test_delete_204_returns_true(client):
    respx.delete("https://testco.amocrm.ru/api/v4/leads/1").mock(
        return_value=httpx.Response(204)
    )
    assert client.delete("/leads/1") is True


@respx.mock
def test_patch_single_resource_204_raises_not_found(client):
    respx.patch("https://testco.amocrm.ru/api/v4/leads/1").mock(
        return_value=httpx.Response(204)
    )
    with pytest.raises(EntityNotFoundError):
        client.patch("/leads/1", json={"name": "x"})


@respx.mock
def test_patch_batch_204_returns_empty_list(client):
    respx.patch("https://testco.amocrm.ru/api/v4/leads").mock(
        return_value=httpx.Response(204)
    )
    result = client.patch("/leads", json=[{"id": 1, "name": "x"}])
    assert result == []


@respx.mock
def test_error_response_raises_api_error(client):
    respx.get("https://testco.amocrm.ru/api/v4/leads").mock(
        return_value=httpx.Response(
            400,
            json={"status": 400, "title": "Bad Request", "detail": "missing name"},
            headers={"content-type": "application/problem+json"},
        )
    )
    with pytest.raises(AmoCRMAPIError) as exc_info:
        client.get("/leads")
    assert exc_info.value.status == 400


@respx.mock
def test_429_retries(client):
    respx.get("https://testco.amocrm.ru/api/v4/leads").mock(
        side_effect=[
            httpx.Response(429),
            httpx.Response(200, json={"_embedded": {"leads": []}}),
        ]
    )
    with patch("time.sleep"):
        result = client.get("/leads")
    assert result is not None


def test_longtoken_mode_skips_refresh():
    client = AmoCRMClient(subdomain="testco", access_token="tok")
    # No refresh_token — should not attempt refresh
    with respx.mock:
        respx.get("https://testco.amocrm.ru/api/v4/account").mock(
            return_value=httpx.Response(200, json={"id": 1})
        )
        result = client.get("/account")
    assert result == {"id": 1}


def test_kwargs_with_expiring_token_refreshes():
    expires_soon = int(time.time()) + 100  # within 300s threshold
    client = AmoCRMClient(
        subdomain="testco",
        access_token="old-tok",
        refresh_token="ref-tok",
        client_id="cid",
        client_secret="csec",
        expires_at=expires_soon,
    )
    with respx.mock:
        respx.post("https://testco.amocrm.ru/oauth2/access_token").mock(
            return_value=httpx.Response(200, json={
                "access_token": "new-tok",
                "refresh_token": "new-ref",
                "expires_in": 86400,
            })
        )
        respx.get("https://testco.amocrm.ru/api/v4/account").mock(
            return_value=httpx.Response(200, json={"id": 1})
        )
        client.get("/account")
    assert client._access_token == "new-tok"


def test_kwargs_refresh_does_not_write_config(tmp_path):
    """After a refresh in kwargs mode, the config file must not be touched."""
    import json as _json
    from amocrm.auth.config import CONFIG_PATH
    # Write a sentinel config file and record its content before the request
    sentinel = {"subdomain": "other", "auth_mode": "longtoken", "access_token": "sentinel"}
    config_file = tmp_path / "config.json"
    config_file.write_text(_json.dumps(sentinel))

    expires_soon = int(time.time()) + 100
    client = AmoCRMClient(
        subdomain="testco",
        access_token="old-tok",
        refresh_token="ref-tok",
        client_id="cid",
        client_secret="csec",
        expires_at=expires_soon,
    )
    with respx.mock, patch("amocrm.auth.config.CONFIG_PATH", config_file):
        respx.post("https://testco.amocrm.ru/oauth2/access_token").mock(
            return_value=httpx.Response(200, json={
                "access_token": "new-tok",
                "refresh_token": "new-ref",
                "expires_in": 86400,
            })
        )
        respx.get("https://testco.amocrm.ru/api/v4/account").mock(
            return_value=httpx.Response(200, json={"id": 1})
        )
        client.get("/account")

    # Config file must be unchanged — kwargs mode never writes to disk
    assert _json.loads(config_file.read_text()) == sentinel


def test_kwargs_expires_at_none_refreshes_on_401():
    """When expires_at=None, no proactive refresh; refresh triggered by 401."""
    client = AmoCRMClient(
        subdomain="testco",
        access_token="old-tok",
        refresh_token="ref-tok",
        client_id="cid",
        client_secret="csec",
        expires_at=None,  # no known expiry
    )
    with respx.mock:
        # First call returns 401, triggering reactive refresh
        respx.post("https://testco.amocrm.ru/oauth2/access_token").mock(
            return_value=httpx.Response(200, json={
                "access_token": "new-tok",
                "refresh_token": "new-ref",
                "expires_in": 86400,
            })
        )
        route = respx.get("https://testco.amocrm.ru/api/v4/account").mock(
            side_effect=[
                httpx.Response(401),
                httpx.Response(200, json={"id": 1}),
            ]
        )
        result = client.get("/account")

    assert result == {"id": 1}
    assert client._access_token == "new-tok"
    assert len(route.calls) == 2  # first call got 401, second succeeded
```

- [ ] **Step 2: Run — expect FAIL**

```bash
pytest tests/test_client.py -v
```

Expected: FAIL — `NotImplementedError`

- [ ] **Step 3: Implement `amocrm/client.py`**

```python
"""AmoCRM API client — synchronous httpx wrapper."""
from __future__ import annotations

import random
import time
from typing import Any

import httpx

from amocrm.auth.config import load_config, save_config
from amocrm.auth.oauth import refresh_tokens
from amocrm.auth.token import is_token_expiring
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError

__all__ = ["AmoCRMClient"]

_MIN_INTERVAL = 1 / 7  # 7 req/s throttle


def _is_single_resource_path(path: str) -> bool:
    """True if path ends with a numeric ID (single-resource, not batch)."""
    return path.rstrip("/").split("/")[-1].isdigit()


class AmoCRMClient:
    def __init__(
        self,
        subdomain: str | None = None,
        access_token: str | None = None,
        refresh_token: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        expires_at: int | None = None,
    ) -> None:
        if subdomain is not None:
            # Kwargs mode: library use, skip config file
            self._subdomain = subdomain
            self._access_token = access_token or ""
            self._refresh_token = refresh_token
            self._client_id = client_id
            self._client_secret = client_secret
            self._expires_at = expires_at
            self._auth_mode = "oauth" if refresh_token else "longtoken"
            self._config_mode = False
            self._redirect_uri = "http://localhost:8080"
        else:
            # Config-file mode: CLI use
            config = load_config()
            self._subdomain = config["subdomain"]
            self._access_token = config["access_token"]
            self._refresh_token = config.get("refresh_token")
            self._client_id = config.get("client_id")
            self._client_secret = config.get("client_secret")
            self._expires_at = config.get("expires_at")
            self._auth_mode = config["auth_mode"]
            self._config_mode = True
            self._redirect_uri = config.get("redirect_uri", "http://localhost:8080")

        self._base_url = f"https://{self._subdomain}.amocrm.ru/api/v4"
        self._last_request_time: float = 0.0
        self._http = httpx.Client(timeout=30.0)

    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_request_time
        wait = _MIN_INTERVAL - elapsed
        if wait > 0:
            time.sleep(wait)
        self._last_request_time = time.monotonic()

    def _maybe_refresh(self) -> None:
        """Proactive token refresh. Reactive 401 refresh is handled in _request."""
        if self._auth_mode == "longtoken":
            return
        if not self._refresh_token or not self._client_id or not self._client_secret:
            return
        # Only refresh proactively if expires_at is known and token is expiring.
        # When expires_at is None (kwargs mode without expiry), refresh happens
        # reactively on 401 in _request — not here.
        if self._expires_at is not None and is_token_expiring(self._expires_at):
            tokens = refresh_tokens(
                subdomain=self._subdomain,
                refresh_token=self._refresh_token,
                client_id=self._client_id,
                client_secret=self._client_secret,
                redirect_uri=self._redirect_uri,
            )
            self._access_token = tokens["access_token"]
            self._refresh_token = tokens["refresh_token"]
            self._expires_at = tokens["expires_at"]
            if self._config_mode:
                config = load_config()
                config["access_token"] = self._access_token
                config["refresh_token"] = self._refresh_token
                config["expires_at"] = self._expires_at
                save_config(config)

    def _do_refresh(self) -> None:
        """Execute token refresh and store new tokens."""
        if not self._refresh_token or not self._client_id or not self._client_secret:
            return
        tokens = refresh_tokens(
            subdomain=self._subdomain,
            refresh_token=self._refresh_token,
            client_id=self._client_id,
            client_secret=self._client_secret,
            redirect_uri=self._redirect_uri,
        )
        self._access_token = tokens["access_token"]
        self._refresh_token = tokens["refresh_token"]
        self._expires_at = tokens["expires_at"]
        if self._config_mode:
            config = load_config()
            config["access_token"] = self._access_token
            config["refresh_token"] = self._refresh_token
            config["expires_at"] = self._expires_at
            save_config(config)

    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        self._throttle()
        self._maybe_refresh()
        url = self._base_url + path
        headers = {"Authorization": f"Bearer {self._access_token}"}
        retries = 3
        for attempt in range(retries):
            response = self._http.request(method, url, headers=headers, **kwargs)
            if response.status_code == 401 and attempt == 0 and self._refresh_token:
                # Reactive refresh on 401 (covers expires_at=None kwargs mode)
                self._do_refresh()
                headers = {"Authorization": f"Bearer {self._access_token}"}
                continue
            if response.status_code in (429, 503, 504) and attempt < retries - 1:
                wait = (2 ** attempt) + random.uniform(0, 0.5)
                time.sleep(wait)
                continue
            return response
        return response  # type: ignore[return-value]

    def _parse(self, response: httpx.Response, method: str, path: str) -> dict | list:
        if response.status_code == 204:
            if method == "DELETE":
                return True  # type: ignore[return-value]
            if method == "PATCH" and not _is_single_resource_path(path):
                return []
            raise EntityNotFoundError(path)
        ct = response.headers.get("content-type", "")
        if "problem+json" in ct or response.status_code >= 400:
            try:
                data = response.json()
                raise AmoCRMAPIError(
                    status=data.get("status", response.status_code),
                    title=data.get("title", "Error"),
                    detail=data.get("detail", response.text),
                )
            except (ValueError, KeyError):
                raise AmoCRMAPIError(response.status_code, "Error", response.text)
        return response.json()

    def get(self, path: str, params: dict | None = None) -> dict | list:
        r = self._request("GET", path, params=params)
        return self._parse(r, "GET", path)

    def post(self, path: str, json: list | dict | None = None) -> dict | list:
        r = self._request("POST", path, json=json)
        return self._parse(r, "POST", path)

    def patch(self, path: str, json: list | dict | None = None) -> dict | list:
        r = self._request("PATCH", path, json=json)
        return self._parse(r, "PATCH", path)

    def delete(self, path: str) -> bool:
        r = self._request("DELETE", path)
        return self._parse(r, "DELETE", path)  # type: ignore[return-value]
```

- [ ] **Step 4: Run — expect PASS**

```bash
pytest tests/test_client.py -v
```

- [ ] **Step 5: Run base resource tests — now should PASS too**

```bash
pytest tests/test_resources/test_base.py -v
```

- [ ] **Step 6: Commit**

```bash
git add amocrm/client.py tests/test_client.py
git commit -m "feat: AmoCRMClient — httpx wrapper with auth, retry, throttle"
```

---

## Task 2A: Wave 2 — Leads Resource + Commands

> **Parallel with 2B, 2C, 2D, 2E. Depends on Wave 0 + Wave 1 being complete.**

**Files:**
- Create: `amocrm/resources/leads.py`
- Create: `amocrm/commands/leads.py`
- Create: `tests/test_resources/test_leads.py`
- Create: `tests/test_commands/test_leads.py`

---

- [ ] **Step 1: Write failing resource tests**

Create `tests/test_resources/test_leads.py`:

```python
import respx
import httpx
import pytest
from amocrm.client import AmoCRMClient
from amocrm.resources.leads import LeadsResource
from amocrm.exceptions import EntityNotFoundError

BASE = "https://testco.amocrm.ru/api/v4"

@pytest.fixture
def client():
    return AmoCRMClient(subdomain="testco", access_token="tok")

@pytest.fixture
def leads(client):
    return LeadsResource(client)

SAMPLE_LEAD = {"id": 1, "name": "Big Deal", "price": 50000, "pipeline_id": 100}

@respx.mock
def test_leads_list(leads):
    respx.get(f"{BASE}/leads").mock(
        return_value=httpx.Response(200, json={"_embedded": {"leads": [SAMPLE_LEAD]}})
    )
    result = leads.list()
    assert result[0]["name"] == "Big Deal"

@respx.mock
def test_leads_list_with_filter(leads):
    route = respx.get(f"{BASE}/leads").mock(
        return_value=httpx.Response(200, json={"_embedded": {"leads": []}})
    )
    leads.list(filters={"pipeline_id": [100]})
    assert "filter" in str(route.calls[0].request.url)

@respx.mock
def test_leads_get(leads):
    respx.get(f"{BASE}/leads/1").mock(
        return_value=httpx.Response(200, json=SAMPLE_LEAD)
    )
    result = leads.get(1)
    assert result["id"] == 1

@respx.mock
def test_leads_get_not_found(leads):
    respx.get(f"{BASE}/leads/999").mock(return_value=httpx.Response(204))
    with pytest.raises(EntityNotFoundError):
        leads.get(999)

@respx.mock
def test_leads_create(leads):
    respx.post(f"{BASE}/leads").mock(
        return_value=httpx.Response(200, json={"_embedded": {"leads": [SAMPLE_LEAD]}})
    )
    result = leads.create([{"name": "Big Deal", "price": 50000}])
    assert result[0]["id"] == 1

@respx.mock
def test_leads_delete(leads):
    respx.delete(f"{BASE}/leads/1").mock(return_value=httpx.Response(204))
    assert leads.delete(1) is True

@respx.mock
def test_leads_create_complex(leads):
    respx.post(f"{BASE}/leads/complex").mock(
        return_value=httpx.Response(200, json={"_embedded": {"leads": [SAMPLE_LEAD]}})
    )
    result = leads.create_complex([{"name": "Deal", "contacts": [{"name": "John"}]}])
    assert result[0]["id"] == 1
```

- [ ] **Step 2: Run — expect FAIL**

```bash
pytest tests/test_resources/test_leads.py -v
```

- [ ] **Step 3: Implement `amocrm/resources/leads.py`**

```python
"""LeadsResource — AmoCRM Leads API."""
from __future__ import annotations
from amocrm.resources.base import BaseResource

__all__ = ["LeadsResource"]

COMPLEX_MAX = 50


class LeadsResource(BaseResource):
    path = "/leads"
    embedded_key = "leads"

    def create_complex(self, items: list[dict]) -> list[dict]:
        """Atomically create leads with contacts and companies. Max 50 per call.
        Resource-layer only — no CLI command exposes this.
        """
        if len(items) > COMPLEX_MAX:
            raise ValueError(f"create_complex accepts max {COMPLEX_MAX} items, got {len(items)}")
        response = self.client.post("/leads/complex", json=items)
        if isinstance(response, dict):
            return response.get("_embedded", {}).get("leads", [])
        return []
```

- [ ] **Step 4: Run resource tests — expect PASS**

```bash
pytest tests/test_resources/test_leads.py -v
```

- [ ] **Step 5: Write failing command tests**

Create `tests/test_commands/test_leads.py`:

```python
import pytest
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from amocrm.commands.leads import app
from amocrm.exceptions import EntityNotFoundError

runner = CliRunner()
SAMPLE_LEAD = {"id": 1, "name": "Big Deal", "price": 50000, "status_id": 1}


def test_leads_list_calls_resource():
    mock_resource = MagicMock()
    mock_resource.list.return_value = [SAMPLE_LEAD]
    with patch("amocrm.commands.leads.get_resource", return_value=mock_resource), \
         patch("amocrm.commands.leads.render"):
        result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    mock_resource.list.assert_called_once()


def test_leads_get_exits_1_on_not_found():
    mock_resource = MagicMock()
    mock_resource.get.side_effect = EntityNotFoundError("/leads/999")
    with patch("amocrm.commands.leads.get_resource", return_value=mock_resource):
        result = runner.invoke(app, ["get", "999"])
    assert result.exit_code == 1


def test_leads_list_parses_filter():
    mock_resource = MagicMock()
    mock_resource.list.return_value = []
    with patch("amocrm.commands.leads.get_resource", return_value=mock_resource), \
         patch("amocrm.commands.leads.render"):
        runner.invoke(app, ["list", "--filter", '{"pipeline_id": [1]}'])
    call_kwargs = mock_resource.list.call_args[1]
    assert call_kwargs.get("filters") == {"pipeline_id": [1]}


def test_leads_list_invalid_filter_exits_1():
    with patch("amocrm.commands.leads.get_resource", return_value=MagicMock()):
        result = runner.invoke(app, ["list", "--filter", "not-json"])
    assert result.exit_code == 1
```

- [ ] **Step 6: Run — expect FAIL**

```bash
pytest tests/test_commands/test_leads.py -v
```

- [ ] **Step 7: Implement `amocrm/commands/leads.py`**

```python
"""CLI commands for Leads resource."""
from __future__ import annotations

import json
import typer
from typing import Optional

from amocrm.client import AmoCRMClient
from amocrm.resources.leads import LeadsResource
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError
from amocrm.commands.output import render

app = typer.Typer(help="Manage AmoCRM leads")


def get_resource() -> LeadsResource:
    return LeadsResource(AmoCRMClient())


def _parse_filter(filter_str: Optional[str]) -> Optional[dict]:
    if not filter_str:
        return None
    try:
        return json.loads(filter_str)
    except json.JSONDecodeError as e:
        typer.echo(f"Invalid JSON in --filter: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def list(
    page: int = typer.Option(1),
    limit: int = typer.Option(50),
    filter: Optional[str] = typer.Option(None),
    order: Optional[str] = typer.Option(None),
    with_: Optional[str] = typer.Option(None, "--with"),
    output: str = typer.Option("table"),
    columns: Optional[str] = typer.Option(None),
):
    """List leads."""
    resource = get_resource()
    filters = _parse_filter(filter)
    with_list = with_.split(",") if with_ else None
    cols = columns.split(",") if columns else None
    try:
        data = resource.list(page=page, limit=limit, filters=filters, order=order, with_=with_list)
        render(data, output=output, columns=cols)
    except AmoCRMAPIError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command()
def get(
    id: int,
    with_: Optional[str] = typer.Option(None, "--with"),
    output: str = typer.Option("table"),
):
    """Get a single lead."""
    resource = get_resource()
    with_list = with_.split(",") if with_ else None
    try:
        data = resource.get(id, with_=with_list)
        render(data, output=output)
    except (EntityNotFoundError, AmoCRMAPIError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command()
def create(
    name: str = typer.Option(...),
    price: Optional[int] = typer.Option(None),
    pipeline_id: Optional[int] = typer.Option(None),
    output: str = typer.Option("table"),
):
    """Create a lead."""
    resource = get_resource()
    item: dict = {"name": name}
    if price is not None:
        item["price"] = price
    if pipeline_id is not None:
        item["pipeline_id"] = pipeline_id
    try:
        data = resource.create([item])
        render(data, output=output)
    except AmoCRMAPIError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command()
def delete(id: int):
    """Delete a lead."""
    resource = get_resource()
    try:
        resource.delete(id)
        typer.echo(f"Lead {id} deleted.")
    except (EntityNotFoundError, AmoCRMAPIError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
```

- [ ] **Step 8: Run all command tests — expect PASS**

```bash
pytest tests/test_commands/test_leads.py -v
```

- [ ] **Step 10: Commit**

```bash
git add amocrm/resources/leads.py amocrm/commands/leads.py tests/test_resources/test_leads.py tests/test_commands/test_leads.py
git commit -m "feat: LeadsResource + leads CLI commands"
```

---

## Tasks 2B–2E: Wave 2 — Contacts, Companies, Tasks, Notes

> **Each agent follows the same pattern as Task 2A. Run in parallel.**
> The pattern: tests → resource → tests → command → commit.

### Task 2B: Contacts

**Resource class:** `ContactsResource` in `amocrm/resources/contacts.py`
- `path = "/contacts"`, `embedded_key = "contacts"`
- No special overrides — inherits all `BaseResource` methods

**Commands:** `amocrm contacts list|get|create|delete`
- Same flags pattern as leads
- `create` flags: `--name`, `--first-name`, `--last-name`

**Tests:** Same required cases as leads (list, list with filter, get, get 404, create, delete, CLI exit code 1 on not found)

- [ ] Write `tests/test_resources/test_contacts.py` — RED
- [ ] Implement `amocrm/resources/contacts.py` — GREEN
- [ ] Write `tests/test_commands/test_contacts.py` — RED
- [ ] Implement `amocrm/commands/contacts.py` — GREEN
- [ ] `git commit -m "feat: ContactsResource + contacts CLI commands"`

### Task 2C: Companies

**Resource class:** `CompaniesResource` in `amocrm/resources/companies.py`
- `path = "/companies"`, `embedded_key = "companies"`

**Commands:** `amocrm companies list|get|create|delete`
- `create` flags: `--name`

- [ ] Write `tests/test_resources/test_companies.py` — RED
- [ ] Implement `amocrm/resources/companies.py` — GREEN
- [ ] Write `tests/test_commands/test_companies.py` — RED
- [ ] Implement `amocrm/commands/companies.py` — GREEN
- [ ] `git commit -m "feat: CompaniesResource + companies CLI commands"`

### Task 2D: Tasks

**Resource class:** `TasksResource` in `amocrm/resources/tasks.py`
- `path = "/tasks"`, `embedded_key = "tasks"`
- Required fields on create: `text` (str), `complete_till` (Unix int)
- Optional: `responsible_user_id`, `entity_id`, `entity_type`, `task_type_id`

**Commands:** `amocrm tasks list|get|create|delete`
- `create` flags: `--text` (required), `--complete-till` (required, Unix int), `--entity-id`, `--entity-type`

**Extra test:** `create` without `--text` or `--complete-till` should error.

- [ ] Write `tests/test_resources/test_tasks.py` — RED
- [ ] Implement `amocrm/resources/tasks.py` — GREEN
- [ ] Write `tests/test_commands/test_tasks.py` — RED
- [ ] Implement `amocrm/commands/tasks.py` — GREEN
- [ ] `git commit -m "feat: TasksResource + tasks CLI commands"`

### Task 2E: Notes

**Resource class:** `NotesResource` in `amocrm/resources/notes.py`
- Constructor: `def __init__(self, client, entity_type: str, entity_id: int | None = None)`
- `path` property: `f"/{self.entity_type}/notes"` or `f"/{self.entity_type}/{self.entity_id}/notes"` if `entity_id` set
- `embedded_key = "notes"`

**Commands:** `amocrm notes list|get|create`
- All commands require `--entity` (leads|contacts|companies)
- `--entity-id` optional for list, required for create
- `create` flags: `--type` (common|call_in|call_out|sms_in|sms_out), `--text`

**Extra tests:**
- `list(entity_type="leads")` hits `/leads/notes`
- `list(entity_type="leads", entity_id=5)` hits `/leads/5/notes`

- [ ] Write `tests/test_resources/test_notes.py` — RED
- [ ] Implement `amocrm/resources/notes.py` — GREEN
- [ ] Write `tests/test_commands/test_notes.py` — RED
- [ ] Implement `amocrm/commands/notes.py` — GREEN
- [ ] `git commit -m "feat: NotesResource + notes CLI commands"`

---

## Tasks 3A–3D: Wave 3 — Metadata Resources

> **Parallel. Depends on Wave 2 complete.**

### Task 3A: Pipelines + Stages

**Resource class:** `PipelinesResource` in `amocrm/resources/pipelines.py`
- `path = "/leads/pipelines"`, `embedded_key = "pipelines"`
- Constants: `WON_STATUS_ID = 142`, `LOST_STATUS_ID = 143`
- `StagesResource` nested class: `path = "/leads/pipelines/{pipeline_id}/statuses"`, `embedded_key = "statuses"`
  - Constructor: `StagesResource(client, pipeline_id: int)`

**Commands:** `amocrm pipelines list|get|create|delete` and `amocrm pipelines stages list <pipeline_id>`

- [ ] Write tests — RED; Implement — GREEN; Commit `"feat: PipelinesResource + StagesResource"`

### Task 3B: Users + Roles

**Resource class:** `UsersResource` in `amocrm/resources/users.py`
- `path = "/users"`, `embedded_key = "users"`
- `RolesResource`: `path = "/roles"`, `embedded_key = "roles"`

**Commands:** `amocrm users list|get` and `amocrm users roles list`

- [ ] Write tests — RED; Implement — GREEN; Commit `"feat: UsersResource + RolesResource"`

### Task 3C: Tags

**Resource class:** `TagsResource` in `amocrm/resources/tags.py`
- Constructor: `def __init__(self, client, entity_type: str)`
- `path` property: `f"/{self.entity_type}/tags"`
- `embedded_key = "tags"`
- Only `list()` and `create()` — no `get`, `update`, `delete` (API doesn't support)

**Commands:** `amocrm tags list --entity leads` and `amocrm tags create --entity leads --name VIP`

**Extra test:** `list()` hits `/{entity_type}/tags` not `/tags`

- [ ] Write tests — RED; Implement — GREEN; Commit `"feat: TagsResource"`

### Task 3D: Custom Fields

**Resource class:** `CustomFieldsResource` in `amocrm/resources/custom_fields.py`
- Constructor: `def __init__(self, client, entity: str)` — entity is e.g. `"leads"`, `"contacts"`
- `path` property: `f"/{entity}/custom_fields"`
- `embedded_key = "custom_fields"`
- `CustomFieldGroupsResource`: `path = f"/{entity}/custom_fields/groups"`, `embedded_key = "custom_field_groups"`

**Commands:** `amocrm custom-fields list --entity leads`

- [ ] Write tests — RED; Implement — GREEN; Commit `"feat: CustomFieldsResource + groups"`

---

## Tasks 4A–4D: Wave 4 — Extended Resources

> **Parallel. Depends on Wave 3 complete.**

### Task 4A: Catalogs + Elements

**`CatalogsResource`:** `path = "/catalogs"`, `embedded_key = "catalogs"`
**`CatalogElementsResource`:** constructor takes `catalog_id: int`; `path = f"/catalogs/{catalog_id}/elements"`, `embedded_key = "elements"`

**Commands:** `amocrm catalogs list|get` and `amocrm catalogs elements list <catalog_id>`

- [ ] Write tests — RED; Implement — GREEN; Commit `"feat: CatalogsResource + CatalogElementsResource"`

### Task 4B: Events

**`EventsResource`:** `path = "/events"`, `embedded_key = "events"`
- Read-only: only `list()` and `get()` — no `create`, `update`, `delete`
- Override `list()`: silently clamp `limit` to `min(limit, 100)` before calling super

**Commands:** `amocrm events list` (no create/update/delete commands)

**Extra test:** `list(limit=250)` sends `limit=100` to API

- [ ] Write tests — RED; Implement — GREEN; Commit `"feat: EventsResource (read-only)"`

### Task 4C: Webhooks

**`WebhooksResource`:** `path = "/webhooks"`, `embedded_key = "webhooks"`
- `list()` — GET /webhooks
- `subscribe(destination: str, settings: list[str]) -> dict`
- `unsubscribe(url: str) -> bool` — lookup-then-delete: list all → find by `destination` == url → DELETE by ID → if not found, raise `EntityNotFoundError`

**Commands:** `amocrm webhooks list`, `amocrm webhooks subscribe --url URL --events e1,e2`, `amocrm webhooks unsubscribe --url URL`

**Extra test:** `unsubscribe("missing-url")` raises `EntityNotFoundError`

- [ ] Write tests — RED; Implement — GREEN; Commit `"feat: WebhooksResource"`

### Task 4D: Account + Auth Commands + Output

**`AccountResource`:** `path = "/account"`, only `get(with_=None)`

**Auth commands** in `amocrm/commands/auth.py`:
- `amocrm auth login --token TOKEN --subdomain SUB` — calls `save_config(make_longtoken_config(...))`
- `amocrm auth login --oauth --subdomain SUB` — requires `--client-id`, `--client-secret`; calls `run_browser_flow()`
- `amocrm auth status` — loads config, prints subdomain + auth_mode + expiry
- `amocrm auth logout` — deletes `~/.amocrm/config.json`

**Commands:** `amocrm account info [--with ...]`

**output.py** is already implemented in Wave 0. Task 4D only needs to test it.

Write `tests/test_commands/test_output.py`:
- `render([{"id": 1}], output="json")` prints valid JSON
- `render({"id": 1}, output="table")` wraps dict in list, renders table
- `render([{"id": 1, "name": "x"}], output="csv")` writes CSV header + row
- `render([{"id": 1, "name": "x"}], output="table", columns=["id"])` shows only `id` column

- [ ] Write tests for AccountResource — RED; Implement — GREEN
- [ ] Write tests for auth commands — RED; Implement auth.py — GREEN
- [ ] Write `tests/test_commands/test_output.py` — run against existing output.py — PASS
- [ ] `git commit -m "feat: AccountResource + auth commands + output tests"`

---

## Task 5A: Wave 5 — Integration

> **Parallel with 5B. All resource and command files must exist.**

**Files:**
- Modify: `amocrm/app.py` (register all command groups)
- Modify: `amocrm/resources/__init__.py` (all exports)
- Modify: `amocrm/__init__.py` (all resource exports)

---

- [ ] **Step 1: Populate `amocrm/resources/__init__.py`**

```python
from amocrm.resources.leads import LeadsResource
from amocrm.resources.contacts import ContactsResource
from amocrm.resources.companies import CompaniesResource
from amocrm.resources.tasks import TasksResource
from amocrm.resources.notes import NotesResource
from amocrm.resources.pipelines import PipelinesResource, StagesResource
from amocrm.resources.users import UsersResource, RolesResource
from amocrm.resources.tags import TagsResource
from amocrm.resources.custom_fields import CustomFieldsResource, CustomFieldGroupsResource
from amocrm.resources.catalogs import CatalogsResource, CatalogElementsResource
from amocrm.resources.events import EventsResource
from amocrm.resources.webhooks import WebhooksResource
from amocrm.resources.account import AccountResource

__all__ = [
    "LeadsResource", "ContactsResource", "CompaniesResource", "TasksResource",
    "NotesResource", "PipelinesResource", "StagesResource", "UsersResource",
    "RolesResource", "TagsResource", "CustomFieldsResource", "CustomFieldGroupsResource",
    "CatalogsResource", "CatalogElementsResource", "EventsResource",
    "WebhooksResource", "AccountResource",
]
```

- [ ] **Step 2: Update `amocrm/__init__.py`**

```python
from amocrm.client import AmoCRMClient
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError
from amocrm.resources import (
    LeadsResource, ContactsResource, CompaniesResource, TasksResource,
    NotesResource, PipelinesResource, StagesResource, UsersResource,
    RolesResource, TagsResource, CustomFieldsResource, CustomFieldGroupsResource,
    CatalogsResource, CatalogElementsResource, EventsResource,
    WebhooksResource, AccountResource,
)

__all__ = [
    "AmoCRMClient", "AmoCRMAPIError", "EntityNotFoundError",
    "LeadsResource", "ContactsResource", "CompaniesResource", "TasksResource",
    "NotesResource", "PipelinesResource", "StagesResource", "UsersResource",
    "RolesResource", "TagsResource", "CustomFieldsResource", "CustomFieldGroupsResource",
    "CatalogsResource", "CatalogElementsResource", "EventsResource",
    "WebhooksResource", "AccountResource",
]
```

- [ ] **Step 3: Register all command groups in `amocrm/app.py`**

```python
import typer
from amocrm.commands import auth, leads, contacts, companies, tasks, notes
from amocrm.commands import pipelines, users, tags, custom_fields
from amocrm.commands import catalogs, events, webhooks, account

app = typer.Typer(name="amocrm", help="AmoCRM API CLI tool", no_args_is_help=True)

app.add_typer(auth.app, name="auth")
app.add_typer(leads.app, name="leads")
app.add_typer(contacts.app, name="contacts")
app.add_typer(companies.app, name="companies")
app.add_typer(tasks.app, name="tasks")
app.add_typer(notes.app, name="notes")
app.add_typer(pipelines.app, name="pipelines")
app.add_typer(users.app, name="users")
app.add_typer(tags.app, name="tags")
app.add_typer(custom_fields.app, name="custom-fields")
app.add_typer(catalogs.app, name="catalogs")
app.add_typer(events.app, name="events")
app.add_typer(webhooks.app, name="webhooks")
app.add_typer(account.app, name="account")

if __name__ == "__main__":
    app()
```

- [ ] **Step 4: Run full test suite**

```bash
pytest -v
```

Fix any failures before proceeding.

- [ ] **Step 5: Run linter and type checker**

```bash
ruff check .
mypy amocrm/
```

Fix any issues.

- [ ] **Step 6: Smoke test the CLI**

```bash
amocrm --help
amocrm leads --help
amocrm contacts --help
```

Expected: help text displays for all commands.

- [ ] **Step 7: Commit**

```bash
git add amocrm/app.py amocrm/__init__.py amocrm/resources/__init__.py
git commit -m "feat: register all command groups, complete public exports"
```

---

## Task 5B: Wave 5 — Claude Skill

> **Parallel with 5A.**

**Files:**
- Create: `skills/amocrm-cli.md`

---

- [ ] **Step 1: Write `skills/amocrm-cli.md`**

The skill document must include all sections from §10 of the spec:
- Trigger conditions
- Full CLI command reference with examples and all flags
- Library usage — both AmoCRMClient construction modes
- How to add a resource (5-step checklist)
- Known API gotchas (all items listed in spec §10)

- [ ] **Step 2: Verify skill is complete against spec §10**

Read spec §10 and check every bullet point is present in the skill.

- [ ] **Step 3: Commit**

```bash
git add skills/amocrm-cli.md
git commit -m "feat: Claude skill for amocrm-cli — CLI and library usage guide"
```

---

## Final: Verification

- [ ] `pytest` — all tests pass
- [ ] `ruff check .` — no issues
- [ ] `mypy amocrm/` — no errors
- [ ] `amocrm --help` — shows all 14 command groups
- [ ] `from amocrm import AmoCRMClient, LeadsResource` — imports without error
- [ ] `git log --oneline` — one commit per feature, clean history
