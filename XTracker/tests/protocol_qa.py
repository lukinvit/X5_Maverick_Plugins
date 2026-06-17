#!/usr/bin/env python3
"""Protocol-QA harness для плагина XTracker (verify-gate, P-15).

Гоняет РЕАЛЬНЫЙ stdio JSON-RPC к процессу server.py с МОК-API XTracker
(живой pulsar.x5.ru отсюда недоступен — финальный Test делает оператор).
Проверяет: tools/list-схемы (P-7), happy + adversarial tools/call,
idempotent-skip (P-3), отсутствие утечки секретов (P-1), structured_content
+ text-fallback (P-11), устойчивость процесса (P-5).

Запуск:  python3 XTracker/tests/protocol_qa.py
Код выхода: 0 = PASS, 1 = FAIL.
"""
import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN_DIR = os.path.join(os.path.dirname(HERE), "plugin")
SERVER = os.path.join(PLUGIN_DIR, "server.py")

API_KEY_SECRET = "SUPERSECRET_TOKEN_123"
PASSWORD_SECRET = "PWSECRET_456"
ACCESS_TOKEN = "JWT_FAKE_ACCESS"

ISSUE = {"key": "PROJ-1", "title": "Тестовый баг", "queue_key": "PROJ",
         "status": "open", "assignee": "u1", "reporter": "u2",
         "type": "bug", "priority": "high", "description": "repro steps"}


class MockHandler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            return {}

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/v1/users/me":
            return self._send(200, {"id": "u0", "email": "svc@x5.ru", "display_name": "Service Account"})
        if path == "/api/v1/issues/FORBIDDEN-1":
            return self._send(403, {"message": "forbidden"})
        if path.startswith("/api/v1/issues/"):
            return self._send(200, dict(ISSUE, key=path.rsplit("/", 1)[-1]))
        return self._send(404, {"message": "not found"})

    def do_PATCH(self):
        self._read_json()
        if self.path.startswith("/api/v1/issues/"):
            return self._send(200, {"key": self.path.rsplit("/", 1)[-1]})
        return self._send(404, {"message": "not found"})

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        self._read_json()
        if path == "/api/v1/auth/login":
            return self._send(200, {"access_token": ACCESS_TOKEN, "refresh_token": "R_FAKE",
                                    "expires_in": 3600, "account": {"id": "u0", "email": "svc@x5.ru",
                                    "display_name": "Service Account"}, "require_org_selection": False})
        if path == "/api/v1/auth/refresh":
            return self._send(200, {"access_token": ACCESS_TOKEN, "refresh_token": "R_FAKE", "expires_in": 3600})
        if path == "/api/v1/issues/_search":
            return self._send(200, {"issues": [dict(ISSUE), dict(ISSUE, key="PROJ-2", title="Вторая")], "total": 2})
        if path == "/api/v1/issues":
            return self._send(201, {"key": "PROJ-99", "title": "new", "queue_key": "PROJ"})
        if path.endswith("/comments"):
            return self._send(201, {"id": "c1"})
        if path.endswith("/transitions"):
            return self._send(200, {})
        if path.endswith("/assign") or path.endswith("/unassign"):
            return self._send(200, {})
        return self._send(404, {"message": "not found"})


