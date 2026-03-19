# Справочник команд

## Авторизация

### Долгосрочный токен

Токен генерируется в AmoCRM: **amoМаркет → Создать интеграцию → Внешняя интеграция**.

```bash
amocrm auth login --token <токен> --subdomain yoursubdomain
amocrm auth status
amocrm auth logout
```

### OAuth 2.0 (нужен для Chats API)

```bash
amocrm auth login --oauth --subdomain yoursubdomain \
  --client-id <id> --client-secret <secret>
```

Учётные данные хранятся в `~/.amocrm/config.json`.

---

## Общие флаги вывода

Доступны во всех командах list/get:

| Флаг | Значения | По умолчанию |
|------|----------|--------------|
| `--output` | `table`, `json`, `csv` | `table` |
| `--columns` | поля через запятую | все |
| `--page` | целое число | 1 |
| `--limit` | целое число | 50 |

---

## Сделки

```bash
amocrm leads list [--page N] [--limit N] [--filter '{"pipeline_id":[1]}'] [--order created_at:desc] [--output table|json|csv] [--columns id,name,price]
amocrm leads get <id> [--with contacts,companies]
amocrm leads create --name "Название" [--price N] [--pipeline-id N] [--status-id N] [--responsible-user-id N]
amocrm leads update <id> [--name ...] [--price N] [--status-id N]
amocrm leads delete <id>
```

## Контакты

```bash
amocrm contacts list [--page N] [--limit N] [--filter JSON] [--output ...]
amocrm contacts get <id>
amocrm contacts create --name "Иван Иванов" [--email addr] [--phone +7...]
amocrm contacts update <id> [--name ...] [--email ...] [--phone ...]
amocrm contacts delete <id>
```

## Компании

```bash
amocrm companies list / get <id> / create --name "..." / update <id> --name "..." / delete <id>
```

## Задачи

```bash
amocrm tasks list [--filter JSON]
amocrm tasks get <id>
amocrm tasks create --text "Перезвонить" --complete-till <unix_ts> [--entity-id N] [--entity-type leads]
amocrm tasks update <id> [--text ...] [--complete-till N] [--is-completed true]
amocrm tasks delete <id>
```

## Заметки

```bash
amocrm notes list --entity leads [--entity-id N]
amocrm notes get <id> --entity leads
amocrm notes create --entity leads --entity-id <id> --text "Текст заметки"
amocrm notes update <id> --entity leads --entity-id <id> --text "Обновлённый текст"
amocrm notes delete <id> --entity leads
```

## Воронки и этапы

```bash
amocrm pipelines list / get <id>
amocrm pipelines create --name "Воронка" --is-unsorted-on true
amocrm pipelines update <id> --name "..."
amocrm pipelines delete <id>
amocrm pipelines stages list <pipeline_id>
amocrm pipelines stages create <pipeline_id> --name "Этап" --color "#fffeb2"
amocrm pipelines stages update <pipeline_id> <stage_id> --name "..."
amocrm pipelines stages delete <pipeline_id> <stage_id>
```

## Теги

```bash
amocrm tags list --entity leads|contacts|companies
amocrm tags get <id> --entity leads
amocrm tags create --entity leads --name "VIP"
amocrm tags update <id> --entity leads --name "..."
amocrm tags delete <id> --entity leads
```

## Пользовательские поля

```bash
amocrm custom-fields list --entity leads
amocrm custom-fields get <id> --entity leads
amocrm custom-fields create --entity leads --name "Бюджет" --type text
amocrm custom-fields delete <id> --entity leads

# Типы полей: text, numeric, checkbox, select, multiselect, date, url, textarea, radiobutton

amocrm custom-fields groups list --entity leads
amocrm custom-fields groups get <id> --entity leads
```

## Каталоги

```bash
amocrm catalogs list / get <id> / create --name "Товары" / delete <id>
amocrm catalogs elements list <catalog_id>
amocrm catalogs elements get <catalog_id> <id>
amocrm catalogs elements create <catalog_id> --name "Товар"
amocrm catalogs elements update <catalog_id> <id> --name "Обновлённый товар"
```

