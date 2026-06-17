# Дизайн: адаптация операционной системы X5_BM (mothership) под XTracker-плагин

**Дата:** 2026-06-17 · **Статус:** утверждён владельцем (брейншторм) · **Тип:** spec → следующий шаг writing-plans.
**Подход:** A — «Mirror-lite» (6-частная структура mothership, масштабированная под один MCP-плагин).

---

## 0. Контекст и цель

**Задача владельца:** адаптировать операционный playbook команды агентов проекта **X5_BM** (mothership; enterprise Go-микросервисы, экспорт `lukinvit/X5_BM` main @ `c87e9ee6`, 2026-06-13) под проект **XTracker-плагин**.

**XTracker (продукт):** внутренний issue/project-трекер X5 класса Jira/YouTrack — 23 Go-микросервиса (auth, ticket, sprint, project, goals/OKR, workflow-engine, collaboration, timetracking, dashboard, query, search, …), `xtracker.x5team.ru`, JWT Bearer + API-ключи, multi-tenant (organizations/tenants, RBAC по очередям). API: 350 путей / 513 операций / 272 схемы (OpenAPI 3.0.3).

**Этот проект (что строим):** **MCP-плагин для платформы Jarvis / X5 Maverick** — мост «чат Jarvis ↔ XTracker». Плагин упаковывается в zip, регистрирует tools, общается по stdio JSON-RPC. Платформенный контракт описан в `XTracker/my-first-plugin-2/mcp_plugins_dev_spec.md` (далее — **spec**).

**Правило по API:** плагин обращается к XTracker по **описанию и структуре** эндпоинтов; полный 1.2MB OpenAPI (`XTracker_Api.json`) **не вендорим** в плагин и не вшиваем в доки — только нужные пути/схемы по месту.

**Зафиксированные решения брейншторма:**
- Объём адаптации: **свод правил + минимальная команда** (§6.2 mothership: builder + QA + docs).
- Доменный слой: определяем функцию XTracker **сейчас** (а не TODO) — см. §7.
- v1 плагина: **ядро иссью** (~8–10 tools).
- Структура: **Подход A (Mirror-lite)**, доки в корне репо `Plugins/`.

---

## 1. Две супер-ценности (фундамент)

> **1. Данные и секреты sacred.** Данные трекера пользователя и секреты инстанса нельзя терять, искажать, **дублировать** или **утекать**. Утечка токена/конфига или порча/дубль тикета — катастрофа, а не баг.
>
> **2. Только production-ready.** Никаких заглушек/MVP/«временно» как финала. Попало в `main` → работает end-to-end под реальным инстансом XTracker, с протокол-тестами и сверкой контракта API.

Все инварианты §2 — операционализация одной или обеих ценностей. Нарушение = блокер (мержа/деплоя/закрытия тикета), пока не устранено или не проведена явная поправка устава.

**Precedence:** Конституция плагина > платформенный канон (`mcp_plugins_dev_spec.md`) + контракт API (структура `XTracker_Api.json`) > CLAUDE.md > память агентов. Память/доки устаревают — при расхождении верь живому коду/API (P-15).

---

## 2. Конституция: 16 инвариантов под класс MCP-плагинов

Формат канона: **MUST** · _Зачем_ · _Как проверить_ · _Источник_. Здесь — сводка; полный текст пишется в `docs/constitution.md`.

### 🔒 Данные и секреты
- **P-1 Secrets Sovereignty (MUST).** Секреты XTracker (token/password/api-key) — ТОЛЬКО из `__jarvis.config`; никогда из env, кода, логов, `SKILL.md`, manifest, structured_content, текста для LLM. В ошибках — маскировать. _Проверка:_ grep на хардкод-секреты пуст; protocol-QA проверяет отсутствие секрета в любом выводе/`runtime.log`. _Источник:_ I-1/I-7 → spec §7.3.
- **P-2 Data Safety (MUST).** Необратимые операции (delete issue/comment, mass-transition) — не дефолт; требуют явного флага/подтверждения. Плагин не теряет и не дублирует данные пользователя. _Проверка:_ деструктивные tools требуют explicit-параметр; нет «тихих» батч-мутаций. _Источник:_ I-2.
- **P-3 Idempotent-Skip (MUST).** Повтор/дубль операции → **успех** (`isError:false`) с маркером `⏭️ ПРОПУСК` + «НЕ ПОВТОРЯЙ», не ошибка. _Проверка:_ тест: повторный вызов с теми же args → `isError:false`, состояние не дублируется. _Источник:_ spec §21.

