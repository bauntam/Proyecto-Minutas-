"""Lógica de negocio para catálogo de alimentos."""

from __future__ import annotations

from src.database.connection import DatabaseManager
from src.models.entities import Alimento


class FoodService:
    def __init__(self, database: DatabaseManager) -> None:
        self.database = database

    def create_food(self, name: str, unit: str = "g") -> int:
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("El nombre del alimento es obligatorio.")

        return self.database.execute(
            "INSERT INTO alimentos (nombre, unidad, activo) VALUES (?, ?, 1)",
            (clean_name, unit),
        )

    def list_foods(self) -> list[Alimento]:
        rows = self.database.fetch_all(
            "SELECT id, nombre, unidad, activo FROM alimentos WHERE activo = 1 ORDER BY nombre"
        )
        return [
            Alimento(
                id=row["id"],
                nombre=row["nombre"],
                unidad=row["unidad"],
                activo=bool(row["activo"]),
            )
            for row in rows
        ]
