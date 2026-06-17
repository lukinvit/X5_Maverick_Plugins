# XTracker Operating System — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Author the adapted operating system (constitution + doctrines + production process + a 3-agent team) for the X5 Maverick Plugins program, ported from the X5_BM mothership and localized to the MCP-plugin / XTracker domain.

**Architecture:** "Mirror-lite" port (design spec `docs/superpowers/specs/2026-06-17-xtracker-operating-system-adaptation-design.md`). Portable **core** (agent personalities, Iron Rules, methodology, zero-trust, scope-the-class, report/memory formats) is ported from the mothership; the project **layer** (URLs, stack, commands, domain taxonomy, traps) is rewritten for MCP plugins. Each project writes its **own** constitution (16 invariants P-1…P-16 reframed from the platform spec). The v1 plugin itself is NOT in this plan — it ships later as the first feature through the resulting `/pipeline-lite`.

**Tech Stack:** Markdown documents + agent prompt files. No application code in this plan. Verification = structural checks, `grep` (no leaked mothership literals / phantom refs), the mothership adaptation DoD (§8) and version-probe (§4), and the Constitution-Check gate self-test.

## Global Constraints

- **Source of truth (read-only inputs):**
  - Mothership playbook: `/Users/v.lukin/Downloads/X5_BM_operating_playbook (1).md` (quote the path — it has a space + parenthesis). Cited below by line ranges.
  - Platform canon (MCP plugins): `XTracker/my-first-plugin-2/mcp_plugins_dev_spec.md` (cited by section §N).
  - Design spec (this work): `docs/superpowers/specs/2026-06-17-xtracker-operating-system-adaptation-design.md` (invariant set §2; v1 plugin §7).
  - XTracker API: by **description + structure only** — never vendor/inline the 1.2 MB `~/Downloads/pulsar-x5-ssl/XTracker_Api.json`.
