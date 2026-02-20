from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from db import init_db
from seed import seed_if_empty
from ui_main import MainWindow


def main() -> None:
    try:
        init_db()
        seed_if_empty()
    except Exception as exc:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"No fue posible inicializar la base de datos.\n{exc}")
        root.destroy()
        return

    root = tk.Tk()
    MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
