from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

import models
from ui_catalogo import CatalogoWindow
from ui_jardines import JardinesWindow
from ui_minutas import MinutaEditorWindow


class MainWindow(ttk.Frame):
    def __init__(self, master: tk.Tk):
        super().__init__(master, padding=12)
        self.master = master
        self.pack(fill="both", expand=True)

        master.title("Minutas por Jardín - MVP")
        master.geometry("700x480")

        top = ttk.Frame(self)
        top.pack(fill="x")

        ttk.Button(top, text="Gestionar Jardines", command=self.open_jardines).pack(side="left")
        ttk.Button(top, text="Gestionar Catálogo", command=self.open_catalogo).pack(side="left", padx=(8, 0))

        selection = ttk.LabelFrame(self, text="Jardín seleccionado", padding=8)
        selection.pack(fill="x", pady=(12, 8))

        self.jardin_var = tk.StringVar()
        self.jardin_combo = ttk.Combobox(selection, textvariable=self.jardin_var, state="readonly")
        self.jardin_combo.pack(side="left", fill="x", expand=True)
        self.jardin_combo.bind("<<ComboboxSelected>>", lambda _e: self.refresh_minutas())

        ttk.Button(selection, text="Actualizar", command=self.refresh_jardines).pack(side="left", padx=(8, 0))

        minuta_actions = ttk.Frame(self)
        minuta_actions.pack(fill="x", pady=(2, 8))
        ttk.Button(minuta_actions, text="Nueva minuta", command=self.nueva_minuta).pack(side="left")
        ttk.Button(minuta_actions, text="Abrir minuta", command=self.abrir_minuta).pack(side="left", padx=(8, 0))
        ttk.Button(minuta_actions, text="Eliminar minuta", command=self.eliminar_minuta).pack(side="left", padx=(8, 0))

        self.tree = ttk.Treeview(self, columns=("nombre", "fecha"), show="headings")
        self.tree.heading("nombre", text="Minuta")
        self.tree.heading("fecha", text="Fecha creación")
        self.tree.column("nombre", width=380)
        self.tree.column("fecha", width=180)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda _e: self.abrir_minuta())

        self._jardines = []
        self._minutas = []
        self.refresh_jardines()

    def open_jardines(self) -> None:
        JardinesWindow(self.master, on_change=self.refresh_jardines)

    def open_catalogo(self) -> None:
        CatalogoWindow(self.master)

    def refresh_jardines(self) -> None:
        selected_name = self.jardin_var.get()
        self._jardines = models.list_jardines()
        names = [j["nombre"] for j in self._jardines]
        self.jardin_combo["values"] = names

        if not names:
            self.jardin_var.set("")
            self.refresh_minutas()
            return

        if selected_name in names:
            self.jardin_var.set(selected_name)
        else:
            self.jardin_var.set(names[0])
        self.refresh_minutas()

    def _selected_jardin(self):
        name = self.jardin_var.get()
        return next((j for j in self._jardines if j["nombre"] == name), None)

    def refresh_minutas(self) -> None:
        for row in self.tree.get_children():
            self.tree.delete(row)

        jardin = self._selected_jardin()
        if not jardin:
            self._minutas = []
            return

        self._minutas = models.list_minutas(jardin["id"])
        for row in self._minutas:
            self.tree.insert("", "end", iid=str(row["id"]), values=(row["nombre"], row["fecha_creacion"]))

    def nueva_minuta(self) -> None:
        jardin = self._selected_jardin()
        if not jardin:
            messagebox.showwarning("Atención", "Primero crea o selecciona un jardín.", parent=self.master)
            return
        nombre = simpledialog.askstring("Nueva minuta", "Nombre de la minuta:", parent=self.master)
        if nombre is None:
            return
        try:
            minuta_id = models.create_minuta(jardin["id"], nombre)
            self.refresh_minutas()
            MinutaEditorWindow(self.master, minuta_id)
        except ValueError as exc:
            messagebox.showerror("Validación", str(exc), parent=self.master)
        except Exception:
            messagebox.showerror("Error", "No fue posible crear la minuta.", parent=self.master)

    def _selected_minuta_id(self) -> int | None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Selecciona una minuta.", parent=self.master)
            return None
        return int(selected[0])

    def abrir_minuta(self) -> None:
        minuta_id = self._selected_minuta_id()
        if minuta_id is None:
            return
        MinutaEditorWindow(self.master, minuta_id)

    def eliminar_minuta(self) -> None:
        minuta_id = self._selected_minuta_id()
        if minuta_id is None:
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar la minuta seleccionada?", parent=self.master):
            return
        try:
            models.delete_minuta(minuta_id)
            self.refresh_minutas()
        except Exception:
            messagebox.showerror("Error", "No fue posible eliminar la minuta.", parent=self.master)
