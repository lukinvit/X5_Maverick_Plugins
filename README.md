# X5 Maverick Plugins

Монорепозиторий **MCP-плагинов для платформы Jarvis / X5 Maverick** — каждый плагин упаковывается в `.zip`, грузится через админку Jarvis, регистрирует свои tools и работает по stdio JSON-RPC.

Репозиторий устроен как **«общая платформа + плагины»**: единый операционный устав, доктрины, производственный процесс и команда агентов переиспользуются всеми плагинами; каждый плагин живёт в своём каталоге.

## Структура

```
Plugins/
├── _platform/                  ← ОБЩЕЕ для всех плагинов
│   ├── constitution.md         · устав: 16 инвариантов (P-1…P-16)
│   ├── bug-handling-process.md · доктрина багов
│   ├── feature-process.md      · доктрина фич
│   ├── production-process.md   · /pipeline-lite (4 стадии) + Git Publish + память
│   ├── constitution-check.md   · gate-процедура (MUST-FLAG)
│   ├── platform-canon.md       · контракт MCP-платформы (указатель на spec)
│   ├── MEMORY_CONVENTION.md    · конвенция памяти агентов
│   └── PLUGIN_AUTHORING_GUIDE.md ← как создать новый плагин (idea → zip)
├── .claude/agents/             ← тонкие стабы агентов (дискаверятся Claude Code)
└── XTracker/                   ← плагин: мост Jarvis ↔ трекер XTracker (pulsar.x5.ru)
    ├── README.md  ·  DOMAIN.md (API/config/tools/UI)
    ├── Product_agents/         · команда агентов плагина (каноны xt-*, AGENTS.md, память)
    ├── docs/superpowers/       · спека + план адаптации (история)
    └── my-first-plugin-2/      · референс-scaffold + платформенный spec
```

## С чего начать

- **Понять правила** → [`_platform/constitution.md`](_platform/constitution.md) (устав) + [`_platform/platform-canon.md`](_platform/platform-canon.md) (контракт платформы).
- **Создать новый плагин** → [`_platform/PLUGIN_AUTHORING_GUIDE.md`](_platform/PLUGIN_AUTHORING_GUIDE.md).
- **Работать с агентами** → открой каталог плагина (напр. `XTracker/`) как рабочий корень; гид команды — [`XTracker/Product_agents/Dev_Agents/AGENTS.md`](XTracker/Product_agents/Dev_Agents/AGENTS.md).

## Текущие плагины

| Плагин | Что делает | Статус |
|---|---|---|
| [XTracker](XTracker/README.md) | Чат-интеграция Jarvis с issue-трекером XTracker (`pulsar.x5.ru`): поиск/создание/обновление/комментарии/смена статуса иссью | Операционка готова; v1-плагин — следующий шаг через `/pipeline-lite` |

## Лицензия

Внутренний корпоративный проект X5.

---
_Операционная система адаптирована из mothership `X5_BM`@c87e9ee6 (см. `XTracker/Product_agents/ADAPTATION.md`)._
