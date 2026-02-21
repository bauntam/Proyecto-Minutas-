from __future__ import annotations

import sqlite3
import unicodedata
from typing import Any

from db import get_connection

MAX_MINUTAS = 25


def normalize_name(nombre: str) -> str:
    return " ".join((nombre or "").strip().split())


def normalize_food_name(nombre: str) -> str:
    text = unicodedata.normalize("NFKC", nombre or "")
    text = text.replace("\u00A0", " ")
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace('"', " ").replace("'", " ")
    text = "".join(
        char
        for char in unicodedata.normalize("NFD", text)
        if unicodedata.category(char) != "Mn"
    )
    normalized_chars: list[str] = []
    for char in text.lower():
        normalized_chars.append(char if char.isalnum() else " ")
    return " ".join("".join(normalized_chars).split())


def _exists_by_name(table: str, nombre: str, current_id: int | None = None) -> bool:
    query = f"SELECT id FROM {table} WHERE lower(nombre) = lower(?)"
    params: list[Any] = [nombre]
    if current_id is not None:
        query += " AND id != ?"
        params.append(current_id)
    with get_connection() as conn:
        row = conn.execute(query, params).fetchone()
    return row is not None


def list_alimentos() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute("SELECT id, nombre FROM alimentos ORDER BY nombre").fetchall()


def create_alimento(nombre: str) -> int:
    nombre = normalize_name(nombre)
    if not nombre:
        raise ValueError("El nombre del alimento es obligatorio.")
    if _exists_by_name("alimentos", nombre):
        raise ValueError("Ya existe un alimento con ese nombre.")
    with get_connection() as conn:
        cursor = conn.execute("INSERT INTO alimentos(nombre) VALUES (?)", (nombre,))
        conn.commit()
        return int(cursor.lastrowid)


def delete_alimento(alimento_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM minuta_items WHERE alimento_id = ?", (alimento_id,))
        conn.execute("DELETE FROM alimentos WHERE id = ?", (alimento_id,))
        conn.commit()


def count_alimentos() -> int:
    with get_connection() as conn:
        return int(conn.execute("SELECT COUNT(*) FROM alimentos").fetchone()[0])


def list_jardines() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute("SELECT id, nombre FROM jardines ORDER BY nombre").fetchall()


def create_jardin(nombre: str) -> int:
    nombre = normalize_name(nombre)
    if not nombre:
        raise ValueError("El nombre del jardín es obligatorio.")
    if _exists_by_name("jardines", nombre):
        raise ValueError("Ya existe un jardín con ese nombre.")
    with get_connection() as conn:
        cursor = conn.execute("INSERT INTO jardines(nombre) VALUES (?)", (nombre,))
        conn.commit()
        return int(cursor.lastrowid)


def rename_jardin(jardin_id: int, nuevo_nombre: str) -> None:
    nuevo_nombre = normalize_name(nuevo_nombre)
    if not nuevo_nombre:
        raise ValueError("El nombre del jardín es obligatorio.")
    if _exists_by_name("jardines", nuevo_nombre, jardin_id):
        raise ValueError("Ya existe un jardín con ese nombre.")
    with get_connection() as conn:
        conn.execute("UPDATE jardines SET nombre = ? WHERE id = ?", (nuevo_nombre, jardin_id))
        conn.commit()


def delete_jardin(jardin_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM jardines WHERE id = ?", (jardin_id,))
        conn.commit()


def list_minutas() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, nombre, fecha_creacion
            FROM minutas
            ORDER BY fecha_creacion DESC, id DESC
            """
        ).fetchall()


def create_minuta(nombre: str) -> int:
    nombre = normalize_name(nombre)
    if not nombre:
        raise ValueError("El nombre de la minuta es obligatorio.")
    if count_minutas() >= MAX_MINUTAS:
        raise ValueError(f"Solo se permiten {MAX_MINUTAS} minutas en total.")
    with get_connection() as conn:
        cursor = conn.execute("INSERT INTO minutas(nombre) VALUES (?)", (nombre,))
        conn.commit()
        return int(cursor.lastrowid)


def count_minutas() -> int:
    with get_connection() as conn:
        return int(conn.execute("SELECT COUNT(*) FROM minutas").fetchone()[0])


def get_minuta(minuta_id: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, nombre, fecha_creacion FROM minutas WHERE id = ?",
            (minuta_id,),
        ).fetchone()


def update_minuta_nombre(minuta_id: int, nombre: str) -> None:
    nombre = normalize_name(nombre)
    if not nombre:
        raise ValueError("El nombre de la minuta es obligatorio.")
    with get_connection() as conn:
        conn.execute("UPDATE minutas SET nombre = ? WHERE id = ?", (nombre, minuta_id))
        conn.commit()


def delete_minuta(minuta_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM minutas WHERE id = ?", (minuta_id,))
        conn.commit()


def list_minuta_items(minuta_id: int) -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT
                mi.id,
                mi.gramos_1_2,
                mi.gramos_3_5,
                a.id AS alimento_id,
                a.nombre AS alimento_nombre
            FROM minuta_items mi
            INNER JOIN alimentos a ON a.id = mi.alimento_id
            WHERE mi.minuta_id = ?
            ORDER BY a.nombre
            """,
            (minuta_id,),
        ).fetchall()


def _validate_gramos(gramos_1_2: float, gramos_3_5: float) -> None:
    if gramos_1_2 <= 0 or gramos_3_5 <= 0:
        raise ValueError("Los gramos deben ser mayores a 0 para ambos grupos.")


def add_or_update_item(minuta_id: int, alimento_id: int, gramos_1_2: float, gramos_3_5: float) -> None:
    _validate_gramos(gramos_1_2, gramos_3_5)
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM minuta_items WHERE minuta_id = ? AND alimento_id = ?",
            (minuta_id, alimento_id),
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE minuta_items SET gramos_1_2 = ?, gramos_3_5 = ? WHERE id = ?",
                (gramos_1_2, gramos_3_5, existing["id"]),
            )
        else:
            conn.execute(
                """
                INSERT INTO minuta_items(minuta_id, alimento_id, gramos_1_2, gramos_3_5)
                VALUES (?, ?, ?, ?)
                """,
                (minuta_id, alimento_id, gramos_1_2, gramos_3_5),
            )
        conn.commit()


