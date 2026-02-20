from __future__ import annotations

from db import get_connection
from models import normalize_name

INITIAL_FOODS = [
    "Aceite, de soya", "Ahuyama", "Apio", "Arroz", "Arveja verde", "Avena", "Azúcar, blanco",
    "Banano bocadillo", "Bienestarina", "Calabaza", "Canela", "Carne de Cerdo, magra", "Carne de res",
    "Carne de res molida", "Cebolla cabezona", "Cebolla junca", "Chocolate", "Crema de leche",
    "Durazno maduro, pulpa", "Esencia de vainilla", "Espinaca", "Fresa", "Frijol rojo", "Galleta Casera",
    "Galleta (craker)", "Galleta de leche", "Galleta de Soda", "Guayaba", "Habichuela", "Harina de maíz blanco",
    "Harina de trigo", "Huevo de gallina", "Kumis, entero con dulce", "Leche en polvo entera de vaca",
    "Leche condensada azucarada", "Lechuga", "Lenteja", "Limón", "Mandarina", "Mango, maduro pulpa",
    "Manzana, maduro pulpa", "Margarina", "Mayonesa", "Mora", "Naranja", "Pan aliñado", "Pan blandito",
    "Pan Coco", "Pan tajado", "Panela", "Papa común", "Papaya, maduro pulpa", "Pasta alimenticia enriq.",
    "Pechuga de pollo", "Pepino común", "Pepino Cohombro", "Pera, maduro pulpa", "Perejil", "Pimentón", "Piña",
    "Polvo de hornear", "Plátano hartón maduro", "Plátano hartón verde", "Remolacha", "Queso doble crema",
    "Repollo, hojas frescas", "Sal", "Pasta spaguetti", "Tomate de árbol", "Tomate, pulpa", "Tostada",
    "Yogurt, entero con dulce", "Zanahoria",
]


def seed_if_empty() -> int:
    with get_connection() as conn:
        total = int(conn.execute("SELECT COUNT(*) FROM alimentos").fetchone()[0])
        if total > 0:
            return 0

        inserted = 0
        for name in INITIAL_FOODS:
            clean = normalize_name(name)
            if not clean:
                continue
            conn.execute("INSERT OR IGNORE INTO alimentos(nombre) VALUES (?)", (clean,))
            inserted += 1
        conn.commit()
        return inserted


if __name__ == "__main__":
    count = seed_if_empty()
    print(f"Seed ejecutado. Registros insertados: {count}")
