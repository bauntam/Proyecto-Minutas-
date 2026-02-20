from __future__ import annotations

import sqlite3
from typing import Any


def normalize_name(name: str) -> str:
    return " ".join(name.split()).strip()


def canonical_name(name: str) -> str:
    return normalize_name(name).lower()


def _validate_non_empty(name: str, label: str) -> str:
    normalized = normalize_name(name)
    if not normalized:
        raise ValueError(f"{label} no puede estar vacío.")
    return normalized


def list_alimentos(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT id, nombre FROM alimentos ORDER BY nombre").fetchall()


def add_alimento(conn: sqlite3.Connection, nombre: str) -> int:
    clean_name = _validate_non_empty(nombre, "El nombre del alimento")
    canonical = canonical_name(clean_name)
    existing = {canonical_name(row["nombre"]) for row in list_alimentos(conn)}
    if canonical in existing:
        raise ValueError("Ese alimento ya existe.")

    cur = conn.execute("INSERT INTO alimentos(nombre) VALUES (?)", (clean_name,))
    conn.commit()
    return cur.lastrowid


def list_jardines(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT id, nombre FROM jardines ORDER BY nombre").fetchall()


def add_jardin(conn: sqlite3.Connection, nombre: str) -> int:
    clean_name = _validate_non_empty(nombre, "El nombre del jardín")
    canonical = canonical_name(clean_name)
    existing = {canonical_name(row["nombre"]) for row in list_jardines(conn)}
    if canonical in existing:
        raise ValueError("Ese jardín ya existe.")

    cur = conn.execute("INSERT INTO jardines(nombre) VALUES (?)", (clean_name,))
    conn.commit()
    return cur.lastrowid


def rename_jardin(conn: sqlite3.Connection, jardin_id: int, nuevo_nombre: str) -> None:
    clean_name = _validate_non_empty(nuevo_nombre, "El nombre del jardín")
    canonical = canonical_name(clean_name)
    existing = {
        row["id"]: canonical_name(row["nombre"])
        for row in list_jardines(conn)
        if row["id"] != jardin_id
    }
    if canonical in existing.values():
        raise ValueError("Ya existe otro jardín con ese nombre.")

    conn.execute("UPDATE jardines SET nombre = ? WHERE id = ?", (clean_name, jardin_id))
    conn.commit()


def delete_jardin(conn: sqlite3.Connection, jardin_id: int) -> None:
    conn.execute("DELETE FROM jardines WHERE id = ?", (jardin_id,))
    conn.commit()


def list_minutas(conn: sqlite3.Connection, jardin_id: int) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT id, nombre, fecha_creacion
        FROM minutas
        WHERE jardin_id = ?
        ORDER BY datetime(fecha_creacion) DESC, id DESC
        """,
        (jardin_id,),
    ).fetchall()


def add_minuta(conn: sqlite3.Connection, jardin_id: int, nombre: str) -> int:
    clean_name = _validate_non_empty(nombre, "El nombre de la minuta")
    cur = conn.execute(
        "INSERT INTO minutas(jardin_id, nombre) VALUES (?, ?)",
        (jardin_id, clean_name),
    )
    conn.commit()
    return cur.lastrowid


def rename_minuta(conn: sqlite3.Connection, minuta_id: int, nuevo_nombre: str) -> None:
    clean_name = _validate_non_empty(nuevo_nombre, "El nombre de la minuta")
    conn.execute("UPDATE minutas SET nombre = ? WHERE id = ?", (clean_name, minuta_id))
    conn.commit()


def delete_minuta(conn: sqlite3.Connection, minuta_id: int) -> None:
    conn.execute("DELETE FROM minutas WHERE id = ?", (minuta_id,))
    conn.commit()


def list_minuta_items(conn: sqlite3.Connection, minuta_id: int) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT mi.id, mi.minuta_id, mi.alimento_id, a.nombre AS alimento, mi.gramos
        FROM minuta_items mi
        JOIN alimentos a ON a.id = mi.alimento_id
        WHERE mi.minuta_id = ?
        ORDER BY a.nombre
        """,
        (minuta_id,),
    ).fetchall()


def _parse_gramos(value: Any) -> float:
    try:
        gramos = float(str(value).replace(",", "."))
    except ValueError as exc:
        raise ValueError("Los gramos deben ser un número.") from exc

    if gramos <= 0:
        raise ValueError("Los gramos deben ser mayores que 0.")
    return gramos


def add_or_update_minuta_item(
    conn: sqlite3.Connection,
    minuta_id: int,
    alimento_id: int,
    gramos: Any,
) -> int:
    gramos_value = _parse_gramos(gramos)
    existing = conn.execute(
        "SELECT id FROM minuta_items WHERE minuta_id = ? AND alimento_id = ?",
        (minuta_id, alimento_id),
    ).fetchone()

    if existing:
        conn.execute(
            "UPDATE minuta_items SET gramos = ? WHERE id = ?",
            (gramos_value, existing["id"]),
        )
        conn.commit()
        return existing["id"]

    cur = conn.execute(
        "INSERT INTO minuta_items(minuta_id, alimento_id, gramos) VALUES (?, ?, ?)",
        (minuta_id, alimento_id, gramos_value),
    )
    conn.commit()
    return cur.lastrowid


def update_minuta_item_gramos(conn: sqlite3.Connection, item_id: int, gramos: Any) -> None:
    gramos_value = _parse_gramos(gramos)
    conn.execute("UPDATE minuta_items SET gramos = ? WHERE id = ?", (gramos_value, item_id))
    conn.commit()


def delete_minuta_item(conn: sqlite3.Connection, item_id: int) -> None:
    conn.execute("DELETE FROM minuta_items WHERE id = ?", (item_id,))
    conn.commit()
