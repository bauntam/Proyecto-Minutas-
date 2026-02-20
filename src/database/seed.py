"""Seed inicial para catálogos del sistema."""

from .connection import DatabaseManager

INITIAL_FOODS = [
    "Arroz",
    "Fideos",
    "Lentejas",
    "Pollo",
    "Carne molida",
    "Zapallo",
    "Zanahoria",
    "Papa",
    "Leche",
    "Pan",
    "Huevo",
    "Manzana",
]


def seed_food_catalog(database: DatabaseManager) -> None:
    """Inserta alimentos iniciales sin duplicar registros existentes."""
    for food_name in INITIAL_FOODS:
        database.execute(
            """
            INSERT OR IGNORE INTO alimentos (nombre, unidad, activo)
            VALUES (?, 'g', 1)
            """,
            (food_name,),
        )
