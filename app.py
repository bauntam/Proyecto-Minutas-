"""Compatibilidad: ejecuta la app desde la raíz del proyecto."""

from src.main import build_application


if __name__ == "__main__":
    app = build_application()
    app.mainloop()
