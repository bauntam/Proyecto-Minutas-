"""Definición del esquema relacional para la aplicación de minutas."""

SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS jardines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        direccion TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS minutas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        jardin_id INTEGER NOT NULL,
        nombre TEXT NOT NULL,
        fecha TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (jardin_id) REFERENCES jardines(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS alimentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        unidad TEXT NOT NULL DEFAULT 'g',
        activo INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS minuta_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        minuta_id INTEGER NOT NULL,
        alimento_id INTEGER NOT NULL,
        cantidad_gramos REAL NOT NULL CHECK (cantidad_gramos > 0),
        FOREIGN KEY (minuta_id) REFERENCES minutas(id) ON DELETE CASCADE,
        FOREIGN KEY (alimento_id) REFERENCES alimentos(id)
    );
    """,
]
