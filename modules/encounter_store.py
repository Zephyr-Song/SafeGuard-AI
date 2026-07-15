"""SQLite persistence layer for SafeBARS v2 encounter sessions.

EncounterStore provides restart-safe storage for study sessions, the
append-only event log, and HMAC-verified researcher/expert access tokens. It
is intentionally isolated from the audit logic in ``encounter_engine``.
"""

from __future__ import annotations

from contextlib import closing
from typing import Any, Dict, List, Optional

import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import threading

from .scenarios import utc_now

class EncounterStore:
    """Small SQLite JSON store for restart-safe study sessions and event logs."""

    def __init__(self, path: str):
        self.path = path
        self._lock = threading.Lock()
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=20)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS encounter_sessions (
                        id TEXT PRIMARY KEY,
                        payload TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                    """
                )
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS encounter_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        payload TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                    """
                )
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS encounter_access (
                        session_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        token_hash TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        PRIMARY KEY (session_id, role)
                    )
                    """
                )

    def save(self, session: Dict[str, Any]) -> None:
        serialized = json.dumps(session, ensure_ascii=True)
        with self._lock, closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    INSERT INTO encounter_sessions (id, payload, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET payload=excluded.payload, updated_at=excluded.updated_at
                    """,
                    (session["id"], serialized, session["created_at"], session["updated_at"]),
                )

    def load(self, session_id: str) -> Optional[Dict[str, Any]]:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT payload FROM encounter_sessions WHERE id = ?", (session_id,)
            ).fetchone()
        return json.loads(row["payload"]) if row else None

    def log(self, session_id: str, event_type: str, payload: Dict[str, Any]) -> None:
        with self._lock, closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    INSERT INTO encounter_events (session_id, event_type, payload, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (session_id, event_type, json.dumps(payload, ensure_ascii=True), utc_now()),
                )

    def list_events(self, session_id: str) -> List[Dict[str, Any]]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                """
                SELECT id, event_type, payload, created_at
                FROM encounter_events
                WHERE session_id = ?
                ORDER BY id ASC
                """,
                (session_id,),
            ).fetchall()
        return [
            {
                "id": row["id"],
                "event_type": row["event_type"],
                "payload": json.loads(row["payload"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    @staticmethod
    def _token_hash(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def rotate_access(self, session_id: str, role: str) -> str:
        if role not in {"researcher", "expert"}:
            raise ValueError("Access role must be researcher or expert.")
        token = secrets.token_urlsafe(32)
        with self._lock, closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    INSERT INTO encounter_access (session_id, role, token_hash, created_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(session_id, role)
                    DO UPDATE SET token_hash=excluded.token_hash, created_at=excluded.created_at
                    """,
                    (session_id, role, self._token_hash(token), utc_now()),
                )
        return token

    def access_role(self, session_id: str, token: str) -> Optional[str]:
        if not token:
            return None
        candidate = self._token_hash(token)
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT role, token_hash FROM encounter_access WHERE session_id = ?",
                (session_id,),
            ).fetchall()
        for row in rows:
            if hmac.compare_digest(candidate, row["token_hash"]):
                return row["role"]
        return None


