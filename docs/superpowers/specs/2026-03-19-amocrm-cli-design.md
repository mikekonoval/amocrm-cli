# AmoCRM CLI — Design Spec

**Date:** 2026-03-19
**Stack:** Python · Typer · httpx (sync) · rich · pytest + respx
**Pattern:** TDD · Modular (one file per resource) · Parallel subagent build

---

## 1. Goals

Build a lightweight Python package for the AmoCRM API v4 that works as **both a CLI tool and an importable library**:

- CLI: pipe-friendly commands (`amocrm leads list`, `amocrm contacts create`)
- Library: importable in Python code (`from amocrm import AmoCRMClient, LeadsResource`)
- Supports both long-lived token auth and full OAuth 2.0 with auto-refresh
- Covers all major AmoCRM resources
- CLI outputs table / JSON / CSV
- Is fully testable at each layer in isolation
- Ships with a Claude skill so future agents know how to use and extend it

---

## 2. Project Structure

```
amocrm-cli/
├── amocrm/
│   ├── __init__.py              # public exports: AmoCRMClient, all Resource classes, exceptions
│   ├── py.typed                 # PEP 561 marker for mypy compatibility
│   ├── app.py                   # Typer root app; registers all command groups
│   ├── client.py                # httpx (sync) session; auth headers; retry/backoff; HAL unpacker
│   ├── exceptions.py            # AmoCRMAPIError, EntityNotFoundError
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── config.py            # read/write ~/.amocrm/config.json; validates auth_mode
│   │   ├── token.py             # long-lived token storage + expiry check
│   │   └── oauth.py             # browser flow + localhost callback server + token exchange
│   ├── resources/
│   │   ├── __init__.py          # populated by Wave 5 Agent A; exports all Resource classes
│   │   ├── base.py              # BaseResource: list/get/create/update/delete mixin
│   │   ├── leads.py             # LeadsResource
│   │   ├── contacts.py          # ContactsResource
│   │   ├── companies.py         # CompaniesResource
│   │   ├── tasks.py             # TasksResource
│   │   ├── notes.py             # NotesResource
│   │   ├── pipelines.py         # PipelinesResource (includes StagesResource)
│   │   ├── users.py             # UsersResource (includes RolesResource)
│   │   ├── tags.py              # TagsResource
│   │   ├── custom_fields.py     # CustomFieldsResource (includes CustomFieldGroupsResource)
│   │   ├── catalogs.py          # CatalogsResource (includes CatalogElementsResource)
│   │   ├── events.py            # EventsResource (read-only; limit max 100)
│   │   ├── webhooks.py          # WebhooksResource (subscribe/unsubscribe only)
│   │   └── account.py           # AccountResource (single GET endpoint)
│   └── commands/
│       ├── __init__.py
│       ├── output.py            # render(data, output, columns) → table | json | csv
│       ├── auth.py              # amocrm auth login|logout|status
│       ├── leads.py
│       ├── contacts.py
│       ├── companies.py
│       ├── tasks.py
│       ├── notes.py
│       ├── pipelines.py
│       ├── users.py
│       ├── tags.py
│       ├── custom_fields.py
│       ├── catalogs.py
│       ├── events.py
│       ├── webhooks.py
│       └── account.py
├── tests/
│   ├── conftest.py              # ONLY: mock_client, mock_config, cli_runner fixtures
│   ├── test_auth/
│   │   ├── test_config.py
│   │   ├── test_token.py
│   │   └── test_oauth.py
│   ├── test_client.py
│   ├── test_resources/          # one file per resource; uses respx to mock httpx
│   └── test_commands/           # one file per command group; uses Typer CliRunner + monkeypatch
├── skills/
│   └── amocrm-cli.md            # Claude skill: CLI commands, library usage, how to add a resource
├── pyproject.toml
└── CLAUDE.md
```

### Resource Class Naming Convention

**All resource classes follow the pattern `{TitleCase}Resource`**, locked in Wave 0 via `base.py` comments and the Wave 0 agent's instruction. Examples:

