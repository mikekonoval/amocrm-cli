---
name: amocrm-cli
description: Use when working with the AmoCRM CLI tool or library, AmoCRM API wrapper, or when adding resources/commands. Trigger on "amocrm", "amoCRM API", "add resource", "CLI command for amoCRM".
---

# AmoCRM CLI Skill

Comprehensive reference for the AmoCRM CLI tool — a lightweight Python wrapper around the AmoCRM API v4, available as both a CLI tool and an importable library.

## 1. CLI Reference

### Authentication

```bash
# Login with a long-lived token (recommended for scripts)
amocrm auth login --token YOUR_LONG_LIVED_TOKEN --subdomain mycompany

# Login with OAuth 2.0 (opens browser, recommended for interactive use)
amocrm auth login --oauth --subdomain mycompany

# Check current auth status
amocrm auth status

# Logout (clears stored credentials)
amocrm auth logout
```

### Leads

```bash
# List all leads (paginated)
amocrm leads list

# List with pagination and filtering
amocrm leads list --page 1 --limit 50 --filter '{"pipeline_id": [5]}' --order "created_at:desc"

# Get a specific lead by ID
amocrm leads get 123

# Get lead with related entities
amocrm leads get 123 --with contacts,tasks

# Create a new lead
amocrm leads create --name "New Deal" --price 50000 --pipeline-id 100

# Delete a lead
amocrm leads delete 123

# Output formatting
amocrm leads list --output json                    # JSON
amocrm leads list --output csv                     # CSV
amocrm leads list --columns id,name,price          # Show specific columns
```

### Contacts

```bash
# List all contacts
amocrm contacts list [--page 1] [--limit 50]

# Search contacts by query
amocrm contacts list --filter '{"query": "John"}'

# Get a specific contact by ID
amocrm contacts get 456

# Create a new contact
amocrm contacts create --name "John Doe"

# Create with email
amocrm contacts create --name "Jane Smith" --email "jane@example.com"

# Delete a contact
amocrm contacts delete 456
```

### Companies

```bash
# List all companies
amocrm companies list [--page 1] [--limit 50]

# Get a specific company by ID
amocrm companies get 789

# Create a new company
amocrm companies create --name "Acme Corp"

# Delete a company
amocrm companies delete 789
```

### Tasks

```bash
# List all tasks
amocrm tasks list [--page 1] [--limit 50]

# Get a specific task by ID
amocrm tasks get 111

# Create a new task
amocrm tasks create --text "Follow up with client" --complete-till 1700000000

# Delete a task
amocrm tasks delete 111
```

### Notes

```bash
# List notes on a lead
amocrm notes list --entity leads --entity-id 123

# List notes on a contact
amocrm notes list --entity contacts --entity-id 456

# Get a specific note by ID
amocrm notes get 222 --entity leads --entity-id 123

# Create a note on a lead
amocrm notes create --entity leads --entity-id 123 --text "Call done, schedule follow-up"

# Delete a note
amocrm notes delete 222 --entity leads --entity-id 123
```

### Pipelines & Stages

```bash
# List all pipelines
amocrm pipelines list [--page 1] [--limit 50]

# Get a specific pipeline by ID
amocrm pipelines get 100

# List stages in a pipeline
amocrm pipelines stages list 100

# Get a specific stage in a pipeline
amocrm pipelines stages get 100 333
```

### Users & Roles

```bash
# List all users
amocrm users list [--page 1] [--limit 50]

# Get a specific user by ID
amocrm users get 555

# List all roles
amocrm users roles list [--page 1] [--limit 50]

# Get a specific role by ID
amocrm users roles get 666
```

### Tags

```bash
# List tags on leads
amocrm tags list --entity leads [--page 1] [--limit 50]

# List tags on contacts
amocrm tags list --entity contacts

# Get a specific tag by ID
amocrm tags get 777 --entity leads

# Create a tag on leads
amocrm tags create --entity leads --name "VIP" --color "#ff0000"

# Delete a tag
amocrm tags delete 777 --entity leads
```

### Custom Fields

```bash
# List custom fields for leads
amocrm custom-fields list --entity leads [--page 1] [--limit 50]

# List custom fields for contacts
amocrm custom-fields list --entity contacts

# Get a specific custom field by ID
amocrm custom-fields get 888 --entity leads

# List custom field groups for leads
amocrm custom-fields groups list --entity leads

# Get a specific custom field group by ID
amocrm custom-fields groups get 999 --entity leads
```

