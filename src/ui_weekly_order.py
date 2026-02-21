from __future__ import annotations

import tkinter as tk
from decimal import Decimal, ROUND_HALF_UP
from tkinter import messagebox, ttk

import models


def normalize_food_name(name: str) -> str:
    return " ".join(name.strip().split()).casefold()


_POUNDS_FOODS_RAW = {
    "Ahuyama",
    "Apio",
    "Arveja verde c/cáscara",
    "Banano bocadillo",
    "Banano común",
    "Calabazín",
    "Cebolla cabezona",
    "Cebolla larga",
    "Crema de leche x 125 gr",
    "Espinaca",
    "Fresa",
    "Durazno NACIONAL MADURO",
    "Guayaba JUGO",
    "Habichuela",
    "Lechuga",
    "Mandarina PORCION",
    "Mango PORCION",
    "Manzana ANA O ROYAL",
    "Mora JUGO",
    "Naranja DULCE PORCION",
    "Papa común",
    "Papaya PORCION",
    "Pepino cohombro",
    "Pepino de guiso",
    "Pera PORCION",
    "Piña ORO MIEL PORCIÓN",
    "Plátano maduro",
    "Plátano verde",
    "Queso doble crema",
    "Remolacha",
    "Repollo blanco",
    "Tomate chonto o río",
    "Zanahoria",
    "Carne de res MAGRA MOLIDA",
    "Carne de res MAGRA BLANDA",
    "Carne de cerdo MAGRA",
    "Pechuga de pollo",
    "Arroz",
    "Azúcar",
    "Chocolate de mesa",
    "Harina de trigo",
    "Harina de maíz para arepas",
    "Lenteja",
    "Sal",
    "Frijol rojo",
    "Tomate de arbol",
}

POUNDS_FOODS = {normalize_food_name(food) for food in _POUNDS_FOODS_RAW}


def _round_half_up(value: Decimal) -> int:
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def format_pedido_final(nombre_alimento: str, total_gramos: float | int) -> str:
    if normalize_food_name(nombre_alimento) in POUNDS_FOODS:
        libras = Decimal(str(total_gramos)) / Decimal("500")
        return f"{_round_half_up(libras)} lb"
    total = Decimal(str(total_gramos))
    total_str = str(int(total)) if total == total.to_integral_value() else str(total.normalize())
    return f"{total_str} g"


class WeeklyOrderWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc):
        super().__init__(master)
        self.title("Pedido semanal")
        self.geometry("1080x640")

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

        left = ttk.LabelFrame(body, text="Minutas cargadas en la semana", padding=8)
        left.pack(side="left", fill="both", expand=True)

        actions = ttk.Frame(left)
        actions.pack(fill="x", pady=(0, 8))
        ttk.Button(actions, text="Agregar minuta a la semana", command=self.add_minuta_semana).pack(side="left")
        ttk.Button(actions, text="Quitar minuta de la semana", command=self.remove_minuta_semana).pack(side="left", padx=(8, 0))

        columns = ("orden", "minuta", "fecha")
        self.semana_tree = ttk.Treeview(left, columns=columns, show="headings", height=15)
        self.semana_tree.heading("orden", text="#")
        self.semana_tree.heading("minuta", text="Minuta")
        self.semana_tree.heading("fecha", text="Fecha creación")
        self.semana_tree.column("orden", width=50, anchor="center")
        self.semana_tree.column("minuta", width=280)
        self.semana_tree.column("fecha", width=180)

        semana_scroll = ttk.Scrollbar(left, orient="vertical", command=self.semana_tree.yview)
        self.semana_tree.configure(yscrollcommand=semana_scroll.set)
        self.semana_tree.pack(side="left", fill="both", expand=True)
        semana_scroll.pack(side="left", fill="y")

        self.minutas_count_var = tk.StringVar(value="Minutas en la semana: 0")
        ttk.Label(left, textvariable=self.minutas_count_var).pack(anchor="w", pady=(8, 0))

        ttk.Button(left, text="Generar pedido semanal", command=self.calculate).pack(fill="x", pady=(8, 0))

        right = ttk.LabelFrame(body, text="Resultado", padding=8)
        right.pack(side="left", fill="both", expand=True, padx=(10, 0))
        ttk.Label(
            right,
            text="El resultado se abrirá en una ventana con el resumen consolidado por alimento.",
            wraplength=380,
            justify="left",
        ).pack(anchor="nw")

        self.refresh_jardines()

    def _update_minutas_count(self) -> None:
        self.minutas_count_var.set(f"Minutas en la semana: {len(self._minutas_jardin)}")

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
        for item in self.semana_tree.get_children():
            self.semana_tree.delete(item)
        self._minutas_jardin = []

        jardin = self._selected_jardin()
        if not jardin:
            self._update_minutas_count()
            return

        self._minutas_jardin = models.list_jardin_minutas_semana(jardin["id"])
        for row in self._minutas_jardin:
            self.semana_tree.insert(
                "",
                "end",
                iid=str(row["minuta_id"]),
                values=(row["orden"], row["minuta_nombre"], row["fecha_creacion"]),
            )
        self._update_minutas_count()

    def add_minuta_semana(self) -> None:
        jardin = self._selected_jardin()
        if not jardin:
            messagebox.showwarning("Atención", "Selecciona un jardín.", parent=self)
            return

        minutas = models.list_minutas()
        if not minutas:
            messagebox.showwarning("Atención", "No hay minutas creadas. Crea una primero.", parent=self)
            return

        already = {row["minuta_id"] for row in self._minutas_jardin}
        candidates = [m for m in minutas if m["id"] not in already]
        if not candidates:
            messagebox.showinfo("Información", "Este jardín ya tiene todas las minutas asignadas.", parent=self)
            return

        selected = self._pick_minuta(candidates)
        if not selected:
            return

        try:
            models.add_minuta_a_semana(jardin["id"], selected["id"])
            self.refresh_minutas()
        except Exception:
            messagebox.showerror("Error", "No fue posible agregar la minuta a la semana.", parent=self)

    def _pick_minuta(self, minutas: list) -> dict | None:
        picker = tk.Toplevel(self)
        picker.title("Seleccionar minuta")
        picker.geometry("420x360")
        picker.transient(self)
        picker.grab_set()

        frame = ttk.Frame(picker, padding=12)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Selecciona la minuta para el pedido semanal:").pack(anchor="w")

        listbox = tk.Listbox(frame)
        listbox.pack(fill="both", expand=True, pady=(8, 8))
        for minuta in minutas:
            listbox.insert(tk.END, minuta["nombre"])

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

    def remove_minuta_semana(self) -> None:
        jardin = self._selected_jardin()
        if not jardin:
            messagebox.showwarning("Atención", "Selecciona un jardín.", parent=self)
            return

        selected = self.semana_tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Selecciona una minuta de la semana.", parent=self)
            return

        minuta_id = int(selected[0])
        if not messagebox.askyesno("Confirmar", "¿Quitar esta minuta del pedido semanal?", parent=self):
            return

        try:
            models.remove_minuta_de_semana(jardin["id"], minuta_id)
            self.refresh_minutas()
        except Exception:
            messagebox.showerror("Error", "No fue posible quitar la minuta de la semana.", parent=self)

    def _parse_non_negative_int(self, raw: str, label: str) -> int:
        try:
            value = int(raw)
        except ValueError as exc:
            raise ValueError(f"{label} debe ser un entero mayor o igual a 0.") from exc
        if value < 0:
            raise ValueError(f"{label} debe ser un entero mayor o igual a 0.")
        return value

    def calculate(self) -> None:
        if not self._minutas_jardin:
            messagebox.showwarning("Validación", "Agrega al menos una minuta.", parent=self)
            return

        try:
            ninos_g1 = self._parse_non_negative_int(self.ninos_g1_var.get(), "#Niños Grupo 1")
            ninos_g2 = self._parse_non_negative_int(self.ninos_g2_var.get(), "#Niños Grupo 2")
        except ValueError as exc:
            messagebox.showerror("Validación", str(exc), parent=self)
            return

        minuta_ids = [row["minuta_id"] for row in self._minutas_jardin]
        resumen = models.calculate_weekly_order(minuta_ids, ninos_g1, ninos_g2)

        if not resumen:
            messagebox.showinfo("Resultado", "No se encontraron alimentos para las minutas de la semana.", parent=self)
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
        window.geometry("840x520")

        root = ttk.Frame(window, padding=12)
        root.pack(fill="both", expand=True)

        ttk.Label(root, text=f"Minutas en la semana: {selected_count}").pack(anchor="w")
        ttk.Label(root, text=f"Niños G1: {ninos_g1} | Niños G2: {ninos_g2}").pack(anchor="w", pady=(2, 10))

        columns = ("alimento", "suma_g1", "suma_g2", "total", "pedido_final")
        tree = ttk.Treeview(root, columns=columns, show="headings")
        tree.heading("alimento", text="Alimento")
        tree.heading("suma_g1", text="Suma gramos G1")
        tree.heading("suma_g2", text="Suma gramos G2")
        tree.heading("total", text="Total general en gramos")
        tree.heading("pedido_final", text="Pedido final")

        tree.column("alimento", width=220)
        tree.column("suma_g1", width=120, anchor="e")
        tree.column("suma_g2", width=120, anchor="e")
        tree.column("total", width=165, anchor="e")
        tree.column("pedido_final", width=110, anchor="e")

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
                    row["suma_gramos_g2"],
                    row["total_general"],
                    format_pedido_final(row["alimento_nombre"], row["total_general"]),
                ),
            )
