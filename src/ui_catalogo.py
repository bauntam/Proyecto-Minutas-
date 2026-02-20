from __future__ import annotations

import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

import models


class CatalogoWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, conn: sqlite3.Connection):
        super().__init__(master)
        self.conn = conn
        self.title("Catálogo de alimentos")
        self.geometry("460x420")

        frame = ttk.Frame(self, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Nuevo alimento:").pack(anchor="w")
        input_row = ttk.Frame(frame)
        input_row.pack(fill="x", pady=(4, 10))

        self.name_var = tk.StringVar()
        ttk.Entry(input_row, textvariable=self.name_var).pack(side="left", fill="x", expand=True)
        ttk.Button(input_row, text="Agregar", command=self._add_food).pack(side="left", padx=(8, 0))

        self.listbox = tk.Listbox(frame)
        self.listbox.pack(fill="both", expand=True)

        self.refresh()

    def refresh(self) -> None:
        self.listbox.delete(0, tk.END)
        for food in models.list_alimentos(self.conn):
            self.listbox.insert(tk.END, food["nombre"])

    def _add_food(self) -> None:
        try:
            models.add_alimento(self.conn, self.name_var.get())
        except ValueError as exc:
            messagebox.showerror("Error", str(exc), parent=self)
            return
        except sqlite3.DatabaseError:
            messagebox.showerror("Error", "No se pudo guardar el alimento.", parent=self)
            return

        self.name_var.set("")
        self.refresh()
