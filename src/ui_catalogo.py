from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

import models


class CatalogoWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, on_change=None):
        super().__init__(master)
        self.title("Catálogo de alimentos")
        self.geometry("420x480")
        self.on_change = on_change

        frame = ttk.Frame(self, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Nuevo alimento:").pack(anchor="w")
        self.nombre_var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=self.nombre_var)
        entry.pack(fill="x", pady=(4, 8))
        entry.focus()

        ttk.Button(frame, text="Agregar", command=self.add_alimento).pack(anchor="w")

        ttk.Label(frame, text="Alimentos registrados:").pack(anchor="w", pady=(12, 4))
        self.listbox = tk.Listbox(frame)
        self.listbox.pack(fill="both", expand=True)

        self.refresh()

    def refresh(self) -> None:
        self.listbox.delete(0, tk.END)
        for row in models.list_alimentos():
            self.listbox.insert(tk.END, row["nombre"])

    def add_alimento(self) -> None:
        try:
            models.create_alimento(self.nombre_var.get())
            self.nombre_var.set("")
            self.refresh()
            if self.on_change:
                self.on_change()
        except ValueError as exc:
            messagebox.showerror("Validación", str(exc), parent=self)
        except Exception:
            messagebox.showerror("Error", "No fue posible guardar el alimento.", parent=self)
