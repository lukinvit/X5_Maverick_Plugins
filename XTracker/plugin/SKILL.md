---
name: xtracker
description: |
  Работа с issue-трекером XTracker (xtracker.x5team.ru) из чата: поиск, чтение,
  создание, обновление, комментирование, смена статуса и назначение иссью.
  Использовать когда пользователь: "найди задачу/иссью", "мои открытые задачи",
  "заведи баг/задачу", "поменяй статус", "назначь на", "прокомментируй задачу",
  "что по PROJ-123". Поиск — на языке запросов YTQL (status, assignee, queue, type).
  НЕ использовать для: трекеров Jira/GitHub/Yandex, аналитики и дашбордов,
  спринтов и тайм-трекинга (это будущие фазы), произвольных HTTP-запросов.
license: MIT
metadata:
  author: X5 Maverick Plugins
  version: "1.0.1"
  category: integrations
allowed-tools: xtracker__search_issues xtracker__get_issue xtracker__create_issue xtracker__update_issue xtracker__comment_issue xtracker__transition_issue xtracker__assign_issue xtracker__whoami xtracker__config_test_connection
---

# XTracker

Плагин-мост между чатом Jarvis и внутренним issue-трекером X5 **XTracker** (`xtracker.x5team.ru`, класс Jira/YouTrack). Действует под сконфигурированной identity инстанса (сервис-аккаунт по API-ключу или вход по email/паролю); права определяются RBAC самого XTracker.

## Выбор инструмента

| Задача пользователя | Инструмент |
|---|---|
| Найти иссью по условию | `search_issues` |
| Показать детали одной иссью | `get_issue` |
| Завести новую иссью | `create_issue` |
| Изменить поля иссью | `update_issue` |
| Добавить комментарий | `comment_issue` |
| Сменить статус (workflow-переход) | `transition_issue` |
| Назначить/снять исполнителя | `assign_issue` |
| Кто текущий пользователь | `whoami` |
| Проверить подключение | `config_test_connection` |

## Рабочие процессы

### Поиск и просмотр
1. По запросу пользователя сформируй YTQL и вызови `search_issues`. Поле `query` — выражение вида `status = open AND assignee = me()` или `queue = PROJ AND type = bug`. Поле `limit` ограничивает выдачу (по умолчанию 20).
2. Покажи карточки результатов; если пользователь просит подробности по конкретному ключу — вызови `get_issue` с этим `key`.

### Создание
1. Убедись, что известны очередь (`queue_key`), заголовок (`summary`), тип (`type`: bug/story/task/epic/subtask) и приоритет (`priority`: critical/high/medium/low/trivial). Если чего-то нет — уточни у пользователя, не угадывай.
2. Вызови `create_issue`. Для защиты от дублей при повторах передавай стабильный `operation_id`.

### Изменение статуса
1. Вызови `transition_issue` с ключом и целевым статусом: передай `to_status_code` (символьный код, напр. `in_progress`) либо `to_status_id`. Достаточно одного из них.
2. Если платформа отклонит переход — сообщи пользователю текст ошибки (он подскажет допустимые переходы), не повторяй вслепую.

### Назначение и комментарии
- `assign_issue`: поле `assignee` — user id; либо `unassign = true`, чтобы снять исполнителя.
- `comment_issue`: поля `issue_key` и `content`.

## Справочные значения

- **Тип иссью**: bug, story, task, epic, subtask.
- **Приоритет**: critical, high, medium, low, trivial.
- **YTQL** (для `search_issues`): поля вроде `status`, `assignee`, `queue`, `type`, оператор `AND`, функция `me()`.

## Лимиты

- Поиск возвращает не более 100 иссью за вызов (по умолчанию 20).
- Действия (создание/обновление/комментарий/переход/назначение) — по одной иссью за вызов.

## Типичные ошибки и решения

- **"нет доступа" (HTTP 401/403)**: токен/права инстанса не позволяют операцию. Проверь конфигурацию инстанса (`config_test_connection`); не повторяй вызов вслепую.
- **"не найдено" (HTTP 404)**: неверный ключ иссью или нет прав видеть её.
- **"api_key/email не задан"**: инстанс не настроен — заполни конфигурацию в админке.
- **"XTracker недоступен"**: сетевая/таймаут-проблема — повтори позже.
