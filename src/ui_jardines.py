from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

import models


class JardinesWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, on_change=None):
        super().__init__(master)
        self.title("Gestión de jardines")
        self.geometry("430x460")
        self.on_change = on_change

        frame = ttk.Frame(self, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Nuevo jardín:").pack(anchor="w")
        self.nombre_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.nombre_var).pack(fill="x", pady=(4, 8))
        ttk.Button(frame, text="Crear jardín", command=self.crear_jardin).pack(anchor="w")

        ttk.Label(frame, text="Jardines:").pack(anchor="w", pady=(12, 4))
        self.listbox = tk.Listbox(frame)
        self.listbox.pack(fill="both", expand=True)

        actions = ttk.Frame(frame)
        actions.pack(fill="x", pady=(8, 0))
        ttk.Button(actions, text="Renombrar", command=self.renombrar).pack(side="left")
        ttk.Button(actions, text="Eliminar", command=self.eliminar).pack(side="left", padx=(8, 0))

        self._jardines = []
        self.refresh()

    def refresh(self) -> None:
        self._jardines = models.list_jardines()
        self.listbox.delete(0, tk.END)
        for row in self._jardines:
            self.listbox.insert(tk.END, row["nombre"])

    def _selected(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Atención", "Selecciona un jardín.", parent=self)
            return None
        return self._jardines[selected[0]]

    def crear_jardin(self) -> None:
        try:
            models.create_jardin(self.nombre_var.get())
            self.nombre_var.set("")
            self.refresh()
            if self.on_change:
                self.on_change()
        except ValueError as exc:
            messagebox.showerror("Validación", str(exc), parent=self)
        except Exception:
            messagebox.showerror("Error", "No fue posible crear el jardín.", parent=self)

    def renombrar(self) -> None:
        jardin = self._selected()
        if not jardin:
            return
        nuevo = simpledialog.askstring(
            "Renombrar jardín",
            "Nuevo nombre:",
            initialvalue=jardin["nombre"],
            parent=self,
        )
        if nuevo is None:
            return
        try:
            models.rename_jardin(jardin["id"], nuevo)
            self.refresh()
            if self.on_change:
                self.on_change()
        except ValueError as exc:
            messagebox.showerror("Validación", str(exc), parent=self)
        except Exception:
            messagebox.showerror("Error", "No fue posible renombrar el jardín.", parent=self)

    def eliminar(self) -> None:
        jardin = self._selected()
        if not jardin:
            return
        if not messagebox.askyesno(
            "Confirmar",
            f"¿Eliminar el jardín '{jardin['nombre']}' y todas sus minutas?",
            parent=self,
        ):
            return
        try:
            models.delete_jardin(jardin["id"])
            self.refresh()
            if self.on_change:
                self.on_change()
        except Exception:
            messagebox.showerror("Error", "No fue posible eliminar el jardín.", parent=self)
