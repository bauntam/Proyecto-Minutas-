from __future__ import annotations

import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

import models


class MinutaEditor(tk.Toplevel):
    def __init__(self, master: tk.Misc, conn: sqlite3.Connection, minuta_id: int, minuta_nombre: str):
        super().__init__(master)
        self.conn = conn
        self.minuta_id = minuta_id
        self.title(f"Editar minuta: {minuta_nombre}")
        self.geometry("700x460")

        frame = ttk.Frame(self, padding=12)
        frame.pack(fill="both", expand=True)

        top = ttk.LabelFrame(frame, text="Agregar ingrediente", padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Alimento").grid(row=0, column=0, sticky="w")
        ttk.Label(top, text="Gramos").grid(row=0, column=1, sticky="w", padx=(8, 0))

        self.food_combo = ttk.Combobox(top, state="readonly")
        self.food_combo.grid(row=1, column=0, sticky="ew")
        self.gramos_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.gramos_var, width=16).grid(row=1, column=1, sticky="w", padx=(8, 0))
        ttk.Button(top, text="Agregar/Actualizar", command=self._add_or_update).grid(row=1, column=2, padx=(8, 0))
        top.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(frame, columns=("alimento", "gramos"), show="headings", height=12)
        self.tree.heading("alimento", text="Alimento")
        self.tree.heading("gramos", text="Gramos")
        self.tree.column("alimento", width=420)
        self.tree.column("gramos", width=120, anchor="e")
        self.tree.pack(fill="both", expand=True, pady=12)

        actions = ttk.Frame(frame)
        actions.pack(fill="x")
        ttk.Button(actions, text="Editar gramos", command=self._edit_gramos).pack(side="left")
        ttk.Button(actions, text="Quitar ingrediente", command=self._remove).pack(side="left", padx=(8, 0))

        self.food_map: dict[str, int] = {}
        self._refresh_foods()
        self.refresh_items()

    def _refresh_foods(self) -> None:
        foods = models.list_alimentos(self.conn)
        values = [f["nombre"] for f in foods]
        self.food_map = {f["nombre"]: f["id"] for f in foods}
        self.food_combo["values"] = values
        if values and not self.food_combo.get():
            self.food_combo.current(0)

    def refresh_items(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in models.list_minuta_items(self.conn, self.minuta_id):
            self.tree.insert(
                "",
                tk.END,
                iid=str(row["id"]),
                values=(row["alimento"], f"{row['gramos']:.2f}"),
            )

    def _add_or_update(self) -> None:
        food_name = self.food_combo.get()
        alimento_id = self.food_map.get(food_name)
        if not alimento_id:
            messagebox.showerror("Error", "Selecciona un alimento.", parent=self)
            return

        try:
            models.add_or_update_minuta_item(self.conn, self.minuta_id, alimento_id, self.gramos_var.get())
        except ValueError as exc:
            messagebox.showerror("Error", str(exc), parent=self)
            return
        except sqlite3.DatabaseError:
            messagebox.showerror("Error", "No se pudo guardar el ingrediente.", parent=self)
            return

        self.gramos_var.set("")
        self.refresh_items()

    def _selected_item_id(self) -> int | None:
        selected = self.tree.selection()
        if not selected:
            return None
        return int(selected[0])

    def _edit_gramos(self) -> None:
        item_id = self._selected_item_id()
        if item_id is None:
            messagebox.showinfo("Atención", "Selecciona un ingrediente.", parent=self)
            return

        old_value = self.tree.item(str(item_id), "values")[1]
        new_value = simpledialog.askstring("Editar gramos", "Nuevo valor en gramos:", initialvalue=old_value, parent=self)
        if new_value is None:
            return

        try:
            models.update_minuta_item_gramos(self.conn, item_id, new_value)
        except ValueError as exc:
            messagebox.showerror("Error", str(exc), parent=self)
            return
        except sqlite3.DatabaseError:
            messagebox.showerror("Error", "No se pudo actualizar el ingrediente.", parent=self)
            return

        self.refresh_items()

    def _remove(self) -> None:
        item_id = self._selected_item_id()
        if item_id is None:
            messagebox.showinfo("Atención", "Selecciona un ingrediente.", parent=self)
            return

        try:
            models.delete_minuta_item(self.conn, item_id)
        except sqlite3.DatabaseError:
            messagebox.showerror("Error", "No se pudo quitar el ingrediente.", parent=self)
            return

        self.refresh_items()
