from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

import models
from ui_catalogo import CatalogoWindow
from ui_jardines import JardinesWindow
from ui_minutas import MinutasWindow


class MainWindow(ttk.Frame):
    def __init__(self, master: tk.Tk):
        super().__init__(master, padding=12)
        self.master = master
        self.pack(fill="both", expand=True)

        master.title("Minutas por Jardín - MVP")
        master.geometry("760x520")

        top = ttk.Frame(self)
        top.pack(fill="x")

        ttk.Button(top, text="Gestionar Jardines", command=self.open_jardines).pack(side="left")
        ttk.Button(top, text="Gestionar Alimentos", command=self.open_catalogo).pack(side="left", padx=(8, 0))
        ttk.Button(top, text="Gestionar Minutas", command=self.open_minutas).pack(side="left", padx=(8, 0))

        selection = ttk.LabelFrame(self, text="Jardín seleccionado", padding=8)
        selection.pack(fill="x", pady=(12, 8))

        self.jardin_var = tk.StringVar()
        self.jardin_combo = ttk.Combobox(selection, textvariable=self.jardin_var, state="readonly")
        self.jardin_combo.pack(side="left", fill="x", expand=True)
        self.jardin_combo.bind("<<ComboboxSelected>>", lambda _e: self.refresh_semana())

        ttk.Button(selection, text="Actualizar", command=self.refresh_jardines).pack(side="left", padx=(8, 0))

        semana_actions = ttk.Frame(self)
        semana_actions.pack(fill="x", pady=(2, 8))
        ttk.Button(semana_actions, text="Agregar minuta a la semana", command=self.agregar_minuta_semana).pack(side="left")
        ttk.Button(semana_actions, text="Quitar minuta de la semana", command=self.quitar_minuta_semana).pack(
            side="left", padx=(8, 0)
        )

        self.tree = ttk.Treeview(self, columns=("orden", "nombre", "fecha"), show="headings")
        self.tree.heading("orden", text="#")
        self.tree.heading("nombre", text="Minuta seleccionada")
        self.tree.heading("fecha", text="Fecha creación")
        self.tree.column("orden", width=50, anchor="center")
        self.tree.column("nombre", width=430)
        self.tree.column("fecha", width=180)
        self.tree.pack(fill="both", expand=True)

        self._jardines = []
        self._semana = []
        self.refresh_jardines()

    def open_jardines(self) -> None:
        JardinesWindow(self.master, on_change=self.refresh_jardines)

    def open_catalogo(self) -> None:
        CatalogoWindow(self.master, on_change=self.refresh_semana)

    def open_minutas(self) -> None:
        MinutasWindow(self.master, on_change=self.refresh_semana)

    def refresh_jardines(self) -> None:
        selected_name = self.jardin_var.get()
        self._jardines = models.list_jardines()
        names = [j["nombre"] for j in self._jardines]
        self.jardin_combo["values"] = names

        if not names:
            self.jardin_var.set("")
            self.refresh_semana()
            return

        if selected_name in names:
            self.jardin_var.set(selected_name)
        else:
            self.jardin_var.set(names[0])
        self.refresh_semana()

    def _selected_jardin(self):
        name = self.jardin_var.get()
        return next((j for j in self._jardines if j["nombre"] == name), None)

    def refresh_semana(self) -> None:
        for row in self.tree.get_children():
            self.tree.delete(row)

        jardin = self._selected_jardin()
        if not jardin:
            self._semana = []
            return

        self._semana = models.list_jardin_minutas_semana(jardin["id"])
        for row in self._semana:
            self.tree.insert(
                "",
                "end",
                iid=str(row["minuta_id"]),
                values=(row["orden"], row["minuta_nombre"], row["fecha_creacion"]),
            )

    def agregar_minuta_semana(self) -> None:
        jardin = self._selected_jardin()
        if not jardin:
            messagebox.showwarning("Atención", "Primero crea o selecciona un jardín.", parent=self.master)
            return

        minutas = models.list_minutas()
        if not minutas:
            messagebox.showwarning("Atención", "No hay minutas creadas. Crea una primero.", parent=self.master)
            return

        already = {row["minuta_id"] for row in self._semana}
        candidates = [m for m in minutas if m["id"] not in already]
        if not candidates:
            messagebox.showinfo("Información", "Este jardín ya tiene todas las minutas asignadas.", parent=self.master)
            return

        selected = self._pick_minuta(candidates)
        if not selected:
            return
        try:
            models.add_minuta_a_semana(jardin["id"], selected["id"])
            self.refresh_semana()
        except Exception:
            messagebox.showerror("Error", "No fue posible agregar la minuta a la semana.", parent=self.master)

    def _pick_minuta(self, minutas: list) -> dict | None:
        picker = tk.Toplevel(self.master)
        picker.title("Seleccionar minuta")
        picker.geometry("420x360")
        picker.transient(self.master)
        picker.grab_set()

        frame = ttk.Frame(picker, padding=12)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Selecciona la minuta para el pedido semanal:").pack(anchor="w")

        listbox = tk.Listbox(frame)
        listbox.pack(fill="both", expand=True, pady=(8, 8))
        for m in minutas:
            listbox.insert(tk.END, m["nombre"])

        chosen = {"row": None}

        def accept() -> None:
            idx = listbox.curselection()
            if not idx:
                return
            chosen["row"] = minutas[idx[0]]
            picker.destroy()

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Cancelar", command=picker.destroy).pack(side="right")
        ttk.Button(buttons, text="Seleccionar", command=accept).pack(side="right", padx=(0, 8))

        picker.wait_window()
        return chosen["row"]

    def quitar_minuta_semana(self) -> None:
        jardin = self._selected_jardin()
        if not jardin:
            messagebox.showwarning("Atención", "Selecciona un jardín.", parent=self.master)
            return

        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Selecciona una minuta de la semana.", parent=self.master)
            return

        minuta_id = int(selected[0])
        if not messagebox.askyesno("Confirmar", "¿Quitar esta minuta del pedido semanal?", parent=self.master):
            return

        try:
            models.remove_minuta_de_semana(jardin["id"], minuta_id)
            self.refresh_semana()
        except Exception:
            messagebox.showerror("Error", "No fue posible quitar la minuta de la semana.", parent=self.master)
