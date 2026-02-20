"""Lógica de negocio asociada a jardines."""

from __future__ import annotations

from src.database.connection import DatabaseManager
from src.models.entities import Jardin


class GardenService:
    def __init__(self, database: DatabaseManager) -> None:
        self.database = database

    def create_garden(self, name: str, address: str = "") -> int:
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("El nombre del jardín es obligatorio.")

        return self.database.execute(
            "INSERT INTO jardines (nombre, direccion) VALUES (?, ?)",
            (clean_name, address.strip() or None),
        )

    def list_gardens(self) -> list[Jardin]:
        rows = self.database.fetch_all("SELECT id, nombre, direccion FROM jardines ORDER BY nombre")
        return [Jardin(id=row["id"], nombre=row["nombre"], direccion=row["direccion"]) for row in rows]
