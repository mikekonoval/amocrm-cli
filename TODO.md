# TODO

## После сборки — протестировать на реальном аккаунте

- [ ] Создать бесплатный trial на amocrm.ru (14 дней)
- [ ] Получить long-lived token в настройках интеграции
- [ ] Авторизоваться в CLI:
  ```bash
  amocrm auth login --token <token> --subdomain <subdomain>
  amocrm auth status
  ```
- [ ] Smoke-тесты CLI:
  ```bash
  amocrm account info
  amocrm leads list --output json
  amocrm contacts list --limit 5
  amocrm pipelines list
  amocrm tasks list
  amocrm notes list --entity leads
  amocrm leads create --name "Test Lead" --price 1000
  ```
- [ ] Smoke-тест библиотеки:
  ```python
  from amocrm import AmoCRMClient, LeadsResource
  client = AmoCRMClient(subdomain="...", access_token="...")
  leads = LeadsResource(client)
  print(leads.list(limit=3))
  ```