| File | Class name |
|---|---|
| `leads.py` | `LeadsResource` |
| `contacts.py` | `ContactsResource` |
| `companies.py` | `CompaniesResource` |
| `tasks.py` | `TasksResource` |
| `notes.py` | `NotesResource` |
| `pipelines.py` | `PipelinesResource` |
| `users.py` | `UsersResource` |
| `tags.py` | `TagsResource` |
| `custom_fields.py` | `CustomFieldsResource` |
| `catalogs.py` | `CatalogsResource` |
| `events.py` | `EventsResource` |
| `webhooks.py` | `WebhooksResource` |
| `account.py` | `AccountResource` |

Sub-resources (stages, roles, elements, groups) follow the same convention: `StagesResource`, `RolesResource`, `CatalogElementsResource`, `CustomFieldGroupsResource`.

---

## 3. Exceptions (`exceptions.py`)

Created in Wave 0. All other modules import from here.

```python
class AmoCRMAPIError(Exception):
    def __init__(self, status: int, title: str, detail: str): ...

class EntityNotFoundError(AmoCRMAPIError):
    """Raised when API returns 204 on a GET or single-resource PATCH."""
```

Exported from `amocrm/__init__.py` so library users can catch them:
```python
from amocrm import AmoCRMAPIError, EntityNotFoundError
```

---

## 4. Authentication

### Config file: `~/.amocrm/config.json`

```json
{
  "subdomain": "mycompany",
  "auth_mode": "longtoken",
  "access_token": "...",
  "refresh_token": null,
  "expires_at": null,
  "client_id": null,
  "client_secret": null,
  "redirect_uri": "http://localhost:8080"
}
```

`auth_mode` valid values: `"longtoken"` or `"oauth"`. On read, `auth/config.py` raises `ValueError` if any other value is found.

`redirect_uri` defaults to `http://localhost:8080` and must match what is registered in the AmoCRM developer cabinet.

### Commands

```bash
amocrm auth login --token <long-lived-token> --subdomain mycompany
amocrm auth login --oauth --subdomain mycompany   # opens browser
amocrm auth status
amocrm auth logout
```

### OAuth 2.0 Flow

1. CLI generates a random CSRF `state` value
2. Authorization URL: `https://www.amocrm.ru/oauth?client_id={id}&state={csrf}&mode=popup`
   - Note: uses `www.amocrm.ru`, NOT the account subdomain
3. CLI starts a temporary HTTP server on the `redirect_uri` port (default `localhost:8080`) to receive the redirect
4. Callback arrives with `?code={auth_code}&state={state}` — validate state matches
5. Exchanges `code` for tokens via `POST https://{subdomain}.amocrm.ru/oauth2/access_token`:
   ```json
   {
     "client_id": "...",
     "client_secret": "...",
     "grant_type": "authorization_code",
     "code": "...",
     "redirect_uri": "http://localhost:8080"
   }
   ```
6. Stores access + refresh token pair atomically in config; sets `auth_mode = "oauth"`, `expires_at = now + 86400`
7. Authorization code is valid 20 minutes; single-use

**Note:** `auth/oauth.py` calls `httpx` directly (not via `AmoCRMClient`) because the token exchange happens before authentication is established.

### Token Lifecycle

| Token | Lifetime |
|---|---|
| Access token | 24 hours |
| Refresh token | 3 months from last use; single-use |
| Long-lived token | Up to 5 years; no refresh needed |

### Auto-refresh in `client.py` (config-file mode)

- If `auth_mode == "longtoken"` → skip expiry check entirely
- If `auth_mode == "oauth"` and `expires_at - now < 300s` → refresh via `POST /oauth2/access_token` with `grant_type=refresh_token` → save new pair atomically to config → old refresh token immediately invalidated

---

## 5. API Client (`client.py`)

### Constructor signatures

```python
class AmoCRMClient:
    def __init__(
        self,
        subdomain: str | None = None,
        access_token: str | None = None,
        refresh_token: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        expires_at: int | None = None,
    ): ...
```

**Two construction modes:**

