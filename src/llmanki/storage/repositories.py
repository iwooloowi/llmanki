from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

from llmanki.domain.models import Generation


@dataclass(frozen=True, slots=True)
class UserState:
    user_id: int
    deck_name: Optional[str]
    daily_count: int
    last_request_ts: int


@dataclass(frozen=True, slots=True)
class PendingGeneration:
    user_id: int
    generation: Generation
    regen_count: int
    meaning_hint: Optional[str]
    updated_ts: int


def _now_ts() -> int:
    return int(time.time())


class UserRepository:
    def __init__(self, conn):
        self._conn = conn

    def get(self, user_id: int) -> UserState:
        row = self._conn.execute(
            "SELECT user_id, deck_name, daily_count, last_request_ts FROM users WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        if row:
            return UserState(
                user_id=row["user_id"],
                deck_name=row["deck_name"],
                daily_count=row["daily_count"],
                last_request_ts=row["last_request_ts"],
            )
        self._conn.execute(
            "INSERT INTO users(user_id, deck_name, daily_count, last_request_ts) VALUES (?, NULL, 0, 0)",
            (user_id,),
        )
        self._conn.commit()
        return UserState(user_id=user_id, deck_name=None, daily_count=0, last_request_ts=0)

    def set_deck(self, user_id: int, deck_name: str) -> None:
        self._conn.execute(
            "INSERT INTO users(user_id, deck_name, daily_count, last_request_ts) "
            "VALUES (?, ?, 0, 0) "
            "ON CONFLICT(user_id) DO UPDATE SET deck_name=excluded.deck_name",
            (user_id, deck_name),
        )
        self._conn.commit()

    def update_usage(self, user_id: int, *, daily_count: int, last_request_ts: int) -> None:
        self._conn.execute(
            "UPDATE users SET daily_count = ?, last_request_ts = ? WHERE user_id = ?",
            (daily_count, last_request_ts, user_id),
        )
        self._conn.commit()


class PendingRepository:
    def __init__(self, conn):
        self._conn = conn

    def get(self, user_id: int) -> Optional[PendingGeneration]:
        row = self._conn.execute(
            "SELECT user_id, word, definition, example, regen_count, meaning_hint, updated_ts "
            "FROM pending WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        if not row:
            return None
        gen = Generation(word=row["word"], definition=row["definition"], example=row["example"])
        return PendingGeneration(
            user_id=row["user_id"],
            generation=gen,
            regen_count=row["regen_count"],
            meaning_hint=row["meaning_hint"],
            updated_ts=row["updated_ts"],
        )

    def upsert(
        self,
        user_id: int,
        generation: Generation,
        regen_count: int,
        meaning_hint: Optional[str],
    ) -> None:
        now = _now_ts()
        self._conn.execute(
            "INSERT INTO pending(user_id, word, definition, example, regen_count, meaning_hint, updated_ts) "
            "VALUES (?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET "
            "word=excluded.word, definition=excluded.definition, example=excluded.example, "
            "regen_count=excluded.regen_count, meaning_hint=excluded.meaning_hint, updated_ts=excluded.updated_ts",
            (
                user_id,
                generation.word,
                generation.definition,
                generation.example,
                regen_count,
                meaning_hint,
                now,
            ),
        )
        self._conn.commit()

    def clear(self, user_id: int) -> None:
        self._conn.execute("DELETE FROM pending WHERE user_id = ?", (user_id,))
        self._conn.commit()
