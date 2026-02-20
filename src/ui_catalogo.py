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

        actions = ttk.Frame(frame)
        actions.pack(fill="x", pady=(8, 0))
        ttk.Button(actions, text="Eliminar alimento", command=self.remove_alimento).pack(side="left")

        self._alimentos = []
        self.refresh()

    def refresh(self) -> None:
        self._alimentos = models.list_alimentos()
        self.listbox.delete(0, tk.END)
        for row in self._alimentos:
            self.listbox.insert(tk.END, row["nombre"])


    def _selected_alimento(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Atención", "Selecciona un alimento.", parent=self)
            return None
        return self._alimentos[selected[0]]

    def remove_alimento(self) -> None:
        alimento = self._selected_alimento()
        if not alimento:
            return

        if not messagebox.askyesno(
            "Confirmar",
            f"¿Eliminar el alimento '{alimento['nombre']}'? También se quitará de todas las minutas.",
            parent=self,
        ):
            return

        try:
            models.delete_alimento(alimento["id"])
            self.refresh()
            if self.on_change:
                self.on_change()
        except Exception:
            messagebox.showerror("Error", "No fue posible eliminar el alimento.", parent=self)

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
