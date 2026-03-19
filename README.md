# amocrm-cli

Инструмент командной строки и Python-библиотека для AmoCRM API v4.

```bash
amocrm leads list --output table
amocrm contacts get 12345
amocrm files upload report.pdf
```

## Зачем

У AmoCRM нет официального CLI. Этот инструмент его заменяет — автоматизируйте рутину из терминала, пишите скрипты или подключайте как Python-библиотеку.

Поддерживает весь API: сделки, контакты, компании, задачи, заметки, воронки, теги, поля, каталоги, звонки, файлы, чаты, вебхуки, события и многое другое.

## Установка

```bash
git clone https://github.com/mikekonoval/amocrm-cli
cd amocrm-cli
pip install .
```

Требуется Python 3.11+.

## Быстрый старт

```bash
# Токен генерируется в AmoCRM → amoМаркет → Создать интеграцию → Внешняя интеграция
amocrm auth login --token <токен> --subdomain mycompany
amocrm auth status

# Список сделок
amocrm leads list

# Создать сделку
amocrm leads create --name "Новая сделка" --price 50000

# Загрузить файл
amocrm files upload report.pdf
```

## Использование в коде

```python
from amocrm import AmoCRMClient
from amocrm.resources import LeadsResource

client = AmoCRMClient(subdomain="yoursubdomain", access_token="your_token")
leads = LeadsResource(client)

results = leads.list(filters={"pipeline_id": [1]}, order="created_at:desc")
lead = leads.get(12345)
leads.update(12345, {"price": 60000})
```

## Документация

Полный справочник команд и API: [docs/reference.md](docs/reference.md)

## Разработка

```bash
pip install -e ".[dev]"
pytest
ruff check .
mypy amocrm/
```
