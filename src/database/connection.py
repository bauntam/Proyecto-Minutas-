"""Utilidades de conexión y acceso SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from .schema import SCHEMA_STATEMENTS


class DatabaseManager:
    """Encapsula la conexión SQLite y operaciones comunes."""

    def __init__(self, db_path: str | Path = "data/minutas.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON;")

    def initialize_schema(self) -> None:
        with self.connection:
            for statement in SCHEMA_STATEMENTS:
                self.connection.execute(statement)

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> int:
        with self.connection:
            cursor = self.connection.execute(query, params)
        return cursor.lastrowid

    def fetch_all(self, query: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
        cursor = self.connection.execute(query, params)
        return cursor.fetchall()

    def fetch_one(self, query: str, params: tuple[Any, ...] = ()) -> sqlite3.Row | None:
        cursor = self.connection.execute(query, params)
        return cursor.fetchone()

    def close(self) -> None:
        self.connection.close()
