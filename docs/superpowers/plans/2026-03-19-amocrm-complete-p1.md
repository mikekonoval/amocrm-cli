# AmoCRM CLI — Complete API (Part 1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fill all missing CRUD commands for existing resources and add three new resource sections (Loss Reasons, Calls, Unsorted) to make the library cover the full standard AmoCRM API v4.

**Architecture:** Same three-layer pattern as the rest of the codebase: `resources/` (pure API, no CLI), `commands/` (Typer CLI, no HTTP), `client.py` (only HTTP layer). New resources follow the same `BaseResource` subclass pattern. Unsorted has two non-standard PATCH actions (`accept` / `decline`) implemented as extra methods on the resource, not via BaseResource CRUD.

**Tech Stack:** Python 3.11+, Typer, httpx (sync), respx (test mocking), pytest

---

## Reading Before You Start

Read these files to understand existing patterns — do not skip:
- `amocrm/resources/base.py` — BaseResource, _build_filter_params, _build_order_params
- `amocrm/commands/leads.py` — canonical command pattern (list/get/create/update/delete)
- `amocrm/commands/pipelines.py` — pattern for sub-resource commands (stages_app)
- `amocrm/commands/notes.py` — entity-scoped command pattern
- `tests/test_commands/test_leads.py` — canonical command test pattern
- `tests/test_resources/test_leads.py` — canonical resource test pattern
- `amocrm/resources/notes.py` — entity-scoped resource pattern (`path: ClassVar[str] = ""`, `self.path = ... # type: ignore[misc]`)

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `amocrm/commands/contacts.py` | Modify | Add `update` command |
| `amocrm/commands/companies.py` | Modify | Add `update` command |
| `amocrm/commands/tasks.py` | Modify | Add `update` command |
| `amocrm/commands/notes.py` | Modify | Add `update` command |
| `amocrm/commands/tags.py` | Modify | Add `update` + `delete` commands |
| `amocrm/commands/custom_fields.py` | Modify | Add `create` + `delete` commands |
| `amocrm/commands/catalogs.py` | Modify | Add `elements update` + `elements delete` commands |
| `amocrm/resources/loss_reasons.py` | Create | `LossReasonsResource(BaseResource)` |
| `amocrm/commands/loss_reasons.py` | Create | CLI: list/get/create/update/delete |
| `amocrm/resources/calls.py` | Create | `CallsResource` — POST-only (no GET in v4) |
| `amocrm/commands/calls.py` | Create | CLI: `calls add` |
| `amocrm/resources/unsorted.py` | Create | `UnsortedResource` — list/get/add/accept/decline |
| `amocrm/commands/unsorted.py` | Create | CLI: list/get/add/accept/decline |
| `amocrm/resources/__init__.py` | Modify | Export new resource classes |
| `amocrm/__init__.py` | Modify | Export new resource classes |
| `amocrm/app.py` | Modify | Register `loss-reasons`, `calls`, `unsorted` apps |
| `tests/test_commands/test_contacts.py` | Modify | Add test for `update` |
| `tests/test_commands/test_companies.py` | Modify | Add test for `update` |
| `tests/test_commands/test_tasks.py` | Modify | Add test for `update` |
| `tests/test_commands/test_notes.py` | Modify | Add test for `update` |
| `tests/test_commands/test_tags.py` | Modify | Add tests for `update` + `delete` |
| `tests/test_commands/test_custom_fields.py` | Modify | Add tests for `create` + `delete` |
| `tests/test_commands/test_catalogs.py` | Modify | Add tests for `elements update` + `elements delete` |
| `tests/test_resources/test_loss_reasons.py` | Create | Resource-level tests |
| `tests/test_commands/test_loss_reasons.py` | Create | CLI-level tests |
| `tests/test_resources/test_calls.py` | Create | Resource-level tests |
| `tests/test_commands/test_calls.py` | Create | CLI-level tests |
| `tests/test_resources/test_unsorted.py` | Create | Resource-level tests |
| `tests/test_commands/test_unsorted.py` | Create | CLI-level tests |

---

## Wave 1 — Missing update commands for existing resources

These are all mechanical. Same pattern for each: add `update` command following `leads.py` exactly.

---

### Task 1A: `contacts update`

**Files:**
- Modify: `amocrm/commands/contacts.py`
- Modify: `tests/test_commands/test_contacts.py`

- [ ] **Step 1: Write failing tests**

Add to `tests/test_commands/test_contacts.py`:

```python
def test_update_command():
    with patch("amocrm.commands.contacts.ContactsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.update.return_value = {"id": 1, "name": "Updated"}
        with patch("amocrm.commands.contacts.AmoCRMClient"):
            result = runner.invoke(app, ["update", "1", "--name", "Updated", "--output", "json"])
    assert result.exit_code == 0
    mock_resource.update.assert_called_once_with(1, {"name": "Updated"})

def test_update_not_found_exits_1():
    with patch("amocrm.commands.contacts.ContactsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.update.side_effect = EntityNotFoundError("/contacts/999")
        with patch("amocrm.commands.contacts.AmoCRMClient"):
            result = runner.invoke(app, ["update", "999", "--name", "X"])
    assert result.exit_code == 1
```

- [ ] **Step 2: Run — expect FAIL** (`pytest tests/test_commands/test_contacts.py -v`)

- [ ] **Step 3: Implement** — add before `delete_contact` in `amocrm/commands/contacts.py`:

