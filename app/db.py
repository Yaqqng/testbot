from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class User:
    user_id: int
    username: str | None
    balance: int


class Database:
    def __init__(self, path: str) -> None:
        self.path = path
        self._init_db()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    balance INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    plan_days INTEGER NOT NULL,
                    remnawave_id TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                );
                """
            )

    def get_or_create_user(self, user_id: int, username: str | None) -> User:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT user_id, username, balance FROM users WHERE user_id = ?",
                (user_id,),
            ).fetchone()
            if row:
                if username != row["username"]:
                    conn.execute(
                        "UPDATE users SET username = ? WHERE user_id = ?",
                        (username, user_id),
                    )
                return User(row["user_id"], username, row["balance"])

            conn.execute(
                "INSERT INTO users (user_id, username, balance, created_at) VALUES (?, ?, 0, ?)",
                (user_id, username, datetime.utcnow().isoformat()),
            )
            return User(user_id, username, 0)

    def get_balance(self, user_id: int) -> int:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT balance FROM users WHERE user_id = ?",
                (user_id,),
            ).fetchone()
            return int(row["balance"]) if row else 0

    def update_balance(self, user_id: int, delta: int, username: str | None = None) -> int:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO users (user_id, username, balance, created_at)
                VALUES (?, ?, 0, ?)
                ON CONFLICT(user_id) DO NOTHING
                """,
                (user_id, username, datetime.utcnow().isoformat()),
            )
            conn.execute(
                "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                (delta, user_id),
            )
            row = conn.execute(
                "SELECT balance FROM users WHERE user_id = ?",
                (user_id,),
            ).fetchone()
            return int(row["balance"])

    def create_subscription(self, user_id: int, plan_days: int, remnawave_id: str | None) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO subscriptions (user_id, plan_days, remnawave_id, status, created_at)
                VALUES (?, ?, ?, 'active', ?)
                """,
                (user_id, plan_days, remnawave_id, datetime.utcnow().isoformat()),
            )

    def get_subscriptions(self, user_id: int) -> list[sqlite3.Row]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT id, plan_days, remnawave_id, status, created_at FROM subscriptions WHERE user_id = ? ORDER BY id DESC",
                (user_id,),
            ).fetchall()
            return list(rows)
