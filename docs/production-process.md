# Производственный процесс — XTracker-плагины

> Адаптировано из X5_BM mothership@c87e9ee6 (2026-06-13). Ядро портировано, слой локализован под MCP-плагины/XTracker.

**Статус:** canonical · процесс поставки фич и фиксов плагина.
**Версия:** 1.0.0 (2026-06-17).

---

## /pipeline-lite — 4-этапный конвейер (облегчённый под один плагин)

```
/pipeline-lite "описание фичи / tool'а"
    │
    Stage 1: Creative ──→ спека tool'а (inputSchema + фрагмент SKILL.md + ожидаемый вывод)
    │
    Stage 2: Audit ─────→ Constitution Check (MUST-FLAG по P-1…P-16)
    │     ┌─ USER APPROVAL ─┐
    │     │ (показывает спеку)│
    │     └──────────────────┘
    │
    Stage 3: Dev ───────→ реализация (xt-builder)
    │   ▲
    │   │ retry (max 2) + список доработок
    │   │
    Stage 4: Quality ───→ xt-protocol-qa verify-gate → вердикт PASS / FAIL

    FAIL + retry < 2 → назад в Stage 3
    FAIL + retry = 2 → спросить владельца
    PASS             → готовый коммит/ветка
```

- **Stage 1 — Creative.** Из запроса/issue → спека tool'а: имя `slug__verb_noun`, `description` «что+когда», `inputSchema` (строгая, P-7), фрагмент `SKILL.md` (P-9), ожидаемый вывод (text + опц. structured_content). Owner: оркестратор / `xt-scribe` по SKILL.md.
- **Stage 2 — Audit.** Прогнать спеку через [constitution-check.md](constitution-check.md). Любой `MUST-FLAG` или `NEEDS-INFO` на MUST блокирует переход. Затем **USER APPROVAL** — показать спеку + результат гейта, спросить Approve / Revise / Abort.
- **Stage 3 — Dev.** `xt-builder` реализует по порядку §4 доктрины фич (контракт → схема → handler → UI → тесты).
- **Stage 4 — Quality.** `xt-protocol-qa` verify-gate: реальный stdio JSON-RPC-прогон (tools/list-валидация + tools/call happy + adversarial), idempotent-skip, проверка отсутствия секретов, валидность structured_content. Вердикт PASS только при выполнении DoD доктрины фич §5.

**Для тривиальных правок** (один handler, без новой схемы) Stage 1–2 сворачиваются (см. выбор трека в [feature-process.md](feature-process.md)); фикс идёт сразу Dev → Quality.

---

## Git Publish Runbook

> Ядро портировано из mothership; пути/репо локализованы. Применяется к агентам, которые меняют репозиторий и публикуют результат.

### Общее правило

Issue можно закрывать только после трёх фактов:

1. Коммит опубликован в `origin/main` (или в целевую ветку PR).
2. Remote SHA проверен после push.
3. В issue оставлен комментарий: что сделано, commit SHA, проверки (протокол-тест/JSON-RPC evidence), остаточные ограничения.

Если любой пункт не выполнен — issue не закрывать; записать blocker в память агента.

### Дисциплина коммита

- **Stage explicit paths** — `git add <конкретные файлы>`, **никогда** `git add -A` (риск утащить `.env`/секреты — P-1).
- Conventional-commit сообщения; тело завершать `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.
- Связывание с issue: `Closes #N` в теле коммита/PR.
- Работа в feature-ветке/worktree; не коммитить напрямую в `main` без явного согласия владельца.

### Если remote ушёл вперёд

Не делать force-push. Безопасные пути: пересобрать коммит поверх свежего `main`, затем повторить публикацию; либо `git fetch origin main` в окружении с доступом на запись.

### Если GitHub недоступен

Оставить локальный коммит/staged changes, затем записать: SHA локального коммита; точную ошибку; какие issues нельзя закрывать до публикации; следующий шаг. Локальный коммит без verified remote SHA — **не** resolved. Для issue-only действий: комментарий/close считается сделанным только после успешного ответа GitHub API/CLI.

### Сборка пакета плагина

Сборка `.zip` плагина — по spec §16 (упаковать каталог плагина: `jarvis-plugin.json` + `SKILL.md` + `server.py`/`src` + `config/` + `_vendored_sdk/`, без `.git/__pycache__/.env` — P-4). Применяется при поставке плагина, не при правке этих доков.

---

## Конвенция памяти (обзор)

Каждый агент ведёт персистентную память; перед прогоном **обязан прочитать свой компакт** `Product_agents/Dev_Agents/memmory_<agent>.md`. Память append-only, двухуровневая (durable-слой + журнал прогонов), с ротацией по лимиту. Источник истины — [../Product_agents/Dev_Agents/MEMORY_CONVENTION.md](../Product_agents/Dev_Agents/MEMORY_CONVENTION.md). Индекс «агент → память → статус» — в [../Product_agents/Dev_Agents/AGENTS.md](../Product_agents/Dev_Agents/AGENTS.md).
