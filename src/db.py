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


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {row["name"] for row in rows}


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
            """
        )

        minuta_cols = _table_columns(conn, "minutas")
        if not minuta_cols:
            conn.execute(
                """
                CREATE TABLE minutas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    fecha_creacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        elif "jardin_id" in minuta_cols:
            conn.execute("PRAGMA foreign_keys = OFF")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS minutas_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    fecha_creacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                INSERT OR IGNORE INTO minutas_new(id, nombre, fecha_creacion)
                SELECT id, nombre, fecha_creacion FROM minutas
                """
            )
            conn.execute("DROP TABLE minutas")
            conn.execute("ALTER TABLE minutas_new RENAME TO minutas")
            conn.execute("PRAGMA foreign_keys = ON")

        item_cols = _table_columns(conn, "minuta_items")
        recreate_for_nullable = False
        if item_cols:
            item_meta = conn.execute("PRAGMA table_info(minuta_items)").fetchall()
            meta_by_name = {row["name"]: row for row in item_meta}
            g1 = meta_by_name.get("gramos_1_2")
            g2 = meta_by_name.get("gramos_3_5")
            if g1 and g2 and (g1["notnull"] == 1 or g2["notnull"] == 1):
                recreate_for_nullable = True

        if not item_cols:
            conn.execute(
                """
                CREATE TABLE minuta_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    minuta_id INTEGER NOT NULL,
                    alimento_id INTEGER NOT NULL,
                    gramos_1_2 REAL CHECK (gramos_1_2 IS NULL OR gramos_1_2 > 0),
                    gramos_3_5 REAL CHECK (gramos_3_5 IS NULL OR gramos_3_5 > 0),
                    FOREIGN KEY (minuta_id) REFERENCES minutas(id) ON DELETE CASCADE,
                    FOREIGN KEY (alimento_id) REFERENCES alimentos(id),
                    UNIQUE (minuta_id, alimento_id)
                )
                """
            )
        elif "gramos" in item_cols or recreate_for_nullable:
            conn.execute("PRAGMA foreign_keys = OFF")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS minuta_items_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    minuta_id INTEGER NOT NULL,
                    alimento_id INTEGER NOT NULL,
                    gramos_1_2 REAL CHECK (gramos_1_2 IS NULL OR gramos_1_2 > 0),
                    gramos_3_5 REAL CHECK (gramos_3_5 IS NULL OR gramos_3_5 > 0),
                    FOREIGN KEY (minuta_id) REFERENCES minutas(id) ON DELETE CASCADE,
                    FOREIGN KEY (alimento_id) REFERENCES alimentos(id),
                    UNIQUE (minuta_id, alimento_id)
                )
                """
            )
            if "gramos" in item_cols:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO minuta_items_new(id, minuta_id, alimento_id, gramos_1_2, gramos_3_5)
                    SELECT id, minuta_id, alimento_id, gramos, gramos FROM minuta_items
                    """
                )
            else:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO minuta_items_new(id, minuta_id, alimento_id, gramos_1_2, gramos_3_5)
                    SELECT id, minuta_id, alimento_id, gramos_1_2, gramos_3_5 FROM minuta_items
                    """
                )
            conn.execute("DROP TABLE minuta_items")
            conn.execute("ALTER TABLE minuta_items_new RENAME TO minuta_items")
            conn.execute("PRAGMA foreign_keys = ON")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jardin_minutas_semana (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jardin_id INTEGER NOT NULL,
                minuta_id INTEGER NOT NULL,
                orden INTEGER NOT NULL,
                FOREIGN KEY (jardin_id) REFERENCES jardines(id) ON DELETE CASCADE,
                FOREIGN KEY (minuta_id) REFERENCES minutas(id) ON DELETE CASCADE,
                UNIQUE (jardin_id, minuta_id),
                UNIQUE (jardin_id, orden)
            )
            """
        )
        conn.commit()
