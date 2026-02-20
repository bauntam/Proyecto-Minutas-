"""Lógica de negocio para minutas e ingredientes."""

from __future__ import annotations

from src.database.connection import DatabaseManager
from src.models.entities import Minuta, MinutaItem


class MinuteService:
    def __init__(self, database: DatabaseManager) -> None:
        self.database = database

    def create_minute(self, garden_id: int, name: str, date: str | None = None) -> int:
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("El nombre de la minuta es obligatorio.")

        return self.database.execute(
            "INSERT INTO minutas (jardin_id, nombre, fecha) VALUES (?, ?, ?)",
            (garden_id, clean_name, date or None),
        )

    def add_item(self, minute_id: int, food_id: int, grams: float) -> int:
        if grams <= 0:
            raise ValueError("La cantidad en gramos debe ser mayor a cero.")

        return self.database.execute(
            "INSERT INTO minuta_items (minuta_id, alimento_id, cantidad_gramos) VALUES (?, ?, ?)",
            (minute_id, food_id, grams),
        )

    def list_minutes(self, garden_id: int | None = None) -> list[Minuta]:
        if garden_id is None:
            rows = self.database.fetch_all(
                "SELECT id, jardin_id, nombre, fecha FROM minutas ORDER BY id DESC"
            )
        else:
            rows = self.database.fetch_all(
                "SELECT id, jardin_id, nombre, fecha FROM minutas WHERE jardin_id = ? ORDER BY id DESC",
                (garden_id,),
            )

        return [
            Minuta(
                id=row["id"],
                jardin_id=row["jardin_id"],
                nombre=row["nombre"],
                fecha=row["fecha"],
            )
            for row in rows
        ]

    def list_minute_items(self, minute_id: int) -> list[MinutaItem]:
        rows = self.database.fetch_all(
            """
            SELECT id, minuta_id, alimento_id, cantidad_gramos
            FROM minuta_items
            WHERE minuta_id = ?
            ORDER BY id DESC
            """,
            (minute_id,),
        )
        return [
            MinutaItem(
                id=row["id"],
                minuta_id=row["minuta_id"],
                alimento_id=row["alimento_id"],
                cantidad_gramos=float(row["cantidad_gramos"]),
            )
            for row in rows
        ]

    def list_minute_items_detail(self, minute_id: int) -> list[dict[str, str | float | int]]:
        rows = self.database.fetch_all(
            """
            SELECT mi.id, a.nombre AS alimento, mi.cantidad_gramos
            FROM minuta_items mi
            JOIN alimentos a ON a.id = mi.alimento_id
            WHERE mi.minuta_id = ?
            ORDER BY mi.id DESC
            """,
            (minute_id,),
        )
        return [
            {
                "id": row["id"],
                "alimento": row["alimento"],
                "cantidad_gramos": float(row["cantidad_gramos"]),
            }
            for row in rows
        ]