def update_item_gramos(item_id: int, gramos_1_2: float, gramos_3_5: float) -> None:
    _validate_gramos(gramos_1_2, gramos_3_5)
    with get_connection() as conn:
        conn.execute(
            "UPDATE minuta_items SET gramos_1_2 = ?, gramos_3_5 = ? WHERE id = ?",
            (gramos_1_2, gramos_3_5, item_id),
        )
        conn.commit()


def remove_item(item_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM minuta_items WHERE id = ?", (item_id,))
        conn.commit()


def list_jardin_minutas_semana(jardin_id: int) -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT jms.id, jms.orden, m.id AS minuta_id, m.nombre AS minuta_nombre, m.fecha_creacion
            FROM jardin_minutas_semana jms
            INNER JOIN minutas m ON m.id = jms.minuta_id
            WHERE jms.jardin_id = ?
            ORDER BY jms.orden ASC
            """,
            (jardin_id,),
        ).fetchall()


def add_minuta_a_semana(jardin_id: int, minuta_id: int) -> None:
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM jardin_minutas_semana WHERE jardin_id = ? AND minuta_id = ?",
            (jardin_id, minuta_id),
        ).fetchone()
        if existing:
            return
        max_orden = conn.execute(
            "SELECT COALESCE(MAX(orden), 0) FROM jardin_minutas_semana WHERE jardin_id = ?",
            (jardin_id,),
        ).fetchone()[0]
        conn.execute(
            "INSERT INTO jardin_minutas_semana(jardin_id, minuta_id, orden) VALUES (?, ?, ?)",
            (jardin_id, minuta_id, int(max_orden) + 1),
        )
        conn.commit()


def remove_minuta_de_semana(jardin_id: int, minuta_id: int) -> None:
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM jardin_minutas_semana WHERE jardin_id = ? AND minuta_id = ?",
            (jardin_id, minuta_id),
        )
        remaining = conn.execute(
            "SELECT id FROM jardin_minutas_semana WHERE jardin_id = ? ORDER BY orden",
            (jardin_id,),
        ).fetchall()
        for idx, row in enumerate(remaining, start=1):
            conn.execute("UPDATE jardin_minutas_semana SET orden = ? WHERE id = ?", (idx, row["id"]))
        conn.commit()


def calculate_weekly_order(minuta_ids: list[int], ninos_grupo_1: int, ninos_grupo_2: int) -> list[dict[str, Any]]:
    if ninos_grupo_1 < 0 or ninos_grupo_2 < 0:
        raise ValueError("La cantidad de niños por grupo debe ser mayor o igual a 0.")

    selected_minuta_ids = [int(minuta_id) for minuta_id in minuta_ids]
    if not selected_minuta_ids:
        return []

    selected_minutas_values = ", ".join(["(?)"] * len(selected_minuta_ids))
    query = f"""
        WITH selected_minutas(minuta_id) AS (
            VALUES {selected_minutas_values}
        )
        SELECT
            a.id AS alimento_id,
            a.nombre AS alimento_nombre,
            COALESCE(SUM(mi.gramos_1_2), 0) AS suma_gramos_g1,
            COALESCE(SUM(mi.gramos_3_5), 0) AS suma_gramos_g2
        FROM selected_minutas sm
        INNER JOIN minuta_items mi ON mi.minuta_id = sm.minuta_id
        INNER JOIN alimentos a ON a.id = mi.alimento_id
        GROUP BY a.id, a.nombre
        ORDER BY lower(a.nombre) ASC
    """

    with get_connection() as conn:
        rows = conn.execute(query, selected_minuta_ids).fetchall()

    resumen: list[dict[str, Any]] = []
    for row in rows:
        suma_g1 = float(row["suma_gramos_g1"] or 0)
        suma_g2 = float(row["suma_gramos_g2"] or 0)
        total_g1 = suma_g1 * ninos_grupo_1
        total_g2 = suma_g2 * ninos_grupo_2
        resumen.append(
            {
                "alimento_id": row["alimento_id"],
                "alimento_nombre": row["alimento_nombre"],
                "suma_gramos_g1": suma_g1,
                "ninos_grupo_1": ninos_grupo_1,
                "total_g1": total_g1,
                "suma_gramos_g2": suma_g2,
                "ninos_grupo_2": ninos_grupo_2,
                "total_g2": total_g2,
                "total_general": total_g1 + total_g2,
            }
        )

    return resumen
