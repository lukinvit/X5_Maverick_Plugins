# XTracker — MCP-плагин Jarvis ↔ трекер XTracker

Чат-интеграция платформы Jarvis / X5 Maverick с внутренним issue-трекером **XTracker** (`pulsar.x5.ru`, класс Jira/YouTrack). Позволяет пользователю Jarvis искать, читать, создавать, обновлять, комментировать иссью, менять статус и назначать — прямо из чата.

## Статус

- **Операционная система:** готова (устав, доктрины, процесс, команда агентов). Адаптирована из mothership `X5_BM` — см. [`Product_agents/ADAPTATION.md`](Product_agents/ADAPTATION.md).
- **v1-плагин:** ещё не реализован — строится первой фичей через `/pipeline-lite` ([`_platform/production-process.md`](../_platform/production-process.md)). Объём v1 — ядро иссью (~10 tools, см. ниже).

## Что внутри каталога

| Путь | Что |
|---|---|
| [DOMAIN.md](DOMAIN.md) | Доменный слой: внешний API, аутентификация, config, tools v1, Generative UI |
| [Product_agents/Dev_Agents/AGENTS.md](Product_agents/Dev_Agents/AGENTS.md) | Гид команды: каноны `xt-builder`/`xt-protocol-qa`/`xt-scribe`, routing, память |
| [Product_agents/ADAPTATION.md](Product_agents/ADAPTATION.md) | Провенанс адаптации + структура репо |
| [docs/superpowers/](docs/superpowers/) | Спека дизайна + план реализации операционки (история) |
| `my-first-plugin-2/` | Референс-scaffold + платформенный `mcp_plugins_dev_spec.md` |
| _(будет)_ `jarvis-plugin.json`, `SKILL.md`, `server.py`, `config/` | Сам плагин |

## v1 tools (ядро иссью)

`search_issues` · `get_issue` · `list_transitions` · `create_issue` · `update_issue` · `comment_issue` · `transition_issue` · `assign_issue` · `whoami` · `config_test_connection`. Детали и маппинг на API — в [DOMAIN.md](DOMAIN.md).

## Как разрабатывать

Правила — общий устав [`_platform/constitution.md`](../_platform/constitution.md) (16 инвариантов). Как строить плагин — [`_platform/PLUGIN_AUTHORING_GUIDE.md`](../_platform/PLUGIN_AUTHORING_GUIDE.md). Для автономной работы агентов открывай `XTracker/` как рабочий корень.

## Лицензия

Внутренний корпоративный проект X5.
