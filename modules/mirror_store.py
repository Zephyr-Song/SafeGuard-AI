"""Isolated SQLite persistence for SafeBARS Ethical Mirror.

The store uses Mirror-specific table names.  It can therefore share a SQLite
database file with another SafeBARS component without reading, altering, or
dropping any legacy tables; the default is a dedicated database file.
"""

from __future__ import annotations

from contextlib import closing
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import json
import os
import sqlite3
import threading


def utc_now() -> str:
    """Return an ISO-8601 UTC timestamp."""

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class MirrorStore:
    """Restart-safe JSON session store with an append-only event log."""

    def __init__(self, path: str):
        if not path:
            raise ValueError("MirrorStore requires a SQLite path.")
        self.path = os.path.abspath(path)
        self._lock = threading.RLock()
        directory = os.path.dirname(self.path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=20)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 20000")
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS mirror_sessions (
                        id TEXT PRIMARY KEY,
                        payload TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                    """
                )
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS mirror_events (
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
                    CREATE INDEX IF NOT EXISTS idx_mirror_events_session
                    ON mirror_events(session_id, id)
                    """
                )

    def save(self, session: Dict[str, Any]) -> None:
        if not session.get("id"):
            raise ValueError("Mirror session id is required.")
        serialized = json.dumps(
            session, ensure_ascii=False, separators=(",", ":"), sort_keys=True
        )
        created_at = str(session.get("created_at") or utc_now())
        updated_at = str(session.get("updated_at") or created_at)
        with self._lock, closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    INSERT INTO mirror_sessions (id, payload, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        payload=excluded.payload,
                        updated_at=excluded.updated_at
                    """,
                    (session["id"], serialized, created_at, updated_at),
                )

    def load(self, session_id: str) -> Optional[Dict[str, Any]]:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT payload FROM mirror_sessions WHERE id = ?",
                (session_id,),
            ).fetchone()
        return json.loads(row["payload"]) if row else None

    def log(self, session_id: str, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        event = {
            "session_id": session_id,
            "event_type": event_type,
            "payload": payload,
            "created_at": utc_now(),
        }
        with self._lock, closing(self._connect()) as connection:
            with connection:
                cursor = connection.execute(
                    """
                    INSERT INTO mirror_events
                        (session_id, event_type, payload, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        session_id,
                        event_type,
                        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
                        event["created_at"],
                    ),
                )
                event["id"] = cursor.lastrowid
        return event

    def list_events(self, session_id: str) -> List[Dict[str, Any]]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                """
                SELECT id, event_type, payload, created_at
                FROM mirror_events
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