```python
@app.command("update")
def update_contact(
    id: int = typer.Argument(...),
    name: Optional[str] = typer.Option(None, "--name"),
    email: Optional[str] = typer.Option(None, "--email"),
    phone: Optional[str] = typer.Option(None, "--phone"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Update a contact by ID."""
    try:
        data: dict[str, object] = {}
        if name is not None:
            data["name"] = name
        if email is not None:
            data["email"] = email
        if phone is not None:
            data["phone"] = phone
        if not data:
            typer.echo("Provide at least one field to update.", err=True)
            raise typer.Exit(1)
        resource = _get_resource()
        result = resource.update(id, data)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
```

- [ ] **Step 4: Run — expect PASS** (`pytest tests/test_commands/test_contacts.py -v`)
- [ ] **Step 5: Commit** (`git commit -m "feat: add contacts update command"`)

---

### Task 1B: `companies update`

**Files:**
- Modify: `amocrm/commands/companies.py`
- Modify: `tests/test_commands/test_companies.py`

- [ ] **Step 1: Write failing tests**

Add to `tests/test_commands/test_companies.py`:

```python
def test_update_command():
    with patch("amocrm.commands.companies.CompaniesResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.update.return_value = {"id": 1, "name": "Updated Corp"}
        with patch("amocrm.commands.companies.AmoCRMClient"):
            result = runner.invoke(app, ["update", "1", "--name", "Updated Corp", "--output", "json"])
    assert result.exit_code == 0
    mock_resource.update.assert_called_once_with(1, {"name": "Updated Corp"})
```

- [ ] **Step 2: Run — expect FAIL**
- [ ] **Step 3: Implement** — add `update_company` command before `delete_company` (same pattern as 1A, fields: `name` only):

```python
@app.command("update")
def update_company(
    id: int = typer.Argument(...),
    name: Optional[str] = typer.Option(None, "--name"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Update a company by ID."""
    try:
        data: dict[str, object] = {}
        if name is not None:
            data["name"] = name
        if not data:
            typer.echo("Provide at least one field to update.", err=True)
            raise typer.Exit(1)
        resource = _get_resource()
        result = resource.update(id, data)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
```

- [ ] **Step 4: Run — expect PASS**
- [ ] **Step 5: Commit**

---

### Task 1C: `tasks update`

Read `amocrm/commands/tasks.py` first to see `create_task` params — they tell you which fields exist.

**Files:**
- Modify: `amocrm/commands/tasks.py`
- Modify: `tests/test_commands/test_tasks.py`

- [ ] **Step 1: Write failing tests**

```python
def test_update_command():
    with patch("amocrm.commands.tasks.TasksResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.update.return_value = {"id": 1, "text": "Updated"}
        with patch("amocrm.commands.tasks.AmoCRMClient"):
            result = runner.invoke(app, ["update", "1", "--text", "Updated", "--output", "json"])
    assert result.exit_code == 0
    mock_resource.update.assert_called_once_with(1, {"text": "Updated"})
```

- [ ] **Step 2: Run — expect FAIL**
- [ ] **Step 3: Implement** — add `update_task` (fields: `text`, `complete-till`, `is-completed`):

```python
@app.command("update")
def update_task(
    id: int = typer.Argument(...),
    text: Optional[str] = typer.Option(None, "--text"),
    complete_till: Optional[int] = typer.Option(None, "--complete-till", help="Unix timestamp"),
    is_completed: Optional[bool] = typer.Option(None, "--is-completed"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Update a task by ID."""
    try:
        data: dict[str, object] = {}
        if text is not None:
            data["text"] = text
        if complete_till is not None:
            data["complete_till"] = complete_till
        if is_completed is not None:
            data["is_completed"] = is_completed
        if not data:
            typer.echo("Provide at least one field to update.", err=True)
            raise typer.Exit(1)
        resource = _get_resource()
        result = resource.update(id, data)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
```

- [ ] **Step 4: Run — expect PASS**
- [ ] **Step 5: Commit**

---

### Task 1D: `notes update`

Notes are entity-scoped. Read `amocrm/commands/notes.py` to see how entity/entity_id is passed.

**Files:**
- Modify: `amocrm/commands/notes.py`
- Modify: `tests/test_commands/test_notes.py`

- [ ] **Step 1: Write failing tests**

```python
def test_update_note_command():
    with patch("amocrm.commands.notes.NotesResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.update.return_value = {"id": 10, "text": "Updated note"}
        with patch("amocrm.commands.notes.AmoCRMClient"):
            result = runner.invoke(app, ["update", "10", "--entity", "leads", "--text", "Updated note"])
    assert result.exit_code == 0
    mock_resource.update.assert_called_once_with(10, {"note_type": "common", "params": {"text": "Updated note"}})
```

- [ ] **Step 2: Run — expect FAIL**
- [ ] **Step 3: Implement** — add `update_note` command. Check how `create_note` builds the body — `update` follows the same `params.text` structure:

```python
@app.command("update")
def update_note(
    id: int = typer.Argument(...),
    entity: str = typer.Option(..., "--entity", help="Entity type: leads, contacts, companies, tasks"),
    text: str = typer.Option(..., "--text"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Update a note by ID."""
    try:
        resource = NotesResource(AmoCRMClient(), entity_type=entity)
        result = resource.update(id, {"note_type": "common", "params": {"text": text}})
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
```

- [ ] **Step 4: Run — expect PASS**
- [ ] **Step 5: Commit**

