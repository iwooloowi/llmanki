from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  user_id INTEGER PRIMARY KEY,
  deck_name TEXT,
  daily_count INTEGER NOT NULL DEFAULT 0,
  last_request_ts INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS pending (
  user_id INTEGER PRIMARY KEY,
  word TEXT NOT NULL,
  definition TEXT NOT NULL,
  example TEXT NOT NULL,
  regen_count INTEGER NOT NULL DEFAULT 0,
  meaning_hint TEXT,
  updated_ts INTEGER NOT NULL
);
"""


def connect(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()