**Config-file mode** (no kwargs, used by CLI):
```python
client = AmoCRMClient()
```
Reads `~/.amocrm/config.json`. Auto-refresh runs as specified in §4.

**Kwargs mode** (library use):
```python
client = AmoCRMClient(subdomain="mycompany", access_token="xxx")
```
- Skips config file entirely
- Auto-refresh logic:
  - If only `access_token` provided (no `refresh_token`) → no auto-refresh; raises `AmoCRMAPIError` on 401
  - If `access_token` + `refresh_token` + `client_id` + `client_secret` provided:
    - If `expires_at` is provided and `expires_at - now < 300s` → refresh proactively
    - If `expires_at` is `None` → refresh reactively on 401 response only
  - Refreshed tokens are kept **in memory only** — never written to `~/.amocrm/config.json`

### Client behaviour

- Base URL: `https://{subdomain}.amocrm.ru/api/v4`
- `Authorization: Bearer {access_token}` on every request
- **Rate limiting:** fixed-delay throttler at 7 req/s. `min_interval = 1/7 ≈ 0.143s`. Track `last_request_time`; sleep `max(0, min_interval - elapsed)` before each request. No third-party library.
- **Retry:** on 429 or 503/504 — exponential backoff starting at 1s, doubling, max 3 retries, with jitter (`random.uniform(0, 0.5)`)
- **HAL unpacker:** extracts `response["_embedded"][resource_key]` from collection responses
- **204 response semantics (method-aware and path-aware):**
  - GET + 204 → raise `EntityNotFoundError`
  - Single-resource PATCH (path ends with `/{id}`) + 204 → raise `EntityNotFoundError`
  - Batch PATCH (path does NOT end with `/{id}`) + 204 → return `[]` (empty result, not an error)
  - DELETE + 204 → return `True` (success)
- **Error responses** (`application/problem+json`) → raise `AmoCRMAPIError(status, title, detail)`

Public interface:

```python
client.get(path: str, params: dict | None = None) -> dict | list
client.post(path: str, json: list | dict | None = None) -> dict | list
client.patch(path: str, json: list | dict | None = None) -> dict | list
client.delete(path: str) -> bool
```

**Typed stub must be committed in Wave 0** (with this exact signature) before Wave 1 parallel agents begin.

---

## 6. Resources Layer (`resources/`)

### `base.py` — BaseResource mixin (built in Wave 0)

```python
class BaseResource:
    path: str                    # e.g. "/leads"
    embedded_key: str            # e.g. "leads"

    def __init__(self, client: AmoCRMClient): ...

    def list(self, page: int = 1, limit: int = 50, filters: dict | None = None,
             order: str | None = None, with_: list[str] | None = None) -> list[dict]: ...
    def get(self, id: int, with_: list[str] | None = None) -> dict: ...
    def create(self, items: list[dict]) -> list[dict]: ...
    def update(self, id: int, data: dict) -> dict: ...           # PATCH /{path}/{id}
    def update_batch(self, items: list[dict]) -> list[dict]: ... # PATCH /{path}
    def delete(self, id: int) -> bool: ...                       # DELETE /{path}/{id} → True
```

**Filter conversion** (dict → bracket notation query params) inside `base.list()`:
```python
{"pipeline_id": [1, 2]} → filter[pipeline_id][0]=1&filter[pipeline_id][1]=2
{"created_at": {"from": 1700000}} → filter[created_at][from]=1700000
```

**Order conversion** (string → bracket notation) inside `base.list()`:
```python
"created_at:asc" → order[created_at]=asc
```

**Batch writes:** `create` and `update_batch` accept up to 250 items. CLI layer normalizes single-item to `[item]`.

### Resource-specific overrides

