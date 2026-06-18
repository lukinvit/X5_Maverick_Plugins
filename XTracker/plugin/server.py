#!/usr/bin/env python3
"""XTracker MCP plugin — мост Jarvis ↔ issue-трекер XTracker (xtracker.x5team.ru).

Ручной MCP-stdio JSON-RPC сервер (newline-delimited). Поддерживает
initialize / tools/list / tools/call. Зависимостей нет — только stdlib.

Инварианты (см. _platform/constitution.md): секреты только из __jarvis.config (P-1),
строгие схемы (P-7), idempotent-skip (P-3), не ронять процесс (P-5),
batch/loop-safe нейминг и compact-результаты (P-10), bounded results (P-16).
"""
import hashlib
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

SLUG = "xtracker"
DEFAULT_BASE_URL = "https://xtracker.x5team.ru"
SEARCH_LIMIT_DEFAULT = 20
SEARCH_LIMIT_MAX = 100

# Процессное состояние (один процесс на пакет; lazy start).
_op_cache = set()        # idempotency: seen f"{tool}:{operation_id}"
_token_cache = {}        # config_hash -> {"access", "refresh", "exp"}


class AuthError(Exception):
    """Ошибка аутентификации/конфигурации (показывается пользователю без секретов)."""


# --------------------------------------------------------------------------- IO

