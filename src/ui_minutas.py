from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

import models


class MinutaEditorWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, minuta_id: int):
        super().__init__(master)
        self.minuta_id = minuta_id
        self.title("Editor de minuta")
        self.geometry("640x500")

        self._alimentos = models.list_alimentos()
        self._items = []

        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)

        minuta = models.get_minuta(minuta_id)
        nombre_inicial = minuta["nombre"] if minuta else ""

        top = ttk.Frame(root)
        top.pack(fill="x")
        ttk.Label(top, text="Nombre minuta:").pack(side="left")
        self.nombre_var = tk.StringVar(value=nombre_inicial)
        ttk.Entry(top, textvariable=self.nombre_var, width=40).pack(side="left", padx=(6, 6))
        ttk.Button(top, text="Guardar nombre", command=self.save_nombre).pack(side="left")

        add_frame = ttk.LabelFrame(root, text="Agregar / actualizar ingrediente", padding=8)
        add_frame.pack(fill="x", pady=(10, 8))

        ttk.Label(add_frame, text="Alimento:").grid(row=0, column=0, sticky="w")
        self.alimento_var = tk.StringVar()
        self.combo = ttk.Combobox(
            add_frame,
            textvariable=self.alimento_var,
            values=[a["nombre"] for a in self._alimentos],
            width=38,
        )
        self.combo.grid(row=0, column=1, sticky="we", padx=(6, 8))

        ttk.Label(add_frame, text="Gramos:").grid(row=0, column=2, sticky="w")
        self.gramos_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.gramos_var, width=10).grid(row=0, column=3, padx=(6, 8))
        ttk.Button(add_frame, text="Agregar/Actualizar", command=self.add_item).grid(row=0, column=4)
        add_frame.grid_columnconfigure(1, weight=1)

        self.tree = ttk.Treeview(root, columns=("alimento", "gramos"), show="headings", height=12)
        self.tree.heading("alimento", text="Alimento")
        self.tree.heading("gramos", text="Gramos")
        self.tree.column("alimento", width=400)
        self.tree.column("gramos", width=120, anchor="e")
        self.tree.pack(fill="both", expand=True)

        actions = ttk.Frame(root)
        actions.pack(fill="x", pady=(8, 0))
        ttk.Button(actions, text="Editar gramos", command=self.edit_gramos).pack(side="left")
        ttk.Button(actions, text="Quitar ingrediente", command=self.remove_item).pack(side="left", padx=(8, 0))

        self.refresh_items()

    def _parse_gramos(self, raw: str) -> float:
        value = float(str(raw).replace(",", "."))
        if value <= 0:
            raise ValueError
        return value

    def save_nombre(self) -> None:
        try:
            models.update_minuta_nombre(self.minuta_id, self.nombre_var.get())
            messagebox.showinfo("Guardado", "Nombre actualizado.", parent=self)
        except ValueError as exc:
            messagebox.showerror("Validación", str(exc), parent=self)
        except Exception:
            messagebox.showerror("Error", "No fue posible actualizar el nombre.", parent=self)

    def refresh_items(self) -> None:
        self._alimentos = models.list_alimentos()
        self.combo["values"] = [a["nombre"] for a in self._alimentos]

        self._items = models.list_minuta_items(self.minuta_id)
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in self._items:
            self.tree.insert("", "end", iid=str(row["id"]), values=(row["alimento_nombre"], row["gramos"]))

    def add_item(self) -> None:
        selected_name = models.normalize_name(self.alimento_var.get())
        alimento = next((a for a in self._alimentos if a["nombre"].lower() == selected_name.lower()), None)
        if not alimento:
            messagebox.showerror("Validación", "Selecciona un alimento válido del catálogo.", parent=self)
            return
        try:
            gramos = self._parse_gramos(self.gramos_var.get())
            models.add_or_update_item(self.minuta_id, alimento["id"], gramos)
            self.gramos_var.set("")
            self.refresh_items()
        except ValueError:
            messagebox.showerror("Validación", "Los gramos deben ser un número mayor a 0.", parent=self)
        except Exception:
            messagebox.showerror("Error", "No fue posible agregar el ingrediente.", parent=self)

    def _selected_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Selecciona un ingrediente.", parent=self)
            return None
        item_id = int(selected[0])
        return next((x for x in self._items if x["id"] == item_id), None)

    def edit_gramos(self) -> None:
        item = self._selected_item()
        if not item:
            return
        nuevo = simpledialog.askstring(
            "Editar gramos",
            "Nueva cantidad en gramos:",
            initialvalue=str(item["gramos"]),
            parent=self,
        )
        if nuevo is None:
            return
        try:
            gramos = self._parse_gramos(nuevo)
            models.update_item_gramos(item["id"], gramos)
            self.refresh_items()
        except ValueError:
            messagebox.showerror("Validación", "Los gramos deben ser un número mayor a 0.", parent=self)
        except Exception:
            messagebox.showerror("Error", "No fue posible actualizar gramos.", parent=self)

    def remove_item(self) -> None:
        item = self._selected_item()
        if not item:
            return
        if not messagebox.askyesno(
            "Confirmar",
            f"¿Quitar {item['alimento_nombre']} de la minuta?",
            parent=self,
        ):
            return
        try:
            models.remove_item(item["id"])
            self.refresh_items()
        except Exception:
            messagebox.showerror("Error", "No fue posible quitar el ingrediente.", parent=self)