### 🏛 Контракт платформы
- **P-4 Package Contract (MUST).** Валидный `jarvis-plugin.json` в корне zip (slug `^[a-z][a-z0-9_-]{2,50}$`, command без shell, `*_path` относительные без `..`); zip без `.git/__pycache__/node_modules/.env`. _Источник:_ spec §3–4.
- **P-5 Protocol Fidelity (MUST).** Корректный stdio JSON-RPC (initialize/tools/list/tools/call); процесс не падает (1 процесс = все tools пакета); внешние вызовы в try/except с actionable-ошибкой. _Источник:_ spec §6, §18.5.
- **P-6 Frozen Identifiers (MUST).** `slug` неизменен между версиями; `remote_name` tools не менять (ломает HITL/сохранённые actions) — только новый tool + deprecated-пометка. _Источник:_ I-6 → spec §18.11.

### 🛡 Безопасность и изоляция
- **P-7 Schema Rigor (MUST).** Каждый tool: `type:object`, строгие `properties` с `description`/`enum`/`default`/`required`, `additionalProperties:false`; неизвестные поля (вкл. `__jarvis`) игнорируются. _Источник:_ spec §7.2.
- **P-8 Identity & RBAC Honesty (MUST).** Плагин действует под сконфигурированной XTracker-identity; не обходит RBAC XTracker; 403 показывается честно, не маскируется под пустой результат и не «обогащается» чужими данными. _Источник:_ I-5/I-7.

### ⚙️ LLM-эргономика и эксплуатация
- **P-9 Discovery Quality (MUST).** `SKILL.md`: YAML `name`+`description` (что/когда/триггеры/НЕ-использовать; ≤1024 симв., без `<>`, на русском); тело — процессы прозой **без литеральных вызовов tools**; ≤5000 слов. _Источник:_ spec §5, §18.1–18.2.
- **P-10 Batch/Loop-Safe (MUST).** Имена `slug__verb_noun`; data-getters `search_/get_/list_`; action-tools возвращают compact `(N) [ref=X]`; ERROR с keyword/`{"type":"ERROR"}`; виртуальные `__name__` не используем. _Источник:_ spec §20.
- **P-11 Generative UI Discipline (MUST).** `structured_content` всегда с text-fallback и никогда не попадает в LLM-контекст; actions с уникальным `id` + полным `slug__remote_name`; файлы >5–10KB — через `upload_file` SDK внутри content `type:json`. _Источник:_ spec §17, §5.3.
- **P-12 Resilience (MUST).** Таймауты/ретраи внешних вызовов; деградация при недоступном/медленном XTracker (понятная ошибка, не краш); уважать лимиты платформы (60s на tool, 100MB stdout). _Источник:_ I-8 → spec §12.4.

### 🔬 Процесс
- **P-13 Production-Ready by Default (MUST).** Ноль stub/TODO/placeholder как финал; работает end-to-end под реальным инстансом против живого API; покрыто протокол-тестами; `// TEMP:` только со ссылкой на issue. _Источник:_ I-11.
- **P-14 Root-Cause + Scope-the-Class (MUST).** На любой баг — `superpowers:systematic-debugging` до фикса (repro → root cause → fix); чинить весь класс по осям: **tool / поле schema / роль XTracker / состояние иссью / поверхность вывода**. _Источник:_ I-12.
- **P-15 Zero-Trust Verification (MUST).** Любой claim («работает», «tools/list ок», «idempotent») — только со свежим evidence, добытым проверяющим (реальный JSON-RPC-прогон), желательно на другой оси. Память устаревает — верь живому коду/API. _Источник:_ I-13.

