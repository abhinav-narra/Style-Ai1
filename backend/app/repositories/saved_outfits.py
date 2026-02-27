from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List

import anyio


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class SavedOutfitRow:
    id: int
    user_id: str
    outfit_id: str
    created_at: datetime
    payload: dict[str, Any]


class SavedOutfitRepository:
    def __init__(self, database_path: str):
        self._db_path = database_path

    async def init(self) -> None:
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)

        def _init() -> None:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS saved_outfits (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        outfit_id TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        payload_json TEXT NOT NULL
                    )
                    """
                )
                conn.execute("CREATE INDEX IF NOT EXISTS idx_saved_outfits_user ON saved_outfits(user_id, created_at)")
                conn.commit()

        await anyio.to_thread.run_sync(_init)

    async def add_saved_outfit(self, user_id: str, outfit_id: str, payload: dict[str, Any]) -> None:
        created_at = _utc_now().isoformat()
        payload_json = json.dumps(payload, ensure_ascii=False)

        def _insert() -> None:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute(
                    "INSERT INTO saved_outfits(user_id, outfit_id, created_at, payload_json) VALUES (?, ?, ?, ?)",
                    (user_id, outfit_id, created_at, payload_json),
                )
                conn.commit()

        await anyio.to_thread.run_sync(_insert)

    async def list_for_user(self, user_id: str, limit: int = 50) -> List[SavedOutfitRow]:
        limit = max(1, min(200, limit))

        def _select() -> List[SavedOutfitRow]:
            with sqlite3.connect(self._db_path) as conn:
                cur = conn.execute(
                    "SELECT id, user_id, outfit_id, created_at, payload_json FROM saved_outfits WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
                    (user_id, limit),
                )
                rows: List[SavedOutfitRow] = []
                for sid, uid, oid, created_at, payload_json in cur.fetchall():
                    try:
                        payload = json.loads(payload_json)
                    except Exception:
                        payload = {}
                    try:
                        created_dt = datetime.fromisoformat(created_at)
                    except Exception:
                        created_dt = _utc_now()
                    rows.append(
                        SavedOutfitRow(
                            id=int(sid),
                            user_id=str(uid),
                            outfit_id=str(oid),
                            created_at=created_dt,
                            payload=payload,
                        )
                    )
                return rows

        return await anyio.to_thread.run_sync(_select)

    async def delete_for_user(self, user_id: str, outfit_id: str) -> None:
        def _delete() -> None:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute(
                    "DELETE FROM saved_outfits WHERE user_id=? AND outfit_id=?",
                    (user_id, outfit_id),
                )
                conn.commit()

        await anyio.to_thread.run_sync(_delete)
