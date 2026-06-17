# ADAPTATION.md — провенанс адаптации команды агентов

> Запись адаптации операционной системы X5_BM (mothership) под проект XTracker-плагин.

## Параметры

| KEY | Значение |
|---|---|
| PROJECT_NAME | X5 Maverick Plugins / XTracker |
| PROJECT_KEY | XT |
| PROJECT_ROOT | `Plugins/` (git-корень) |
| GH_REPO | `lukinvit/X5_Maverick_Plugins` (origin); зеркало X5: `scm.x5.ru/airun/copilot/devops/X5_Maverick_Plugins` (remote `x5`) |
| Платформа | Jarvis / X5 Maverick (MCP-плагины, stdio JSON-RPC, zip) |
| Цель-плагин | XTracker — issue-трекер X5 (`pulsar.x5.ru`), v1 = ядро иссью |
| UPSTREAM_SHA (mothership) | `c87e9ee6` (X5_BM, экспорт 2026-06-13) |
| Bootstrap | 2026-06-17 (вручную, через brainstorming → writing-plans → executing-plans) |
| Подход | Mirror-lite (6-частная структура mothership, масштабированная под один плагин) |
| Состав (roster) | `xt-builder` (←Kulibin), `xt-protocol-qa` (←Renata+Zanuda), `xt-scribe` (←Pushkin) |
| AGENT_LANG | ru |
| MODEL | opus |

## Карта локализации (ядро / слой)

| Артефакт | Ядро (портировано) | Слой (локализовано под XTracker/MCP) |
|---|---|---|
| `docs/constitution.md` | модель apex+ссылки, две супер-ценности, precedence, поправки | 16 инвариантов P-1…P-16 выведены из платформенного spec (секреты `__jarvis.config`, idempotent-skip, frozen identifiers, schema rigor, Generative UI, batch-safe, bounded results) |
| `docs/bug-handling-process.md` | systematic-debugging, scope-the-class, evidence-first, fix-loop, DoD | 3 стража (контракт-платформы/LLM-эргономика/безопасность-секретов), 5 осей класса, MCP-ловушки |
| `docs/feature-process.md` | главный принцип, выбор трека, DoD фичи | «фича» = tool/кластер; clean-порядок для MCP-плагина |
| `docs/production-process.md` | 4-стадийный конвейер, Git Publish Runbook, конвенция памяти | `/pipeline-lite`, пути/репо, сборка zip |
| `xt-builder` | личность Kulibin, Iron Rules, BUG-HUNTER, workflow, эскалации | среда, TEST PROTOCOL (харнесс+pytest/ruff/mypy), что-не-делает (frozen ids) |
| `xt-protocol-qa` | философия Renata, zero-trust, формат находки; closure-gates Zanuda | тест-скоуп = stdio JSON-RPC (схемы, adversarial, idempotent, secret-scan); браузерный QA заменён полностью |
| `xt-scribe` | принципы Pushkin, guardianship, docs-freshness | SKILL.md (P-9), README, docs плагина |

## Опущено из mothership (неприменимо к плагину-клиенту)

Серверно-инфраструктурные инварианты (audit-триггеры, clean-architecture слоёв и межсервисная шина, метрики/health, deploy-скрипт/миграции, optimistic concurrency) и cron-routines/реестр-адаптаций/скрипт `agent-team-adapt.sh` (overkill для одного плагина). Из инварианта целостности данных под нагрузкой взята половина «bounded results» как P-16.

## Статус

**Адаптация завершена 2026-06-17 — DoD §8 зелёный.**

Evidence DoD-чеклиста (§8 пайплайна mothership):
- **Стабы:** все 3 — 16 строк (≤35), маркер `runtime-стаб`, frontmatter byte-identical каноном (diff пуст).
- **Литералы mothership:** в канон-доках (`docs/` кроме `docs/superpowers/` — там design-spec/plan законно ссылаются на mothership), `Product_agents/`, `.claude/agents/` — не найдено (grep по mothership-литералам и доменным ловушкам X5_BM пуст).
- **Фантомные ссылки:** все `.md`-пути в канон-доках резолвятся в воркдереве. Внешняя ссылка `XTracker/my-first-plugin-2/mcp_plugins_dev_spec.md` отсутствует в изолированном воркдереве, но EXISTS в основном чекауте `Plugins/` — резолвится при мерже (ожидаемо для worktree-изоляции).
- **Память:** все 3 агента — seed + указатель на `MEMORY_CONVENTION.md`.
- **Aspirational ≠ гейт:** owner-нормы (покрытие tools) оформлены как измеряемые цели с честным gap-отчётом в каноне `xt-protocol-qa`, не как блокирующие гейты.
- **Version-probe (зеро-траст, свежие субагенты):** xt-builder / xt-protocol-qa / xt-scribe — все PASS (стаб→канон резолвится, проект = XTracker-плагин, дрейфа нет; QA тестирует через stdio JSON-RPC).
- **Constitution-Check self-тест:** `spec-bad` → FLAG P-1/P-7/P-2 (`MUST-FLAG ≥ 3`), `spec-clean` → `MUST-FLAG: 0` — согласовано.

**Остаток (следующая итерация):** v1-плагин XTracker (`X5Tracker/`: `jarvis-plugin.json`, `SKILL.md`, `config/`, `server.py` + tools ядра иссью, vendored SDK) + протокол-харнесс — строятся первой фичей через `/pipeline-lite` (отдельный план).

## Релокация в бандл (2026-06-17)

По решению владельца вся операционка и плагин уложены в самодостаточный каталог `X5Tracker/` (репо `Plugins/` — монорепо под много плагинов; корень остаётся чистым). Перемещены `docs/`, `Product_agents/`, `.claude/agents/` → `X5Tracker/…`; внутрибандловые относительные ссылки сохранены. Платформенный spec (`XTracker/my-first-plugin-2/mcp_plugins_dev_spec.md`) — общий reference, остаётся на месте (repo-root-relative). Чтобы агенты подхватились в Claude Code, рабочим корнем открывать `X5Tracker/` (вложенный `.claude/agents/` не автодискаверится из корня репо).
