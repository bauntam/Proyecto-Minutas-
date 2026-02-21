from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

import models


class WeeklyOrderWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc):
        super().__init__(master)
        self.title("Pedido semanal")
        self.geometry("980x620")

        self._jardines = []
        self._minutas_jardin = []

        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)

        top = ttk.LabelFrame(root, text="Selección", padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Jardín:").grid(row=0, column=0, sticky="w")
        self.jardin_var = tk.StringVar()
        self.jardin_combo = ttk.Combobox(top, textvariable=self.jardin_var, state="readonly", width=35)
        self.jardin_combo.grid(row=0, column=1, sticky="we", padx=(6, 8))
        self.jardin_combo.bind("<<ComboboxSelected>>", lambda _e: self.refresh_minutas())

        ttk.Button(top, text="Actualizar", command=self.refresh_jardines).grid(row=0, column=2)

        ttk.Label(top, text="#Niños Grupo 1:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.ninos_g1_var = tk.StringVar(value="0")
        ttk.Entry(top, textvariable=self.ninos_g1_var, width=12).grid(row=1, column=1, sticky="w", padx=(6, 0), pady=(8, 0))

        ttk.Label(top, text="#Niños Grupo 2:").grid(row=1, column=2, sticky="w", pady=(8, 0), padx=(8, 0))
        self.ninos_g2_var = tk.StringVar(value="0")
        ttk.Entry(top, textvariable=self.ninos_g2_var, width=12).grid(row=1, column=3, sticky="w", padx=(6, 0), pady=(8, 0))

        top.grid_columnconfigure(1, weight=1)

        body = ttk.Frame(root)
        body.pack(fill="both", expand=True, pady=(10, 0))

        left = ttk.LabelFrame(body, text="Minutas de la semana (selección múltiple)", padding=8)
        left.pack(side="left", fill="both", expand=False)

        self.minutas_listbox = tk.Listbox(left, selectmode=tk.EXTENDED, width=45, height=18)
        self.minutas_listbox.pack(fill="both", expand=True)

        ttk.Button(left, text="Calcular", command=self.calculate).pack(fill="x", pady=(8, 0))

        right = ttk.LabelFrame(body, text="Resumen pedido semanal", padding=8)
        right.pack(side="left", fill="both", expand=True, padx=(10, 0))

        columns = ("alimento", "suma_g1", "ninos_g1", "total_g1", "suma_g2", "ninos_g2", "total_g2", "total")
        self.tree = ttk.Treeview(right, columns=columns, show="headings")
        self.tree.heading("alimento", text="Alimento")
        self.tree.heading("suma_g1", text="Suma gramos G1")
        self.tree.heading("ninos_g1", text="#Niños G1")
        self.tree.heading("total_g1", text="Total G1")
        self.tree.heading("suma_g2", text="Suma gramos G2")
        self.tree.heading("ninos_g2", text="#Niños G2")
        self.tree.heading("total_g2", text="Total G2")
        self.tree.heading("total", text="Total general")

        self.tree.column("alimento", width=220)
        for col in columns[1:]:
            self.tree.column(col, width=95, anchor="e")

        self.tree.pack(fill="both", expand=True)

        self.refresh_jardines()

    def _selected_jardin(self):
        name = self.jardin_var.get()
        return next((j for j in self._jardines if j["nombre"] == name), None)

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

    def refresh_minutas(self) -> None:
        self.minutas_listbox.delete(0, tk.END)
        self._minutas_jardin = []

        jardin = self._selected_jardin()
        if not jardin:
            return

        self._minutas_jardin = models.list_jardin_minutas_semana(jardin["id"])
        for row in self._minutas_jardin:
            self.minutas_listbox.insert(tk.END, row["minuta_nombre"])

    def _parse_non_negative_int(self, raw: str, label: str) -> int:
        try:
            value = int(raw)
        except ValueError as exc:
            raise ValueError(f"{label} debe ser un entero mayor o igual a 0.") from exc
        if value < 0:
            raise ValueError(f"{label} debe ser un entero mayor o igual a 0.")
        return value

    def calculate(self) -> None:
        selected_indices = self.minutas_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Validación", "Selecciona al menos una minuta.", parent=self)
            return

        try:
            ninos_g1 = self._parse_non_negative_int(self.ninos_g1_var.get(), "#Niños Grupo 1")
            ninos_g2 = self._parse_non_negative_int(self.ninos_g2_var.get(), "#Niños Grupo 2")
        except ValueError as exc:
            messagebox.showerror("Validación", str(exc), parent=self)
            return

        minuta_ids = [self._minutas_jardin[idx]["minuta_id"] for idx in selected_indices]
        resumen = models.calculate_weekly_order(minuta_ids, ninos_g1, ninos_g2)

        for row_id in self.tree.get_children():
            self.tree.delete(row_id)

        for row in resumen:
            self.tree.insert(
                "",
                "end",
                values=(
                    row["alimento_nombre"],
                    row["suma_gramos_g1"],
                    row["ninos_grupo_1"],
                    row["total_g1"],
                    row["suma_gramos_g2"],
                    row["ninos_grupo_2"],
                    row["total_g2"],
                    row["total_general"],
                ),
            )

        if not resumen:
            messagebox.showinfo("Resultado", "No se encontraron alimentos para las minutas seleccionadas.", parent=self)
