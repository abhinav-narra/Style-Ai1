from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import anyio


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class UserRow:
    id: str
    email: str
    password_hash: str
    created_at: datetime
    display_name: str | None
    gender: str | None


class UserRepository:
    def __init__(self, database_path: str):
        self._db_path = database_path

    async def init(self) -> None:
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)

        def _init() -> None:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id TEXT PRIMARY KEY,
                        email TEXT NOT NULL UNIQUE,
                        password_hash TEXT NOT NULL,
                        display_name TEXT,
                        gender TEXT,
                        created_at TEXT NOT NULL
                    )
                    """
                )
                conn.commit()

        await anyio.to_thread.run_sync(_init)

    async def create_user(self, *, user_id: str, email: str, password_hash: str, display_name: str | None = None, gender: str | None = None) -> UserRow:

        created_at = _utc_now().isoformat()

        def _insert() -> None:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute(
                    "INSERT INTO users(id, email, password_hash, display_name, gender, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (user_id, email, password_hash, display_name, gender, created_at),
                )
                conn.commit()

        await anyio.to_thread.run_sync(_insert)
        return UserRow(
            id=user_id,
            email=email,
            password_hash=password_hash,
            display_name=display_name,
            gender=gender,
            created_at=_utc_now(),
        )

    async def get_by_email(self, email: str) -> Optional[UserRow]:
        def _select() -> Optional[UserRow]:
            with sqlite3.connect(self._db_path) as conn:
                cur = conn.execute(
                    "SELECT id, email, password_hash, display_name, gender, created_at FROM users WHERE email=?",
                    (email,),
                )
                row = cur.fetchone()
                if not row:
                    return None
                uid, em, ph, dn, gd, created_at = row
                try:
                    created_dt = datetime.fromisoformat(created_at)
                except Exception:
                    created_dt = _utc_now()
                return UserRow(
                    id=str(uid),
                    email=str(em),
                    password_hash=str(ph),
                    display_name=str(dn) if dn is not None else None,
                    gender=str(gd) if gd is not None else None,
                    created_at=created_dt,
                )

        return await anyio.to_thread.run_sync(_select)

    async def get_by_id(self, user_id: str) -> Optional[UserRow]:
        def _select() -> Optional[UserRow]:
            with sqlite3.connect(self._db_path) as conn:
                cur = conn.execute(
                    "SELECT id, email, password_hash, display_name, gender, created_at FROM users WHERE id=?",
                    (user_id,),
                )
                row = cur.fetchone()
                if not row:
                    return None
                uid, em, ph, dn, gd, created_at = row
                try:
                    created_dt = datetime.fromisoformat(created_at)
                except Exception:
                    created_dt = _utc_now()
                return UserRow(
                    id=str(uid),
                    email=str(em),
                    password_hash=str(ph),
                    display_name=str(dn) if dn is not None else None,
                    gender=str(gd) if gd is not None else None,
                    created_at=created_dt,
                )

        return await anyio.to_thread.run_sync(_select)