---

### Task 1E: `tags update` + `tags delete`

Tags are entity-scoped. Read `amocrm/commands/tags.py` first.

**Files:**
- Modify: `amocrm/commands/tags.py`
- Modify: `tests/test_commands/test_tags.py`

- [ ] **Step 1: Write failing tests**

```python
def test_update_tag_command():
    with patch("amocrm.commands.tags.TagsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.update.return_value = {"id": 5, "name": "VIP"}
        with patch("amocrm.commands.tags.AmoCRMClient"):
            result = runner.invoke(app, ["update", "5", "--entity", "leads", "--name", "VIP"])
    assert result.exit_code == 0
    mock_resource.update.assert_called_once_with(5, {"name": "VIP"})

def test_delete_tag_command():
    with patch("amocrm.commands.tags.TagsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.delete.return_value = True
        with patch("amocrm.commands.tags.AmoCRMClient"):
            result = runner.invoke(app, ["delete", "5", "--entity", "leads"])
    assert result.exit_code == 0
```

- [ ] **Step 2: Run — expect FAIL**
- [ ] **Step 3: Implement** — add both commands to `amocrm/commands/tags.py`:

```python
@app.command("update")
def update_tag(
    id: int = typer.Argument(...),
    entity: str = typer.Option(..., "--entity", help="Entity type: leads, contacts, companies"),
    name: str = typer.Option(..., "--name"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Update a tag by ID."""
    try:
        resource = TagsResource(AmoCRMClient(), entity_type=entity)
        result = resource.update(id, {"name": name})
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("delete")
def delete_tag(
    id: int = typer.Argument(...),
    entity: str = typer.Option(..., "--entity", help="Entity type: leads, contacts, companies"),
) -> None:
    """Delete a tag by ID."""
    try:
        resource = TagsResource(AmoCRMClient(), entity_type=entity)
        resource.delete(id)
        typer.echo(f"Tag {id} deleted.")
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
```

- [ ] **Step 4: Run — expect PASS**
- [ ] **Step 5: Commit**

---

### Task 1F: `custom-fields create` + `custom-fields delete`

Read `amocrm/commands/custom_fields.py` and `amocrm/resources/custom_fields.py` first.

The AmoCRM API requires `name` and `type` (field type ID) when creating a custom field. Valid `type` values are integers: 1=text, 2=numeric, 3=checkbox, 4=select, 5=multiselect, 6=date, 13=url, 16=textarea, 18=radiobutton, 22=date_time.

**Files:**
- Modify: `amocrm/commands/custom_fields.py`
- Modify: `tests/test_commands/test_custom_fields.py`

- [ ] **Step 1: Write failing tests**

```python
def test_create_field_command():
    with patch("amocrm.commands.custom_fields.CustomFieldsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.create.return_value = [{"id": 1, "name": "Budget"}]
        with patch("amocrm.commands.custom_fields.AmoCRMClient"):
            result = runner.invoke(app, ["create", "--entity", "leads", "--name", "Budget", "--type", "2"])
    assert result.exit_code == 0
    call_args = mock_resource.create.call_args[0][0][0]
    assert call_args["name"] == "Budget"
    assert call_args["type"] == 2

def test_delete_field_command():
    with patch("amocrm.commands.custom_fields.CustomFieldsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.delete.return_value = True
        with patch("amocrm.commands.custom_fields.AmoCRMClient"):
            result = runner.invoke(app, ["delete", "1", "--entity", "leads"])
    assert result.exit_code == 0
```

- [ ] **Step 2: Run — expect FAIL**
- [ ] **Step 3: Implement** — add to `amocrm/commands/custom_fields.py`:

```python
@app.command("create")
def create_field(
    entity: str = typer.Option(..., "--entity", help="Entity: leads, contacts, companies, tasks"),
    name: str = typer.Option(..., "--name"),
    type: int = typer.Option(..., "--type", help="Field type ID: 1=text, 2=numeric, 3=checkbox, 4=select, 6=date"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Create a custom field for an entity."""
    try:
        resource = CustomFieldsResource(AmoCRMClient(), entity=entity)
        results = resource.create([{"name": name, "type": type}])
        render(results, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("delete")
def delete_field(
    id: int = typer.Argument(...),
    entity: str = typer.Option(..., "--entity", help="Entity: leads, contacts, companies, tasks"),
) -> None:
    """Delete a custom field by ID."""
    try:
        resource = CustomFieldsResource(AmoCRMClient(), entity=entity)
        resource.delete(id)
        typer.echo(f"Custom field {id} deleted.")
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
```

- [ ] **Step 4: Run — expect PASS**
- [ ] **Step 5: Commit**

---

### Task 1G: `catalogs elements update` + `catalogs elements delete`

Read `amocrm/commands/catalogs.py` to see the existing `elements` sub-app pattern.

**Files:**
- Modify: `amocrm/commands/catalogs.py`
- Modify: `tests/test_commands/test_catalogs.py`

- [ ] **Step 1: Write failing tests**

```python
def test_elements_update():
    with patch("amocrm.commands.catalogs.CatalogElementsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.update.return_value = {"id": 10, "name": "Updated"}
        with patch("amocrm.commands.catalogs.AmoCRMClient"):
            result = runner.invoke(app, ["elements", "update", "1", "10", "--name", "Updated"])
    assert result.exit_code == 0
    mock_resource.update.assert_called_once_with(10, {"name": "Updated"})

def test_elements_delete():
    with patch("amocrm.commands.catalogs.CatalogElementsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.delete.return_value = True
        with patch("amocrm.commands.catalogs.AmoCRMClient"):
            result = runner.invoke(app, ["elements", "delete", "1", "10"])
    assert result.exit_code == 0
```