### Catalogs & Elements

```bash
# List all catalogs
amocrm catalogs list [--page 1] [--limit 50]

# Get a specific catalog by ID
amocrm catalogs get 1

# List elements in a catalog
amocrm catalogs elements list 1 [--page 1] [--limit 50]

# Get a specific element by ID in a catalog
amocrm catalogs elements get 1 2

# Create an element in a catalog
amocrm catalogs elements create 1 --name "Product A" --cost 100

# Delete an element from a catalog
amocrm catalogs elements delete 1 2
```

### Events

```bash
# List events (max limit is 100)
amocrm events list [--limit 100]

# Events are read-only, most recent first
```

### Webhooks

```bash
# List all webhooks
amocrm webhooks list

# Subscribe to events at a destination URL
amocrm webhooks subscribe --url https://myserver.com/hook --events "leads_add,leads_update,task_add"

# Unsubscribe a webhook by its destination URL
amocrm webhooks unsubscribe --url https://myserver.com/hook
```

### Account

```bash
# Get account information
amocrm account info

# Get account info with additional data
amocrm account info --with "users_groups,task_types"
```

### Global Flags (available on most list commands)

```bash
--page INT              # Page number (default: 1)
--limit INT             # Items per page (default: 50)
--filter JSON           # JSON filter string, e.g. '{"status_id": 142}'
--order FIELD:DIR       # Sort field and direction, e.g. "created_at:desc"
--with CSV              # Comma-separated related entities to include
--output FORMAT         # Output format: table (default), json, csv
--columns CSV           # Comma-separated column names to display
```

## 2. Library Reference

### Basic Setup

```python
from amocrm import (
    AmoCRMClient,
    AmoCRMAPIError,
    EntityNotFoundError,
    LeadsResource,
    ContactsResource,
    # ... and many more
)

# Minimal client — no auto-refresh
client = AmoCRMClient(subdomain="mycompany", access_token="xxx")

# Full client with OAuth refresh capability
client = AmoCRMClient(
    subdomain="mycompany",
    access_token="xxx",
    refresh_token="yyy",
    client_id="zzz",
    client_secret="aaa",
    expires_at=1234567890,  # Unix timestamp; None = reactive refresh on 401 only
)
```

### Resource: Leads

```python
leads = LeadsResource(client)

# List leads
results = leads.list(
    page=1,
    limit=50,
    filters={"pipeline_id": [5]},
    order="created_at:desc",
    with_=["contacts", "tasks"]
)

# Get a single lead
lead = leads.get(123, with_=["contacts"])

# Create leads (array, max 50 at once)
new_leads = leads.create([
    {"name": "Deal A", "price": 50000, "pipeline_id": 100},
    {"name": "Deal B", "price": 75000},
])

# Create with complex nested data (atomic, max 50)
leads.create_complex([
    {
        "name": "Deal C",
        "price": 100000,
        "contacts": [{"id": 456}]  # link existing contacts
    }
])

# Update a lead
updated = leads.update(123, {"price": 60000})

# Delete a lead
leads.delete(123)  # Returns True on success
```

### Resource: Contacts

```python
contacts = ContactsResource(client)

# List contacts
results = contacts.list(page=1, limit=50, filters={"query": "John"})

# Get a single contact
contact = contacts.get(456)

# Create contacts
new_contacts = contacts.create([
    {"name": "John Doe", "email": "john@example.com"},
])

# Update a contact
updated = contacts.update(456, {"name": "Jane Doe"})

# Delete a contact
contacts.delete(456)
```

### Resource: Companies

```python
companies = CompaniesResource(client)

companies.list(page=1, limit=50)
companies.get(789)
companies.create([{"name": "Acme Corp"}])
companies.update(789, {"name": "Acme Inc"})
companies.delete(789)
```

### Resource: Tasks

```python
tasks = TasksResource(client)

tasks.list(page=1, limit=50)
tasks.get(111)
tasks.create([{"text": "Follow up", "complete_till": 1700000000}])
tasks.update(111, {"text": "Updated task"})
tasks.delete(111)
```

### Resource: Notes (Entity-Scoped)

```python
from amocrm import NotesResource

# Notes are scoped to an entity type and optional entity ID
notes = NotesResource(client, entity_type="leads", entity_id=123)

# List notes for a specific lead
results = notes.list(page=1, limit=50)

# Get a specific note
note = notes.get(222)

# Create a note
new_note = notes.create([{"text": "Call completed"}])

# Delete a note
notes.delete(222)

# Scope to entity type only (all notes of that type)
notes_all = NotesResource(client, entity_type="leads")
results = notes_all.list()
```

