from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "minutas.db"


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Return SQLite connection with row access by column name."""
    path = db_path or DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def migrate(conn: sqlite3.Connection) -> None:
    """Create database tables and indexes when missing."""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS alimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS jardines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
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
            gramos REAL NOT NULL,
            FOREIGN KEY (minuta_id) REFERENCES minutas(id) ON DELETE CASCADE,
            FOREIGN KEY (alimento_id) REFERENCES alimentos(id) ON DELETE RESTRICT,
            UNIQUE(minuta_id, alimento_id)
        );

        CREATE UNIQUE INDEX IF NOT EXISTS idx_alimentos_nombre_lower
            ON alimentos(lower(trim(nombre)));

        CREATE UNIQUE INDEX IF NOT EXISTS idx_jardines_nombre_lower
            ON jardines(lower(trim(nombre)));
        """
    )
    conn.commit()