- [ ] **Step 2: Run — expect FAIL**
- [ ] **Step 3: Implement** — add to elements sub-app in `amocrm/commands/catalogs.py`:

```python
@elements_app.command("update")
def update_element(
    catalog_id: int = typer.Argument(...),
    id: int = typer.Argument(...),
    name: Optional[str] = typer.Option(None, "--name"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Update a catalog element by ID."""
    try:
        data: dict[str, object] = {}
        if name is not None:
            data["name"] = name
        if not data:
            typer.echo("Provide at least one field to update.", err=True)
            raise typer.Exit(1)
        resource = CatalogElementsResource(AmoCRMClient(), catalog_id=catalog_id)
        result = resource.update(id, data)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@elements_app.command("delete")
def delete_element(
    catalog_id: int = typer.Argument(...),
    id: int = typer.Argument(...),
) -> None:
    """Delete a catalog element by ID."""
    try:
        resource = CatalogElementsResource(AmoCRMClient(), catalog_id=catalog_id)
        resource.delete(id)
        typer.echo(f"Element {id} deleted.")
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
```

- [ ] **Step 4: Run — expect PASS**
- [ ] **Step 5: Commit**

---

## Wave 2 — Loss Reasons

Loss reasons are a simple CRUD resource for managing reasons why deals are lost.
API path: `/leads/loss_reasons`, embedded key: `loss_reasons`.

---

### Task 2A: `LossReasonsResource`

**Files:**
- Create: `amocrm/resources/loss_reasons.py`
- Create: `tests/test_resources/test_loss_reasons.py`

- [ ] **Step 1: Write failing resource tests**

```python
# tests/test_resources/test_loss_reasons.py
import respx
import httpx
import pytest
from amocrm.client import AmoCRMClient
from amocrm.resources.loss_reasons import LossReasonsResource
from amocrm.exceptions import EntityNotFoundError

SAMPLE_REASON = {"id": 1, "name": "Too expensive"}

@pytest.fixture
def client():
    return AmoCRMClient(subdomain="testco", access_token="test-token")

@pytest.fixture
def resource(client):
    return LossReasonsResource(client)

@respx.mock
def test_list_returns_reasons(resource):
    respx.get("https://testco.amocrm.ru/api/v4/leads/loss_reasons").mock(
        return_value=httpx.Response(200, json={"_embedded": {"loss_reasons": [SAMPLE_REASON]}})
    )
    result = resource.list()
    assert result == [SAMPLE_REASON]

@respx.mock
def test_get_returns_reason(resource):
    respx.get("https://testco.amocrm.ru/api/v4/leads/loss_reasons/1").mock(
        return_value=httpx.Response(200, json=SAMPLE_REASON)
    )
    result = resource.get(1)
    assert result["id"] == 1

@respx.mock
def test_create_returns_reasons(resource):
    respx.post("https://testco.amocrm.ru/api/v4/leads/loss_reasons").mock(
        return_value=httpx.Response(200, json={"_embedded": {"loss_reasons": [SAMPLE_REASON]}})
    )
    result = resource.create([{"name": "Too expensive"}])
    assert result == [SAMPLE_REASON]

@respx.mock
def test_update_returns_reason(resource):
    respx.patch("https://testco.amocrm.ru/api/v4/leads/loss_reasons/1").mock(
        return_value=httpx.Response(200, json=SAMPLE_REASON)
    )
    result = resource.update(1, {"name": "Updated"})
    assert result["id"] == 1

@respx.mock
def test_delete_returns_true(resource):
    respx.delete("https://testco.amocrm.ru/api/v4/leads/loss_reasons/1").mock(
        return_value=httpx.Response(204)
    )
    assert resource.delete(1) is True
```

- [ ] **Step 2: Run — expect FAIL**

- [ ] **Step 3: Implement**

```python
# amocrm/resources/loss_reasons.py
"""LossReasonsResource for AmoCRM API v4."""
from __future__ import annotations

from amocrm.resources.base import BaseResource

__all__ = ["LossReasonsResource"]


class LossReasonsResource(BaseResource):
    path = "/leads/loss_reasons"
    embedded_key = "loss_reasons"
```

- [ ] **Step 4: Run — expect PASS**
- [ ] **Step 5: Commit**

---

### Task 2B: `loss-reasons` CLI commands

**Files:**
- Create: `amocrm/commands/loss_reasons.py`
- Create: `tests/test_commands/test_loss_reasons.py`

- [ ] **Step 1: Write failing CLI tests**

