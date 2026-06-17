# Доктрина работы с новыми фичами — XTracker-плагины

> Адаптировано из X5_BM mothership@c87e9ee6 (2026-06-13). Ядро портировано, слой локализован под MCP-плагины/XTracker.

**Статус:** canonical · доктрина авторинга новых фич плагина. Выводится из Конституции (P-13/P-14/P-15), скилла `superpowers:brainstorming` и процесса `/pipeline-lite` ([production-process.md](production-process.md)).
**Версия:** 1.0.0 (2026-06-17).

## 1. Главный принцип

**Фича — это не «написать tool, который работает на happy-path». Фича — это production-ready поставка с первого коммита (P-13).** Для плагина «фича» = **новый tool или кластер tools**. Полная (ноль stub/TODO/placeholder как финал), покрыта протокол-тестами, безопасная (секрет только из `__jarvis.config`, RBAC честный), задокументированная (`SKILL.md` обновлён) и прогнанная **сквозным JSON-RPC-раунд-трипом под реальным инстансом** — а не «по кусочкам».

## 2. Когда что запускать (выбор трека)

Перед любой творческой работой — **`superpowers:brainstorming`** (исследовать намерение до кода). «Добавь tool X» не значит «пропусти дизайн». После брейншторма выбери трек по масштабу:

| Масштаб изменения | Трек | Инструмент |
|---|---|---|
| Тривиальное (правка одного handler'а, < 50 LoC, без новой схемы/контракта) | прямая правка + протокол-тест + verify | — |
| Новый tool / новая `inputSchema` / новый кластер | **`/pipeline-lite`** (4 стадии) | см. [production-process.md](production-process.md) |
| Неоднозначные требования на любом треке | вернуться в брейншторм | `superpowers:brainstorming` |

Правило большого пальца: **если у изменения есть «как строим» с развилками — это `/pipeline-lite`, а не прямая правка.**

## 3. Совместимость с уставом — на этапе авторинга, не на ревью

Спека пишется совместимой с инвариантами P-1…P-16 **уже когда её создают** (дешевле, чем падать на гейте). В спеке tool'а явно отмечается, какие инварианты затрагивает фича. На Stage 2 спека проходит **Constitution Check** ([constitution-check.md](constitution-check.md)): любой `MUST-FLAG` или `NEEDS-INFO` на MUST блокирует переход к разработке. Молчаливый обход запрещён.

## 4. Порядок реализации (clean сверху вниз, для MCP-плагина)

Жёсткий порядок, чтобы контракт фиксировался до реализации:

```
manifest/SKILL.md-фрагмент → JSON Schema (inputSchema) → tool-handler → Generative UI → протокол-тесты
```

1. **Контракт наружу:** запись tool'а в `tools/list` (имя `slug__verb_noun` по P-10, `description` «что+когда»), фрагмент `SKILL.md` (P-9, без литеральных вызовов).
2. **Схема:** `inputSchema` — `type:object`, `additionalProperties:false`, `description`/`enum`/`default`/`required` у полей (P-7); `limit` с `maximum` для списков (P-16).
3. **Handler:** извлечь `__jarvis` (секрет — только из `__jarvis.config`, P-1), вызвать XTracker API (по структуре), обернуть в try/except с actionable-ошибкой (P-5, P-12), idempotent-skip для повторов (P-3), деструктив — за explicit-флагом (P-2).
4. **Generative UI:** сначала `text`-fallback, затем `structured_content` (P-11); actions с полным `slug__remote_name`.
5. **Протокол-тесты:** tools/list-валидация + tools/call happy + adversarial; проверка отсутствия секрета в выводе.

## 5. Definition of Done для фичи

Фича готова, только если на все «да»:

1. Брейншторм проведён; трек выбран осознанно; спека существует (для не-тривиальных).
2. Constitution Check: `MUST-FLAG: 0`.
3. Production-ready (P-13): ноль stub/TODO/placeholder как финал; временный workaround только помечен `# TEMP: … см. #issue`.
4. Tool появляется в `tools/list` с валидной строгой `inputSchema`.
5. happy + adversarial `tools/call` проходят; процесс не падает (P-5).
6. Idempotent-skip соблюдён для повторов (P-3); деструктив за explicit-флагом (P-2).
7. Секрет XTracker не утекает в вывод/лог (P-1); RBAC честный (P-8).
8. `structured_content` (если есть) имеет text-fallback и не уходит в LLM-контекст (P-11).
9. `SKILL.md` обновлён (P-9); README при необходимости.
10. **Verify-gate** `xt-protocol-qa`: сквозной JSON-RPC-прогон под реальным инстансом (при доступности), evidence-транскрипт сохранён.

## 6. Автономный режим

Backlog-кампании и фидбэк владельца ведутся **автономно** (fix→verify без approval-гейтов между фазами), пока не достигнут критерий готовности. Исключение — Stage-2 USER APPROVAL в полном `/pipeline-lite` (показывает спеку + Constitution Check перед разработкой) и решения, требующие владельца как product-oracle (метятся `NEEDS_ORACLE`).