## Причины отказа

```bash
amocrm loss-reasons list / get <id> / create --name "Дорого" / update <id> --name "..." / delete <id>
```

## Звонки

```bash
# Телефон должен совпадать с номером существующего контакта
amocrm calls add \
  --direction inbound|outbound \
  --duration <секунды> \
  --source "Название телефонии" \
  --phone "+79001234567" \
  --call-status 4 \
  --responsible-user-id <id> \
  [--link "https://запись.url"] \
  [--created-at <unix_ts>]

# Статусы: 1=не ответили, 2=занято, 3=отклонён, 4=отвечен, 5=неизвестно, 6=голосовая почта
```

## Неразобранное

```bash
amocrm unsorted list [--page N] [--limit N]
amocrm unsorted get <uid>
amocrm unsorted accept --uid <uid> --user-id <id>
amocrm unsorted decline --uid <uid>
```

## Файлы

```bash
amocrm files list [--page N] [--limit N]
amocrm files get <uuid>
amocrm files upload /путь/к/файлу.pdf
amocrm files download <uuid> -o /путь/к/выходному.pdf
amocrm files delete <uuid>
```

Большие файлы загружаются частями автоматически (максимум 512 КБ на часть).

## Чаты (amojo API)

Требуется OAuth с `client_secret`.

```bash
# Сначала узнайте account_chat_id:
amocrm account get --with amojo_id   # поле amojo_id

amocrm chats connect <account_chat_id> --title "Мой бот" --hook-url "https://example.com/webhook"
amocrm chats create <account_chat_id> --source-uid "ext-chat-001" [--contact-id N]
amocrm chats send <account_chat_id> <chat_id> --text "Привет" --sender-id "u1" --sender-name "Бот"
amocrm chats disconnect <account_chat_id>
```

## Вебхуки

```bash
amocrm webhooks list
amocrm webhooks subscribe --url "https://myapp.com/hook" --event add_lead --event update_lead
amocrm webhooks unsubscribe --url "https://myapp.com/hook"
```

## События

```bash
amocrm events list [--filter JSON] [--limit N]   # максимум 100 за запрос
```

## Аккаунт

```bash
amocrm account get [--with amojo_id]
```

## Пользователи

```bash
amocrm users list / get <id>
```

---

## Python API

```python
from amocrm import AmoCRMClient, AmoCRMAPIError, EntityNotFoundError
from amocrm.resources import LeadsResource, ContactsResource, FilesResource

# Долгосрочный токен
client = AmoCRMClient(subdomain="yoursubdomain", access_token="your_token")

# OAuth с автообновлением токена
client = AmoCRMClient(
    subdomain="yoursubdomain",
    access_token="your_token",
    refresh_token="your_refresh_token",
    client_id="your_client_id",
    client_secret="your_client_secret",
    expires_at=1234567890,
)

leads = LeadsResource(client)
results = leads.list(filters={"pipeline_id": [1]}, order="created_at:desc", limit=10)

try:
    lead = leads.get(12345)
except EntityNotFoundError:
    print("не найдено")

leads.create([{"name": "Сделка", "price": 50000}])
leads.update(12345, {"price": 60000})

# Файлы
files = FilesResource(client)
file_meta = files.upload("report.pdf")
content = files.download(file_meta["uuid"])
```

Все классы ресурсов: `LeadsResource`, `ContactsResource`, `CompaniesResource`, `TasksResource`, `NotesResource`, `PipelinesResource`, `StagesResource`, `TagsResource`, `CustomFieldsResource`, `CustomFieldGroupsResource`, `CatalogsResource`, `CatalogElementsResource`, `LossReasonsResource`, `CallsResource`, `UnsortedResource`, `FilesResource`, `ChatsResource`, `WebhooksResource`, `EventsResource`, `AccountResource`, `UsersResource`.
