from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from .db import get_connection, migrate
from .seed import seed_if_empty
from .ui_main import MainWindow


def main() -> None:
    conn = get_connection()
    try:
        migrate(conn)
        seeded = seed_if_empty(conn)
    except Exception:
        messagebox.showerror("Error", "No fue posible iniciar la base de datos.")
        conn.close()
        return

    root = tk.Tk()
    root.title("MVP Minutas por Jardín")
    root.geometry("700x520")

    MainWindow(root, conn)

    if seeded:
        messagebox.showinfo("Catálogo inicial", f"Se cargaron {seeded} alimentos iniciales.", parent=root)

    def on_close() -> None:
        conn.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
