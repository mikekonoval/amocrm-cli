# amocrm-cli

AmoCRM API v4 — CLI tool and Python library.

```bash
amocrm leads list --output table
amocrm contacts get 12345 --output json
amocrm files upload report.pdf
```

## Install

```bash
pip install -e ".[dev]"   # with dev dependencies (pytest, mypy, ruff)
pip install -e .           # production only
```

Requires Python 3.11+.

## Authentication

### Long-lived token (simple)

Generate a long-lived token in your AmoCRM account under **Settings → Integrations → API**.

```bash
amocrm auth login --token <token> --subdomain mycompany
amocrm auth status
```

### OAuth 2.0 (required for Chats API)

```bash
amocrm auth login --oauth --subdomain mycompany \
  --client-id <id> --client-secret <secret>
```

Credentials are stored in `~/.amocrm/config.json`.

```bash
amocrm auth status    # show current auth state
amocrm auth logout    # remove credentials
```

## CLI Reference

### Leads

```bash
amocrm leads list [--page N] [--limit N] [--filter '{"pipeline_id":[1]}'] [--order created_at:desc] [--output table|json|csv] [--columns id,name,price]
amocrm leads get <id> [--with contacts,companies]
amocrm leads create --name "Deal name" [--price N] [--pipeline-id N] [--status-id N] [--responsible-user-id N]
amocrm leads update <id> [--name ...] [--price N] [--status-id N]
amocrm leads delete <id>
```

### Contacts

```bash
amocrm contacts list [--page N] [--limit N] [--filter JSON] [--output ...]
amocrm contacts get <id>
amocrm contacts create --name "John Doe" [--email addr] [--phone +7...]
amocrm contacts update <id> [--name ...] [--email ...] [--phone ...]
amocrm contacts delete <id>
```

### Companies

```bash
amocrm companies list / get <id> / create --name "..." / update <id> --name "..." / delete <id>
```

### Tasks

```bash
amocrm tasks list [--filter JSON]
amocrm tasks get <id>
amocrm tasks create --text "Call back" --complete-till <unix_ts> [--entity-id N] [--entity-type leads]
amocrm tasks update <id> [--text ...] [--complete-till N] [--is-completed true]
amocrm tasks delete <id>
```

### Notes

```bash
amocrm notes list --entity leads [--entity-id N]
amocrm notes get <id> --entity leads
amocrm notes create --entity leads --entity-id <id> --text "Note text"
amocrm notes update <id> --entity leads --entity-id <id> --text "Updated"
amocrm notes delete <id> --entity leads
```

### Pipelines & Stages

```bash
amocrm pipelines list / get <id>
amocrm pipelines create --name "Pipeline" --is-unsorted-on true
amocrm pipelines update <id> --name "..."
amocrm pipelines delete <id>
amocrm pipelines stages list <pipeline_id>
amocrm pipelines stages create <pipeline_id> --name "Stage" --color "#fffeb2"
amocrm pipelines stages update <pipeline_id> <stage_id> --name "..."
amocrm pipelines stages delete <pipeline_id> <stage_id>
```

### Tags

```bash
amocrm tags list --entity leads|contacts|companies
amocrm tags get <id> --entity leads
amocrm tags create --entity leads --name "VIP"
amocrm tags update <id> --entity leads --name "..."
amocrm tags delete <id> --entity leads
```

### Custom Fields

```bash
amocrm custom-fields list --entity leads
amocrm custom-fields get <id> --entity leads
amocrm custom-fields create --entity leads --name "Budget" --type text
amocrm custom-fields delete <id> --entity leads

# Field types: text, numeric, checkbox, select, multiselect, date, url, textarea, radiobutton

amocrm custom-fields groups list --entity leads
amocrm custom-fields groups get <id> --entity leads
```

### Catalogs (product lists)

```bash
amocrm catalogs list / get <id> / create --name "Products" / delete <id>
amocrm catalogs elements list <catalog_id>
amocrm catalogs elements get <catalog_id> <id>
amocrm catalogs elements create <catalog_id> --name "Item"
amocrm catalogs elements update <catalog_id> <id> --name "Updated Item"
```

### Loss Reasons

```bash
amocrm loss-reasons list / get <id> / create --name "Too expensive" / update <id> --name "..." / delete <id>
```

