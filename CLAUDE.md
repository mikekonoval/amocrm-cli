# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Python package for the AmoCRM API v4. Works as both a **CLI tool** (`amocrm leads list`) and an **importable library** (`from amocrm import AmoCRMClient, LeadsResource`).

## Commands

```bash
pip install -e ".[dev]"          # install with dev dependencies
pytest                            # run all tests
pytest tests/test_resources/test_leads.py::test_list_returns_leads  # single test
ruff check .                      # lint
mypy amocrm/                      # type check
```

## Architecture — Three Strict Layers

- `amocrm/auth/` — credential storage (`~/.amocrm/config.json`), long-lived token mode, full OAuth 2.0 flow with auto-refresh. `oauth.py` calls httpx directly (not via `AmoCRMClient`) because token exchange happens before auth is established.
- `amocrm/resources/` — pure Python API functions. No CLI, no Typer. Each file has one `{Name}Resource` class subclassing `BaseResource`.
- `amocrm/commands/` — Typer CLI commands. Calls resource methods, formats output via `output.py`. No HTTP here.
- `amocrm/client.py` — the only file that uses httpx. Rate-limits at 7 req/s, retries on 429/503/504 with exponential backoff, handles 204 semantics, proactive/reactive OAuth token refresh.
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

`tests/conftest.py` has exactly three shared fixtures (`mock_config`, `mock_client`, `cli_runner`). Resource-specific sample data belongs in each test file — do not add to conftest.

## CLI Command Structure

Noun-verb: `amocrm <resource> <action>`

Global flags on list commands: `--page`, `--limit`, `--filter` (JSON string), `--order` (field:asc), `--with`, `--output table|json|csv`, `--columns`

Auth commands (special — no resource class, calls auth layer directly):

```bash
amocrm auth login --token <token> --subdomain mycompany
amocrm auth login --oauth --subdomain mycompany --client-id <id> --client-secret <sec>
amocrm auth status
amocrm auth logout
```

## Library Usage

```python
from amocrm import AmoCRMClient, AmoCRMAPIError, EntityNotFoundError
from amocrm.resources import LeadsResource

# Minimal — no auto-refresh
client = AmoCRMClient(subdomain="mycompany", access_token="xxx")

# Full OAuth with proactive refresh (expires_at=None → reactive refresh on 401 only)
client = AmoCRMClient(
    subdomain="mycompany", access_token="xxx", refresh_token="yyy",
    client_id="zzz", client_secret="aaa", expires_at=1234567890,
)

leads = LeadsResource(client)
results = leads.list(filters={"pipeline_id": [1]}, order="created_at:desc")
```

## API Gotchas

- 204 on GET = `EntityNotFoundError`; 204 on DELETE = `True`; 204 on batch PATCH = `[]`; 204 on single-resource PATCH = `EntityNotFoundError`
- 204 on list GET (empty collection) = `[]` — `BaseResource.list()` catches `EntityNotFoundError` and returns `[]` instead of raising
- Refresh tokens are single-use — new pair saved atomically to config on every refresh; kwargs-mode refresh is memory-only (never written to disk)
- Tags, notes, custom_fields, catalogs are entity-scoped (constructor takes `entity_type` or `entity` or `catalog_id`)
- `EventsResource.list()` silently clamps limit to 100
- `WebhooksResource.unsubscribe(url)` does lookup-then-delete; embedded key is `"hooks"` (not `"webhooks"`); raises `EntityNotFoundError` if URL not found
- `LeadsResource.create_complex()` is resource-layer only — no CLI command for it
- `AccountResource` does not subclass `BaseResource` — standalone `get()` only
- All timestamps are Unix integers
- Pipelines stages path: `/leads/pipelines/{id}/statuses` (not `/stages/`)
- `pipelines create` requires `is_unsorted_on` + `_embedded.statuses` (at least one) — bare `{"name": "..."}` returns 400
- Stage colors: only specific hex values accepted by the API (e.g. `#fffeb2`, `#fffeb2`, `#D5D8DB`); arbitrary hex returns 400
- OAuth consent URL uses `www.amocrm.ru`, not the account subdomain

## mypy Notes

`mypy amocrm/` is configured with `strict = true`. Two patterns require special attention:

- **Entity-scoped resources** (Notes, Tags, CustomFields, CustomFieldGroups, StagesResource, CatalogElements) declare `path: ClassVar[str] = ""` then set `self.path = ...` in `__init__`. This pattern requires `# type: ignore[misc]` on the assignment lines — it's intentional, not a bug.
- **`BaseResource` and `EventsResource`** both define a method named `list`, which shadows the builtin `list` in type annotations within those classes. Use `List` from `typing` (not the builtin `list`) for annotations inside those class bodies to avoid mypy resolving `list[...]` as the method.
