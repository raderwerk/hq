#!/usr/bin/env python3
"""Minimal Linear GraphQL client (stdlib only).

Auth: personal API key read from ~/.config/linear/api_key.
Header is `Authorization: <key>` -- no `Bearer` prefix (personal keys only).

Usage as a library:

    from linear_api import gql, paginate, LinearError
    data = gql("query { viewer { id name } }")
    teams = paginate("query($first:Int!,$after:String){ teams(first:$first, after:$after)"
                     "{ nodes { id key } pageInfo { hasNextPage endCursor } } }", "teams")

Usage as a CLI:

    python3 linear_api.py query '<graphql>' ['<json vars>']
    python3 linear_api.py paginate '<graphql with $first/$after>' <path> ['<json vars>']
    python3 linear_api.py whoami
"""

import argparse
import json
import os
import random
import sys
import time
import urllib.error
import urllib.request

ENDPOINT = "https://api.linear.app/graphql"
API_KEY_PATH = os.path.expanduser("~/.config/linear/api_key")
USER_AGENT = "raderwerk-linear-tools/1.0"

# Retry policy for transport-level failures (429 / 5xx / socket errors).
MAX_ATTEMPTS = 6
BASE_BACKOFF = 2.0
MAX_BACKOFF = 60.0

# Stop and wait when the hourly request budget gets thin. A rate-limit window is
# hourly, so a wait driven by a `*-Reset` header may legitimately be ~60 minutes.
REQUEST_FLOOR = 40
COMPLEXITY_FLOOR = 20000
RESET_WAIT_CAP = 3900.0

_KEY_CACHE = None
_KEY_SOURCE = None
_LAST_HEADERS = {}
_STATS = {"requests": 0, "retries": 0, "complexity": 0.0}


class LinearError(RuntimeError):
    """A GraphQL-level error returned by the Linear API."""

    def __init__(self, message, errors=None, query=None, variables=None):
        super().__init__(message)
        self.errors = errors or []
        self.query = query
        self.variables = variables

    @property
    def codes(self):
        out = []
        for err in self.errors:
            ext = err.get("extensions") or {}
            for key in ("code", "type", "userPresentableMessage"):
                if ext.get(key):
                    out.append(str(ext[key]))
        return out

    def matches(self, *needles):
        """True when any needle appears in the message or in an error code."""
        hay = (str(self) + " " + " ".join(self.codes)).lower()
        return any(n.lower() in hay for n in needles)


def api_key():
    global _KEY_CACHE, _KEY_SOURCE
    if _KEY_CACHE is None:
        env = os.environ.get("LINEAR_API_KEY")
        if env:
            _KEY_CACHE = env.strip()
            _KEY_SOURCE = "env:LINEAR_API_KEY"
        else:
            if not os.path.exists(API_KEY_PATH):
                raise LinearError("No API key: set LINEAR_API_KEY or create %s" % API_KEY_PATH)
            with open(API_KEY_PATH, "r", encoding="utf-8") as fh:
                _KEY_CACHE = fh.read().strip()
            _KEY_SOURCE = "file:%s" % API_KEY_PATH
        if not _KEY_CACHE:
            raise LinearError("API key from %s is empty" % _KEY_SOURCE)
    return _KEY_CACHE


def key_source():
    """Where the key came from -- never the key itself.

    An exported LINEAR_API_KEY silently wins over the key file, which is exactly
    how a destructive run ends up pointed at somebody else's workspace, so the
    caller prints this next to the workspace-identity check.
    """
    api_key()
    return _KEY_SOURCE


def last_headers():
    return dict(_LAST_HEADERS)


def stats():
    return dict(_STATS)


def _sleep(seconds, reason="", cap=300.0):
    seconds = max(0.0, min(seconds, cap))
    if seconds <= 0:
        return
    if reason:
        sys.stderr.write("  ... waiting %.1fs (%s)\n" % (seconds, reason))
        sys.stderr.flush()
    time.sleep(seconds)


def _reset_wait(header_value):
    """`*-Reset` headers are UTC epoch milliseconds."""
    try:
        reset_ms = float(header_value)
    except (TypeError, ValueError):
        return None
    return max(0.0, reset_ms / 1000.0 - time.time()) + 1.0