```python
# tests/test_commands/test_loss_reasons.py
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from amocrm.commands.loss_reasons import app
from amocrm.exceptions import EntityNotFoundError

runner = CliRunner()
SAMPLE_REASON = {"id": 1, "name": "Too expensive"}

def test_list_command():
    with patch("amocrm.commands.loss_reasons.LossReasonsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.list.return_value = [SAMPLE_REASON]
        with patch("amocrm.commands.loss_reasons.AmoCRMClient"):
            result = runner.invoke(app, ["list", "--output", "json"])
    assert result.exit_code == 0

def test_get_command():
    with patch("amocrm.commands.loss_reasons.LossReasonsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.return_value = SAMPLE_REASON
        with patch("amocrm.commands.loss_reasons.AmoCRMClient"):
            result = runner.invoke(app, ["get", "1", "--output", "json"])
    assert result.exit_code == 0

def test_create_command():
    with patch("amocrm.commands.loss_reasons.LossReasonsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.create.return_value = [SAMPLE_REASON]
        with patch("amocrm.commands.loss_reasons.AmoCRMClient"):
            result = runner.invoke(app, ["create", "--name", "Too expensive"])
    assert result.exit_code == 0

def test_update_command():
    with patch("amocrm.commands.loss_reasons.LossReasonsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.update.return_value = SAMPLE_REASON
        with patch("amocrm.commands.loss_reasons.AmoCRMClient"):
            result = runner.invoke(app, ["update", "1", "--name", "Updated"])
    assert result.exit_code == 0
    mock_resource.update.assert_called_once_with(1, {"name": "Updated"})

def test_delete_command():
    with patch("amocrm.commands.loss_reasons.LossReasonsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.delete.return_value = True
        with patch("amocrm.commands.loss_reasons.AmoCRMClient"):
            result = runner.invoke(app, ["delete", "1"])
    assert result.exit_code == 0

def test_get_not_found_exits_1():
    with patch("amocrm.commands.loss_reasons.LossReasonsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get.side_effect = EntityNotFoundError("/leads/loss_reasons/999")
        with patch("amocrm.commands.loss_reasons.AmoCRMClient"):
            result = runner.invoke(app, ["get", "999"])
    assert result.exit_code == 1
```

- [ ] **Step 2: Run — expect FAIL**

- [ ] **Step 3: Implement**

```python
# amocrm/commands/loss_reasons.py
"""CLI commands for loss reasons resource."""
from __future__ import annotations

import typer

from amocrm.client import AmoCRMClient
from amocrm.commands.output import render
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError
from amocrm.resources.loss_reasons import LossReasonsResource

app = typer.Typer(name="loss-reasons", help="Manage lead loss reasons")


def _get_resource() -> LossReasonsResource:
    return LossReasonsResource(AmoCRMClient())


@app.command("list")
def list_reasons(
    page: int = typer.Option(1, "--page"),
    limit: int = typer.Option(50, "--limit"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """List loss reasons."""
    try:
        results = _get_resource().list(page=page, limit=limit)
        render(results, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("get")
def get_reason(
    id: int = typer.Argument(...),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Get a loss reason by ID."""
    try:
        result = _get_resource().get(id)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("create")
def create_reason(
    name: str = typer.Option(..., "--name"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Create a loss reason."""
    try:
        results = _get_resource().create([{"name": name}])
        render(results, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("update")
def update_reason(
    id: int = typer.Argument(...),
    name: str = typer.Option(..., "--name"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Update a loss reason by ID."""
    try:
        result = _get_resource().update(id, {"name": name})
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("delete")
def delete_reason(
    id: int = typer.Argument(...),
) -> None:
    """Delete a loss reason by ID."""
    try:
        _get_resource().delete(id)
        typer.echo(f"Loss reason {id} deleted.")
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
```

- [ ] **Step 4: Run — expect PASS**

- [ ] **Step 5: Register** — add to `amocrm/app.py`:

```python
from amocrm.commands.loss_reasons import app as loss_reasons_app
# ...
app.add_typer(loss_reasons_app, name="loss-reasons")
```

Add to `amocrm/resources/__init__.py` and `amocrm/__init__.py`:
```python
from amocrm.resources.loss_reasons import LossReasonsResource
```

- [ ] **Step 6: Commit** (`git commit -m "feat: add loss-reasons resource and CLI"`)

---

## Wave 3 — Calls

Calls in AmoCRM v4 are **write-only** — you POST a call log, there is no GET/list endpoint in the standard API. One `add` command is enough.

Call fields:
- `direction` — `"inbound"` or `"outbound"` (required)
- `duration` — integer seconds (required)
- `source` — string, name of call source (required)
- `link` — recording URL (optional)
- `phone` — phone number (required)
- `call_result` — string, result description (optional)
- `call_status` — integer: 1=no answer, 2=busy, 3=rejected, 4=answered, 5=unknown, 6=voicemail (required)
- `responsible_user_id` — integer (required)
- `created_by` — integer user ID (optional)
- `created_at` — Unix timestamp (optional)

---

### Task 3A: `CallsResource`

**Files:**
- Create: `amocrm/resources/calls.py`
- Create: `tests/test_resources/test_calls.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_resources/test_calls.py
import respx
import httpx
import pytest
from amocrm.client import AmoCRMClient
from amocrm.resources.calls import CallsResource

SAMPLE_CALL = {"id": 1, "duration": 60, "direction": "inbound"}

@pytest.fixture
def client():
    return AmoCRMClient(subdomain="testco", access_token="test-token")

@pytest.fixture
def resource(client):
    return CallsResource(client)

@respx.mock
def test_add_call(resource):
    respx.post("https://testco.amocrm.ru/api/v4/calls").mock(
        return_value=httpx.Response(200, json={"_embedded": {"calls": [SAMPLE_CALL]}})
    )
    result = resource.add([{
        "direction": "inbound", "duration": 60, "source": "Telephony",
        "phone": "+79001234567", "call_status": 4, "responsible_user_id": 1,
    }])
    assert result == [SAMPLE_CALL]
```