### Resource: Pipelines & Stages

```python
from amocrm import PipelinesResource, StagesResource

pipelines = PipelinesResource(client)
pipelines.list(page=1, limit=50)
pipelines.get(100)

# Stages are scoped to a pipeline
stages = StagesResource(client, pipeline_id=100)
stages.list()
stages.get(333)
```

### Resource: Users & Roles

```python
from amocrm import UsersResource, RolesResource

users = UsersResource(client)
users.list(page=1, limit=50)
users.get(555)

roles = RolesResource(client)
roles.list(page=1, limit=50)
roles.get(666)
```

### Resource: Tags (Entity-Scoped)

```python
from amocrm import TagsResource

# Tags are scoped to an entity type
tags = TagsResource(client, entity_type="leads")

tags.list(page=1, limit=50)
tags.get(777)
tags.create([{"name": "VIP", "color": "#ff0000"}])
tags.delete(777)
```

### Resource: Custom Fields (Entity-Scoped)

```python
from amocrm import CustomFieldsResource, CustomFieldGroupsResource

# Custom fields scoped to an entity
custom_fields = CustomFieldsResource(client, entity="leads")
custom_fields.list(page=1, limit=50)
custom_fields.get(888)

# Custom field groups
groups = CustomFieldGroupsResource(client, entity="leads")
groups.list(page=1, limit=50)
groups.get(999)
```

### Resource: Catalogs & Elements

```python
from amocrm import CatalogsResource, CatalogElementsResource

catalogs = CatalogsResource(client)
catalogs.list(page=1, limit=50)
catalogs.get(1)

# Elements are scoped to a catalog
elements = CatalogElementsResource(client, catalog_id=1)
elements.list(page=1, limit=50)
elements.get(2)
elements.create([{"name": "Product A", "cost": 100}])
elements.delete(2)
```

### Resource: Events

```python
from amocrm import EventsResource

events = EventsResource(client)
results = events.list(limit=50)  # max 100, silently clamped
# Events are read-only
```

### Resource: Webhooks

```python
from amocrm import WebhooksResource

webhooks = WebhooksResource(client)

# List all webhooks
results = webhooks.list()

# Subscribe to events
webhook = webhooks.subscribe(
    url="https://myserver.com/hook",
    settings=["leads_add", "leads_update", "task_add"]
)

# Unsubscribe — does lookup then delete
# Raises EntityNotFoundError if webhook not found
webhooks.unsubscribe(url="https://myserver.com/hook")
```

### Resource: Account

```python
from amocrm import AccountResource

account = AccountResource(client)

# Get account info
info = account.get()

# Get with additional data
info = account.get(with_=["users_groups", "task_types"])
```

### Error Handling

```python
from amocrm import AmoCRMAPIError, EntityNotFoundError

try:
    lead = leads.get(999)
except EntityNotFoundError as e:
    # Raised on: GET 404/204, DELETE not found
    print(f"Not found at {e.path}")
except AmoCRMAPIError as e:
    # Base class for all API errors
    print(f"API error {e.status}: {e.title}")
    print(f"Detail: {e.detail}")
```

## 3. Adding a New Resource (Step-by-Step)

### Step 1: Create Resource Class

Create `amocrm/resources/{name}.py`:

```python
from amocrm.resources.base import BaseResource

class MyThingResource(BaseResource):
    path = "/my_things"
    embedded_key = "my_things"
```

Key attributes:
- `path`: API endpoint path (e.g., `/leads`, `/contacts`)
- `embedded_key`: HAL `_embedded` key for list responses (usually plural form of resource)

Override methods as needed from `BaseResource`: `list()`, `get()`, `create()`, `update()`, `delete()`.

### Step 2: Create CLI Command File

Create `amocrm/commands/{name}.py`:

```python
from amocrm.client import AmoCRMClient
from amocrm.commands.output import render
from amocrm.resources.my_thing import MyThingResource
import typer

app = typer.Typer(name="my-things", help="Manage my things")

def _get_resource() -> MyThingResource:
    return MyThingResource(AmoCRMClient())

@app.command("list")
def list_things(
    page: int = typer.Option(1, "--page"),
    limit: int = typer.Option(50, "--limit"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """List my things."""
    try:
        resource = _get_resource()
        results = resource.list(page=page, limit=limit)
        render(results, output=output)
    except Exception as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
```