| Resource | Override |
|---|---|
| `notes.py` | Constructor takes `entity_type: str`, optional `entity_id: int \| None = None`. Path is `/{entity_type}/notes` or `/{entity_type}/{entity_id}/notes` when `entity_id` is set. |
| `pipelines.py` | Stages sub-resource at `/leads/pipelines/{id}/statuses`. Exposes `StagesResource` as a nested class. |
| `users.py` | Roles sub-resource at `/roles`. Exposes `RolesResource`. |
| `tags.py` | Constructor takes `entity_type: str`. Path is `/{entity_type}/tags`. |
| `custom_fields.py` | Constructor takes `entity: str`. Path is `/{entity}/custom_fields`. Groups sub-resource at `/{entity}/custom_fields/groups`. |
| `catalogs.py` | Elements sub-resource at `/catalogs/{id}/elements` via `CatalogElementsResource`. |
| `events.py` | Read-only (list + get only). `list()` silently clamps `limit` to max 100 before sending. |
| `webhooks.py` | No `get` by ID. `subscribe(destination, settings)` = POST. `unsubscribe(url)` = lookup-then-delete: list all → find by `destination` URL → DELETE by ID. If URL not found in list, raises `EntityNotFoundError`. |
| `account.py` | Single `get(with_: list[str] \| None = None) -> dict`. No list/create/update/delete. |

### `leads.py` — extra method

`create_complex(items: list[dict]) -> list[dict]` — POSTs to `/leads/complex`; max 50 per call; atomically creates lead + contacts + companies.

**No CLI command is exposed for `create_complex`** — resource layer only, for programmatic use. `commands/leads.py` does not implement this method.

### Notable API facts baked into resources

- **System pipeline status IDs:** 142 (Won), 143 (Lost) — hardcoded constants in `pipelines.py`
- **Tags are entity-scoped** — tag IDs differ between entity types
- **`with_` trailing underscore** — Python reserved word avoidance; the CLI flag is `--with`
- **Custom field filter alpha** — check `account.get(with_=["is_api_filter_enabled"])` before filter-heavy operations

---

## 7. Commands Layer (`commands/`)

One Typer app per resource, registered in `app.py`.

**Error handling:** On `AmoCRMAPIError` or `EntityNotFoundError`, commands call `typer.echo(str(e), err=True)` then `raise typer.Exit(1)`.

**Filter parsing:** Command layer calls `json.loads(filter_string)` → passes resulting `dict` to `resource.list(filters=dict)`. Invalid JSON → stderr + exit 1.

### Common flags on every list command

```
--page INT          [default: 1]
--limit INT         [default: 50]
--filter TEXT       JSON string: '{"pipeline_id": [1,2]}'
--order TEXT        e.g. "created_at:asc"
--with TEXT         comma-separated: "contacts,catalog_elements"
--output TEXT       table|json|csv  [default: table]
--columns TEXT      comma-separated field names to display
```

### Example command signatures

```bash
amocrm leads list [--filter '{"status_id": 142}'] [--output json]
amocrm leads get 123 [--with contacts]
amocrm leads create --name "Deal" --price 50000 --pipeline-id 100
amocrm leads delete 123

amocrm notes list --entity leads [--entity-id 456]
amocrm notes create --entity leads --entity-id 456 --type common --text "Call done"

amocrm pipelines list
amocrm pipelines stages list 100

amocrm tags list --entity leads
amocrm tags create --entity leads --name "VIP" --color "#ff0000"

amocrm webhooks subscribe --url https://myserver.com/hook --events leads_add,task_add
amocrm webhooks list
amocrm webhooks unsubscribe --url https://myserver.com/hook

amocrm account info [--with users_groups,task_types]
```

### `output.py`

```python
def render(data: list[dict] | dict, output: str = "table", columns: list[str] | None = None) -> None
```

- When `data` is a `dict`, all modes wrap it in `[data]` before processing
- `table` — `rich.Table`, auto-columns from keys, or `columns` subset
- `json` — `json.dumps(data, indent=2, ensure_ascii=False)` to stdout
- `csv` — `csv.DictWriter` to stdout; `columns` controls field order

---

## 8. Testing Strategy

### Stack

| Layer | Tools |
|---|---|
| `auth/` | pytest + respx |
| `resources/` | pytest + respx |
| `commands/` | pytest + `typer.testing.CliRunner` + monkeypatch on resource layer |
| `output.py` | pytest, pure unit tests |
| `client.py` | pytest + respx |

