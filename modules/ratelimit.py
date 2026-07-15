"""Minimal in-memory rate limiting for SafeBARS API endpoints.

This avoids an extra dependency while protecting LLM-backed endpoints from
abuse (each call can cost money and latency). It is intentionally simple:
a fixed-window counter keyed by (scope, client IP). For the single-worker
Render free tier this is sufficient; if the app is ever scaled to multiple
workers, swap this for a shared store (Redis) or flask-limiter.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from functools import wraps

from flask import jsonify, request


class _WindowCounter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.hits: deque[float] = deque()

    def allow(self) -> bool:
        now = time.time()
        while self.hits and self.hits[0] <= now - self.window_seconds:
            self.hits.popleft()
        if len(self.hits) >= self.max_requests:
            return False
        self.hits.append(now)
        return True


_LIMITERS: dict[tuple[str, int, int], _WindowCounter] = {}


def _get_counter(scope: str, max_requests: int, window_seconds: int) -> _WindowCounter:
    key = (scope, max_requests, window_seconds)
    counter = _LIMITERS.get(key)
    if counter is None:
        counter = _WindowCounter(max_requests, window_seconds)
        _LIMITERS[key] = counter
    return counter


def rate_limit(max_requests: int = 20, window_seconds: int = 60, scope: str = "global"):
    """Decorator that rejects requests beyond ``max_requests`` per window.

    Example::

        @encounter_api.post("/sessions/<session_id>/audit")
        @rate_limit(max_requests=10, window_seconds=60, scope="audit")
        def run_audit(session_id): ...
    """

    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            counter = _get_counter(scope, max_requests, window_seconds)
            client = request.remote_addr or request.headers.get("X-Forwarded-For", "unknown")
            if not counter.allow():
                return jsonify({
                    "success": False,
                    "error": "Rate limit exceeded. Please wait a moment before retrying.",
                }), 429
            return view(*args, **kwargs)

        return wrapped

    return decorator
