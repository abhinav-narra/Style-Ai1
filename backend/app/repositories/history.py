from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import anyio


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class HistoryRow:
    user_id: str
    outfit_id: str
    created_at: datetime
    payload: dict[str, Any]


class HistoryRepository:
    def __init__(self, database_path: str):
        self._db_path = database_path

    async def init(self) -> None:
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)

        def _init() -> None:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS history (
                        user_id TEXT NOT NULL,
                        outfit_id TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        payload_json TEXT NOT NULL
                    )
                    """
                )
                conn.execute("CREATE INDEX IF NOT EXISTS idx_history_user ON history(user_id, created_at)")
                conn.commit()

        await anyio.to_thread.run_sync(_init)

    async def add_entry(self, user_id: str, outfit_id: str, payload: dict[str, Any]) -> None:
        created_at = _utc_now().isoformat()
        payload_json = json.dumps(payload, ensure_ascii=False)

        def _insert() -> None:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute(
                    "INSERT INTO history(user_id, outfit_id, created_at, payload_json) VALUES (?, ?, ?, ?)",
                    (user_id, outfit_id, created_at, payload_json),
                )
                conn.commit()

        await anyio.to_thread.run_sync(_insert)

    async def list_recent(self, user_id: str, limit: int = 50) -> list[HistoryRow]:
        limit = max(1, min(500, limit))

        def _select() -> list[HistoryRow]:
            with sqlite3.connect(self._db_path) as conn:
                cur = conn.execute(
                    "SELECT user_id, outfit_id, created_at, payload_json FROM history WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
                    (user_id, limit),
                )
                rows: list[HistoryRow] = []
                for u, oid, created_at, payload_json in cur.fetchall():
                    try:
                        payload = json.loads(payload_json)
                    except Exception:
                        payload = {}
                    try:
                        dt = datetime.fromisoformat(created_at)
                    except Exception:
                        dt = _utc_now()
                    rows.append(HistoryRow(user_id=u, outfit_id=oid, created_at=dt, payload=payload))
                return rows

        return await anyio.to_thread.run_sync(_select)

