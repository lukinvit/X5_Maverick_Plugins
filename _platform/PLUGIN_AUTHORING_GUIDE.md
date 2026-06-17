# Как создать MCP-плагин для Jarvis / X5 Maverick

Пошаговый гайд: от идеи до загружаемого `.zip`. Источник истины контракта — [platform-canon.md](platform-canon.md) → `mcp_plugins_dev_spec.md`. Все решения сверяются с уставом [constitution.md](constitution.md).

> **Главный принцип (P-13):** плагин production-ready с первого коммита — ноль заглушек, работает end-to-end под реальным инстансом, покрыт протокол-тестами. MVP/«временно» как финал запрещены.

---

## 0. Структура нового плагина в репо

Каждый плагин — свой каталог в корне `Plugins/`. Минимум:

```
<PluginName>/
├── README.md                 · что делает, статус
├── DOMAIN.md                 · внешний API/сервис, config, tools, Generative UI (доменный слой)
├── jarvis-plugin.json        · манифест (slug, command, runtime, config_*_path)
├── SKILL.md                  · Progressive Disclosure (name+description) + рабочие процессы
├── requirements.txt          · зависимости (Python)
├── server.py (или src/)      · MCP-stdio сервер: tools/list + tools/call
├── config/{schema,ui.schema,defaults}.json
└── _vendored_sdk/mcp_plugin_sdk/   · для upload_file (если возвращаешь файлы)
```

Общие устав/доктрины/процесс **не копируются** — берутся из `_platform/`. Команда агентов (для автономной разработки) — опционально, в `<PluginName>/Product_agents/` (см. как сделано в `XTracker/`), с тонкими стабами в корневом `.claude/agents/`.

---

## 1. Идея → спека (Stage 1 Creative)

1. Сформулируй: **что трекаем/делаем, какой внешний сервис, какие действия нужны пользователю в чате**.
2. Прогони через `superpowers:brainstorming` (намерение, требования, развилки — до кода).
3. Зафиксируй **доменный слой** в `DOMAIN.md`: база URL, аутентификация (как секреты попадут в `__jarvis.config`), список tools с назначением, нужен ли Generative UI / возврат файлов.
4. На каждый tool — черновик `inputSchema` + строки `description` + ожидаемый вывод.

**Выбор трека** (см. [feature-process.md](feature-process.md)): тривиальная правка одного handler'а — напрямую; новый tool/кластер/схема — через `/pipeline-lite`.

---

## 2. Сверка с уставом (Stage 2 Audit)

Прогони спеку через [constitution-check.md](constitution-check.md) — оцени каждый инвариант P-1…P-16, получи `MUST-FLAG: N`. Частые места:

- **P-1** секреты — только из `__jarvis.config`, не из env/кода/логов;
- **P-7** `inputSchema`: `type:object`, `additionalProperties:false`, `description` у полей;
- **P-9** `SKILL.md`: `description` ≤1024 без `<>`, тело без литеральных вызовов tools;
- **P-10** имена `slug__verb_noun`, data-getters `get_/list_/search_`, action-tools — compact `(N)`;
- **P-2/P-3** деструктив за флагом; дубль операции → idempotent-skip (`isError:false` + `⏭️ ПРОПУСК`);
- **P-16** у списков — `limit` с `maximum`.

Любой `MUST-FLAG` — блокер: либо чинится в спеке, либо явная поправка устава. После — USER APPROVAL.

---

## 3. Реализация (Stage 3 Dev) — clean сверху вниз

Порядок (см. [feature-process.md](feature-process.md) §4):

1. **Манифест** `jarvis-plugin.json` (slug `^[a-z][a-z0-9_-]{2,50}$`, `command` без shell, `runtime`, `config_*_path`).
2. **`SKILL.md`** — frontmatter `name`+`description` (P-9) + тело-процессы.
3. **`inputSchema`** каждого tool (строгая, P-7).
4. **Handler** `server.py`: разобрать строку JSON-RPC → `tools/list` / `tools/call`; извлечь `__jarvis` (секрет из `config`); вызвать внешний API (по структуре, не вендорить OpenAPI); обернуть в try/except с actionable-ошибкой (P-5, P-12); idempotent-skip (P-3); деструктив за флагом (P-2).
5. **Generative UI** (опц., P-11): сначала `text`-fallback, затем `structured_content` (пресеты card/card_list/table…); actions с полным `slug__remote_name`. Файлы >5–10KB — через `upload_file` SDK (artifact_id).
6. **`config_test_connection`** tool — для кнопки Test в админке.

Минимальный каркас сервера — см. `mcp_plugins_dev_spec.md` §15.1 (ручной newline-JSON-RPC, полный контроль над `__jarvis`/structured_content/`_meta`).

---

## 4. Верификация (Stage 4 Quality) — реальный JSON-RPC

Прогони плагин **реальным stdio JSON-RPC** (не «по коду»):

- `tools/list` → схемы валидны (P-7), имена по P-10;
- `tools/call` happy + **adversarial** (пропуск required, неверный тип, неизвестное поле, инъекция `__jarvis`, гигантский вход) → процесс НЕ падает (P-5);
- повтор операции → idempotent-skip (P-3);
- `structured_content` имеет text-fallback и не уходит в LLM-контекст (P-11);
- **секрет не утёк** в `content`/`_meta`/`runtime.log` (P-1).

Сохрани транскрипт запрос→ответ как evidence (P-15). Критерии PASS — DoD фичи ([feature-process.md](feature-process.md) §5).

---

## 5. Упаковка и загрузка

1. Сгенерируй `requirements.lock` (`pip-compile --generate-hashes requirements.in`).
2. Заархивируй каталог плагина в `.zip` (без `.git/__pycache__/node_modules/.env` — P-4). См. `mcp_plugins_dev_spec.md` §16.
3. Загрузи через админку Jarvis: «Авторские плагины» → «Загрузить плагин».
4. Создай инстанс (профиль): заполни config (секреты шифруются backend'ом), нажми **Test** (вызовет `config_test_connection`).

---

## 6. Чек-лист перед выпуском (из устава + spec §18.12)

- [ ] `jarvis-plugin.json` валиден; zip без лишнего (P-4).
- [ ] У всех tools `description` «что+когда»; у полей schema — `description`; `additionalProperties:false` (P-7).
- [ ] `config_test_connection` реализован.
- [ ] Секреты только из `__jarvis.config`; не утекают никуда (P-1).
- [ ] Имена `slug__verb_noun`; action-tools — compact `(N)`; ERROR с keyword (P-10).
- [ ] Idempotent-skip на дубли (P-3); деструктив за флагом (P-2).
- [ ] `SKILL.md`: триггеры + «НЕ использовать для», без литеральных вызовов tools, ≤5000 слов (P-9).
- [ ] Generative UI (если есть) с text-fallback; файлы через `upload_file` (P-11).
- [ ] Прогнан реальным JSON-RPC: happy + adversarial; процесс не падает (P-5, P-15).
- [ ] Ноль stub/TODO как финал (P-13).
