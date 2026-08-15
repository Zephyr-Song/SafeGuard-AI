"""Lightweight session store for the StressLens study.

Sessions are simple JSON blobs keyed by a public token.  We keep the schema
minimal so it is easy to export for analysis.
"""

from __future__ import annotations

import json
import os
import secrets
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class MirrorStudyStore:
    """SQLite-backed store for mirror-study sessions."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.getenv(
                "SAFEBARS_MIRROR_STUDY_DB",
                str(Path(__file__).parent.parent / "data" / "mirror_study.db"),
            )
        self.db_path = db_path
        self._local = threading.local()
        if db_path and db_path != ":memory:":
            db_dir = os.path.dirname(db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS mirror_study_sessions (
                    id TEXT PRIMARY KEY,
                    condition_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    payload TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_mirror_study_created
                ON mirror_study_sessions(created_at)
                """
            )

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def create(self, condition_id: str, payload: Dict[str, Any]) -> str:
        session_id = "ms_" + secrets.token_hex(16)
        now = self._now()
        record = {
            "id": session_id,
            "condition_id": condition_id,
            "created_at": now,
            "updated_at": now,
            "status": "active",
            "payload": payload,
        }
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO mirror_study_sessions VALUES (?,?,?,?,?,?)",
                (
                    record["id"],
                    record["condition_id"],
                    record["created_at"],
                    record["updated_at"],
                    record["status"],
                    json.dumps(payload, ensure_ascii=False),
                ),
            )
            conn.commit()
        return session_id

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM mirror_study_sessions WHERE id = ?",
                (session_id,),
            ).fetchone()
        if row is None:
            return None
        record = dict(row)
        record["payload"] = json.loads(record["payload"])
        return record

    def update_payload(self, session_id: str, payload: Dict[str, Any]) -> bool:
        with self._conn() as conn:
            cur = conn.execute(
                "UPDATE mirror_study_sessions SET payload = ?, updated_at = ? WHERE id = ?",
                (json.dumps(payload, ensure_ascii=False), self._now(), session_id),
            )
            conn.commit()
        return cur.rowcount > 0

    def set_status(self, session_id: str, status: str) -> bool:
        with self._conn() as conn:
            cur = conn.execute(
                "UPDATE mirror_study_sessions SET status = ?, updated_at = ? WHERE id = ?",
                (status, self._now(), session_id),
            )
            conn.commit()
        return cur.rowcount > 0

    def list_recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM mirror_study_sessions ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        out = []
        for row in rows:
            record = dict(row)
            record["payload"] = json.loads(record["payload"])
            out.append(record)
        return out