### 🗄 Целостность под объёмом
- **P-16 Bounded Results (SHOULD).** Поиск/списки иссью ограничены: явный `limit` (с дефолтом и максимумом) + пагинация по контракту XTracker; не тянуть тысячи иссью в один tool-результат — это раздувает MCP-IPC и context-window агента (и снижает качество планирования LLM). Большие выгрузки — через `upload_file` (P-11). _Проверка:_ у `search_issues` есть `limit` с `maximum`; нет неограниченной выдачи. _Источник:_ I-15 (bounded queries) → spec §5.3, §20.

**Опущены из mothership** (про серверный Go-продукт, не про плагин-клиент): I-3 audit-триггеры, I-4 clean-architecture слоёв/NATS, I-9 Prometheus/health, I-10 deploy.sh/миграции, I-15 optimistic-concurrency (берём только половину «bounded queries» как P-16).

**Поправки/enforcement:** semver устава (MAJOR удаление инварианта / MINOR добавление / PATCH формулировка); журнал поправок; Constitution-Check как gate в Stage-2 (см. §5).

---

## 3. Раскладка репозитория

> **Обновление 2026-06-17 (монорепо-раскладка).** Репо `Plugins/` ведётся как монорепо под много плагинов. Финальная раскладка: **`_platform/`** — общая операционка (устав/доктрины/процесс/гейт/контракт/гайд/память) для всех плагинов; **`XTracker/`** — этот плагин (команда `Product_agents/`, `DOMAIN.md`, история `docs/superpowers/`, scaffold, исходники); **`.claude/agents/`** в корне репо — стабы → каноны в `XTracker/Product_agents/`. Дерево ниже (исходный план) отражает идею; фактические пути — по этой раскладке (shared → `_platform/…`, plugin → `XTracker/…`).

Общая операционка — в `_platform/`; этот плагин и его команда — в `XTracker/`.

```
Plugins/                          # git-корень
├── docs/
│   ├── constitution.md           # 15 инвариантов (§2) + precedence + amendments + журнал
│   ├── bug-handling-process.md   # доктрина багов (ядро mothership + MCP-ловушки)
│   ├── feature-process.md        # доктрина фич
│   ├── production-process.md     # /pipeline-lite + Git Publish Runbook + memory-конвенция
│   ├── constitution-check.md     # gate-процедура (MUST-FLAG по P-1…P-15)
│   └── platform-canon.md         # указатель на mcp_plugins_dev_spec.md + структуру XTracker API
├── Product_agents/
│   ├── Dev_Agents/
│   │   ├── xt-builder.md  xt-protocol-qa.md  xt-scribe.md     # КАНОНЫ (полные профили)
│   │   ├── AGENTS.md  MEMORY_CONVENTION.md
│   │   └── memmory_xt-builder.md  memmory_xt-protocol-qa.md  memmory_xt-scribe.md  # seed-память
│   └── ADAPTATION.md             # провенанс: adapted from X5_BM mothership@c87e9ee6, 2026-06-13
├── .claude/agents/               # ТОНКИЕ СТАБЫ → канон (≤35 строк, frontmatter == канон)
│   └── xt-builder.md  xt-protocol-qa.md  xt-scribe.md
└── XTracker/                     # сам плагин
    ├── jarvis-plugin.json  SKILL.md  requirements.txt  README.md
    ├── server.py (или src/) + tools/ + _vendored_sdk/mcp_plugin_sdk/
    ├── config/{schema.json, ui.schema.json, defaults.json}
    └── my-first-plugin-2/        # существующий scaffold — оставляем как reference (НЕ удаляем без отдельного решения)
```

---

## 4. Доктрины (ядро / слой)

