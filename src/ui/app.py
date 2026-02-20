"""Interfaz Tkinter mínima para gestionar jardines, minutas y alimentos."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from src.services.food_service import FoodService
from src.services.garden_service import GardenService
from src.services.minute_service import MinuteService


class MinutasApp(tk.Tk):
    def __init__(
        self,
        garden_service: GardenService,
        food_service: FoodService,
        minute_service: MinuteService,
    ) -> None:
        super().__init__()
        self.garden_service = garden_service
        self.food_service = food_service
        self.minute_service = minute_service

        self.garden_ids: dict[str, int] = {}
        self.food_ids: dict[str, int] = {}
        self.minute_ids: dict[str, int] = {}

        self.title("Gestor de Minutas por Jardín")
        self.geometry("760x520")

        self._build_layout()
        self.refresh_all()

    def _build_layout(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=12, pady=12)

        self.garden_tab = ttk.Frame(notebook)
        self.food_tab = ttk.Frame(notebook)
        self.minute_tab = ttk.Frame(notebook)

        notebook.add(self.garden_tab, text="Jardines")
        notebook.add(self.food_tab, text="Alimentos")
        notebook.add(self.minute_tab, text="Minutas")

        self._build_gardens_tab()
        self._build_foods_tab()
        self._build_minutes_tab()

    def _build_gardens_tab(self) -> None:
        ttk.Label(self.garden_tab, text="Nombre del jardín:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.garden_name_var = tk.StringVar()
        ttk.Entry(self.garden_tab, textvariable=self.garden_name_var, width=36).grid(
            row=0, column=1, sticky="ew", padx=8, pady=6
        )

        ttk.Label(self.garden_tab, text="Dirección:").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        self.garden_address_var = tk.StringVar()
        ttk.Entry(self.garden_tab, textvariable=self.garden_address_var, width=36).grid(
            row=1, column=1, sticky="ew", padx=8, pady=6
        )

        ttk.Button(self.garden_tab, text="Guardar jardín", command=self._create_garden).grid(
            row=2, column=1, sticky="e", padx=8, pady=8
        )

        self.garden_listbox = tk.Listbox(self.garden_tab, height=12)
        self.garden_listbox.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
        self.garden_tab.columnconfigure(1, weight=1)
        self.garden_tab.rowconfigure(3, weight=1)

    def _build_foods_tab(self) -> None:
        ttk.Label(self.food_tab, text="Nombre del alimento:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.food_name_var = tk.StringVar()
        ttk.Entry(self.food_tab, textvariable=self.food_name_var, width=36).grid(
            row=0, column=1, sticky="ew", padx=8, pady=6
        )

        ttk.Button(self.food_tab, text="Agregar alimento", command=self._create_food).grid(
            row=1, column=1, sticky="e", padx=8, pady=8
        )

        self.food_listbox = tk.Listbox(self.food_tab, height=16)
        self.food_listbox.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
        self.food_tab.columnconfigure(1, weight=1)
        self.food_tab.rowconfigure(2, weight=1)

    def _build_minutes_tab(self) -> None:
        ttk.Label(self.minute_tab, text="Jardín:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.minute_garden_var = tk.StringVar()
        self.minute_garden_combo = ttk.Combobox(self.minute_tab, textvariable=self.minute_garden_var, state="readonly")
        self.minute_garden_combo.grid(row=0, column=1, sticky="ew", padx=8, pady=6)

        ttk.Label(self.minute_tab, text="Nombre minuta:").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        self.minute_name_var = tk.StringVar()
        ttk.Entry(self.minute_tab, textvariable=self.minute_name_var).grid(row=1, column=1, sticky="ew", padx=8, pady=6)

        ttk.Label(self.minute_tab, text="Fecha (YYYY-MM-DD):").grid(row=2, column=0, sticky="w", padx=8, pady=6)
        self.minute_date_var = tk.StringVar()
        ttk.Entry(self.minute_tab, textvariable=self.minute_date_var).grid(row=2, column=1, sticky="ew", padx=8, pady=6)

        ttk.Button(self.minute_tab, text="Crear minuta", command=self._create_minute).grid(
            row=3, column=1, sticky="e", padx=8, pady=8
        )

        separator = ttk.Separator(self.minute_tab, orient="horizontal")
        separator.grid(row=4, column=0, columnspan=2, sticky="ew", padx=8, pady=10)

        ttk.Label(self.minute_tab, text="Minuta:").grid(row=5, column=0, sticky="w", padx=8, pady=6)
        self.item_minute_var = tk.StringVar()
        self.item_minute_combo = ttk.Combobox(self.minute_tab, textvariable=self.item_minute_var, state="readonly")
        self.item_minute_combo.grid(row=5, column=1, sticky="ew", padx=8, pady=6)
        self.item_minute_combo.bind("<<ComboboxSelected>>", lambda _e: self._refresh_minute_items())

        ttk.Label(self.minute_tab, text="Alimento:").grid(row=6, column=0, sticky="w", padx=8, pady=6)
        self.item_food_var = tk.StringVar()
        self.item_food_combo = ttk.Combobox(self.minute_tab, textvariable=self.item_food_var, state="readonly")
        self.item_food_combo.grid(row=6, column=1, sticky="ew", padx=8, pady=6)

        ttk.Label(self.minute_tab, text="Cantidad (gramos):").grid(row=7, column=0, sticky="w", padx=8, pady=6)
        self.item_grams_var = tk.StringVar()
        ttk.Entry(self.minute_tab, textvariable=self.item_grams_var).grid(row=7, column=1, sticky="ew", padx=8, pady=6)

        ttk.Button(self.minute_tab, text="Agregar ingrediente", command=self._add_item).grid(
            row=8, column=1, sticky="e", padx=8, pady=8
        )

        self.minute_items_listbox = tk.Listbox(self.minute_tab, height=9)
        self.minute_items_listbox.grid(row=9, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)

        self.minute_tab.columnconfigure(1, weight=1)
        self.minute_tab.rowconfigure(9, weight=1)

    def _create_garden(self) -> None:
        try:
            self.garden_service.create_garden(
                self.garden_name_var.get(),
                self.garden_address_var.get(),
            )
            self.garden_name_var.set("")
            self.garden_address_var.set("")
            self.refresh_all()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _create_food(self) -> None:
        try:
            self.food_service.create_food(self.food_name_var.get())
            self.food_name_var.set("")
            self.refresh_all()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _create_minute(self) -> None:
        try:
            garden_id = self.garden_ids[self.minute_garden_var.get()]
            self.minute_service.create_minute(garden_id, self.minute_name_var.get(), self.minute_date_var.get())
            self.minute_name_var.set("")
            self.minute_date_var.set("")
            self.refresh_all()
        except KeyError:
            messagebox.showerror("Error", "Seleccione un jardín válido.")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _add_item(self) -> None:
        try:
            minute_id = self.minute_ids[self.item_minute_var.get()]
            food_id = self.food_ids[self.item_food_var.get()]
            grams = float(self.item_grams_var.get())
            self.minute_service.add_item(minute_id, food_id, grams)
            self.item_grams_var.set("")
            self._refresh_minute_items()
        except KeyError:
            messagebox.showerror("Error", "Seleccione una minuta y un alimento válidos.")
        except ValueError as exc:
            messagebox.showerror("Error", str(exc))

    def refresh_all(self) -> None:
        self._refresh_gardens()
        self._refresh_foods()
        self._refresh_minutes()

    def _refresh_gardens(self) -> None:
        gardens = self.garden_service.list_gardens()
        self.garden_ids = {f"{g.nombre} (#{g.id})": g.id for g in gardens}

        self.garden_listbox.delete(0, tk.END)
        for garden in gardens:
            address = f" - {garden.direccion}" if garden.direccion else ""
            self.garden_listbox.insert(tk.END, f"#{garden.id} {garden.nombre}{address}")

        garden_options = list(self.garden_ids.keys())
        self.minute_garden_combo["values"] = garden_options
        if garden_options and self.minute_garden_var.get() not in self.garden_ids:
            self.minute_garden_var.set(garden_options[0])

    def _refresh_foods(self) -> None:
        foods = self.food_service.list_foods()
        self.food_ids = {f"{f.nombre} (#{f.id})": f.id for f in foods}

        self.food_listbox.delete(0, tk.END)
        for food in foods:
            self.food_listbox.insert(tk.END, f"#{food.id} {food.nombre} ({food.unidad})")

        food_options = list(self.food_ids.keys())
        self.item_food_combo["values"] = food_options
        if food_options and self.item_food_var.get() not in self.food_ids:
            self.item_food_var.set(food_options[0])

    def _refresh_minutes(self) -> None:
        minutes = self.minute_service.list_minutes()
        self.minute_ids = {f"{m.nombre} (#{m.id})": m.id for m in minutes}

        minute_options = list(self.minute_ids.keys())
        self.item_minute_combo["values"] = minute_options
        if minute_options and self.item_minute_var.get() not in self.minute_ids:
            self.item_minute_var.set(minute_options[0])
        self._refresh_minute_items()

    def _refresh_minute_items(self) -> None:
        self.minute_items_listbox.delete(0, tk.END)
        selected = self.item_minute_var.get()
        if selected not in self.minute_ids:
            return

        minute_id = self.minute_ids[selected]
        details = self.minute_service.list_minute_items_detail(minute_id)
        for item in details:
            self.minute_items_listbox.insert(
                tk.END,
                f"#{item['id']} {item['alimento']}: {item['cantidad_gramos']} g",
            )