**Client is synchronous** — no `pytest-asyncio` or `anyio` needed.

### TDD Cycle Per Resource

1. Write `tests/test_resources/test_{resource}.py` — RED
2. Implement `amocrm/resources/{resource}.py` — GREEN
3. Write `tests/test_commands/test_{resource}.py` — RED
4. Implement `amocrm/commands/{resource}.py` — GREEN

### `conftest.py` — Shared Base Fixtures Only

```python
mock_config    # in-memory config dict with test subdomain + access_token
mock_client    # AmoCRMClient(subdomain="test", access_token="test-token")
cli_runner     # typer.testing.CliRunner()
```

**Resource-specific sample data** (e.g., `sample_lead`) lives in each test file. Do NOT add to `conftest.py` — prevents write conflicts across parallel agents.

### Required Test Cases Per Resource

- `list()` returns parsed entity list from `_embedded`
- `list(filters={...})` builds correct bracket-notation query string (assert exact)
- `list(order="field:asc")` builds correct `order[field]=asc`
- `get(id)` on 204 raises `EntityNotFoundError`
- `create([...])` sends array body, returns list
- `update(id, data)` sends PATCH to `/{path}/{id}`, returns dict
- `update_batch([...])` sends PATCH to `/{path}` (no ID), on 204 returns `[]`
- `delete(id)` on 204 returns `True`
- CLI: `list` command calls resource with correct parsed args
- CLI: `get` command on `EntityNotFoundError` exits with code 1

### Additional Required Test Cases for `client.py`

- 429 → retries with backoff → succeeds on retry
- Access token expiring within 5 min (config mode) → refresh triggered before request
- Long-lived token mode (`auth_mode="longtoken"`) → no refresh attempted
- Kwargs mode with only `access_token` → 401 raises `AmoCRMAPIError`, no refresh
- Kwargs mode with full credentials + `expires_at=None` → refresh on 401 only
- Kwargs mode refresh → tokens NOT written to `~/.amocrm/config.json`
- DELETE + 204 → `True`
- GET + 204 → `EntityNotFoundError`
- Batch PATCH (no ID in path) + 204 → `[]`

---

## 9. Build Orchestration — Parallel Subagent Waves

### Wave 0 — Scaffold (sequential, 1 agent)

Creates the foundation all other agents depend on:

- `pyproject.toml` (see §11)
- `amocrm/exceptions.py` — `AmoCRMAPIError` + `EntityNotFoundError`
- `amocrm/__init__.py` — exports `AmoCRMClient`, `AmoCRMAPIError`, `EntityNotFoundError`; placeholder comments for resource class exports (populated by Wave 5 Agent A)
- `amocrm/py.typed` — empty file
- `amocrm/app.py` — stub with no commands registered
- `amocrm/client.py` — **full typed stub**: exact `__init__` signature, method signatures, return types, docstrings. No implementation logic.
- `amocrm/resources/__init__.py` — placeholder with comment "# populated by Wave 5 Agent A"
- `amocrm/resources/base.py` — full implementation of `BaseResource` including filter/order conversion
- `tests/conftest.py` — three shared fixtures only
- `CLAUDE.md` — contents per §13

### Wave 1 — Auth + Client (parallel, 3 agents)

- **Agent A:** `auth/config.py` + `auth/token.py` + tests (config reads/writes, auth_mode validation, token expiry check)
- **Agent B:** `auth/oauth.py` + tests (calls httpx directly — no AmoCRMClient dependency)
- **Agent C:** `client.py` full implementation + `tests/test_client.py`

### Wave 2 — Core Resources (parallel, 5 agents)

- **Agent A:** `resources/leads.py` (LeadsResource + create_complex) + `commands/leads.py` (no create_complex CLI) + tests
- **Agent B:** `resources/contacts.py` (ContactsResource) + `commands/contacts.py` + tests
- **Agent C:** `resources/companies.py` (CompaniesResource) + `commands/companies.py` + tests
- **Agent D:** `resources/tasks.py` (TasksResource) + `commands/tasks.py` + tests
- **Agent E:** `resources/notes.py` (NotesResource) + `commands/notes.py` + tests

