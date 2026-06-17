# XTracker — доменный слой плагина

Доменный контракт плагина XTracker: внешний сервис, аутентификация, config, tools v1, Generative UI. Общий контракт MCP-платформы — в [`_platform/platform-canon.md`](../_platform/platform-canon.md). Правило: API используется **по описанию и структуре**, полный OpenAPI не вендрится (P-1/owner-instruction).

## Внешний сервис

- **Продукт:** XTracker — внутренний issue/project-трекер X5 класса Jira/YouTrack.
- **База:** `https://pulsar.x5.ru` (свой SSL-сертификат — справка в `~/Downloads/pulsar-x5-ssl/`).
- **Природа:** 23 Go-микросервиса (auth, ticket, sprint, project, goals/OKR, workflow-engine, collaboration, timetracking, dashboard, query, search…), multi-tenant (organizations/tenants, RBAC по очередям). API: 350 путей / 513 операций / 272 схемы (OpenAPI 3.0.3).
- **OpenAPI (справка, вне репо):** `~/Downloads/pulsar-x5-ssl/XTracker_Api.json` (1.2 MB) — читать по месту, не вшивать.

## Аутентификация

- JWT Bearer на всех эндпоинтах.
- `POST /api/v1/auth/login {email,password}` → токен + refresh; `POST /api/v1/auth/refresh`.
- Долгоживущие **API-ключи** (`/api/v1/api-keys`, со scopes) — **дефолт плагина** (`auth_mode: api_key`, сервис-аккаунт).
- Плагин кэширует JWT и рефрешит. Секреты — только из `__jarvis.config` (P-1).

## Config инстанса (`config/schema.json` → `__jarvis.config`)

| Поле | Тип | Назначение |
|---|---|---|
| `base_url` | string (uri) | по умолчанию `https://pulsar.x5.ru` |
| `auth_mode` | enum `api_key`\|`password` | дефолт `api_key` |
| `api_key` | string (secret) | при `auth_mode=api_key` |
| `email` + `password` | string + secret | при `auth_mode=password` |
| `organization` | string (опц.) | tenant/организация |
| `default_queue` | string (опц.) | очередь по умолчанию для создания |
| `verify_ssl` | bool (default true) | + опц. `ca_cert` (свой сертификат pulsar) |
| `timeout` | integer | таймаут запроса, сек |

## Tools v1 (ядро иссью)

Имена — `xtracker__<name>` (P-10: data-getters — защищённые verb'ы; action-tools — compact `(N) [key=…]`).

| Tool | API (по структуре) | Вывод |
|---|---|---|
| `search_issues` | `POST /api/v1/issues/_search` (язык запросов) · `GET /api/v1/search/issues` | `preset:card_list` + action-кнопки; `limit` с `maximum` (P-16) |
| `get_issue` | `GET /api/v1/issues/{key}` (+ `/comments`, `/links`) | `preset:card` |
| `list_transitions` | `GET …/workflows/{id}/transitions/valid` | text / `preset:key_value` |
| `create_issue` | `POST /api/v1/issues` | compact `(+1) [key=…]` |
| `update_issue` | `PATCH /api/v1/issues/{key}` | compact |
| `comment_issue` | `POST /api/v1/issues/{key}/comments` | compact |
| `transition_issue` | `POST /api/v1/issues/{key}/transitions` | compact / card |
| `assign_issue` | `POST /api/v1/issues/{key}/assign` · `/unassign` | compact |
| `whoami` | `GET /api/v1/users/me` | text |
| `config_test_connection` | login / `GET /api/v1/users/me` | OK/Error (кнопка Test) |

## Generative UI

- `search_issues` → `preset:card_list`: карточки (key, summary, status-badge, assignee) + per-item actions «Открыть»/«Transition»/«Назначить»/«Коммент»; всегда с `text`-fallback (P-11).
- `get_issue` → `preset:card`: детали иссью.
- `structured_content` никогда не уходит в LLM-контекст; actions — с полным `xtracker__<name>`.

## Будущие фазы (вне v1)

Спринты/борды (sprint-service), тайм-трекинг (timetracking-service), проекты/очереди, цели/OKR (goals-service), дашборды/аналитика, saved-filters (query-service) — добавляются отдельными tools через `/pipeline-lite`.
