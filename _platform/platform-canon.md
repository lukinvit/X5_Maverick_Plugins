# Платформенный канон — контракт MCP-плагинов Jarvis / X5 Maverick

> Адаптировано из X5_BM mothership@c87e9ee6 (2026-06-13). Указательный документ: детали — в источниках ниже, не дублируются здесь. **Общий для всех плагинов репо.**

**Статус:** canonical-pointer · источник истины деталей контракта платформы (Часть II устава, инварианты P-4…P-11). Доменные детали конкретного плагина (внешний API, config, tools) живут в `<plugin>/DOMAIN.md`, не здесь.

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

## 2. Общее правило по внешним API (все плагины)

**Owner-instruction:** внешний API плагина использовать **по описанию и структуре** — НЕ вендорить и не вшивать полные OpenAPI-спеки в плагин или доки. Тянуть только нужные пути/схемы по месту. Секреты доступа — только через `__jarvis.config` (P-1).

## 3. Доменный слой плагина

Контракт конкретного внешнего сервиса (база URL, аутентификация, эндпоинты, config, tools, Generative UI) описывается в `DOMAIN.md` каждого плагина — НЕ в этом общем каноне.

- Пример (плагин XTracker): [XTracker/DOMAIN.md](../XTracker/DOMAIN.md).

## 4. Локальные копии источников

- Платформенный spec: `XTracker/my-first-plugin-2/mcp_plugins_dev_spec.md` (в репозитории; общий reference для всех плагинов).