### Wave 3 — Metadata Resources (parallel, 4 agents)

- **Agent A:** `resources/pipelines.py` (PipelinesResource + StagesResource) + `commands/pipelines.py` + tests
- **Agent B:** `resources/users.py` (UsersResource + RolesResource) + `commands/users.py` + tests
- **Agent C:** `resources/tags.py` (TagsResource) + `commands/tags.py` + tests
- **Agent D:** `resources/custom_fields.py` (CustomFieldsResource + CustomFieldGroupsResource) + `commands/custom_fields.py` + tests

### Wave 4 — Extended Resources (parallel, 4 agents)

- **Agent A:** `resources/catalogs.py` (CatalogsResource + CatalogElementsResource) + `commands/catalogs.py` + tests
- **Agent B:** `resources/events.py` (EventsResource, limit clamped to 100) + `commands/events.py` + tests
- **Agent C:** `resources/webhooks.py` (WebhooksResource, unsubscribe = lookup-then-delete) + `commands/webhooks.py` + tests
- **Agent D:** `resources/account.py` (AccountResource) + `commands/account.py` + tests

### Wave 5 — Integration + Skill (parallel, 2 agents)

- **Agent A:** Populate `amocrm/resources/__init__.py` with all 13 resource class exports; register all command groups in `app.py`; update `amocrm/__init__.py` with resource class exports; run `pytest` full suite; fix failures; run `ruff check .` and `mypy amocrm/`; fix issues
- **Agent B:** Write `skills/amocrm-cli.md` Claude skill (per §10)

---

## 10. Claude Skill (`skills/amocrm-cli.md`)

**Trigger:** when user mentions `amocrm` CLI or library, AmoCRM API wrapper, or asks to add a resource/command.

The skill covers both CLI and library usage:

### CLI reference
- All commands with examples and all flags with defaults (noun-verb pattern)
- Auth setup: `--token` (long-lived) vs `--oauth` flow; config stored at `~/.amocrm/config.json`
- Output formatting: `--output json|table|csv`, `--columns`
- Filter syntax: JSON string input, examples for common patterns

### Library reference
```python
from amocrm import AmoCRMClient, AmoCRMAPIError, EntityNotFoundError
from amocrm.resources import LeadsResource, ContactsResource  # etc.

# Minimal (no auto-refresh)
client = AmoCRMClient(subdomain="mycompany", access_token="xxx")

# Full OAuth with proactive refresh
client = AmoCRMClient(
    subdomain="mycompany",
    access_token="xxx",
    refresh_token="yyy",
    client_id="zzz",
    client_secret="aaa",
    expires_at=1234567890,
)

leads = LeadsResource(client)
results = leads.list(filters={"pipeline_id": [1]}, order="created_at:desc")
new_leads = leads.create([{"name": "Deal", "price": 50000}])
leads.create_complex([{"name": "Deal", "contacts": [...]}])  # atomic, max 50
```

### How to add a resource (checklist)
1. Create `amocrm/resources/{name}.py`, class `{TitleCase}Resource(BaseResource)`, set `path` and `embedded_key`
2. Create `amocrm/commands/{name}.py`, create Typer app, call resource methods
3. Register command group in `amocrm/app.py`
4. Add class to `amocrm/resources/__init__.py` and `amocrm/__init__.py`
5. Write tests in `tests/test_resources/test_{name}.py` and `tests/test_commands/test_{name}.py`

### Known API gotchas
- 204 on GET = not found (`EntityNotFoundError`); 204 on batch PATCH = empty result `[]`; 204 on DELETE = `True`
- Token rotation: refresh tokens are single-use; save new pair immediately
- Tags, notes, custom_fields are entity-scoped (constructor takes `entity_type`)
- Rate limit: 7 req/s per integration; client throttles automatically
- All timestamps are Unix integers
- Pipelines → stages path: `/leads/pipelines/{id}/statuses`
- Events limit max is 100 (silently clamped by client)
- `webhooks.unsubscribe(url)` does a lookup-then-delete; raises `EntityNotFoundError` if URL not found
- `leads.create_complex()` is resource-layer only — no CLI command