def _send(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _ok(req_id, content, meta=None):
    result = {"isError": False, "content": content}
    if meta:
        result["_meta"] = meta
    _send({"jsonrpc": "2.0", "id": req_id, "result": result})


def _text_ok(req_id, text, meta=None):
    _ok(req_id, [{"type": "text", "text": text}], meta)


def _error(req_id, text, code="XTRACKER_ERROR"):
    # P-10: ERROR-результат содержит keyword + machine-readable JSON.
    _send({
        "jsonrpc": "2.0", "id": req_id,
        "result": {
            "isError": True,
            "content": [{"type": "text", "text": json.dumps(
                {"type": "ERROR", "code": code, "text": text}, ensure_ascii=False)}],
        },
    })


def _data_result(req_id, text, contextual, template_id, data, actions=None):
    """Dual-response (spec §17.6): данные доходят до LLM/не-GUI И до UI.

    - text — читаемое резюме С ДАННЫМИ (LLM + клиенты без Generative UI, §17.2);
    - json `_contextual` — структурированные данные для LLM (payload);
    - structured_content — интерактивный UI (НЕ в LLM-контексте, P-11).
    Без `_meta.user_text` — он бы скрыл text и спрятал данные (баг 2026-06-17)."""
    sc = {"template_id": template_id, "data": data}
    if actions:
        sc["actions"] = actions
    ctx = dict(contextual)
    ctx["_contextual"] = True
    _ok(req_id, [
        {"type": "text", "text": text},
        {"type": "json", "json": ctx},
        {"type": "structured_content", "json": sc},
    ])


# ------------------------------------------------------------------------- HTTP

def _ssl_ctx(cfg):
    ctx = ssl.create_default_context()
    if not cfg.get("verify_ssl", True):
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    ca = cfg.get("ca_cert")
    if ca and os.path.exists(ca):
        ctx.load_verify_locations(ca)
    return ctx


def _request(cfg, method, path, token=None, body=None, query=None):
    """Выполнить HTTP-запрос. Возвращает (status:int, parsed_json:dict|list).

    Сетевые/таймаут-ошибки → AuthError-независимый RuntimeError с понятным текстом
    (P-12 resilience). Секреты в текст ошибки не попадают (P-1)."""
    base = (cfg.get("base_url") or DEFAULT_BASE_URL).rstrip("/")
    url = base + path
    if query:
        url += "?" + urllib.parse.urlencode(query)
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/json")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    timeout = cfg.get("timeout", 30)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ssl_ctx(cfg)) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, (json.loads(raw) if raw.strip() else {})
    except urllib.error.HTTPError as exc:
        raw = ""
        try:
            raw = exc.read().decode("utf-8")
            parsed = json.loads(raw)
        except Exception:
            parsed = {"message": (raw or "").strip()[:300]}
        return exc.code, parsed
    except urllib.error.URLError as exc:
        raise RuntimeError("XTracker недоступен (%s). Проверьте base_url/сеть или повторите позже."
                           % getattr(exc, "reason", "network error"))
    except (TimeoutError, ssl.SSLError) as exc:
        raise RuntimeError("Запрос к XTracker не выполнен: %s. Проверьте таймаут/SSL." % exc)


def _http_error_text(status, body):
    msg = ""
    if isinstance(body, dict):
        msg = body.get("message") or body.get("error") or body.get("detail") or ""
    base = "HTTP %s от XTracker" % status
    if status in (401, 403):
        return base + " — нет доступа (проверьте права/токен инстанса). " + msg
    if status == 404:
        return base + " — не найдено. " + msg
    return (base + ". " + msg).strip()


# ------------------------------------------------------------------------- AUTH

def _config_key(cfg):
    raw = json.dumps({k: cfg.get(k) for k in
                      ("base_url", "auth_mode", "api_key", "email", "password", "organization")},
                     sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _get_token(cfg):
    """Вернуть Bearer-токен. api_key → сам ключ; password → JWT (login/refresh, кэш)."""
    mode = (cfg.get("auth_mode") or "api_key").lower()
    if mode == "api_key":
        key = cfg.get("api_key")
        if not key:
            raise AuthError("api_key не задан в конфигурации инстанса")
        return key

    ck = _config_key(cfg)
    now = time.time()
    ent = _token_cache.get(ck)
    if ent and ent["exp"] - 30 > now:
        return ent["access"]
    if ent and ent.get("refresh"):
        status, body = _request(cfg, "POST", "/api/v1/auth/refresh",
                                body={"refresh_token": ent["refresh"]})
        if status == 200 and isinstance(body, dict) and body.get("access_token"):
            _token_cache[ck] = {"access": body["access_token"],
                                "refresh": body.get("refresh_token", ent["refresh"]),
                                "exp": now + body.get("expires_in", 3600)}
            return _token_cache[ck]["access"]
    email, password = cfg.get("email"), cfg.get("password")
    if not email or not password:
        raise AuthError("email/password не заданы в конфигурации инстанса (auth_mode=password)")
    status, body = _request(cfg, "POST", "/api/v1/auth/login",
                            body={"email": email, "password": password})
    if status != 200 or not isinstance(body, dict) or not body.get("access_token"):
        raise AuthError("логин в XTracker не удался (HTTP %s)" % status)
    _token_cache[ck] = {"access": body["access_token"],
                        "refresh": body.get("refresh_token"),
                        "exp": now + body.get("expires_in", 3600)}
    return _token_cache[ck]["access"]


# ------------------------------------------------------------------- helpers UI

def _issue_card_fields(issue):
    fields = []
    if issue.get("status"):
        fields.append({"label": "Статус", "value": str(issue["status"]), "type": "badge"})
    if issue.get("type"):
        fields.append({"label": "Тип", "value": str(issue["type"])})
    if issue.get("priority"):
        fields.append({"label": "Приоритет", "value": str(issue["priority"]), "type": "badge"})
    if issue.get("assignee"):
        fields.append({"label": "Исполнитель", "value": str(issue["assignee"])})
    return fields


def _issue_title(issue):
    return issue.get("title") or issue.get("summary") or issue.get("key") or "—"


def _issue_actions(key):
    return [
        {"id": "open_%s" % key, "label": "Открыть", "tool": "%s__get_issue" % SLUG,
         "params": {"key": key}, "style": "default", "icon": "search"},
        {"id": "comment_%s" % key, "label": "Коммент", "tool": "%s__comment_issue" % SLUG,
         "params": {"issue_key": key}, "style": "default"},
    ]


# ----------------------------------------------------------------------- tools

def _t_whoami(req_id, args, cfg):
    token = _get_token(cfg)
    status, body = _request(cfg, "GET", "/api/v1/users/me", token=token)
    if status != 200:
        return _error(req_id, _http_error_text(status, body), code="AUTH")
    name = (body.get("display_name") or body.get("email") or body.get("id") or "—") if isinstance(body, dict) else "—"
    email = body.get("email", "") if isinstance(body, dict) else ""
    _text_ok(req_id, "Текущий пользователь XTracker: %s%s" % (name, (" <%s>" % email) if email else ""))


def _t_config_test_connection(req_id, args, cfg):
    try:
        token = _get_token(cfg)
    except AuthError as exc:
        return _error(req_id, str(exc), code="CONFIG")
    status, body = _request(cfg, "GET", "/api/v1/users/me", token=token)
    if status == 200:
        name = body.get("display_name") or body.get("email") or "ok" if isinstance(body, dict) else "ok"
        return _text_ok(req_id, "OK: соединение с XTracker установлено (%s)." % name)
    return _error(req_id, _http_error_text(status, body), code="CONFIG")


def _t_search_issues(req_id, args, cfg):
    query = (args.get("query") or "").strip()
    if not query:
        return _error(req_id, "Пустой query. Укажите YTQL-запрос, напр. \"status = open AND assignee = me()\".",
                      code="INVALID_ARG")
    try:
        limit = int(args.get("limit", SEARCH_LIMIT_DEFAULT))
    except (TypeError, ValueError):
        limit = SEARCH_LIMIT_DEFAULT
    limit = max(1, min(limit, SEARCH_LIMIT_MAX))
    token = _get_token(cfg)
    body_req = {"query": query}
    if args.get("source"):
        body_req["source"] = args["source"]
    status, body = _request(cfg, "POST", "/api/v1/issues/_search", token=token, body=body_req)
    if status != 200:
        return _error(req_id, _http_error_text(status, body), code="SEARCH")
    issues = []
    if isinstance(body, dict):
        issues = body.get("issues") or body.get("results") or body.get("data") or []
    elif isinstance(body, list):
        issues = body
    total = (body.get("total") if isinstance(body, dict) else None) or len(issues)
    shown = issues[:limit]  # P-16: bounded results
    lines = ["Найдено иссью: %s (показано %s)." % (total, len(shown))]
    items = []
    ctx_issues = []
    for it in shown:
        key = it.get("key", "?")
        title = _issue_title(it)
        bits = [b for b in [str(it.get("status") or ""), str(it.get("type") or ""),
                            str(it.get("priority") or ""),
                            ("исп. " + str(it["assignee"])) if it.get("assignee") else ""] if b]
        lines.append("• %s — %s%s" % (key, title, (" [" + ", ".join(bits) + "]") if bits else ""))
        items.append({
            "title": "%s — %s" % (key, title),
            "badge": str(it.get("status") or ""),
            "fields": _issue_card_fields(it),
            "actions": _issue_actions(key),
        })
        ctx_issues.append({"key": key, "title": title, "status": it.get("status"),
                           "assignee": it.get("assignee"), "type": it.get("type"),
                           "priority": it.get("priority"), "queue_key": it.get("queue_key")})
    _data_result(req_id, "\n".join(lines),
                 {"issues": ctx_issues, "total": total, "query": query},
                 "preset:card_list",
                 {"title": "Поиск: %s" % query, "total_count": total, "items": items})


def _t_get_issue(req_id, args, cfg):
    key = (args.get("key") or "").strip()
    if not key:
        return _error(req_id, "Не указан key иссью (напр. PROJ-123).", code="INVALID_ARG")
    token = _get_token(cfg)
    status, issue = _request(cfg, "GET", "/api/v1/issues/" + urllib.parse.quote(key), token=token)
    if status != 200:
        return _error(req_id, _http_error_text(status, issue), code="GET")
    ikey = issue.get("key", key)
    lines = ["%s — %s" % (ikey, _issue_title(issue))]
    for label, val in [("Очередь", issue.get("queue_key")), ("Статус", issue.get("status")),
                       ("Тип", issue.get("type")), ("Приоритет", issue.get("priority")),
                       ("Исполнитель", issue.get("assignee")), ("Репортёр", issue.get("reporter"))]:
        if val:
            lines.append("%s: %s" % (label, val))
    if issue.get("description"):
        lines.append("Описание: %s" % issue["description"])
    text = "\n".join(lines)
    ctx = {"issue": {k: issue.get(k) for k in
                     ("key", "title", "queue_key", "status", "type", "priority",
                      "assignee", "reporter", "description") if issue.get(k) is not None}}
    data = {"title": "%s — %s" % (ikey, _issue_title(issue)),
            "subtitle": issue.get("queue_key", ""),
            "badge": str(issue.get("status") or ""),
            "fields": _issue_card_fields(issue) +
                      ([{"label": "Описание", "value": issue["description"]}] if issue.get("description") else [])}
    _data_result(req_id, text, ctx, "preset:card", data, actions=_issue_actions(ikey))


def _dedup(tool, args):
    """Idempotent-skip (P-3): True если operation_id уже виден в этом процессе."""
    op = args.get("operation_id")
    if not op:
        return False
    sig = "%s:%s" % (tool, op)
    if sig in _op_cache:
        return True
    _op_cache.add(sig)
    return False


def _t_create_issue(req_id, args, cfg):
    if _dedup("create_issue", args):
        return _text_ok(req_id, "⏭️ ПРОПУСК: иссью с этим operation_id уже создано. НЕ ПОВТОРЯЙ вызов — иди дальше по плану.",
                        meta={"user_text": "Пропущен дубль создания"})
    missing = [f for f in ("queue_key", "summary", "type", "priority") if not args.get(f)]
    if missing:
        return _error(req_id, "Не заполнены обязательные поля: %s." % ", ".join(missing), code="INVALID_ARG")
    body = {k: args[k] for k in ("queue_key", "summary", "type", "priority")}
    for opt in ("description", "assignee_id"):
        if args.get(opt):
            body[opt] = args[opt]
    token = _get_token(cfg)
    status, created = _request(cfg, "POST", "/api/v1/issues", token=token, body=body)
    if status not in (200, 201):
        return _error(req_id, _http_error_text(status, created), code="CREATE")
    key = created.get("key", "?") if isinstance(created, dict) else "?"
    _text_ok(req_id, "✅ Готово: иссью создано (1) [key=%s]" % key,
             meta={"user_text": "Иссью %s создано" % key})


def _t_update_issue(req_id, args, cfg):
    if _dedup("update_issue", args):
        return _text_ok(req_id, "⏭️ ПРОПУСК: обновление с этим operation_id уже выполнено. НЕ ПОВТОРЯЙ вызов.",
                        meta={"user_text": "Пропущен дубль обновления"})
    key = (args.get("key") or "").strip()
    if not key:
        return _error(req_id, "Не указан key иссью.", code="INVALID_ARG")
    allowed = ("summary", "description", "priority", "type", "due_date", "start_date")
    body = {k: args[k] for k in allowed if args.get(k) is not None}
    if not body:
        return _error(req_id, "Нечего обновлять: укажите хотя бы одно поле (%s)." % ", ".join(allowed),
                      code="INVALID_ARG")
    token = _get_token(cfg)
    status, _b = _request(cfg, "PATCH", "/api/v1/issues/" + urllib.parse.quote(key), token=token, body=body)
    if status not in (200, 204):
        return _error(req_id, _http_error_text(status, _b), code="UPDATE")
    _text_ok(req_id, "✅ Готово: иссью обновлено (1) [key=%s]" % key,
             meta={"user_text": "Иссью %s обновлено" % key})


def _t_comment_issue(req_id, args, cfg):
    if _dedup("comment_issue", args):
        return _text_ok(req_id, "⏭️ ПРОПУСК: комментарий с этим operation_id уже добавлен. НЕ ПОВТОРЯЙ вызов.",
                        meta={"user_text": "Пропущен дубль комментария"})
    key = (args.get("issue_key") or "").strip()
    content = (args.get("content") or "").strip()
    if not key or not content:
        return _error(req_id, "Нужны issue_key и непустой content.", code="INVALID_ARG")
    token = _get_token(cfg)
    status, _b = _request(cfg, "POST",
                          "/api/v1/issues/" + urllib.parse.quote(key) + "/comments",
                          token=token, body={"content": content})
    if status not in (200, 201):
        return _error(req_id, _http_error_text(status, _b), code="COMMENT")
    _text_ok(req_id, "✅ Готово: комментарий добавлен (1) [key=%s]" % key,
             meta={"user_text": "Комментарий к %s добавлен" % key})


def _t_transition_issue(req_id, args, cfg):
    if _dedup("transition_issue", args):
        return _text_ok(req_id, "⏭️ ПРОПУСК: переход с этим operation_id уже выполнен. НЕ ПОВТОРЯЙ вызов.",
                        meta={"user_text": "Пропущен дубль перехода"})
    key = (args.get("key") or "").strip()
    code = args.get("to_status_code")
    sid = args.get("to_status_id")
    if not key or (not code and not sid):
        return _error(req_id, "Нужны key и ровно один из to_status_code / to_status_id.", code="INVALID_ARG")
    body = {}
    if sid:
        body["to_status_id"] = sid
    else:
        body["to_status_code"] = code
    token = _get_token(cfg)
    status, _b = _request(cfg, "POST",
                          "/api/v1/issues/" + urllib.parse.quote(key) + "/transitions",
                          token=token, body=body)
    if status not in (200, 201, 204):
        return _error(req_id, _http_error_text(status, _b), code="TRANSITION")
    target = code or sid
    _text_ok(req_id, "✅ Готово: статус изменён (1) [key=%s → %s]" % (key, target),
             meta={"user_text": "Статус %s изменён" % key})


def _t_assign_issue(req_id, args, cfg):
    if _dedup("assign_issue", args):
        return _text_ok(req_id, "⏭️ ПРОПУСК: назначение с этим operation_id уже выполнено. НЕ ПОВТОРЯЙ вызов.",
                        meta={"user_text": "Пропущен дубль назначения"})
    key = (args.get("key") or "").strip()
    if not key:
        return _error(req_id, "Не указан key иссью.", code="INVALID_ARG")
    token = _get_token(cfg)
    if args.get("unassign"):
        status, _b = _request(cfg, "POST",
                              "/api/v1/issues/" + urllib.parse.quote(key) + "/unassign", token=token)
        if status not in (200, 201, 204):
            return _error(req_id, _http_error_text(status, _b), code="ASSIGN")
        return _text_ok(req_id, "✅ Готово: исполнитель снят (1) [key=%s]" % key,
                        meta={"user_text": "Исполнитель %s снят" % key})
    assignee = (args.get("assignee") or "").strip()
    if not assignee:
        return _error(req_id, "Укажите assignee (user id) или unassign=true.", code="INVALID_ARG")
    status, _b = _request(cfg, "POST",
                          "/api/v1/issues/" + urllib.parse.quote(key) + "/assign",
                          token=token, body={"assignee": assignee})
    if status not in (200, 201, 204):
        return _error(req_id, _http_error_text(status, _b), code="ASSIGN")
    _text_ok(req_id, "✅ Готово: иссью назначено (1) [key=%s]" % key,
             meta={"user_text": "Иссью %s назначено" % key})


_TOOLS = {
    "search_issues": _t_search_issues,
    "get_issue": _t_get_issue,
    "create_issue": _t_create_issue,
    "update_issue": _t_update_issue,
    "comment_issue": _t_comment_issue,
    "transition_issue": _t_transition_issue,
    "assign_issue": _t_assign_issue,
    "whoami": _t_whoami,
    "config_test_connection": _t_config_test_connection,
}


# --------------------------------------------------------------------- tools/list

def _tools_list_result():
    s = {"type": "string"}
    return {"tools": [
        {"name": "search_issues",
         "description": "Поиск иссью в XTracker по YTQL-запросу. Используй когда пользователь ищет задачи: \"найди иссью\", \"мои открытые задачи\", \"баги в очереди PROJ\". Возвращает карточки с ключом, статусом, исполнителем.",
         "inputSchema": {"type": "object", "additionalProperties": False,
                         "properties": {
                             "query": {"type": "string", "minLength": 1,
                                       "description": "YTQL-запрос, напр. 'status = open AND assignee = me()' или 'queue = PROJ AND type = bug'"},
                             "source": {"type": "string", "enum": ["postgres", "pg", "elasticsearch", "es"],
                                        "description": "Источник данных (опц.)"},
                             "limit": {"type": "integer", "minimum": 1, "maximum": SEARCH_LIMIT_MAX,
                                       "default": SEARCH_LIMIT_DEFAULT, "description": "Макс. число результатов"}},
                         "required": ["query"]}},
        {"name": "get_issue",
         "description": "Получить детали одной иссью XTracker по ключу (напр. PROJ-123): заголовок, статус, исполнитель, приоритет, описание.",
         "inputSchema": {"type": "object", "additionalProperties": False,
                         "properties": {"key": {"type": "string", "minLength": 1,
                                                "description": "Ключ иссью, напр. PROJ-123"}},
                         "required": ["key"]}},
        {"name": "create_issue",
         "description": "Создать иссью в XTracker. Используй когда пользователь просит \"заведи задачу\", \"создай баг\". Обязательны очередь, заголовок, тип и приоритет.",
         "inputSchema": {"type": "object", "additionalProperties": False,
                         "properties": {
                             "queue_key": {"type": "string", "description": "Очередь, напр. PROJ"},
                             "summary": {"type": "string", "minLength": 1, "maxLength": 500, "description": "Заголовок иссью"},
                             "type": {"type": "string", "enum": ["bug", "story", "task", "epic", "subtask"], "description": "Тип иссью"},
                             "priority": {"type": "string", "enum": ["critical", "high", "medium", "low", "trivial"], "description": "Приоритет"},
                             "description": {"type": "string", "description": "Описание (опц.)"},
                             "assignee_id": {"type": "string", "description": "UUID исполнителя (опц.)"},
                             "operation_id": {"type": "string", "description": "Идемпотентный ключ операции (опц.): повторный вызов с тем же значением пропускается"}},
                         "required": ["queue_key", "summary", "type", "priority"]}},
        {"name": "update_issue",
         "description": "Обновить поля существующей иссью XTracker (заголовок, описание, приоритет, тип, даты).",
         "inputSchema": {"type": "object", "additionalProperties": False,
                         "properties": {
                             "key": {"type": "string", "minLength": 1, "description": "Ключ иссью"},
                             "summary": s, "description": s, "priority": s, "type": s,
                             "due_date": {"type": "string", "description": "Срок (date-time)"},
                             "start_date": {"type": "string", "description": "Старт (date-time)"},
                             "operation_id": {"type": "string", "description": "Идемпотентный ключ (опц.)"}},
                         "required": ["key"]}},
        {"name": "comment_issue",
         "description": "Добавить комментарий к иссью XTracker.",
         "inputSchema": {"type": "object", "additionalProperties": False,
                         "properties": {
                             "issue_key": {"type": "string", "minLength": 1, "description": "Ключ иссью"},
                             "content": {"type": "string", "minLength": 1, "description": "Текст комментария"},
                             "operation_id": {"type": "string", "description": "Идемпотентный ключ (опц.)"}},
                         "required": ["issue_key", "content"]}},
        {"name": "transition_issue",
         "description": "Сменить статус иссью XTracker (выполнить переход workflow). Укажи ровно один из to_status_code / to_status_id.",
         "inputSchema": {"type": "object", "additionalProperties": False,
                         "properties": {
                             "key": {"type": "string", "minLength": 1, "description": "Ключ иссью"},
                             "to_status_code": {"type": "string", "description": "Символьный код целевого статуса (напр. in_progress)"},
                             "to_status_id": {"type": "string", "description": "UUID целевого статуса"},
                             "operation_id": {"type": "string", "description": "Идемпотентный ключ (опц.)"}},
                         "required": ["key"]}},
        {"name": "assign_issue",
         "description": "Назначить иссью XTracker исполнителю (assignee = user id) или снять назначение (unassign=true).",
         "inputSchema": {"type": "object", "additionalProperties": False,
                         "properties": {
                             "key": {"type": "string", "minLength": 1, "description": "Ключ иссью"},
                             "assignee": {"type": "string", "description": "User id исполнителя"},
                             "unassign": {"type": "boolean", "description": "true → снять исполнителя"},
                             "operation_id": {"type": "string", "description": "Идемпотентный ключ (опц.)"}},
                         "required": ["key"]}},
        {"name": "whoami",
         "description": "Показать текущего пользователя XTracker (под чьей identity работает инстанс плагина).",
         "inputSchema": {"type": "object", "additionalProperties": False, "properties": {}}},
        {"name": "config_test_connection",
         "description": "Проверить соединение и аутентификацию инстанса с XTracker (для кнопки Test в админке).",
         "inputSchema": {"type": "object", "additionalProperties": False, "properties": {}}},
    ]}


# ------------------------------------------------------------------------- loop

def _handle_tools_call(req_id, params):
    name = (params or {}).get("name")
    args = (params or {}).get("arguments")
    if not isinstance(args, dict):
        args = {}
    jarvis = args.pop("__jarvis", {})
    if not isinstance(jarvis, dict):
        jarvis = {}
    cfg = jarvis.get("config", {})
    if not isinstance(cfg, dict):
        cfg = {}
    handler = _TOOLS.get(name)
    if not handler:
        return _send({"jsonrpc": "2.0", "id": req_id, "error": {"message": "Unknown tool: %s" % name}})
    try:
        handler(req_id, args, cfg)
    except AuthError as exc:
        _error(req_id, str(exc), code="CONFIG")
    except RuntimeError as exc:
        _error(req_id, str(exc), code="UPSTREAM")
    except Exception as exc:  # P-5: процесс не падает ни при каких аргументах
        _error(req_id, "Внутренняя ошибка инструмента %s: %s" % (name, type(exc).__name__), code="INTERNAL")


def main():
    for line in sys.stdin:
        line = (line or "").strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except Exception:
            continue
        if not isinstance(msg, dict):
            continue
        mid = msg.get("id")
        method = msg.get("method")
        params = msg.get("params") if isinstance(msg.get("params"), dict) else {}
        if method == "initialize":
            _send({"jsonrpc": "2.0", "id": mid, "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SLUG, "version": "1.0.2"}}})
        elif method == "notifications/initialized" or method == "initialized":
            continue
        elif method == "tools/list":
            _send({"jsonrpc": "2.0", "id": mid, "result": _tools_list_result()})
        elif method == "tools/call":
            _handle_tools_call(mid, params)
        # прочие методы игнорируем (best-effort)


if __name__ == "__main__":
    main()