### Calls

```bash
# Log a call (phone must match an existing contact/lead)
amocrm calls add \
  --direction inbound|outbound \
  --duration <seconds> \
  --source "Telephony name" \
  --phone "+79001234567" \
  --call-status 4 \          # 1=no answer, 2=busy, 3=rejected, 4=answered, 5=unknown, 6=voicemail
  --responsible-user-id <id> \
  [--link "https://recording.url"] \
  [--created-at <unix_ts>]
```

### Unsorted (inbox)

```bash
amocrm unsorted list [--page N] [--limit N]
amocrm unsorted get <uid>
amocrm unsorted accept --uid <uid> --user-id <id>
amocrm unsorted decline --uid <uid>
```

### Files (Drive)

```bash
amocrm files list [--page N] [--limit N]
amocrm files get <uuid>
amocrm files upload /path/to/file.pdf
amocrm files download <uuid> -o /path/to/output.pdf
amocrm files delete <uuid>
```

Large files are uploaded in chunks automatically (max 512 KB per chunk).

### Chats (amojo API)

Requires OAuth authentication with `client_secret`.

```bash
# Get your account_chat_id first:
amocrm account get --with amojo_id   # use the amojo_id field

amocrm chats connect <account_chat_id> --title "My Bot" --hook-url "https://example.com/webhook"
amocrm chats create <account_chat_id> --source-uid "ext-chat-001" [--contact-id N]
amocrm chats send <account_chat_id> <chat_id> --text "Hello" --sender-id "u1" --sender-name "Bot"
amocrm chats disconnect <account_chat_id>
```

### Webhooks

```bash
amocrm webhooks list
amocrm webhooks subscribe --url "https://myapp.com/hook" --event add_lead --event update_lead
amocrm webhooks unsubscribe --url "https://myapp.com/hook"
```

### Events

```bash
amocrm events list [--filter JSON] [--limit N]   # max 100 per request
```

### Account

```bash
amocrm account get [--with amojo_id]
```

### Users

```bash
amocrm users list / get <id>
```

## Global output options

All list/get commands support:

| Flag | Values | Default |
|------|--------|---------|
| `--output` | `table`, `json`, `csv` | `table` |
| `--columns` | comma-separated field names | all |
| `--page` | integer | 1 |
| `--limit` | integer | 50 |

## Library usage

```python
from amocrm import AmoCRMClient, AmoCRMAPIError, EntityNotFoundError
from amocrm.resources import LeadsResource, ContactsResource, FilesResource

# Long-lived token
client = AmoCRMClient(subdomain="mycompany", access_token="xxx")

# Full OAuth with proactive token refresh
client = AmoCRMClient(
    subdomain="mycompany",
    access_token="xxx",
    refresh_token="yyy",
    client_id="zzz",
    client_secret="aaa",
    expires_at=1234567890,
)

leads = LeadsResource(client)
results = leads.list(filters={"pipeline_id": [1]}, order="created_at:desc", limit=10)

try:
    lead = leads.get(12345)
except EntityNotFoundError:
    print("not found")

new_leads = leads.create([{"name": "Deal", "price": 50000}])
leads.update(12345, {"price": 60000})

# Files
from amocrm.resources import FilesResource
files = FilesResource(client)
file_meta = files.upload("report.pdf")
print(file_meta["uuid"])
content = files.download(file_meta["uuid"])
```

All resources: `LeadsResource`, `ContactsResource`, `CompaniesResource`, `TasksResource`, `NotesResource`, `PipelinesResource`, `StagesResource`, `TagsResource`, `CustomFieldsResource`, `CustomFieldGroupsResource`, `CatalogsResource`, `CatalogElementsResource`, `LossReasonsResource`, `CallsResource`, `UnsortedResource`, `FilesResource`, `ChatsResource`, `WebhooksResource`, `EventsResource`, `AccountResource`, `UsersResource`.

## Development

```bash
pip install -e ".[dev]"
pytest                          # all tests
pytest tests/test_resources/    # resource tests only
pytest -k test_list_leads       # single test
ruff check .                    # lint
mypy amocrm/                    # type check (strict)
```

Tests use `respx` to mock HTTP — no real API calls needed.
