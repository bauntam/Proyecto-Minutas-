"""Punto de entrada de la aplicación de minutas."""

from src.database.connection import DatabaseManager
from src.database.seed import seed_food_catalog
from src.services.food_service import FoodService
from src.services.garden_service import GardenService
from src.services.minute_service import MinuteService
from src.ui.app import MinutasApp


def build_application() -> MinutasApp:
    database = DatabaseManager()
    database.initialize_schema()
    seed_food_catalog(database)

    garden_service = GardenService(database)
    food_service = FoodService(database)
    minute_service = MinuteService(database)

    app = MinutasApp(
        garden_service=garden_service,
        food_service=food_service,
        minute_service=minute_service,
    )

    app.protocol("WM_DELETE_WINDOW", lambda: (database.close(), app.destroy()))
    return app


if __name__ == "__main__":
    application = build_application()
    application.mainloop()
