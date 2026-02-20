from __future__ import annotations

import sqlite3
from typing import Any

from db import get_connection


def normalize_name(nombre: str) -> str:
    return " ".join((nombre or "").strip().split())


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


def list_minutas(jardin_id: int) -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, nombre, fecha_creacion
            FROM minutas
            WHERE jardin_id = ?
            ORDER BY fecha_creacion DESC, id DESC
            """,
            (jardin_id,),
        ).fetchall()


def create_minuta(jardin_id: int, nombre: str) -> int:
    nombre = normalize_name(nombre)
    if not nombre:
        raise ValueError("El nombre de la minuta es obligatorio.")
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO minutas(jardin_id, nombre) VALUES (?, ?)",
            (jardin_id, nombre),
        )
        conn.commit()
        return int(cursor.lastrowid)


def get_minuta(minuta_id: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, jardin_id, nombre, fecha_creacion FROM minutas WHERE id = ?",
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
            SELECT mi.id, mi.gramos, a.id AS alimento_id, a.nombre AS alimento_nombre
            FROM minuta_items mi
            INNER JOIN alimentos a ON a.id = mi.alimento_id
            WHERE mi.minuta_id = ?
            ORDER BY a.nombre
            """,
            (minuta_id,),
        ).fetchall()


def add_or_update_item(minuta_id: int, alimento_id: int, gramos: float) -> None:
    if gramos <= 0:
        raise ValueError("Los gramos deben ser mayores a 0.")
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM minuta_items WHERE minuta_id = ? AND alimento_id = ?",
            (minuta_id, alimento_id),
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE minuta_items SET gramos = ? WHERE id = ?",
                (gramos, existing["id"]),
            )
        else:
            conn.execute(
                "INSERT INTO minuta_items(minuta_id, alimento_id, gramos) VALUES (?, ?, ?)",
                (minuta_id, alimento_id, gramos),
            )
        conn.commit()


def update_item_gramos(item_id: int, gramos: float) -> None:
    if gramos <= 0:
        raise ValueError("Los gramos deben ser mayores a 0.")
    with get_connection() as conn:
        conn.execute("UPDATE minuta_items SET gramos = ? WHERE id = ?", (gramos, item_id))
        conn.commit()


def remove_item(item_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM minuta_items WHERE id = ?", (item_id,))
        conn.commit()