### Step 3: Register in App

Edit `amocrm/app.py`:

```python
from amocrm.commands.my_thing import app as my_thing_app

app.add_typer(my_thing_app, name="my-things")
```

### Step 4: Export from Package

Add to `amocrm/resources/__init__.py` and `amocrm/__init__.py`:

```python
from amocrm.resources.my_thing import MyThingResource

__all__ = [..., "MyThingResource"]
```

### Step 5: Write Tests

`tests/test_resources/test_my_thing.py` (resource layer, using `respx` to mock httpx):

```python
import respx
from amocrm import MyThingResource

@respx.mock
def test_list():
    respx.get("https://mycompany.amocrm.ru/api/v4/my_things").mock(
        return_value=httpx.Response(200, json={
            "_embedded": {"my_things": [{"id": 1, "name": "Thing"}]}
        })
    )
    resource = MyThingResource(client)
    results = resource.list()
    assert len(results) == 1
```

`tests/test_commands/test_my_thing.py` (CLI layer, using CliRunner + monkeypatch):

```python
from typer.testing import CliRunner
from amocrm.commands.my_thing import app

def test_list(monkeypatch):
    def mock_list(*args, **kwargs):
        return [{"id": 1, "name": "Thing"}]

    monkeypatch.setattr("amocrm.commands.my_thing.MyThingResource.list", mock_list)

    runner = CliRunner()
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
```

## 4. Architecture Overview

Three strict isolation layers — no crossing:

1. **`amocrm/resources/`** — Pure Python API functions. No CLI knowledge, no Typer.
   - Each resource: one class subclassing `BaseResource`
   - Override only methods that differ from CRUD defaults
   - No HTTP client directly; uses `self.client` injected in constructor

2. **`amocrm/commands/`** — Typer CLI commands. No httpx, no direct HTTP.
   - Each resource gets one Typer app
   - Calls resource methods, formats output via `output.py`
   - Handles CLI-specific errors and formatting

3. **`amocrm/client.py`** — Single source of HTTP truth.
   - Only file using `httpx`
   - Handles: auth headers, token refresh, retry/backoff (7 req/s), HAL unpacking

4. **`amocrm/exceptions.py`** — Standard exception classes.
   - `AmoCRMAPIError(status, title, detail)` — base for all API errors
   - `EntityNotFoundError(path)` — specific for 404/204 on GET

## 5. Known API Quirks & Gotchas

### HTTP Status Semantics

- **GET 204**: Treat as not found → raise `EntityNotFoundError`
- **PATCH/DELETE 204**: Success, but no body → return `[]` or `True`
- **DELETE success**: Returns `True` (not the deleted object)

### Token & Auth

- **Refresh tokens are single-use**: Save the new pair immediately after every refresh
- **Expires_at**: Unix timestamp. If not provided, refresh happens reactively on 401 only
- **Config file**: `~/.amocrm/config.json` stores subdomain, access_token, refresh_token, client_id, client_secret, expires_at

### Resource-Specific

- **Entity-scoped resources**: `NotesResource`, `TagsResource`, `CustomFieldsResource` take `entity_type` or `entity` in constructor
- **Sub-resources**: `StagesResource`, `CatalogElementsResource`, `RolesResource` take parent ID in constructor
- **Rate limit**: 7 requests per second per integration (client throttles automatically)
- **All timestamps**: Unix integers (seconds since epoch)
- **Pipelines stages path**: `/leads/pipelines/{id}/statuses` (not `/stages/`)
- **Events limit**: Max 100 (silently clamped by `EventsResource.list()`)
- **Webhooks lookup**: `webhooks.unsubscribe(url)` does lookup-then-delete; raises `EntityNotFoundError` if not found
- **Batch operations**: `create()` max 50 items per call; `create_complex()` is resource-layer only (no CLI command)

### HAL Response Unpacking

The client automatically unpacks HAL `_embedded` responses, so you get clean lists of entities, not nested objects.

## 6. Stack & Tools

- **CLI**: Typer
- **HTTP**: httpx
- **Output**: rich (for tables)
- **Testing**: pytest + respx (for mocking httpx)
- **Linting**: ruff
- **Type checking**: mypy

## 7. Common Commands

```bash
# Install with dev deps
pip install -e ".[dev]"

# Run all tests
pytest

# Run single test
pytest tests/test_resources/test_leads.py::test_leads_list

# Lint
ruff check .

# Type check
mypy amocrm/
```
