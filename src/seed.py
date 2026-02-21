from __future__ import annotations

from db import get_connection
from models import normalize_food_name, normalize_name

INITIAL_FOODS = [
    "Aceite, de soya",
    "Ahuyama",
    "Apio",
    "Arroz",
    "Arveja verde",
    "Avena",
    "Azúcar, blanco",
    "Banano común, maduro",
    "Banano bocadillo",
    "Bienestarina",
    "Calabaza",
    "Canela",
    "Carne de Cerdo, magra",
    "Carne de res",
    "Carne de res molida",
    "Cebolla cabezona",
    "Cebolla junca",
    "Chocolate",
    "Crema de leche",
    "Durazno maduro, pulpa",
    "Esencia de vainilla",
    "Espinaca",
    "Fresa",
    "Frijol rojo",
    "Galleta (craker)",
    "Galleta Casera",
    "Galleta de leche",
    "Galleta de Soda",
    "Guayaba",
    "Habichuela",
    "Harina de maíz blanco",
    "Harina de trigo",
    "Huevo de gallina",
    "Kumis, entero con dulce",
    "Leche condensada azucarada",
    "Leche en polvo entera de vaca",
    "Lechuga",
    "Lenteja",
    "Limón",
    "Mandarina",
    "Mango, maduro pulpa",
    "Manzana, maduro pulpa",
    "Margarina",
    "Mayonesa",
    "Mora",
    "Naranja",
    "Pan aliñado",
    "Pan blandito",
    "Pan Coco",
    "Pan tajado",
    "Panela",
    "Papa común",
    "Papaya, maduro pulpa",
    "Pasta alimenticia enriq.",
    "Pasta spaguetti",
    "Pechuga de pollo",
    "Pepino Cohombro",
    "Pepino común",
    "Pera, maduro pulpa",
    "Perejil",
    "Pimentón",
    "Piña",
    "Plátano hartón maduro",
    "Plátano hartón verde",
    "Polvo de hornear",
    "Queso doble crema",
    "Remolacha",
    "Repollo, hojas frescas",
    "Sal",
    "Tomate de árbol",
    "Tomate, pulpa",
    "Tostada",
    "Yogurt, entero con dulce",
    "Zanahoria",
]


def seed_if_empty() -> int:
    with get_connection() as conn:
        existing = conn.execute("SELECT nombre FROM alimentos").fetchall()
        existing_normalized = {normalize_food_name(row["nombre"]) for row in existing}

        inserted = 0
        for name in INITIAL_FOODS:
            display_name = normalize_name(name)
            normalized = normalize_food_name(display_name)
            if not display_name or not normalized or normalized in existing_normalized:
                continue
            conn.execute("INSERT OR IGNORE INTO alimentos(nombre) VALUES (?)", (display_name,))
            existing_normalized.add(normalized)
            inserted += 1
        conn.commit()
        return inserted


if __name__ == "__main__":
    count = seed_if_empty()
    print(f"Seed ejecutado. Registros insertados: {count}")
