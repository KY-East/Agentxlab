"""Structured logging for AXL backend.

Provides:
- `request_id_var` contextvars to carry request id across async calls
- `configure_logging()` to install root handler with JSON Lines format
- `RequestIdMiddleware` FastAPI middleware that assigns request_id per HTTP request
- `get_logger(name)` convenience wrapper

Design goals (per Ken 2026-04-16 after Lawrence's methodology tweet):
- Every log line carries request_id so a single user request is traceable across
  classifier / expert_builder / debate_engine / axl_client / ledger.
- JSON Lines output so cc / cursor / future AI can grep structured fields.
- Minimal invasion: existing `logger.info(...)` calls keep working, they just
  get request_id auto-attached via filter.
- No external dependency (Sentry / DataDog / OpenTelemetry not introduced).
"""
from __future__ import annotations

import contextvars
import datetime as _dt
import json
import logging
import sys
import time
import uuid
from typing import Any, Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


# ---------------------------------------------------------------------------
# Context variables (survive across async/await boundaries)
# ---------------------------------------------------------------------------

request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default="-"
)


def current_request_id() -> str:
    """Return current request_id or '-' if outside a request scope."""
    return request_id_var.get()


def set_request_id(rid: str) -> contextvars.Token:
    """Manually set request_id (e.g. for background tasks / experiment runners).
    Returns a token; pass it to `request_id_var.reset(token)` when done."""
    return request_id_var.set(rid)


# ---------------------------------------------------------------------------
# JSON Lines formatter
# ---------------------------------------------------------------------------

_RESERVED_LOGRECORD_ATTRS = {
    "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
    "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
    "created", "msecs", "relativeCreated", "thread", "threadName",
    "processName", "process", "message", "asctime",
}


class JsonLineFormatter(logging.Formatter):
    """Emit one JSON object per log line.

    Fields: ts / level / logger / msg / req_id + any extra kwargs passed via
    `logger.info("msg", extra={"step": "round_1", "agent_id": 42})`.
    Exceptions are captured in `exc` field as string.
    """

    def format(self, record: logging.LogRecord) -> str:
        # ISO 8601 with millisecond precision. Build manually because Windows
        # strftime does not support %f.
        ts = _dt.datetime.fromtimestamp(record.created, tz=_dt.timezone.utc)
        payload: dict[str, Any] = {
            "ts": ts.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "req_id": getattr(record, "req_id", current_request_id()),
            "msg": record.getMessage(),
        }
        # Surface any extra=... fields the caller attached.
        for key, val in record.__dict__.items():
            if key in _RESERVED_LOGRECORD_ATTRS or key == "req_id":
                continue
            try:
                json.dumps(val)  # cheap serializability check
            except (TypeError, ValueError):
                val = repr(val)
            payload[key] = val
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


class RequestIdFilter(logging.Filter):
    """Attach current request_id to every log record emitted within a request."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "req_id"):
            record.req_id = current_request_id()
        return True


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_CONFIGURED = False


def configure_logging(level: str = "INFO") -> None:
    """Install a single stderr handler with JSON Lines format.

    Idempotent — safe to call multiple times (second call is no-op).
    Existing handlers are left alone the first time, then replaced on
    the first call to avoid double-emission.
    """
    global _CONFIGURED
    if _CONFIGURED:
        return
    root = logging.getLogger()
    # Clear anything that might have been auto-attached (uvicorn default).
    for h in list(root.handlers):
        root.removeHandler(h)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonLineFormatter())
    handler.addFilter(RequestIdFilter())
    root.addHandler(handler)
    root.setLevel(level.upper())
    # Uvicorn / sqlalchemy are chatty; keep them at WARNING by default.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    _CONFIGURED = True


# ---------------------------------------------------------------------------
# FastAPI middleware
# ---------------------------------------------------------------------------

class RequestIdMiddleware(BaseHTTPMiddleware):
    """Assign a request_id to every HTTP request.

    Honors incoming `X-Request-Id` header if present (for downstream correlation),
    otherwise generates a short uuid4 hex.

    Also emits a single access log line at request completion with latency and
    status code.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        incoming = request.headers.get("X-Request-Id")
        rid = incoming or uuid.uuid4().hex[:12]
        token = request_id_var.set(rid)
        access_logger = logging.getLogger("axl.access")
        start = time.perf_counter()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            response.headers["X-Request-Id"] = rid
            return response
        finally:
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
            access_logger.info(
                "request",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status": status,
                    "latency_ms": elapsed_ms,
                },
            )
            request_id_var.reset(token)
