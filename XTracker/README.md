# XTracker — MCP-плагин Jarvis ↔ трекер XTracker

Чат-интеграция платформы Jarvis / X5 Maverick с внутренним issue-трекером **XTracker** (`xtracker.x5team.ru`, класс Jira/YouTrack). Позволяет пользователю Jarvis искать, читать, создавать, обновлять, комментировать иссью, менять статус и назначать — прямо из чата.

## Статус

- **Операционная система:** готова (устав, доктрины, процесс, команда агентов). Адаптирована из mothership `X5_BM` — см. [`Product_agents/ADAPTATION.md`](Product_agents/ADAPTATION.md).
- **v1-плагин:** ✅ **реализован** (`plugin/`, stdlib-only Python). Verify-gate пройден (64/64, `tests/protocol_qa.py` против мок-API). Пакет собран: `dist/xtracker-1.0.0.zip`. Финальный «Test connection» против живого `xtracker.x5team.ru` — за оператором после загрузки.

## Что внутри каталога

| Путь | Что |
|---|---|
| [plugin/](plugin/) | **Сам плагин**: `jarvis-plugin.json`, `SKILL.md`, `server.py`, `config/`, `requirements.txt` |
| [tests/protocol_qa.py](tests/protocol_qa.py) | Verify-gate: мок-API + реальный JSON-RPC (64 проверки) |
| `dist/xtracker-1.0.0.zip` | Собранный пакет для загрузки (build-артефакт, в `.gitignore`) |
| [DOMAIN.md](DOMAIN.md) | Доменный слой: внешний API, аутентификация, config, tools v1, Generative UI |
| [Product_agents/Dev_Agents/AGENTS.md](Product_agents/Dev_Agents/AGENTS.md) | Гид команды: каноны `xt-builder`/`xt-protocol-qa`/`xt-scribe`, routing, память |
| [Product_agents/ADAPTATION.md](Product_agents/ADAPTATION.md) | Провенанс адаптации + структура репо |
| [docs/superpowers/](docs/superpowers/) | Спека дизайна + план реализации операционки (история) |
| `my-first-plugin-2/` | Референс-scaffold + платформенный `mcp_plugins_dev_spec.md` |

## v1 tools (ядро иссью, 9 шт.)

`search_issues` · `get_issue` · `create_issue` · `update_issue` · `comment_issue` · `transition_issue` · `assign_issue` · `whoami` · `config_test_connection`. Детали и маппинг на API — в [DOMAIN.md](DOMAIN.md). (`list_transitions` — фаза 2.)

## Сборка пакета

```
cd XTracker/plugin
zip -rX ../dist/xtracker-1.0.0.zip . -x '*.pyc' -x '*/__pycache__/*'
```
Затем — админка Jarvis → «Авторские плагины» → «Загрузить плагин» → создать инстанс → «Test».

## Как разрабатывать

Правила — общий устав [`_platform/constitution.md`](../_platform/constitution.md) (16 инвариантов). Как строить плагин — [`_platform/PLUGIN_AUTHORING_GUIDE.md`](../_platform/PLUGIN_AUTHORING_GUIDE.md). Для автономной работы агентов открывай `XTracker/` как рабочий корень.

## Лицензия

Внутренний корпоративный проект X5.