---

## 11. Dependencies (`pyproject.toml`)

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
```

---

## 12. `amocrm/__init__.py` — Full Export List

```python
from amocrm.client import AmoCRMClient
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError
from amocrm.resources import (
    LeadsResource,
    ContactsResource,
    CompaniesResource,
    TasksResource,
    NotesResource,
    PipelinesResource,
    StagesResource,
    UsersResource,
    RolesResource,
    TagsResource,
    CustomFieldsResource,
    CustomFieldGroupsResource,
    CatalogsResource,
    CatalogElementsResource,
    EventsResource,
    WebhooksResource,
    AccountResource,
)

__all__ = [
    "AmoCRMClient",
    "AmoCRMAPIError",
    "EntityNotFoundError",
    "LeadsResource",
    "ContactsResource",
    "CompaniesResource",
    "TasksResource",
    "NotesResource",
    "PipelinesResource",
    "StagesResource",
    "UsersResource",
    "RolesResource",
    "TagsResource",
    "CustomFieldsResource",
    "CustomFieldGroupsResource",
    "CatalogsResource",
    "CatalogElementsResource",
    "EventsResource",
    "WebhooksResource",
    "AccountResource",
]
```

Wave 0 writes this file with placeholder comments. Wave 5 Agent A fills in the actual imports after all resource classes exist.

---

## 13. CLAUDE.md Contents (Required)

The `CLAUDE.md` at project root must contain:

1. **Build / test / lint commands** — `pip install -e ".[dev]"`, `pytest`, `pytest tests/test_resources/test_leads.py::test_name`, `ruff check .`, `mypy amocrm/`
2. **Three-layer architecture** — resources (no CLI), commands (no HTTP), client (no business logic); exceptions in `amocrm/exceptions.py`
3. **TDD workflow** — test first, resource second, command test third, command fourth
4. **How to add a resource** — 5-step checklist from §10
5. **CLI command structure** — noun-verb pattern, global flags
6. **Library usage** — `AmoCRMClient` kwargs constructor, resource class imports, where to find exceptions

---

## 14. API Reference Summary

| Resource | Base Path | Notes |
|---|---|---|
| Leads | `/api/v4/leads` | `/leads/complex` for atomic creation (resource only) |
| Contacts | `/api/v4/contacts` | |
| Companies | `/api/v4/companies` | |
| Tasks | `/api/v4/tasks` | Required: `text`, `complete_till` |
| Notes | `/api/v4/{entity_type}/notes` | `entity_id` optional for narrowing |
| Pipelines | `/api/v4/leads/pipelines` | Stages at `/leads/pipelines/{id}/statuses` |
| Users | `/api/v4/users` | Roles at `/api/v4/roles` |
| Tags | `/api/v4/{entity_type}/tags` | Entity-scoped; leads/contacts/companies |
| Custom Fields | `/api/v4/{entity}/custom_fields` | Admin-only writes; groups sub-resource |
| Catalogs | `/api/v4/catalogs` | Elements at `/catalogs/{id}/elements` |
| Events | `/api/v4/events` | Read-only; max limit=100 (silently clamped) |
| Webhooks | `/api/v4/webhooks` | Admin-only; max 100/account |
| Account | `/api/v4/account` | Single GET |

**Rate limits:** 7 req/s per integration (enforced by client), 50 req/s per account (not enforced)
**Batch limits:** max 250 items per POST/PATCH (50 recommended)
**204 semantics:** GET 204 = `EntityNotFoundError`; single-resource PATCH 204 = `EntityNotFoundError`; batch PATCH 204 = `[]`; DELETE 204 = `True`
**All timestamps** = Unix integers
**Auth token endpoint:** `https://{subdomain}.amocrm.ru/oauth2/access_token`
**OAuth consent URL:** `https://www.amocrm.ru/oauth` (uses `www`, not subdomain)
**System pipeline status IDs:** 142 = Won, 143 = Lost