def _respect_budget():
    """Pause when the rate-limit headers say we are nearly out of budget."""
    if not _LAST_HEADERS:
        return
    remaining = _LAST_HEADERS.get("x-ratelimit-requests-remaining")
    if remaining is not None:
        try:
            if int(float(remaining)) < REQUEST_FLOOR:
                wait = _reset_wait(_LAST_HEADERS.get("x-ratelimit-requests-reset"))
                if wait:
                    _sleep(wait, "request budget nearly exhausted", cap=RESET_WAIT_CAP)
                    return
        except ValueError:
            pass
    remaining = _LAST_HEADERS.get("x-ratelimit-complexity-remaining")
    if remaining is not None:
        try:
            if float(remaining) < COMPLEXITY_FLOOR:
                wait = _reset_wait(_LAST_HEADERS.get("x-ratelimit-complexity-reset"))
                if wait:
                    _sleep(wait, "complexity budget nearly exhausted", cap=RESET_WAIT_CAP)
        except ValueError:
            pass


def gql(query, variables=None, timeout=90, retry_transport=True):
    """Run one GraphQL operation. Returns the `data` object, raises LinearError.

    `retry_transport=False` keeps the 429 retry (the request provably did not run)
    but never re-POSTs after a 5xx, a timeout or a socket error. Mutations pass it:
    a lost response to an `issueCreate` that Linear did commit would otherwise be
    retried into a duplicate record.
    """
    global _LAST_HEADERS
    payload = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": api_key(),
        "User-Agent": USER_AGENT,
    }

    _respect_budget()
    last_exc = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        req = urllib.request.Request(ENDPOINT, data=payload, headers=headers, method="POST")
        status = None
        body = None
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status = resp.status
                _LAST_HEADERS = {k.lower(): v for k, v in resp.headers.items()}
                body = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            status = exc.code
            _LAST_HEADERS = {k.lower(): v for k, v in (exc.headers or {}).items()}
            try:
                body = exc.read().decode("utf-8")
            except Exception:
                body = ""
            last_exc = exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_exc = exc
            status = None
            body = None

        _STATS["requests"] += 1
        try:
            _STATS["complexity"] += float(_LAST_HEADERS.get("x-complexity") or 0)
        except ValueError:
            pass

        transport_failure = status is None or (status is not None and status >= 500)
        retryable = status == 429 or (transport_failure and retry_transport)
        if not retryable and transport_failure and body is None:
            raise LinearError("Network failure (no retry, mutation may or may not have "
                              "landed -- re-run and let name matching reconcile): %s" % last_exc)
        if retryable and attempt < MAX_ATTEMPTS:
            _STATS["retries"] += 1
            wait, cap = None, 300.0
            if status == 429:
                wait = _reset_wait(_LAST_HEADERS.get("x-ratelimit-requests-reset"))
                if wait is None:
                    try:
                        wait = float(_LAST_HEADERS.get("retry-after", ""))
                    except ValueError:
                        wait = None
                cap = RESET_WAIT_CAP
            if wait is None:
                wait = min(MAX_BACKOFF, BASE_BACKOFF * (2 ** (attempt - 1)))
                wait += random.uniform(0, 0.5 * wait)
            _sleep(wait, "HTTP %s, attempt %d/%d" % (status, attempt, MAX_ATTEMPTS), cap=cap)
            continue

        if body is None:
            raise LinearError("Network failure after %d attempts: %s" % (attempt, last_exc))

        try:
            parsed = json.loads(body)
        except ValueError:
            raise LinearError("HTTP %s: non-JSON response: %s" % (status, body[:400]))

        if parsed.get("errors"):
            errs = parsed["errors"]
            msg = "; ".join(str(e.get("message", e)) for e in errs)
            raise LinearError(msg, errors=errs, query=query, variables=variables)
        if status is not None and status >= 400:
            raise LinearError("HTTP %s: %s" % (status, body[:400]))
        if "data" not in parsed:
            raise LinearError("HTTP %s: response has no data: %s" % (status, body[:400]))
        return parsed["data"]

    raise LinearError("Exhausted %d attempts: %s" % (MAX_ATTEMPTS, last_exc))


