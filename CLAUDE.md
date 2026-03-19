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