- [ ] **Step 2: Run — expect FAIL**

- [ ] **Step 3: Implement**

```python
# amocrm/resources/calls.py
"""CallsResource for AmoCRM API v4 — write-only call log."""
from __future__ import annotations

from typing import Any, List

from amocrm.resources.base import BaseResource

__all__ = ["CallsResource"]


class CallsResource(BaseResource):
    path = "/calls"
    embedded_key = "calls"

    def add(self, items: List[dict[str, Any]]) -> List[dict[str, Any]]:
        """POST call log entries. No GET endpoint exists in AmoCRM v4."""
        return self.create(items)
```

- [ ] **Step 4: Run — expect PASS**
- [ ] **Step 5: Commit**

---

### Task 3B: `calls add` CLI

**Files:**
- Create: `amocrm/commands/calls.py`
- Create: `tests/test_commands/test_calls.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_commands/test_calls.py
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from amocrm.commands.calls import app

runner = CliRunner()

def test_add_call_command():
    with patch("amocrm.commands.calls.CallsResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.add.return_value = [{"id": 1}]
        with patch("amocrm.commands.calls.AmoCRMClient"):
            result = runner.invoke(app, [
                "add",
                "--direction", "inbound",
                "--duration", "60",
                "--source", "Telephony",
                "--phone", "+79001234567",
                "--call-status", "4",
                "--responsible-user-id", "1",
            ])
    assert result.exit_code == 0
    call_body = mock_resource.add.call_args[0][0][0]
    assert call_body["direction"] == "inbound"
    assert call_body["duration"] == 60
    assert call_body["call_status"] == 4
```

- [ ] **Step 2: Run — expect FAIL**

- [ ] **Step 3: Implement**

```python
# amocrm/commands/calls.py
"""CLI commands for calls resource."""
from __future__ import annotations

from typing import Optional

import typer

from amocrm.client import AmoCRMClient
from amocrm.commands.output import render
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError
from amocrm.resources.calls import CallsResource

app = typer.Typer(name="calls", help="Log calls")


@app.command("add")
def add_call(
    direction: str = typer.Option(..., "--direction", help="inbound or outbound"),
    duration: int = typer.Option(..., "--duration", help="Duration in seconds"),
    source: str = typer.Option(..., "--source", help="Call source name"),
    phone: str = typer.Option(..., "--phone", help="Phone number"),
    call_status: int = typer.Option(..., "--call-status", help="1=no answer, 2=busy, 3=rejected, 4=answered, 5=unknown, 6=voicemail"),
    responsible_user_id: int = typer.Option(..., "--responsible-user-id"),
    link: Optional[str] = typer.Option(None, "--link", help="Recording URL"),
    call_result: Optional[str] = typer.Option(None, "--call-result"),
    created_at: Optional[int] = typer.Option(None, "--created-at", help="Unix timestamp"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Log a call."""
    try:
        data: dict[str, object] = {
            "direction": direction,
            "duration": duration,
            "source": source,
            "phone": phone,
            "call_status": call_status,
            "responsible_user_id": responsible_user_id,
        }
        if link is not None:
            data["link"] = link
        if call_result is not None:
            data["call_result"] = call_result
        if created_at is not None:
            data["created_at"] = created_at
        resource = CallsResource(AmoCRMClient())
        results = resource.add([data])
        render(results, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
```

- [ ] **Step 4: Run — expect PASS**

- [ ] **Step 5: Register** — add to `amocrm/app.py`, `amocrm/resources/__init__.py`, `amocrm/__init__.py`

- [ ] **Step 6: Commit**

---

## Wave 4 — Unsorted

Unsorted leads (`/api/v4/leads/unsorted`) are leads that haven't been assigned to a pipeline yet — they come from forms, chats, callbacks. Besides standard CRUD there are two special actions:

- **`accept`** — moves unsorted leads into a pipeline: `PATCH /api/v4/leads/unsorted/accept`
  - Body: `[{"uid": "...", "status_id": 123, "pipeline_id": 456}]`
  - Returns `{"_embedded": {"unsorted": [...]}}`
- **`decline`** — rejects unsorted leads: `PATCH /api/v4/leads/unsorted/decline`
  - Body: `[{"uid": "..."}]`

The `uid` field (string UUID) is the identifier for unsorted leads, not an integer `id`. The `get` endpoint uses uid: `GET /api/v4/leads/unsorted/{uid}`.

`BaseResource.get(id: int)` won't work for string UIDs — `UnsortedResource` needs its own `get(uid: str)` method.

---

### Task 4A: `UnsortedResource`