def dig(obj, path):
    """Walk a dot-path ('team.issues') through nested dicts; None if absent."""
    cur = obj
    for part in path.split("."):
        if cur is None:
            return None
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def paginate(query, path, variables=None, page_size=50, min_page_size=5):
    """Page a Relay connection, shrinking `first` when the query is too complex.

    `query` must declare `$first: Int!` and `$after: String` and select
    `nodes { ... }` plus `pageInfo { hasNextPage endCursor }` at `path`.
    """
    variables = dict(variables or {})
    nodes = []
    after = None
    size = page_size
    guard = 0
    rate_limit_waits = 0
    while True:
        guard += 1
        if guard > 2000:
            raise LinearError("paginate(%s) exceeded 2000 pages -- likely a cursor loop" % path)
        vars_now = dict(variables)
        vars_now["first"] = size
        vars_now["after"] = after
        try:
            data = gql(query, vars_now)
        except LinearError as exc:
            # Two different failures that must not share one remedy: a complexity
            # rejection wants a smaller page, a rate limit wants the reset window.
            if exc.matches("RATELIMITED", "rate limit") and rate_limit_waits < 3:
                rate_limit_waits += 1
                wait = _reset_wait(last_headers().get("x-ratelimit-requests-reset")) or 60.0
                _sleep(wait, "rate limited while paging %s" % path, cap=RESET_WAIT_CAP)
                continue
            too_big = exc.matches("complexity", "too complex", "query is too large")
            if too_big and size > min_page_size:
                size = max(min_page_size, size // 2)
                sys.stderr.write("  ... complexity hit, retrying %s with first=%d\n" % (path, size))
                _sleep(2.0)
                continue
            raise
        conn = dig(data, path)
        if conn is None:
            raise LinearError("paginate: path %r not found in response" % path)
        nodes.extend(conn.get("nodes") or [])
        info = conn.get("pageInfo") or {}
        if not info.get("hasNextPage"):
            return nodes
        after = info.get("endCursor")
        if not after:
            return nodes


def page(root, fields, include_archived=False, page_size=50, extra="", variables=None,
         on_problem=None):
    """Page a root connection by name, retrying without includeArchived if rejected.

    A silent fallback to a non-archived listing would hide archived records from
    the caller (an archived team that still eats a plan slot, say), so the caller
    can pass `on_problem` to have that recorded rather than printed and forgotten.
    """
    for use_archived in ([True, False] if include_archived else [False]):
        args = ["first: $first", "after: $after"]
        if use_archived:
            args.append("includeArchived: true")
        if extra:
            args.append(extra)
        query = (
            "query($first: Int!, $after: String) { %s(%s) { nodes { %s } "
            "pageInfo { hasNextPage endCursor } } }" % (root, ", ".join(args), fields)
        )
        try:
            return paginate(query, root, variables=variables, page_size=page_size)
        except LinearError as exc:
            if use_archived and exc.matches("includeArchived", "Unknown argument"):
                message = ("%s does not accept includeArchived; archived records are NOT in "
                           "this listing (%s)" % (root, exc))
                sys.stderr.write("  (%s)\n" % message)
                if on_problem:
                    on_problem(message)
                continue
            raise
    return []


def _cli():
    parser = argparse.ArgumentParser(description="Linear GraphQL client")
    sub = parser.add_subparsers(dest="cmd")

    q = sub.add_parser("query", help="run one GraphQL operation")
    q.add_argument("graphql")
    q.add_argument("variables", nargs="?", default=None, help="JSON object")
    q.add_argument("--compact", action="store_true")

    p = sub.add_parser("paginate", help="page a connection and print all nodes")
    p.add_argument("graphql")
    p.add_argument("path", help="dot-path to the connection, e.g. 'teams'")
    p.add_argument("variables", nargs="?", default=None)
    p.add_argument("--page-size", type=int, default=50)

    sub.add_parser("whoami", help="print viewer + organization + teams")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return 2

    try:
        if args.cmd == "query":
            variables = json.loads(args.variables) if args.variables else {}
            out = gql(args.graphql, variables)
        elif args.cmd == "paginate":
            variables = json.loads(args.variables) if args.variables else {}
            out = paginate(args.graphql, args.path, variables, page_size=args.page_size)
        else:
            out = gql(
                "query { viewer { id name email admin } "
                "organization { id name urlKey createdIssueCount userCount } "
                "teams(first: 50) { nodes { id key name } } }"
            )
    except LinearError as exc:
        sys.stderr.write("LinearError: %s\n" % exc)
        if exc.errors:
            sys.stderr.write(json.dumps(exc.errors, indent=2)[:4000] + "\n")
        return 1

    indent = None if getattr(args, "compact", False) else 2
    print(json.dumps(out, indent=indent, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
