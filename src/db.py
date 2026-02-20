from __future__ import annotations

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "minutas.db"


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS alimentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE COLLATE NOCASE
            );

            CREATE TABLE IF NOT EXISTS jardines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE COLLATE NOCASE
            );

            CREATE TABLE IF NOT EXISTS minutas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jardin_id INTEGER NOT NULL,
                nombre TEXT NOT NULL,
                fecha_creacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (jardin_id) REFERENCES jardines(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS minuta_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                minuta_id INTEGER NOT NULL,
                alimento_id INTEGER NOT NULL,
                gramos REAL NOT NULL CHECK (gramos > 0),
                FOREIGN KEY (minuta_id) REFERENCES minutas(id) ON DELETE CASCADE,
                FOREIGN KEY (alimento_id) REFERENCES alimentos(id),
                UNIQUE (minuta_id, alimento_id)
            );
            """
        )
        conn.commit()
