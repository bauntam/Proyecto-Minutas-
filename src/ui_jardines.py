from __future__ import annotations

import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from . import models


class JardinesWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, conn: sqlite3.Connection, on_change=None):
        super().__init__(master)
        self.conn = conn
        self.on_change = on_change
        self.title("Gestión de jardines")
        self.geometry("520x420")

        frame = ttk.Frame(self, padding=12)
        frame.pack(fill="both", expand=True)

        top_row = ttk.Frame(frame)
        top_row.pack(fill="x")

        self.name_var = tk.StringVar()
        ttk.Entry(top_row, textvariable=self.name_var).pack(side="left", fill="x", expand=True)
        ttk.Button(top_row, text="Crear jardín", command=self._create).pack(side="left", padx=(8, 0))

        self.listbox = tk.Listbox(frame)
        self.listbox.pack(fill="both", expand=True, pady=10)

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Renombrar", command=self._rename).pack(side="left")
        ttk.Button(buttons, text="Eliminar", command=self._delete).pack(side="left", padx=(8, 0))

        self._id_by_index: list[int] = []
        self.refresh()

    def refresh(self) -> None:
        self.listbox.delete(0, tk.END)
        self._id_by_index = []
        for row in models.list_jardines(self.conn):
            self._id_by_index.append(row["id"])
            self.listbox.insert(tk.END, row["nombre"])

    def _selected_id(self) -> int | None:
        selected = self.listbox.curselection()
        if not selected:
            return None
        return self._id_by_index[selected[0]]

    def _notify_change(self) -> None:
        if callable(self.on_change):
            self.on_change()

    def _create(self) -> None:
        try:
            models.add_jardin(self.conn, self.name_var.get())
        except ValueError as exc:
            messagebox.showerror("Error", str(exc), parent=self)
            return
        except sqlite3.DatabaseError:
            messagebox.showerror("Error", "No se pudo crear el jardín.", parent=self)
            return

        self.name_var.set("")
        self.refresh()
        self._notify_change()

    def _rename(self) -> None:
        jardin_id = self._selected_id()
        if jardin_id is None:
            messagebox.showinfo("Atención", "Selecciona un jardín.", parent=self)
            return

        new_name = simpledialog.askstring("Renombrar jardín", "Nuevo nombre:", parent=self)
        if new_name is None:
            return

        try:
            models.rename_jardin(self.conn, jardin_id, new_name)
        except ValueError as exc:
            messagebox.showerror("Error", str(exc), parent=self)
            return
        except sqlite3.DatabaseError:
            messagebox.showerror("Error", "No se pudo renombrar el jardín.", parent=self)
            return

        self.refresh()
        self._notify_change()

    def _delete(self) -> None:
        jardin_id = self._selected_id()
        if jardin_id is None:
            messagebox.showinfo("Atención", "Selecciona un jardín.", parent=self)
            return

        confirm = messagebox.askyesno(
            "Confirmar eliminación",
            "¿Eliminar jardín? También se eliminarán sus minutas.",
            parent=self,
        )
        if not confirm:
            return

        try:
            models.delete_jardin(self.conn, jardin_id)
        except sqlite3.DatabaseError:
            messagebox.showerror("Error", "No se pudo eliminar el jardín.", parent=self)
            return

        self.refresh()
        self._notify_change()
