from __future__ import annotations

import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

import models
from ui_catalogo import CatalogoWindow
from ui_jardines import JardinesWindow
from ui_minutas import MinutaEditor


class MainWindow(ttk.Frame):
    def __init__(self, master: tk.Tk, conn: sqlite3.Connection):
        super().__init__(master, padding=12)
        self.master = master
        self.conn = conn

        self.pack(fill="both", expand=True)

        self.jardin_var = tk.StringVar()
        self.jardin_combo = ttk.Combobox(self, state="readonly", textvariable=self.jardin_var)
        self.jardin_combo.pack(fill="x")
        self.jardin_combo.bind("<<ComboboxSelected>>", lambda _event: self.refresh_minutas())

        top_actions = ttk.Frame(self)
        top_actions.pack(fill="x", pady=(8, 12))
        ttk.Button(top_actions, text="Gestionar jardines", command=self.open_jardines).pack(side="left")
        ttk.Button(top_actions, text="Catálogo alimentos", command=self.open_catalogo).pack(side="left", padx=(8, 0))

        self.minutas_list = tk.Listbox(self)
        self.minutas_list.pack(fill="both", expand=True)

        actions = ttk.Frame(self)
        actions.pack(fill="x", pady=(12, 0))
        ttk.Button(actions, text="Nueva minuta", command=self.create_minuta).pack(side="left")
        ttk.Button(actions, text="Renombrar", command=self.rename_minuta).pack(side="left", padx=(8, 0))
        ttk.Button(actions, text="Abrir/Editar", command=self.edit_minuta).pack(side="left", padx=(8, 0))
        ttk.Button(actions, text="Eliminar", command=self.delete_minuta).pack(side="left", padx=(8, 0))

        self._jardines_id_by_name: dict[str, int] = {}
        self._minuta_id_by_index: list[int] = []

        self.refresh_jardines()

    def open_jardines(self) -> None:
        JardinesWindow(self.master, self.conn, on_change=self.refresh_jardines)

    def open_catalogo(self) -> None:
        CatalogoWindow(self.master, self.conn)

    def selected_jardin_id(self) -> int | None:
        name = self.jardin_combo.get()
        return self._jardines_id_by_name.get(name)

    def refresh_jardines(self) -> None:
        gardens = models.list_jardines(self.conn)
        values = [row["nombre"] for row in gardens]
        self._jardines_id_by_name = {row["nombre"]: row["id"] for row in gardens}
        self.jardin_combo["values"] = values

        current = self.jardin_combo.get()
        if current in self._jardines_id_by_name:
            pass
        elif values:
            self.jardin_combo.current(0)
        else:
            self.jardin_var.set("")

        self.refresh_minutas()

    def refresh_minutas(self) -> None:
        self.minutas_list.delete(0, tk.END)
        self._minuta_id_by_index = []

        jardin_id = self.selected_jardin_id()
        if jardin_id is None:
            return

        for row in models.list_minutas(self.conn, jardin_id):
            self._minuta_id_by_index.append(row["id"])
            self.minutas_list.insert(tk.END, f"{row['nombre']} ({row['fecha_creacion'][:10]})")

    def selected_minuta_id(self) -> int | None:
        selected = self.minutas_list.curselection()
        if not selected:
            return None
        return self._minuta_id_by_index[selected[0]]

    def create_minuta(self) -> None:
        jardin_id = self.selected_jardin_id()
        if jardin_id is None:
            messagebox.showinfo("Atención", "Primero crea o selecciona un jardín.", parent=self.master)
            return

        name = simpledialog.askstring("Nueva minuta", "Nombre de la minuta:", parent=self.master)
        if name is None:
            return

        try:
            models.add_minuta(self.conn, jardin_id, name)
        except ValueError as exc:
            messagebox.showerror("Error", str(exc), parent=self.master)
            return
        except sqlite3.DatabaseError:
            messagebox.showerror("Error", "No se pudo crear la minuta.", parent=self.master)
            return

        self.refresh_minutas()

    def rename_minuta(self) -> None:
        minuta_id = self.selected_minuta_id()
        if minuta_id is None:
            messagebox.showinfo("Atención", "Selecciona una minuta.", parent=self.master)
            return

        name = simpledialog.askstring("Renombrar minuta", "Nuevo nombre:", parent=self.master)
        if name is None:
            return

        try:
            models.rename_minuta(self.conn, minuta_id, name)
        except ValueError as exc:
            messagebox.showerror("Error", str(exc), parent=self.master)
            return
        except sqlite3.DatabaseError:
            messagebox.showerror("Error", "No se pudo renombrar la minuta.", parent=self.master)
            return

        self.refresh_minutas()

    def edit_minuta(self) -> None:
        minuta_id = self.selected_minuta_id()
        if minuta_id is None:
            messagebox.showinfo("Atención", "Selecciona una minuta.", parent=self.master)
            return

        raw_name = self.minutas_list.get(self.minutas_list.curselection()[0])
        MinutaEditor(self.master, self.conn, minuta_id=minuta_id, minuta_nombre=raw_name)

    def delete_minuta(self) -> None:
        minuta_id = self.selected_minuta_id()
        if minuta_id is None:
            messagebox.showinfo("Atención", "Selecciona una minuta.", parent=self.master)
            return

        if not messagebox.askyesno("Confirmar", "¿Eliminar minuta?", parent=self.master):
            return

        try:
            models.delete_minuta(self.conn, minuta_id)
        except sqlite3.DatabaseError:
            messagebox.showerror("Error", "No se pudo eliminar la minuta.", parent=self.master)
            return

        self.refresh_minutas()