**Files:**
- Create: `amocrm/resources/unsorted.py`
- Create: `tests/test_resources/test_unsorted.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_resources/test_unsorted.py
import respx
import httpx
import pytest
from amocrm.client import AmoCRMClient
from amocrm.resources.unsorted import UnsortedResource
from amocrm.exceptions import EntityNotFoundError

SAMPLE_UID = "abc123def456"
SAMPLE_UNSORTED = {"uid": SAMPLE_UID, "source_uid": "src1", "pipeline_id": 100}

@pytest.fixture
def client():
    return AmoCRMClient(subdomain="testco", access_token="test-token")

@pytest.fixture
def resource(client):
    return UnsortedResource(client)

@respx.mock
def test_list_returns_unsorted(resource):
    respx.get("https://testco.amocrm.ru/api/v4/leads/unsorted").mock(
        return_value=httpx.Response(200, json={"_embedded": {"unsorted": [SAMPLE_UNSORTED]}})
    )
    result = resource.list()
    assert result == [SAMPLE_UNSORTED]

@respx.mock
def test_get_by_uid(resource):
    respx.get(f"https://testco.amocrm.ru/api/v4/leads/unsorted/{SAMPLE_UID}").mock(
        return_value=httpx.Response(200, json=SAMPLE_UNSORTED)
    )
    result = resource.get_by_uid(SAMPLE_UID)
    assert result["uid"] == SAMPLE_UID

@respx.mock
def test_get_204_raises_not_found(resource):
    respx.get(f"https://testco.amocrm.ru/api/v4/leads/unsorted/notexist").mock(
        return_value=httpx.Response(204)
    )
    with pytest.raises(EntityNotFoundError):
        resource.get_by_uid("notexist")

@respx.mock
def test_add_unsorted(resource):
    respx.post("https://testco.amocrm.ru/api/v4/leads/unsorted").mock(
        return_value=httpx.Response(200, json={"_embedded": {"unsorted": [SAMPLE_UNSORTED]}})
    )
    result = resource.add([{"source_uid": "src1", "pipeline_id": 100}])
    assert result == [SAMPLE_UNSORTED]

@respx.mock
def test_accept(resource):
    respx.patch("https://testco.amocrm.ru/api/v4/leads/unsorted/accept").mock(
        return_value=httpx.Response(200, json={"_embedded": {"unsorted": [SAMPLE_UNSORTED]}})
    )
    result = resource.accept([{"uid": SAMPLE_UID, "status_id": 10, "pipeline_id": 100}])
    assert result == [SAMPLE_UNSORTED]

@respx.mock
def test_decline(resource):
    respx.patch("https://testco.amocrm.ru/api/v4/leads/unsorted/decline").mock(
        return_value=httpx.Response(200, json={"_embedded": {"unsorted": [SAMPLE_UNSORTED]}})
    )
    result = resource.decline([{"uid": SAMPLE_UID}])
    assert result == [SAMPLE_UNSORTED]
```

- [ ] **Step 2: Run — expect FAIL**

- [ ] **Step 3: Implement**

```python
# amocrm/resources/unsorted.py
"""UnsortedResource for AmoCRM API v4."""
from __future__ import annotations

from typing import Any, ClassVar, List, cast

from amocrm.resources.base import BaseResource

__all__ = ["UnsortedResource"]


class UnsortedResource(BaseResource):
    path: ClassVar[str] = "/leads/unsorted"
    embedded_key: ClassVar[str] = "unsorted"

    def get_by_uid(self, uid: str) -> dict[str, Any]:
        """Get an unsorted lead by its string UID (not integer id)."""
        result = self.client.get(f"{self.path}/{uid}")
        return cast(dict[str, Any], result)

    def add(self, items: List[dict[str, Any]]) -> List[dict[str, Any]]:
        """Create unsorted leads (POST /leads/unsorted)."""
        return self.create(items)

    def accept(self, items: List[dict[str, Any]]) -> List[dict[str, Any]]:
        """Accept unsorted leads into a pipeline.
        Each item: {"uid": "...", "status_id": int, "pipeline_id": int}
        """
        response = self.client.patch(f"{self.path}/accept", json=items)
        if isinstance(response, dict):
            embedded = response.get("_embedded", {})
            return cast(List[dict[str, Any]], embedded.get(self.embedded_key, []))
        return []

    def decline(self, items: List[dict[str, Any]]) -> List[dict[str, Any]]:
        """Decline (reject) unsorted leads.
        Each item: {"uid": "..."}
        """
        response = self.client.patch(f"{self.path}/decline", json=items)
        if isinstance(response, dict):
            embedded = response.get("_embedded", {})
            return cast(List[dict[str, Any]], embedded.get(self.embedded_key, []))
        return []
```

- [ ] **Step 4: Run — expect PASS**
- [ ] **Step 5: Commit**

---

### Task 4B: `unsorted` CLI commands

**Files:**
- Create: `amocrm/commands/unsorted.py`
- Create: `tests/test_commands/test_unsorted.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_commands/test_unsorted.py
import json
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from amocrm.commands.unsorted import app
from amocrm.exceptions import EntityNotFoundError

runner = CliRunner()
SAMPLE_UNSORTED = {"uid": "abc123", "source_uid": "src1", "pipeline_id": 100}

def test_list_command():
    with patch("amocrm.commands.unsorted.UnsortedResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.list.return_value = [SAMPLE_UNSORTED]
        with patch("amocrm.commands.unsorted.AmoCRMClient"):
            result = runner.invoke(app, ["list", "--output", "json"])
    assert result.exit_code == 0

def test_get_command():
    with patch("amocrm.commands.unsorted.UnsortedResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get_by_uid.return_value = SAMPLE_UNSORTED
        with patch("amocrm.commands.unsorted.AmoCRMClient"):
            result = runner.invoke(app, ["get", "abc123", "--output", "json"])
    assert result.exit_code == 0
    mock_resource.get_by_uid.assert_called_once_with("abc123")

def test_accept_command():
    with patch("amocrm.commands.unsorted.UnsortedResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.accept.return_value = [SAMPLE_UNSORTED]
        with patch("amocrm.commands.unsorted.AmoCRMClient"):
            result = runner.invoke(app, ["accept", "abc123", "--pipeline-id", "100", "--status-id", "10"])
    assert result.exit_code == 0
    mock_resource.accept.assert_called_once_with([{"uid": "abc123", "pipeline_id": 100, "status_id": 10}])

def test_decline_command():
    with patch("amocrm.commands.unsorted.UnsortedResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.decline.return_value = [SAMPLE_UNSORTED]
        with patch("amocrm.commands.unsorted.AmoCRMClient"):
            result = runner.invoke(app, ["decline", "abc123"])
    assert result.exit_code == 0
    mock_resource.decline.assert_called_once_with([{"uid": "abc123"}])

def test_get_not_found():
    with patch("amocrm.commands.unsorted.UnsortedResource") as mock_cls:
        mock_resource = MagicMock()
        mock_cls.return_value = mock_resource
        mock_resource.get_by_uid.side_effect = EntityNotFoundError("/leads/unsorted/nope")
        with patch("amocrm.commands.unsorted.AmoCRMClient"):
            result = runner.invoke(app, ["get", "nope"])
    assert result.exit_code == 1
```