**Доктрина багов** (`docs/bug-handling-process.md`):
- _Ядро (механически):_ `systematic-debugging` на любой баг → repro → root cause → fix; scope-the-class; **три сквозных стража** (адаптированы: **контракт-платформы / LLM-эргономика / безопасность-секретов** вместо «архитектура/перф/секьюрити»); evidence-first zero-trust; единый loop fix→test→verify→close; DoD-self-audit перед закрытием.
- _Слой:_ оси класса = tool / поле schema / роль XTracker / состояние иссью / поверхность вывода; MCP-ловушки: loop слабых LLM на `isError:true` (→ P-3), batch-limits/compression (→ P-10), дубли tool-call, structured_content утёкший в контекст, секрет в логе.

**Доктрина фич** (`docs/feature-process.md`):
- _Ядро:_ clean-сверху-вниз, DoD фичи, совместимость с уставом на этапе авторинга (не на ревью), выбор трека trivial/speckit.
- _Слой:_ «фича» = новый tool/кластер tools; порядок реализации под MCP-плагин: manifest+SKILL.md-фрагмент → JSON Schema → tool-handler → Generative UI → протокол-тесты.

---

## 5. Производственный процесс (`docs/production-process.md`)

**`/pipeline-lite`** — 4 стадии, облегчённые под один плагин:
1. **Stage 1 Creative** — из запроса/issue → спека tool'а (inputSchema + фрагмент SKILL.md + ожидаемый вывод).
2. **Stage 2 Audit** — Constitution-Check: MUST-FLAG по P-1…P-15 + ревью schema/описаний; блокирует переход дальше.
3. **Stage 3 Dev** — `xt-builder` реализует.
4. **Stage 4 Quality** — `xt-protocol-qa` verify-gate: реальный JSON-RPC-прогон + adversarial + проверка секретов.

Плюс **Git Publish Runbook** (ветка, безопасный push без `git add -A`, `Closes #N`, поведение при divergence) и **конвенция памяти** (append-only, двухуровневая, ротация).

---

## 6. Команда (3 канона + стабы + AGENTS.md + seed-память)

| Агент | Ядро (порт mothership) | Слой (XTracker) |
|---|---|---|
| **xt-builder** (←Kulibin) | личность, Iron Rules, systematic-debugging, self-audit, run-summary, эскалации, координация | среда (`Plugins/XTracker`), TEST PROTOCOL = протокол-харнесс + `pytest`/`ruff`/`mypy`, сборка zip, stop-list, «не меняет slug/tool-names» |
| **xt-protocol-qa** (←Renata+Zanuda; **замена browser-QA**) | философия bug-hunter, zero-trust verify-gate, adversarial-мышление, формат находки/отчёта, intersection-секции | гоняет `server.py` по stdio JSON-RPC: валидирует tools/list-схемы; happy + adversarial tools/call (битые/недостающие/неизвестные args, инъекция `__jarvis`); idempotent-skip; batch-нейминг; валидность structured_content + text-fallback; **проверка утечки секретов** в выводе/`runtime.log`; file-offload |
| **xt-scribe** (←Pushkin) | док-куратор, guardianship `AGENTS.md`, docs-freshness | качество `SKILL.md` (P-9), `README`, структура вики/доков |

**Анти-дрейф:** `.claude/agents/*` — только тонкие стабы → канон (§6.1 mothership). Невыполнимые BLOCKING переводим в условную форму («при доступности инстанса»). Aspirational-нормы — измеряемые цели с честным gap-отчётом, не гейты. `ADAPTATION.md` фиксирует провенанс (upstream SHA, дата, состав, карта локализации).

---

## 7. Доменный слой: спека v1-плагина (первая цель пайплайна)

- **slug:** `xtracker` · **name:** «XTracker» · **runtime:** Python, **ручной stdio JSON-RPC** по spec §15.1 (полный контроль над `__jarvis`, structured_content, `_meta`; FastMCP-scaffold заменяем — он не извлекает `__jarvis`).
- **Config (`__jarvis.config`, схема в `config/schema.json`):**
  - `base_url` (default `https://xtracker.x5team.ru`)
  - `auth_mode` (`api_key` | `password`; **default `api_key`** — сервис-аккаунт, scoped, долгоживущий)
  - `api_key` (secret) **или** `email` + `password` (secret)
  - `organization` (опц.), `default_queue` (опц.)
  - `verify_ssl` (bool, default true) + опц. `ca_cert` (если у XTracker свой корневой сертификат)
  - `timeout` (сек)
  - Плагин кэширует JWT и рефрешит через `POST /api/v1/auth/refresh`.
