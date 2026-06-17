# Платформенный канон — MCP-плагины Jarvis + контракт XTracker API

> Адаптировано из X5_BM mothership@c87e9ee6 (2026-06-13). Указательный документ: детали — в источниках ниже, не дублируются здесь.

**Статус:** canonical-pointer · источник истины деталей контракта (Часть II устава, инварианты P-4…P-11).

## 1. Контракт платформы (MCP-плагины Jarvis / X5 Maverick)

Источник истины — `XTracker/my-first-plugin-2/mcp_plugins_dev_spec.md` (далее **spec**). Плагины упаковываются в zip, регистрируются платформой, общаются по stdio JSON-RPC. Краткий индекс ключевых разделов spec:

| Раздел spec | О чём |
|---|---|
| §3–4 | Zip-контракт + manifest `jarvis-plugin.json` (slug, command, `*_path`) → P-4 |
| §5 | `SKILL.md` / Progressive Disclosure (name+description для discovery) → P-9 |
| §6 | MCP-stdio протокол (initialize / tools/list / tools/call) → P-5 |
| §7 | Tools: нейминг `slug__remote_name`, JSON Schema, инжект `__jarvis` (config/user_id/session_id) → P-7, P-1 |
| §8 | Profiles/Instances, `config_test_connection`, шифрование конфига |
| §5.3, §15.5 | Возврат файлов: `upload_file` SDK (artifact_id вместо base64) → P-11 |
| §17 | Structured Content / Generative UI (пресеты card/card_list/chart/table, actions) → P-11 |
| §18 | Best practices (discovery quality, описания tools, error-handling) → P-9 |
| §20 | Batch State Stop-Signal (verb-нейминг, compact-результаты, ERROR-формат) → P-10 |
| §21 | Idempotent-Skip pattern → P-3 |

## 2. Контракт XTracker API

**Правило (owner-instruction):** использовать API **по описанию и структуре**, НЕ вендорить и не вшивать полный OpenAPI (`XTracker_Api.json`, 1.2 MB) ни в плагин, ни в эти доки. Тянуть только нужные пути/схемы по месту.

- **База:** `https://pulsar.x5.ru` (свой SSL-сертификат — см. `~/Downloads/pulsar-x5-ssl/`).
- **Аутентификация:** JWT Bearer (`POST /api/v1/auth/login {email,password}` → токен + refresh; `POST /api/v1/auth/refresh`) **или** долгоживущие API-ключи (`/api/v1/api-keys`, со scopes). Дефолт плагина — `api_key` (сервис-аккаунт).
- **Природа:** issue/project-трекер класса Jira/YouTrack, 23 Go-микросервиса, multi-tenant (organizations/tenants, RBAC по очередям). 350 путей / 513 операций / 272 схемы.
- **Чат-релевантные эндпоинты (ядро иссью, v1 плагина):**

| Назначение | Эндпоинт (по структуре) |
|---|---|
| Поиск иссью | `POST /api/v1/issues/_search` (язык запросов) · `GET /api/v1/search/issues` |
| Чтение иссью | `GET /api/v1/issues/{key}` (+ `/comments`, `/links`) |
| Допустимые переходы | `GET …/workflows/{id}/transitions/valid` |
| Создание | `POST /api/v1/issues` |
| Обновление | `PATCH /api/v1/issues/{key}` |
| Комментарий | `POST /api/v1/issues/{key}/comments` |
| Смена статуса | `POST /api/v1/issues/{key}/transitions` |
| Назначение | `POST /api/v1/issues/{key}/assign` · `/unassign` |
| Текущий пользователь | `GET /api/v1/users/me` |

## 3. Локальные копии источников

- Платформенный spec: `XTracker/my-first-plugin-2/mcp_plugins_dev_spec.md` (в репозитории).
- XTracker OpenAPI + SSL: `~/Downloads/pulsar-x5-ssl/` (`XTracker_Api.json`, `pulsar.x5.ru.*`, вики по сетевой инфраструктуре) — **вне репозитория**, read-only справка.
