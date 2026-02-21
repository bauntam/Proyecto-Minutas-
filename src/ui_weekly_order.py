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
        self.minutas_listbox.bind("<<ListboxSelect>>", lambda _e: self._update_selected_count())

        self.selected_count_var = tk.StringVar(value="Minutas seleccionadas: 0")
        ttk.Label(left, textvariable=self.selected_count_var).pack(anchor="w", pady=(8, 0))

        ttk.Button(left, text="Generar pedido / Sumar minutas", command=self.calculate).pack(fill="x", pady=(8, 0))

        right = ttk.LabelFrame(body, text="Resultado", padding=8)
        right.pack(side="left", fill="both", expand=True, padx=(10, 0))
        ttk.Label(
            right,
            text="El resultado se abrirá en una ventana con el resumen consolidado por alimento.",
            wraplength=380,
            justify="left",
        ).pack(anchor="nw")

        self.refresh_jardines()

    def _update_selected_count(self) -> None:
        selected_count = len(self.minutas_listbox.curselection())
        self.selected_count_var.set(f"Minutas seleccionadas: {selected_count}")

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
            self._update_selected_count()
            return

        self._minutas_jardin = models.list_jardin_minutas_semana(jardin["id"])
        for row in self._minutas_jardin:
            self.minutas_listbox.insert(tk.END, row["minuta_nombre"])
        self._update_selected_count()

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

        if not resumen:
            messagebox.showinfo("Resultado", "No se encontraron alimentos para las minutas seleccionadas.", parent=self)
            return

        self._show_result_window(resumen, len(set(minuta_ids)), ninos_g1, ninos_g2)

    def _show_result_window(
        self,
        resumen: list[dict[str, float | int | str]],
        selected_count: int,
        ninos_g1: int,
        ninos_g2: int,
    ) -> None:
        window = tk.Toplevel(self)
        window.title("Pedido semanal consolidado")
        window.geometry("1040x520")

        root = ttk.Frame(window, padding=12)
        root.pack(fill="both", expand=True)

        ttk.Label(root, text=f"Minutas seleccionadas: {selected_count}").pack(anchor="w")
        ttk.Label(root, text=f"Niños G1: {ninos_g1} | Niños G2: {ninos_g2}").pack(anchor="w", pady=(2, 10))

        columns = ("alimento", "suma_g1", "total_g1", "suma_g2", "total_g2", "total")
        tree = ttk.Treeview(root, columns=columns, show="headings")
        tree.heading("alimento", text="Alimento")
        tree.heading("suma_g1", text="Suma gramos G1")
        tree.heading("total_g1", text="Total G1")
        tree.heading("suma_g2", text="Suma gramos G2")
        tree.heading("total_g2", text="Total G2")
        tree.heading("total", text="Total general")

        tree.column("alimento", width=220)
        for col in columns[1:]:
            tree.column(col, width=130, anchor="e")

        yscroll = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=yscroll.set)

        tree.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="left", fill="y")

        for row in resumen:
            tree.insert(
                "",
                "end",
                values=(
                    row["alimento_nombre"],
                    row["suma_gramos_g1"],
                    row["total_g1"],
                    row["suma_gramos_g2"],
                    row["total_g2"],
                    row["total_general"],
                ),
            )