- **v1 tools (ядро иссью):**

| Tool (`xtracker__…`) | API (по структуре) | Вывод |
|---|---|---|
| `search_issues` | `POST /api/v1/issues/_search` (язык запросов) / `GET /api/v1/search/issues` | `preset:card_list` + action-кнопки |
| `get_issue` | `GET /api/v1/issues/{key}` (+comments/links) | `preset:card` |
| `list_transitions` | `GET …/workflows/{id}/transitions/valid` | text / `preset:key_value` |
| `create_issue` | `POST /api/v1/issues` | compact `(+1) [key=…]` |
| `update_issue` | `PATCH /api/v1/issues/{key}` | compact |
| `comment_issue` | `POST /api/v1/issues/{key}/comments` | compact |
| `transition_issue` | `POST /api/v1/issues/{key}/transitions` | compact / card |
| `assign_issue` | `POST /api/v1/issues/{key}/assign` · `/unassign` | compact |
| `whoami` | `GET /api/v1/users/me` | text |
| `config_test_connection` | login / `GET /api/v1/users/me` | OK/Error (кнопка Test) |

- **Generative UI:** `card_list` для поиска (key, summary, status-badge, assignee, кнопки Открыть/Transition/Назначить/Коммент), `card` для деталей иссью.
- **Нейминг под P-10:** data-getters (`search_issues`, `get_issue`, `list_transitions`, `whoami`) — защищённые verb'ы; action-tools (`create_issue`, `update_issue`, `comment_issue`, `transition_issue`, `assign_issue`) — compact-результаты.

---

## 8. Поставка реализации (что авторим в плане)

**A. Операционная система (доки):** `docs/constitution.md`, `docs/bug-handling-process.md`, `docs/feature-process.md`, `docs/production-process.md`, `docs/constitution-check.md`, `docs/platform-canon.md`.

**B. Команда:** каноны `xt-builder`/`xt-protocol-qa`/`xt-scribe`; тонкие стабы в `.claude/agents/`; `AGENTS.md`, `MEMORY_CONVENTION.md`, seed-память; `ADAPTATION.md` (провенанс).

**C. Плагин v1 (XTracker):** `jarvis-plugin.json`, `SKILL.md`, `config/{schema,ui.schema,defaults}.json`, `server.py` + handlers tools §7, `requirements.txt`, `_vendored_sdk/mcp_plugin_sdk` (для `upload_file`), `README.md`.

**D. Протокол-харнесс** (инструмент `xt-protocol-qa`): Python-скрипт, который пайпит JSON-RPC в процесс плагина, проверяет tools/list + tools/call (happy + adversarial), idempotent-skip, отсутствие секретов в выводе; собирает evidence.

**Порядок:** A (устав+процесс) → B (команда) → затем v1-плагин (C+D) идёт первой фичей через `/pipeline-lite`.

---

## 9. Решённые вопросы (владелец, 2026-06-17 — «по дефолтам»)
1. **P-16 Bounded Results** — добавлен как SHOULD (см. §2, группа «Целостность под объёмом»).
2. **Auth по умолчанию** — `api_key` (сервис-аккаунт). Оба режима поддержим; `defaults.json` → `auth_mode: "api_key"`.
3. **`my-first-plugin-2`** — оставляем как reference, не удаляем и не переносим в этой итерации.
4. **Объём первой реализации** — авторим всю операционную систему (поставка §8 A+B: устав + доктрины + процесс + 3 агента/стабы/память/AGENTS.md), затем v1-плагин (§8 C+D) идёт первой фичей через `/pipeline-lite`.