- **Language:** all documents in Russian (`AGENT_LANG=ru`), matching mothership and Jarvis LLM.
- **Provenance banner:** every ported canon doc/agent starts with a one-line banner `> Адаптировано из X5_BM mothership@c87e9ee6 (2026-06-13). Ядро портировано, слой локализован под MCP-плагины/XTracker.`
- **Core/layer rule:** never invent new Iron Rules; localize the layer only. Never carry mothership domain traps (secretary, кворум, 208-ФЗ) into this project.
- **Anti-drift:** `.claude/agents/*` are thin stubs (≤35 lines, marker `runtime-стаб`, frontmatter byte-identical to the canon's frontmatter) pointing to the canon. No full runtime copies.
- **No unachievable BLOCKING:** every «ОБЯЗАТЕЛЬНО/BLOCKING» must be executable in this environment; otherwise phrase conditionally («при доступности инстанса») or drop it.
- **Aspirational ≠ gate:** coverage targets are measurable goals with honest gap reports, never blocking gates.
- **Data sacred:** append-only memory, archive-not-delete; do NOT delete `XTracker/my-first-plugin-2/` (reference scaffold).
- **Invariant IDs are frozen:** P-1…P-16 exactly as in design spec §2. A tool/doc citing `P-7` must mean Schema Rigor everywhere.
- **Commits:** stage explicit paths (never `git add -A`). Conventional-commit messages. End each commit body with `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.

---

## File Structure

All paths relative to the git root (`Plugins/`, here the worktree root). Author order matches task order: docs first (agents reference them), then agents, then index/provenance, then validation.

| File | Responsibility |
|---|---|
| `docs/constitution.md` | 16 invariants P-1…P-16, two super-values, precedence, amendments, журнал поправок. Apex doc. |
| `docs/constitution-check.md` | Gate procedure: read Часть-I invariants, emit per-invariant verdict + `MUST-FLAG: N`. DRY on constitution. |
| `docs/bug-handling-process.md` | Bug doctrine: systematic-debugging, scope-the-class, 3 guards (platform/LLM-ergonomics/secrets), evidence-first, DoD. |
| `docs/feature-process.md` | Feature doctrine: clean top-down for a plugin, track choice, feature DoD. |
| `docs/production-process.md` | `/pipeline-lite` (4 stages), Git Publish Runbook, memory convention overview. |
| `docs/platform-canon.md` | Pointer doc: where the MCP-plugin spec lives + XTracker API structure summary (no full OpenAPI). |
| `Product_agents/Dev_Agents/MEMORY_CONVENTION.md` | Memory file naming, two-level structure, append-only invariants, read-protocol, rotation. |
| `Product_agents/Dev_Agents/memmory_xt-builder.md` | Seed memory (pointer to convention + first journal stub). |
| `Product_agents/Dev_Agents/memmory_xt-protocol-qa.md` | Seed memory. |
| `Product_agents/Dev_Agents/memmory_xt-scribe.md` | Seed memory. |
| `Product_agents/Dev_Agents/xt-builder.md` | Canon: autonomous plugin developer. |
| `Product_agents/Dev_Agents/xt-protocol-qa.md` | Canon: adversarial MCP-protocol QA + zero-trust verify-gate. |
| `Product_agents/Dev_Agents/xt-scribe.md` | Canon: docs curator + AGENTS.md guardianship. |
| `.claude/agents/xt-builder.md` | Thin stub → canon. |
| `.claude/agents/xt-protocol-qa.md` | Thin stub → canon. |
| `.claude/agents/xt-scribe.md` | Thin stub → canon. |
| `Product_agents/Dev_Agents/AGENTS.md` | Cross-agent guide: Canonical Locations, Team Status, routing, evidence rules, stub rule. |
| `Product_agents/ADAPTATION.md` | Provenance: upstream SHA, date, roster, localization map, DoD status. |

---

## Task 1: Constitution (`docs/constitution.md`)

**Files:**
- Create: `docs/constitution.md`

**Interfaces:**
- Produces: invariant IDs `P-1`…`P-16` (frozen), two super-values, precedence chain, amendment process. Consumed by `constitution-check.md` (Task 2), both doctrines (Tasks 3–4), every agent canon (Tasks 11–13).

- [ ] **Step 1: Author the document.** Structure (headings exactly):
  - `# Конституция XTracker-плагинов — операционный устав` + provenance banner + `**Версия:** 1.0.0 (2026-06-17)`.
  - `## Преамбула — две супер-ценности` — copy verbatim the two super-values from design spec §1 (Данные и секреты sacred; Только production-ready) + the «нарушение = блокер» sentence.
  - `## Как пользоваться` — adapt mothership playbook lines 108–114 (sverka before decision/merge; spec-driven via Constitution-Check; agents check before action).
  - `## Часть I — 16 инвариантов` — for EACH of P-1…P-16, write the full 4-line canon form (**MUST/SHOULD** · _Зачем_ · _Как проверить_ · _Источник_) expanding the one-line summaries in design spec §2 (they already contain the rule text, the source ref, and a проверка hint). Keep the group emojis (🔒 Данные и секреты / 🏛 Контракт платформы / 🛡 Безопасность и изоляция / ⚙️ LLM-эргономика и эксплуатация / 🔬 Процесс / 🗄 Целостность под объёмом).
  - `## Часть II — Карта доменных канонов` — table mapping domains→canon: bug lifecycle→`bug-handling-process.md`; platform contract→`platform-canon.md` + `mcp_plugins_dev_spec.md`; feature flow→`feature-process.md`; process/gate→`production-process.md` + `constitution-check.md`; agents→`Product_agents/Dev_Agents/AGENTS.md`.
  - `## Часть III — Precedence, поправки, enforcement` — precedence chain from design spec §1; amendment semver (MAJOR remove invariant / MINOR add / PATCH wording); enforcement points (Stage-2 Constitution-Check, PR review, QA verify-gate).
  - `## Журнал поправок` — one row: `1.0.0 | 2026-06-17 | Первая редакция. 16 инвариантов (P-1…P-16), адаптация из X5_BM mothership@c87e9ee6. Супер-ценности: данные+секреты sacred; production-ready.`
- [ ] **Step 2: Verify structure.** Run: `grep -cE '^#### P-([1-9]|1[0-6]) ' docs/constitution.md` → Expected: `16`. Run: `grep -c 'MUST\|SHOULD' docs/constitution.md` → Expected: ≥16.
- [ ] **Step 3: Verify no leaked mothership literals.** Run: `grep -niE 'boardmaps|bm\.lukinvit|208-ФЗ|кворум|секретар|loadXForCaller|NATS|goose' docs/constitution.md` → Expected: no output.
- [ ] **Step 4: Commit.**
```bash
git add docs/constitution.md
git commit -m "docs: constitution v1.0.0 — 16 invariants for MCP plugins"
```

---

## Task 2: Constitution-Check gate (`docs/constitution-check.md`)

**Files:**
- Create: `docs/constitution-check.md`

**Interfaces:**
- Consumes: invariant IDs P-1…P-16 from Task 1 (reads them, does not hardcode their text — DRY).
- Produces: gate output format `MUST-FLAG: N` / `NEEDS-INFO` used by `production-process.md` Stage 2 (Task 5).

- [ ] **Step 1: Author.** Port mothership playbook lines 668–728 as core (DRY principle, вход, процедура, выход format, блокировка rule, self-test). Localize: the gate reads `docs/constitution.md` Часть I; for a spec/PR it emits a row per invariant `P-N | PASS|MUST-FLAG|NEEDS-INFO|N/A | <обоснование>` + a final `MUST-FLAG: N` count; any `MUST-FLAG` or `NEEDS-INFO`-on-a-MUST blocks Stage-3. Include a `## Self-тест` section: a deliberately bad mini-spec (hardcodes a token in env, no `additionalProperties`, mutates without confirm) MUST raise flags on P-1, P-7, P-2; a clean mini-spec MUST raise 0.
- [ ] **Step 2: Verify DRY.** Run: `grep -c 'Секреты XTracker\|systematic-debugging' docs/constitution-check.md` → Expected: `0` (it must reference invariants by ID, not copy their text).
- [ ] **Step 3: Dry-run the self-test by hand.** Read the bad mini-spec in the doc; confirm in prose the expected flags (P-1/P-2/P-7) are listed and the clean one lists 0. Expected: matches.
- [ ] **Step 4: Commit.**
```bash
git add docs/constitution-check.md
git commit -m "docs: constitution-check gate procedure (DRY on Часть I)"
```

---

## Task 3: Bug-handling doctrine (`docs/bug-handling-process.md`)

**Files:**
- Create: `docs/bug-handling-process.md`

**Interfaces:**
- Consumes: P-13, P-14, P-15 from Task 1.
- Produces: the fix loop + DoD self-audit referenced by `xt-builder` (Task 11) and `xt-protocol-qa` (Task 12).

- [ ] **Step 1: Author.** Port as CORE (mothership playbook lines 306–477): planka enterprise; systematic-debugging on ANY bug; enterprise-fix-not-patch; scope-the-class; evidence-first zero-trust; fix→test→verify→close loop; DoD self-audit. LOCALIZE the LAYER:
  - Three cross-cut guards renamed for plugins: **контракт-платформы** (manifest/protocol/schema/frozen ids), **LLM-эргономика** (SKILL.md discovery, batch/loop-safety, Generative-UI discipline), **безопасность-секретов** (no leak, RBAC honesty) — replacing mothership's architecture/perf/security.
  - Scope-the-class axes: **tool / поле schema / роль XTracker / состояние иссью / поверхность вывода**.
  - MCP traps section: weak-LLM loop on `isError:true` (→ P-3 idempotent-skip), batch-limits/compression (→ P-10), duplicate tool-calls, structured_content leaking into LLM context, secret in `runtime.log`.
  - Verify = real stdio JSON-RPC run (no browser); evidence on a different axis than the claim.
- [ ] **Step 2: Verify localization.** Run: `grep -niE 'browser|playwright|renata|кворум|meeting' docs/bug-handling-process.md` → Expected: no output. Run: `grep -c 'systematic-debugging\|scope-the-class\|stdio JSON-RPC' docs/bug-handling-process.md` → Expected: ≥3.
- [ ] **Step 3: Commit.**
```bash
git add docs/bug-handling-process.md
git commit -m "docs: bug-handling doctrine (core ported, MCP layer localized)"
```

---

## Task 4: Feature doctrine (`docs/feature-process.md`)

**Files:**
- Create: `docs/feature-process.md`

**Interfaces:**
- Consumes: P-13 from Task 1; the build order referenced by `xt-builder` (Task 11) and Stage-3 of `production-process.md` (Task 5).

- [ ] **Step 1: Author.** Port CORE (mothership playbook lines 730–790): главный принцип (production-ready), track choice (trivial vs speckit), constitution-compat at authoring time not review, feature DoD, autonomous mode. LOCALIZE: «фича» = a new tool or tool-cluster; build order top-down for an MCP plugin: `jarvis-plugin.json`/`SKILL.md` fragment → JSON Schema (`inputSchema`, `additionalProperties:false`) → tool handler (extract `__jarvis`, try/except) → Generative UI (text-fallback first) → protocol tests. Feature DoD = tool appears in `tools/list` with valid schema, happy+adversarial `tools/call` pass, idempotent-skip honored, no secret leak, SKILL.md updated.
- [ ] **Step 2: Verify.** Run: `grep -c 'tools/list\|inputSchema\|__jarvis\|идемпотент\|idempotent' docs/feature-process.md` → Expected: ≥4.
- [ ] **Step 3: Commit.**
```bash
git add docs/feature-process.md
git commit -m "docs: feature doctrine (clean top-down for MCP plugins)"
```

---

## Task 5: Production process (`docs/production-process.md`)

**Files:**
- Create: `docs/production-process.md`

**Interfaces:**
- Consumes: `constitution-check.md` (Task 2) as the Stage-2 gate; the three agents (Tasks 11–13) as stage owners; `MEMORY_CONVENTION.md` (Task 7).

- [ ] **Step 1: Author.** Three subsections:
  - `## /pipeline-lite` — 4 stages scaled for one plugin: **Stage 1 Creative** (request/issue → tool spec: inputSchema + SKILL.md fragment + expected output); **Stage 2 Audit** (run `constitution-check.md`, MUST-FLAG blocks); **Stage 3 Dev** (`xt-builder`); **Stage 4 Quality** (`xt-protocol-qa` verify-gate: real JSON-RPC run + adversarial + secret scan). State that for trivial single-tool tweaks stages 1–2 may be folded (track choice from `feature-process.md`).
  - `## Git Publish Runbook` — port mothership playbook lines 1576–1724 as CORE, localize: branch off main, stage explicit paths (never `git add -A` — protects `.env`/secrets per P-1), `Closes #N`, behavior on remote divergence, behavior when GitHub unreachable. Build/package note: zip the plugin per spec §16 (`rebuild_plugins.py`-style) — applies when building the plugin, not these docs.
  - `## Конвенция памяти (обзор)` — one-paragraph summary pointing to `Product_agents/Dev_Agents/MEMORY_CONVENTION.md` (Task 7) as the source of truth.
- [ ] **Step 2: Verify executability of every BLOCKING.** Read each «ОБЯЗАТЕЛЬНО/BLOCKING» line; confirm each is runnable here (git available; constitution-check is a doc procedure; JSON-RPC run needs only Python + the plugin). Rephrase any that need a live XTracker instance as «при доступности инстанса». Expected: no unconditional BLOCKING requires resources absent in dev.
- [ ] **Step 3: Verify.** Run: `grep -c 'Stage 1\|Stage 2\|Stage 3\|Stage 4\|git add -A' docs/production-process.md` → Expected: stages present; `git add -A` appears only in a "НЕ делай" context.
- [ ] **Step 4: Commit.**
```bash
git add docs/production-process.md
git commit -m "docs: production process — /pipeline-lite + git publish + memory"
```

---

## Task 6: Platform canon pointer (`docs/platform-canon.md`)

**Files:**
- Create: `docs/platform-canon.md`

**Interfaces:**
- Produces: the single pointer the constitution Часть II and agents cite for platform/API details.

- [ ] **Step 1: Author.** Sections: (1) pointer to `XTracker/my-first-plugin-2/mcp_plugins_dev_spec.md` as the platform contract canon, with a 1-line index of its key sections (§4 manifest, §5 SKILL.md, §6 protocol, §7 tools/`__jarvis`, §8 instances, §17 Generative UI, §20 batch, §21 idempotent-skip). (2) XTracker API structure summary: base `pulsar.x5.ru`, JWT Bearer + API-keys, multi-tenant; the chat-relevant services and their core endpoints from design spec §7 table; the rule «use API by description+structure only, do not vendor `XTracker_Api.json`». (3) where local copies live (`~/Downloads/pulsar-x5-ssl/`).
- [ ] **Step 2: Verify.** Run: `grep -c 'mcp_plugins_dev_spec\|pulsar.x5.ru\|description+structure\|description \+ structure\|структуре' docs/platform-canon.md` → Expected: ≥2. Confirm the doc does NOT paste large API schemas. Run: `wc -l docs/platform-canon.md` → Expected: < 120 lines.
- [ ] **Step 3: Commit.**
```bash
git add docs/platform-canon.md
git commit -m "docs: platform canon pointer (MCP spec + XTracker API structure)"
```

---

## Task 7: Memory convention + seed memories

**Files:**
- Create: `Product_agents/Dev_Agents/MEMORY_CONVENTION.md`
- Create: `Product_agents/Dev_Agents/memmory_xt-builder.md`
- Create: `Product_agents/Dev_Agents/memmory_xt-protocol-qa.md`
- Create: `Product_agents/Dev_Agents/memmory_xt-scribe.md`

**Interfaces:**
- Produces: memory file naming + read/append protocol referenced by all agent canons (Tasks 11–13) and `production-process.md` (Task 5).

- [ ] **Step 1: Author `MEMORY_CONVENTION.md`.** Port mothership playbook lines 1725–1809 as CORE: file naming (`memmory_<agent>.md`), two-level structure (long-term lessons + dated run journal), data-sacred invariants (append-only, archive-not-delete), read-protocol (read your memory before each run), rotation (who/when, byte-exact archival). Localize paths to `Product_agents/Dev_Agents/`.
- [ ] **Step 2: Author the 3 seed memories.** Each: a header pointer `> Конвенция: Product_agents/Dev_Agents/MEMORY_CONVENTION.md` + a `## Долгосрочные уроки` (empty placeholder line `(пока пусто — заполняется по итогам прогонов)`) + a `## Журнал прогонов` with one seed entry dated 2026-06-17: `seed — агент создан адаптацией из mothership@c87e9ee6`.
- [ ] **Step 3: Verify.** Run: `ls Product_agents/Dev_Agents/memmory_xt-*.md | wc -l` → Expected: `3`. Run: `grep -L 'MEMORY_CONVENTION' Product_agents/Dev_Agents/memmory_xt-*.md` → Expected: no output (all reference convention).
- [ ] **Step 4: Commit.**
```bash
git add Product_agents/Dev_Agents/MEMORY_CONVENTION.md Product_agents/Dev_Agents/memmory_xt-builder.md Product_agents/Dev_Agents/memmory_xt-protocol-qa.md Product_agents/Dev_Agents/memmory_xt-scribe.md
git commit -m "docs: memory convention + seed agent memories"
```

---

## Task 8: Canon `xt-builder` (`Product_agents/Dev_Agents/xt-builder.md`)

**Files:**
- Create: `Product_agents/Dev_Agents/xt-builder.md`

**Interfaces:**
- Consumes: constitution (P-1…P-16), all doctrines, memory convention.
- Produces: frontmatter (`name: xt-builder`, `description`, `model: opus`) reused byte-identically by the stub (Task 14); routing entry in AGENTS.md (Task 15).

- [ ] **Step 1: Author.** Provenance banner. CORE ported from Kulibin (mothership playbook lines 2028–2430): personality (autonomous engineer-inventor), Iron Rules, BUG-HUNTER at fix-verification, systematic-debugging, stop-list mechanics, self-audit before close, run summary, escalation, coordination, источники истины (priority order), final instruction. LOCALIZE the LAYER:
  - **Среда:** repo root `Plugins/`, plugin dir `XTracker/`, this op-system under `docs/` + `Product_agents/`.
  - **TEST PROTOCOL:** the MCP protocol harness (Task: see plugin plan) + `pytest -q`, `ruff check`, `mypy` for Python; build = zip per spec §16.
  - **Что НЕ делает:** never change `slug`/`remote_name` (P-6); never put secrets anywhere but `__jarvis.config` (P-1); never ship stubs (P-13).
  - **Источники истины:** constitution > `docs/platform-canon.md` (+spec) > API structure > CLAUDE.md > memory.
- [ ] **Step 2: Verify no mothership leakage.** Run: `grep -niE 'boardmaps|bm\.lukinvit|deploy\.sh|go-backend|meeting|кворум' Product_agents/Dev_Agents/xt-builder.md` → Expected: no output.
- [ ] **Step 3: Verify frontmatter present.** Run: `head -6 Product_agents/Dev_Agents/xt-builder.md` → Expected: YAML frontmatter with `name: xt-builder` and `model:`.
- [ ] **Step 4: Commit.**
```bash
git add Product_agents/Dev_Agents/xt-builder.md
git commit -m "docs: xt-builder canon (Kulibin core ported, XTracker layer)"
```

---

## Task 9: Canon `xt-protocol-qa` (`Product_agents/Dev_Agents/xt-protocol-qa.md`)

**Files:**
- Create: `Product_agents/Dev_Agents/xt-protocol-qa.md`

**Interfaces:**
- Consumes: P-15 (zero-trust), P-1/P-3/P-7/P-10/P-11 (the things it checks), bug-handling doctrine.
- Produces: frontmatter reused by stub (Task 14); the verify-gate Stage 4 owner in `production-process.md`.

- [ ] **Step 1: Author.** Provenance banner. CORE merged from Renata + Zanuda (mothership playbook lines 2431–2914 and 3665–4104): bug-hunter philosophy, zero-trust verify-gate, adversarial-before-happy-path, finding/report format, intersection sections, closure gates (same reproducer & proven root cause). LOCALIZE the LAYER — this REPLACES browser-QA entirely; its test scope is the stdio JSON-RPC surface:
  - Validate `tools/list`: every tool has `inputSchema` `type:object`, `additionalProperties:false`, per-field `description`, correct `required`/`enum`/`default` (P-7); names follow `slug__verb_noun`, data-getters use protected verbs (P-10).
  - Drive `tools/call`: happy path + adversarial (missing required, wrong types, unknown fields, `__jarvis` injection, oversized input); confirm process never crashes (P-5).
  - Idempotent-skip (P-3): repeat same args → `isError:false` + `⏭️ ПРОПУСК`, state not duplicated.
  - Generative UI (P-11): every `structured_content` has a `text` fallback; actions have unique `id` + full `slug__remote_name`; structured_content absent from any LLM-facing text.
  - **Secret-leak scan (P-1):** no token/password from `__jarvis.config` appears in any `content`, `_meta`, or `runtime.log`.
  - File-offload (P-11/§5.3): large outputs use `upload_file` artifact_id, not base64.
  - Evidence rule: every verdict backed by a captured JSON-RPC request/response transcript.
- [ ] **Step 2: Verify localization.** Run: `grep -niE 'playwright|browser|screenshot|viewport|sidebar|meeting' Product_agents/Dev_Agents/xt-protocol-qa.md` → Expected: no output. Run: `grep -c 'tools/list\|tools/call\|idempotent\|structured_content\|секрет' Product_agents/Dev_Agents/xt-protocol-qa.md` → Expected: ≥4.
- [ ] **Step 3: Commit.**
```bash
git add Product_agents/Dev_Agents/xt-protocol-qa.md
git commit -m "docs: xt-protocol-qa canon (Renata+Zanuda core, stdio-JSON-RPC QA layer)"
```

---

## Task 10: Canon `xt-scribe` (`Product_agents/Dev_Agents/xt-scribe.md`)

**Files:**
- Create: `Product_agents/Dev_Agents/xt-scribe.md`

**Interfaces:**
- Consumes: P-9 (SKILL.md discovery quality), AGENTS.md guardianship duty.
- Produces: frontmatter reused by stub (Task 14).

- [ ] **Step 1: Author.** Provenance banner. CORE ported from Pushkin (mothership playbook lines 4105–4359): tech-writer principles, style, audiences, источники истины, publish discipline, AGENTS.md guardianship, docs-freshness standing duty, output contract. LOCALIZE: docs = `SKILL.md` (enforce P-9: description ≤1024, no `<>`, triggers + НЕ-использовать, body without literal tool-calls per spec §18.2), `README`, this op-system's `docs/`; wiki structure for plugin docs.
- [ ] **Step 2: Verify.** Run: `grep -c 'SKILL.md\|AGENTS.md\|P-9\|description' Product_agents/Dev_Agents/xt-scribe.md` → Expected: ≥3. Run: `grep -niE 'boardmaps|obsidian-база X5_BM|meeting' Product_agents/Dev_Agents/xt-scribe.md` → Expected: no output.
- [ ] **Step 3: Commit.**
```bash
git add Product_agents/Dev_Agents/xt-scribe.md
git commit -m "docs: xt-scribe canon (Pushkin core, SKILL.md/docs layer)"
```

---

## Task 11: Thin stubs (`.claude/agents/*.md`)

**Files:**
- Create: `.claude/agents/xt-builder.md`
- Create: `.claude/agents/xt-protocol-qa.md`
- Create: `.claude/agents/xt-scribe.md`

**Interfaces:**
- Consumes: the frontmatter of each canon (Tasks 8–10) — must be byte-identical.

- [ ] **Step 1: Author each stub.** ≤35 lines. Content: the canon's exact frontmatter block, then a body of only: marker line `# runtime-стаб — НЕ полный профиль`, a pointer `Полный канон: Product_agents/Dev_Agents/<agent>.md — прочитай его ПЕРВЫМ перед любым действием`, and the mandatory start-of-run order (read canon → read your `memmory_<agent>.md` → read `docs/constitution.md`). No rules, no test protocols, no domain content (those live in the canon only).
- [ ] **Step 2: Verify length + marker.** Run: `for f in .claude/agents/xt-*.md; do echo "$f: $(wc -l < $f) lines"; grep -q 'runtime-стаб' "$f" && echo OK || echo MISSING-MARKER; done` → Expected: each ≤35 lines and `OK`.
- [ ] **Step 3: Verify frontmatter parity.** For each agent, compare the frontmatter block (between the first two `---` lines) of the stub vs the canon. Run: `for a in xt-builder xt-protocol-qa xt-scribe; do diff <(awk '/^---$/{c++} c==1{print} c==2{exit}' .claude/agents/$a.md) <(awk '/^---$/{c++} c==1{print} c==2{exit}' Product_agents/Dev_Agents/$a.md) && echo "$a: parity OK" || echo "$a: MISMATCH"; done` → Expected: all `parity OK`.
- [ ] **Step 4: Commit.**
```bash
git add .claude/agents/xt-builder.md .claude/agents/xt-protocol-qa.md .claude/agents/xt-scribe.md
git commit -m "docs: thin runtime stubs → canon (anti-drift)"
```

---

## Task 12: Cross-agent guide (`Product_agents/Dev_Agents/AGENTS.md`)

**Files:**
- Create: `Product_agents/Dev_Agents/AGENTS.md`

**Interfaces:**
- Consumes: all three canons (Tasks 8–10), constitution, doctrines, memory convention.

- [ ] **Step 1: Author.** Port mothership AGENTS.md structure (playbook lines 1852–2022) as CORE, localized: `## Canonical Locations` (canons in `Product_agents/Dev_Agents/`, stubs in `.claude/agents/`, docs in `docs/`, memory convention path); `## Start-Of-Run Commands` (read stub→canon→memory→constitution; `git status`); `## Publish Discipline` (pointer to `production-process.md` Git Publish Runbook); `## Team Status & Memory Index` table (3 agents, status `активен (адаптация 2026-06-17)`, memory file); `## Agent Routing` (builder=implement/fix tools; protocol-qa=verify/adversarial/verify-gate; scribe=SKILL.md/README/docs); `## Evidence And Issue Rules` (zero-trust, evidence on different axis — P-15); `## Editing This File` (guardianship = xt-scribe); `## Стаб-правило` (no full runtime copies). Add transitional note: stubs/agents work in this repo; the v1 plugin is built next as the first `/pipeline-lite` feature.
- [ ] **Step 2: Verify routing covers all agents.** Run: `grep -c 'xt-builder\|xt-protocol-qa\|xt-scribe' Product_agents/Dev_Agents/AGENTS.md` → Expected: ≥6 (each named in Team Status + Routing). Run: `grep -niE 'kulibin|renata|semiglazka|zanuda|pushkin|dobivatel|her' Product_agents/Dev_Agents/AGENTS.md` → Expected: no output (mothership names replaced).
- [ ] **Step 3: Commit.**
```bash
git add Product_agents/Dev_Agents/AGENTS.md
git commit -m "docs: AGENTS.md cross-agent guide (3-agent team, routing, stub rule)"
```

---

## Task 13: Provenance (`Product_agents/ADAPTATION.md`)

**Files:**
- Create: `Product_agents/ADAPTATION.md`

**Interfaces:**
- Consumes: nothing (records facts about Tasks 1–12).

- [ ] **Step 1: Author.** Port mothership `ADAPTATION_PIPELINE`/`ADAPTATIONS` provenance shape (playbook lines 7765–7785) as a single project record: `PROJECT_NAME=X5 Maverick Plugins / XTracker`, `PROJECT_KEY=XT`, `GH_REPO` (fill from `git remote -v`, or `-` if none), `UPSTREAM_SHA=c87e9ee6`, `Bootstrap=2026-06-17 (manual, via brainstorming+plan)`, roster `xt-builder, xt-protocol-qa, xt-scribe`, approach `Mirror-lite`, и localization map (what was core-ported vs layer-rewritten, per design spec §4/§6). Status: `адаптация в процессе` until Task 14 DoD passes, then flip to `адаптация завершена 2026-06-17, DoD зелёный`.
- [ ] **Step 2: Verify.** Run: `grep -c 'c87e9ee6\|xt-builder\|xt-protocol-qa\|xt-scribe\|Mirror-lite' Product_agents/ADAPTATION.md` → Expected: ≥4.
- [ ] **Step 3: Commit.**
```bash
git add Product_agents/ADAPTATION.md
git commit -m "docs: ADAPTATION.md provenance record"
```

---

## Task 14: Adaptation DoD validation + version-probe

**Files:**
- Modify: `Product_agents/ADAPTATION.md` (flip status at the end)

**Interfaces:**
- Consumes: all prior tasks' outputs.

- [ ] **Step 1: Run the mothership adaptation DoD §8 checklist** (playbook lines 7736–7748) against this repo. For each line, produce a one-line evidence note:
  - stubs ≤35 lines + marker + frontmatter parity (re-run Task 11 Step 2–3 commands) → record PASS/FAIL.
  - no mothership literals anywhere. Run: `grep -rniE 'boardmaps|bm\.lukinvit\.tech|lukinvit/X5_BM|loadXForCaller|кворум|208-ФЗ' docs/ Product_agents/ .claude/agents/` → Expected: no output.
  - no phantom references (every doc/agent path cited actually exists). Run a check: `grep -rhoE '(docs|Product_agents|\.claude/agents)/[A-Za-z0-9_./-]+\.md' docs/ Product_agents/ .claude/agents/ | sort -u | while read p; do [ -e "$p" ] || echo "MISSING: $p"; done` → Expected: no `MISSING:` lines (paths under `XTracker/` and the live spec are allowed external refs — verify those exist too).
  - memory: each agent has seed + convention pointer (re-run Task 7 Step 3).
  - aspirational norms phrased as goals not gates (manual read of doctrines/agents) → record note.
- [ ] **Step 2: Version-probe each agent** (playbook §6.1 step 4). Dispatch a fresh subagent per agent with a NON-working probe prompt: "Прочитай свой стаб `.claude/agents/<a>.md`: процитируй маркер; есть ли строка 'runtime-стаб'; назови путь канона и процитируй первые 3 строки канона; назови проект." Expected: each confirms stub→canon→correct project (XTracker, not BoardMaps). Record results in `ADAPTATION.md`.
- [ ] **Step 3: Constitution-Check self-test** (from Task 2). Manually run the gate's bad/clean mini-specs; confirm bad → flags on P-1/P-2/P-7, clean → 0. Expected: matches.
- [ ] **Step 4: Flip status + commit.** Update `ADAPTATION.md` status to `адаптация завершена 2026-06-17, DoD §8 зелёный` with the evidence notes appended.
```bash
git add Product_agents/ADAPTATION.md
git commit -m "docs: adaptation DoD green — version-probe + checks passed"
```

---

## Self-Review (completed by plan author)

**Spec coverage:** design spec §2 (16 invariants)→Task 1; §3 layout→Tasks 1–13 file map; §4 doctrines→Tasks 3–4; §5 process→Task 5; §6 agents→Tasks 8–12; §8 deliverables A+B→Tasks 1–13; §8 C+D (plugin+harness)→**out of scope, separate plan** (per §9.4). Constitution-Check enforcement→Tasks 2,14. Provenance/anti-drift→Tasks 11,13,14.

**Placeholder scan:** seed memories intentionally contain an empty `(пока пусто)` long-term-lessons line — that is correct seed content, not a plan placeholder. No "TBD/implement later" directives; every doc task names exact source lines/sections and exact verification commands.

**Consistency:** invariant IDs P-1…P-16 used identically across all tasks; agent names `xt-builder`/`xt-protocol-qa`/`xt-scribe` consistent; frontmatter-parity check (Task 11) guards stub↔canon drift; `MUST-FLAG: N` gate format defined in Task 2 and consumed in Tasks 5/14.

**Out of scope (next plan):** the v1 XTracker plugin (`jarvis-plugin.json`, `SKILL.md`, `config/*`, `server.py` + the §7 tools, vendored SDK, README) and the protocol-QA harness — built as the first `/pipeline-lite` feature using the system this plan produces.