- [ ] **Step 2: Run — expect FAIL**

- [ ] **Step 3: Implement**

```python
# amocrm/commands/unsorted.py
"""CLI commands for unsorted leads."""
from __future__ import annotations

import json
from typing import Optional

import typer

from amocrm.client import AmoCRMClient
from amocrm.commands.output import render
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError
from amocrm.resources.unsorted import UnsortedResource

app = typer.Typer(name="unsorted", help="Manage unsorted leads")


def _get_resource() -> UnsortedResource:
    return UnsortedResource(AmoCRMClient())


@app.command("list")
def list_unsorted(
    page: int = typer.Option(1, "--page"),
    limit: int = typer.Option(50, "--limit"),
    filter: Optional[str] = typer.Option(None, "--filter", help="JSON filter string"),
    output: str = typer.Option("table", "--output"),
    columns: Optional[str] = typer.Option(None, "--columns"),
) -> None:
    """List unsorted leads."""
    try:
        filters = json.loads(filter) if filter else None
        cols = columns.split(",") if columns else None
        results = _get_resource().list(page=page, limit=limit, filters=filters)
        render(results, output=output, columns=cols)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
    except json.JSONDecodeError:
        typer.echo("Invalid JSON in --filter", err=True)
        raise typer.Exit(1)


@app.command("get")
def get_unsorted(
    uid: str = typer.Argument(..., help="Unsorted lead UID"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Get an unsorted lead by UID."""
    try:
        result = _get_resource().get_by_uid(uid)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("accept")
def accept_unsorted(
    uid: str = typer.Argument(..., help="Unsorted lead UID"),
    pipeline_id: int = typer.Option(..., "--pipeline-id"),
    status_id: int = typer.Option(..., "--status-id"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Accept an unsorted lead into a pipeline."""
    try:
        results = _get_resource().accept([{"uid": uid, "pipeline_id": pipeline_id, "status_id": status_id}])
        render(results, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("decline")
def decline_unsorted(
    uid: str = typer.Argument(..., help="Unsorted lead UID"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Decline (reject) an unsorted lead."""
    try:
        results = _get_resource().decline([{"uid": uid}])
        render(results, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
```

- [ ] **Step 4: Run — expect PASS**

- [ ] **Step 5: Register** — add to `amocrm/app.py`, `amocrm/resources/__init__.py`, `amocrm/__init__.py`

- [ ] **Step 6: Commit**

---

## Wave 5 — Final Registration

### Task 5A: Register all new resources and run full suite

- [ ] **Step 1: Update `amocrm/resources/__init__.py`** — add imports and `__all__` entries for:
  - `LossReasonsResource`
  - `CallsResource`
  - `UnsortedResource`

- [ ] **Step 2: Update `amocrm/__init__.py`** — same three classes

- [ ] **Step 3: Update `amocrm/app.py`** — verify all three new command groups are registered (should already be done in prior tasks, double-check):
  ```python
  from amocrm.commands.loss_reasons import app as loss_reasons_app
  from amocrm.commands.calls import app as calls_app
  from amocrm.commands.unsorted import app as unsorted_app
  # ...
  app.add_typer(loss_reasons_app, name="loss-reasons")
  app.add_typer(calls_app, name="calls")
  app.add_typer(unsorted_app, name="unsorted")
  ```

- [ ] **Step 4: Run full suite** (`pytest -q`) — all tests must pass

- [ ] **Step 5: Lint + type check** (`ruff check . && mypy amocrm/`) — zero errors

- [ ] **Step 6: Final commit** (`git commit -m "feat: complete standard AmoCRM API v4 coverage"`)

---

## Notes for Implementer

- The `accept` and `decline` paths (`/leads/unsorted/accept`, `/leads/unsorted/decline`) end in a word, not a number — `_is_single_resource_path()` in `client.py` returns False for these, so 204 on PATCH returns `[]` (correct behavior).
- `CallsResource.add()` is just an alias for `create()` — it exists for semantic clarity in library usage (`calls.add(...)` reads better than `calls.create(...)`).
- `UnsortedResource.get_by_uid()` bypasses `BaseResource.get(id: int)` because UIDs are strings. The pattern mirrors `AccountResource.get()`.
- All mypy strict rules apply. If you add `list[...]` annotations inside a class that defines a method named `list`, use `List` from `typing` instead (see CLAUDE.md mypy section).