class Plugin:
    def __init__(self, config):
        self.config = config
        self.proc = subprocess.Popen(
            [sys.executable, "server.py"], cwd=PLUGIN_DIR,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, bufsize=1)
        self._rpc({"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {}})

    def _rpc(self, msg):
        self.proc.stdin.write(json.dumps(msg, ensure_ascii=False) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        return json.loads(line) if line.strip() else None

    def list_tools(self):
        return self._rpc({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})

    def call(self, name, args, rid=2):
        a = dict(args)
        a["__jarvis"] = {"config": self.config, "user_id": "uX", "session_id": "sX"}
        return self._rpc({"jsonrpc": "2.0", "id": rid, "method": "tools/call",
                          "params": {"name": name, "arguments": a}})

    def close(self):
        try:
            self.proc.stdin.close()
            self.proc.terminate()
            self.proc.wait(timeout=5)
        except Exception:
            self.proc.kill()
        return self.proc.stderr.read()


RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((bool(cond), name, detail))
    print(("  PASS " if cond else "  FAIL ") + name + ((" — " + detail) if detail and not cond else ""))


def result_text(resp):
    if not resp or "result" not in resp:
        return ""
    parts = []
    for c in resp["result"].get("content", []):
        if c.get("type") == "text":
            parts.append(c.get("text", ""))
    return "\n".join(parts)


def is_error(resp):
    return bool(resp and resp.get("result", {}).get("isError"))


def full_blob(resp):
    return json.dumps(resp, ensure_ascii=False)


def run_suite(label, config, port):
    print("\n=== Suite: %s ===" % label)
    pg = Plugin(config)
    try:
        # tools/list schema validation (P-7)
        lst = pg.list_tools()
        tools = (lst or {}).get("result", {}).get("tools", [])
        check("tools/list returns 9 tools", len(tools) == 9, "got %d" % len(tools))
        for t in tools:
            sch = t.get("inputSchema", {})
            ok = sch.get("type") == "object"
            if t["name"] != "config_test_connection":
                ok = ok and sch.get("additionalProperties") is False
                for pn, pv in sch.get("properties", {}).items():
                    ok = ok and bool(pv.get("description") or pv.get("enum") or pv.get("type"))
            check("schema ok: %s" % t["name"], ok)

        # happy paths
        r = pg.call("whoami", {})
        check("whoami ok", not is_error(r) and "Service Account" in result_text(r))

        r = pg.call("config_test_connection", {})
        check("config_test_connection OK", not is_error(r) and "OK" in result_text(r))

        r = pg.call("search_issues", {"query": "status = open", "limit": 5})
        sc = r["result"]["content"]
        has_text = any(c.get("type") == "text" for c in sc)
        has_sc = any(c.get("type") == "structured_content" for c in sc)
        check("search: text-fallback present (P-11)", has_text)
        check("search: structured_content card_list", has_sc and
              sc[-1]["json"]["template_id"] == "preset:card_list")

        r = pg.call("get_issue", {"key": "PROJ-1"})
        check("get_issue card + text", not is_error(r) and "PROJ-1" in result_text(r))

        r = pg.call("create_issue", {"queue_key": "PROJ", "summary": "x", "type": "bug",
                                     "priority": "high", "operation_id": "op-1"})
        check("create_issue ok + compact (N)", not is_error(r) and "(1)" in result_text(r) and "PROJ-99" in result_text(r))

        # idempotent-skip (P-3): repeat same operation_id
        r2 = pg.call("create_issue", {"queue_key": "PROJ", "summary": "x", "type": "bug",
                                      "priority": "high", "operation_id": "op-1"})
        check("create_issue idempotent-skip", not is_error(r2) and "ПРОПУСК" in result_text(r2))

        r = pg.call("update_issue", {"key": "PROJ-1", "summary": "new title"})
        check("update_issue ok", not is_error(r) and "(1)" in result_text(r))

        r = pg.call("comment_issue", {"issue_key": "PROJ-1", "content": "hi"})
        check("comment_issue ok", not is_error(r))

        r = pg.call("transition_issue", {"key": "PROJ-1", "to_status_code": "in_progress"})
        check("transition_issue ok", not is_error(r))

        r = pg.call("assign_issue", {"key": "PROJ-1", "assignee": "u9"})
        check("assign_issue ok", not is_error(r))
        r = pg.call("assign_issue", {"key": "PROJ-1", "unassign": True})
        check("unassign ok", not is_error(r))

        # adversarial — process must NOT crash, must return ERROR
        adv = [
            ("get_issue", {}),                                   # missing required
            ("create_issue", {"queue_key": "PROJ"}),             # missing fields
            ("search_issues", {"query": ""}),                    # empty query
            ("transition_issue", {"key": "PROJ-1"}),             # no target status
            ("get_issue", {"key": "PROJ-1", "bogus": 123}),      # unknown field (ignored, still ok)
            ("get_issue", {"key": "FORBIDDEN-1"}),               # 403 from upstream
        ]
        for i, (nm, a) in enumerate(adv):
            r = pg.call(nm, a, rid=100 + i)
            crashed = r is None
            check("adversarial survives: %s %s" % (nm, list(a.keys())), not crashed,
                  "process died / no response")
        # the unknown-field one should actually succeed (ignored)
        r = pg.call("get_issue", {"key": "PROJ-1", "bogus": 1}, rid=200)
        check("unknown field ignored, still works", not is_error(r))

        # secret-leak scan (P-1): configured secrets must NOT appear in any response
        all_blob = []
        for nm, a in [("whoami", {}), ("config_test_connection", {}),
                      ("search_issues", {"query": "x"}), ("get_issue", {"key": "PROJ-1"})]:
            all_blob.append(full_blob(pg.call(nm, a, rid=300)))
        blob = "\n".join(all_blob)
        check("no api_key secret leak (P-1)", API_KEY_SECRET not in blob)
        check("no password secret leak (P-1)", PASSWORD_SECRET not in blob)
        check("no access token leak (P-1)", ACCESS_TOKEN not in blob)
    finally:
        stderr = pg.close()
    return stderr


def main():
    httpd = HTTPServer(("127.0.0.1", 0), MockHandler)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d" % port

    run_suite("api_key auth", {"base_url": base, "auth_mode": "api_key",
                               "api_key": API_KEY_SECRET, "verify_ssl": False}, port)
    run_suite("password auth", {"base_url": base, "auth_mode": "password",
                                "email": "svc@x5.ru", "password": PASSWORD_SECRET,
                                "verify_ssl": False}, port)

    httpd.shutdown()
    passed = sum(1 for ok, _, _ in RESULTS if ok)
    failed = [r for r in RESULTS if not r[0]]
    print("\n==================== SUMMARY ====================")
    print("PASS: %d / %d" % (passed, len(RESULTS)))
    if failed:
        print("FAILED:")
        for _, n, d in failed:
            print("  - %s %s" % (n, ("(" + d + ")") if d else ""))
        sys.exit(1)
    print("ALL GREEN")
    sys.exit(0)


if __name__ == "__main__":
    main()
