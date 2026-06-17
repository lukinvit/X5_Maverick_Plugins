# _platform — общая операционная система плагинов

Этот каталог — **общий для всех плагинов** репозитория. Здесь живут устав, доктрины, производственный процесс, гейт, контракт платформы и конвенция памяти. Плагины (`XTracker/` и будущие) **не дублируют** эти документы — ссылаются на них.

| Файл | Назначение |
|---|---|
| [constitution.md](constitution.md) | **Устав** (apex): 16 инвариантов P-1…P-16 для класса MCP-плагинов, две супер-ценности, precedence, поправки. |
| [bug-handling-process.md](bug-handling-process.md) | Доктрина багов: systematic-debugging, scope-the-class, evidence-first, DoD. |
| [feature-process.md](feature-process.md) | Доктрина фич: выбор трека, clean-порядок реализации tool'а, DoD фичи. |
| [production-process.md](production-process.md) | `/pipeline-lite` (Creative→Audit→Dev→Quality) + Git Publish Runbook + обзор памяти. |
| [constitution-check.md](constitution-check.md) | Gate-процедура: сверка спеки/PR с Частью I устава (`MUST-FLAG`). |
| [platform-canon.md](platform-canon.md) | Контракт MCP-платформы Jarvis (указатель на `mcp_plugins_dev_spec.md`). |
| [MEMORY_CONVENTION.md](MEMORY_CONVENTION.md) | Конвенция персистентной памяти агентов (append-only, ротация). |
| [PLUGIN_AUTHORING_GUIDE.md](PLUGIN_AUTHORING_GUIDE.md) | **Как создать новый плагин** — пошагово от идеи до zip. |

**Precedence:** устав > платформенный канон (spec) > контракт API плагина (структура) > CLAUDE.md > память.

**Изменение `_platform/`** затрагивает все плагины — правится через поправку устава (см. `constitution.md` Часть III) и ревью. Доменные детали конкретного плагина сюда не кладутся — они в `<plugin>/DOMAIN.md`.
