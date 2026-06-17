# XTracker Dev Agents Guide

> Адаптировано из X5_BM mothership@c87e9ee6 (2026-06-13). Ядро (структура guide) портировано, слой локализован.

Кросс-агентный справочник команды MCP-плагина XTracker: где что лежит, кто за что отвечает, как публиковать. Хранитель файла — `xt-scribe` (guardianship).

> **Переходная оговорка.** Бандл плагина — `X5Tracker/` в репозитории `Plugins/` (монорепо: много плагинов, каждый в своём каталоге). Все пути в этом файле относительны корню бандла `X5Tracker/`. Сам v1-плагин XTracker (`X5Tracker/`: `jarvis-plugin.json`, `SKILL.md`, `server.py`, `config/`) ещё не реализован — он строится первой фичей через `/pipeline-lite` (см. `docs/production-process.md`). До этого момента у агентов есть устав, доктрины и процесс, но боевых прогонов против плагина ещё не было.

## Canonical Locations

| Что | Где |
|---|---|
| Устав (apex) | `docs/constitution.md` |
| Доктрины | `docs/bug-handling-process.md`, `docs/feature-process.md` |
| Процесс + гейты | `docs/production-process.md`, `docs/constitution-check.md` |
| Платформенный канон + контракт API | `docs/platform-canon.md` → `XTracker/my-first-plugin-2/mcp_plugins_dev_spec.md` |
| Каноны агентов (полные профили) | `Product_agents/Dev_Agents/xt-{builder,protocol-qa,scribe}.md` |
| Тонкие стабы → канон | `.claude/agents/xt-{builder,protocol-qa,scribe}.md` |
| Память агентов | `Product_agents/Dev_Agents/memmory_xt-*.md` |
| Конвенция памяти | `Product_agents/Dev_Agents/MEMORY_CONVENTION.md` |
| Провенанс адаптации | `Product_agents/ADAPTATION.md` |
| Плагин (цель) | `X5Tracker/` (корень бандла: `jarvis-plugin.json`, `SKILL.md`, `server.py`, `config/`) |

## Start-Of-Run Commands

1. Прочитать свой стаб `.claude/agents/<agent>.md` → перейти в канон и прочитать его целиком.
2. Прочитать свою память `memmory_<agent>.md` целиком (правила — `MEMORY_CONVENTION.md`).
3. Прочитать устав `docs/constitution.md`.
4. `git status` — рабочая копия чистая до начала.

## Publish Discipline

Публикация и закрытие issue — строго по `docs/production-process.md` → Git Publish Runbook: `git add` явных файлов (НЕ `-A`), published SHA + verify remote SHA + комментарий (что сделано, SHA, проверки). Нет доступа к GitHub — blocker в память, issue не закрывать.

## Team Status & Memory Index

| Agent | Роль | Память | Статус |
|---|---|---|---|
| `xt-builder` | автономный разработчик плагина (реализация/фиксы tools) | `memmory_xt-builder.md` | активен (адаптация 2026-06-17) |
| `xt-protocol-qa` | ultra-критичный QA по stdio JSON-RPC + verify-gate | `memmory_xt-protocol-qa.md` | активен (адаптация 2026-06-17) |
| `xt-scribe` | технический писатель (SKILL.md/README/docs) + guardianship AGENTS.md | `memmory_xt-scribe.md` | активен (адаптация 2026-06-17) |

## Agent Routing

| Задача | Агент |
|---|---|
| Реализовать новый tool / починить handler / собрать zip | `xt-builder` |
| Верифицировать фикс/фичу (реальный JSON-RPC, adversarial, secret-scan), verify-gate перед закрытием | `xt-protocol-qa` |
| Написать/отревизить `SKILL.md`, описания tools, README; обновить этот файл | `xt-scribe` |
| Спека новой фичи / новый tool с развилками | оркестратор → `/pipeline-lite` (Creative → Audit → Dev `xt-builder` → Quality `xt-protocol-qa`) |

## Evidence And Issue Rules

- **Zero-trust (P-15):** claim («работает», «tools/list ок», «idempotent») принимается только со свежим evidence, добытым проверяющим — реальный JSON-RPC-транскрипт, желательно на другой оси, чем источник claim'а. «FIXED» агента — не доказательство.
- Issue заводятся на русском с обязательными секциями (см. каноны QA/builder); перед созданием — поиск дублей.
- Секреты XTracker (token/password/api-key) запрещены в issue, логах, evidence, памяти (P-1).

## Editing This File

Хранитель — `xt-scribe`. Этот файл описывает **где что лежит и кто за что отвечает**; он НЕ дублирует каноны и НЕ содержит доменных правил (правила — в `docs/`, профили — в `Product_agents/Dev_Agents/`).

## Стаб-правило (анти-дрейф)

`.claude/agents/*` — только тонкие стабы (≤35 строк, маркер `runtime-стаб`, frontmatter == frontmatter канона), указывающие на канон. **Полные runtime-копии канонов запрещены** (дрейф). При изменении канона стаб не трогаем, кроме frontmatter-синхронизации.
