from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

import excel_minutas
import models


class MinutaEditorWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, minuta_id: int):
        super().__init__(master)
        self.minuta_id = minuta_id
        self.title("Editor de minuta")
        self.geometry("760x520")

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
        ttk.Button(top, text="Eliminar minuta", command=self.delete_current_minuta).pack(side="left", padx=(8, 0))

        add_frame = ttk.LabelFrame(root, text="Agregar / actualizar alimento", padding=8)
        add_frame.pack(fill="x", pady=(10, 8))

        ttk.Label(add_frame, text="Alimento:").grid(row=0, column=0, sticky="w")
        self.alimento_var = tk.StringVar()
        self.combo = ttk.Combobox(
            add_frame,
            textvariable=self.alimento_var,
            values=[a["nombre"] for a in self._alimentos],
            width=30,
        )
        self.combo.grid(row=0, column=1, sticky="we", padx=(6, 8))
        ttk.Button(add_frame, text="Nuevo alimento", command=self.add_new_alimento).grid(row=0, column=2)

        ttk.Label(add_frame, text="Gramos 1-2 años:").grid(row=0, column=3, sticky="w")
        self.gramos_1_2_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.gramos_1_2_var, width=10).grid(row=0, column=4, padx=(6, 8))

        ttk.Label(add_frame, text="Gramos 3-5 años:").grid(row=0, column=5, sticky="w")
        self.gramos_3_5_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.gramos_3_5_var, width=10).grid(row=0, column=6, padx=(6, 8))

        ttk.Button(add_frame, text="Agregar/Actualizar", command=self.add_item).grid(row=0, column=7)
        add_frame.grid_columnconfigure(1, weight=1)

        self.tree = ttk.Treeview(root, columns=("alimento", "g12", "g35"), show="headings", height=12)
        self.tree.heading("alimento", text="Alimento")
        self.tree.heading("g12", text="Gramos 1-2")
        self.tree.heading("g35", text="Gramos 3-5")
        self.tree.column("alimento", width=390)
        self.tree.column("g12", width=120, anchor="e")
        self.tree.column("g35", width=120, anchor="e")
        self.tree.pack(fill="both", expand=True)

        actions = ttk.Frame(root)
        actions.pack(fill="x", pady=(8, 0))
        ttk.Button(actions, text="Editar gramos", command=self.edit_gramos).pack(side="left")
        ttk.Button(actions, text="Quitar alimento", command=self.remove_item).pack(side="left", padx=(8, 0))
        ttk.Button(actions, text="Eliminar del catálogo", command=self.remove_alimento_catalogo).pack(side="left", padx=(8, 0))

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


    def delete_current_minuta(self) -> None:
        minuta = models.get_minuta(self.minuta_id)
        if not minuta:
            messagebox.showwarning("Atención", "La minuta ya no existe.", parent=self)
            self.destroy()
            return

        if not messagebox.askyesno(
            "Confirmar",
            f"¿Eliminar la minuta '{minuta['nombre']}'?",
            parent=self,
        ):
            return

        try:
            models.delete_minuta(self.minuta_id)
            messagebox.showinfo("Eliminada", "La minuta fue eliminada.", parent=self)
            self.destroy()
        except Exception:
            messagebox.showerror("Error", "No fue posible eliminar la minuta.", parent=self)

    def refresh_items(self) -> None:
        self._alimentos = models.list_alimentos()
        self.combo["values"] = [a["nombre"] for a in self._alimentos]

        self._items = models.list_minuta_items(self.minuta_id)
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in self._items:
            self.tree.insert(
                "",
                "end",
                iid=str(row["id"]),
                values=(row["alimento_nombre"], row["gramos_1_2"], row["gramos_3_5"]),
            )

    def add_item(self) -> None:
        selected_name = models.normalize_name(self.alimento_var.get())
        alimento = next((a for a in self._alimentos if a["nombre"].lower() == selected_name.lower()), None)
        if not alimento:
            messagebox.showerror("Validación", "Selecciona un alimento válido del catálogo.", parent=self)
            return
        try:
            gramos_1_2 = self._parse_gramos(self.gramos_1_2_var.get())
            gramos_3_5 = self._parse_gramos(self.gramos_3_5_var.get())
            models.add_or_update_item(self.minuta_id, alimento["id"], gramos_1_2, gramos_3_5)
            self.gramos_1_2_var.set("")
            self.gramos_3_5_var.set("")
            self.refresh_items()
        except ValueError:
            messagebox.showerror(
                "Validación",
                "Los gramos de ambos grupos deben ser números mayores a 0.",
                parent=self,
            )
        except Exception:
            messagebox.showerror("Error", "No fue posible agregar el alimento.", parent=self)

    def add_new_alimento(self) -> None:
        nombre = simpledialog.askstring("Nuevo alimento", "Nombre del nuevo alimento:", parent=self)
        if nombre is None:
            return
        try:
            models.create_alimento(nombre)
            self.refresh_items()
            self.alimento_var.set(models.normalize_name(nombre))
            self.combo.focus_set()
        except ValueError as exc:
            messagebox.showerror("Validación", str(exc), parent=self)
        except Exception:
            messagebox.showerror("Error", "No fue posible crear el alimento.", parent=self)

    def _selected_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Selecciona un alimento.", parent=self)
            return None
        item_id = int(selected[0])
        return next((x for x in self._items if x["id"] == item_id), None)

    def edit_gramos(self) -> None:
        item = self._selected_item()
        if not item:
            return
        nuevo_1_2 = simpledialog.askstring(
            "Editar gramos 1-2 años",
            "Nueva cantidad en gramos (1-2 años):",
            initialvalue=str(item["gramos_1_2"]),
            parent=self,
        )
        if nuevo_1_2 is None:
            return

        nuevo_3_5 = simpledialog.askstring(
            "Editar gramos 3-5 años",
            "Nueva cantidad en gramos (3-5 años):",
            initialvalue=str(item["gramos_3_5"]),
            parent=self,
        )
        if nuevo_3_5 is None:
            return

        try:
            gramos_1_2 = self._parse_gramos(nuevo_1_2)
            gramos_3_5 = self._parse_gramos(nuevo_3_5)
            models.update_item_gramos(item["id"], gramos_1_2, gramos_3_5)
            self.refresh_items()
        except ValueError:
            messagebox.showerror(
                "Validación",
                "Los gramos de ambos grupos deben ser números mayores a 0.",
                parent=self,
            )
        except Exception:
            messagebox.showerror("Error", "No fue posible actualizar gramos.", parent=self)


    def remove_alimento_catalogo(self) -> None:
        item = self._selected_item()
        if not item:
            return

        if not messagebox.askyesno(
            "Confirmar",
            f"¿Eliminar '{item['alimento_nombre']}' del catálogo? También se quitará de todas las minutas.",
            parent=self,
        ):
            return

        try:
            models.delete_alimento(item["alimento_id"])
            self.refresh_items()
        except Exception:
            messagebox.showerror("Error", "No fue posible eliminar el alimento del catálogo.", parent=self)

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
            messagebox.showerror("Error", "No fue posible quitar el alimento.", parent=self)


class MinutasWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, on_change=None):
        super().__init__(master)
        self.title("Gestión de minutas")
        self.geometry("700x470")
        self.on_change = on_change

        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)

        top = ttk.Frame(root)
        top.pack(fill="x", pady=(0, 8))
        ttk.Button(top, text="Nueva minuta", command=self.nueva_minuta).pack(side="left")
        ttk.Button(top, text="Abrir minuta", command=self.abrir_minuta).pack(side="left", padx=(8, 0))
        ttk.Button(top, text="Eliminar minuta", command=self.eliminar_minuta).pack(side="left", padx=(8, 0))
        ttk.Button(top, text="Descargar plantilla Excel", command=self.descargar_plantilla).pack(side="left", padx=(8, 0))
        ttk.Button(top, text="Importar Excel", command=self.importar_excel).pack(side="left", padx=(8, 0))

        self.counter_var = tk.StringVar()
        ttk.Label(top, textvariable=self.counter_var).pack(side="right")

        self.tree = ttk.Treeview(root, columns=("nombre", "fecha"), show="headings")
        self.tree.heading("nombre", text="Minuta")
        self.tree.heading("fecha", text="Fecha creación")
        self.tree.column("nombre", width=420)
        self.tree.column("fecha", width=180)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda _e: self.abrir_minuta())

        self._minutas = []
        self.refresh()

    def refresh(self) -> None:
        self._minutas = models.list_minutas()
        for row in self.tree.get_children():
            self.tree.delete(row)
        for row in self._minutas:
            self.tree.insert("", "end", iid=str(row["id"]), values=(row["nombre"], row["fecha_creacion"]))
        self.counter_var.set(f"Minutas: {len(self._minutas)}/{models.MAX_MINUTAS}")
        if self.on_change:
            self.on_change()

    def nueva_minuta(self) -> None:
        nombre = simpledialog.askstring("Nueva minuta", "Nombre de la minuta:", parent=self)
        if nombre is None:
            return
        try:
            minuta_id = models.create_minuta(nombre)
            self.refresh()
            MinutaEditorWindow(self, minuta_id)
        except ValueError as exc:
            messagebox.showerror("Validación", str(exc), parent=self)
        except Exception:
            messagebox.showerror("Error", "No fue posible crear la minuta.", parent=self)

    def _selected_minuta_id(self) -> int | None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Selecciona una minuta.", parent=self)
            return None
        return int(selected[0])

    def abrir_minuta(self) -> None:
        minuta_id = self._selected_minuta_id()
        if minuta_id is None:
            return
        MinutaEditorWindow(self, minuta_id)

    def eliminar_minuta(self) -> None:
        minuta_id = self._selected_minuta_id()
        if minuta_id is None:
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar la minuta seleccionada?", parent=self):
            return
        try:
            models.delete_minuta(minuta_id)
            self.refresh()
        except Exception:
            messagebox.showerror("Error", "No fue posible eliminar la minuta.", parent=self)

    def descargar_plantilla(self) -> None:
        file_path = filedialog.asksaveasfilename(
            parent=self,
            title="Guardar plantilla",
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            initialfile="plantilla_minutas.xlsx",
        )
        if not file_path:
            return
        try:
            excel_minutas.export_template(file_path)
            messagebox.showinfo("Plantilla creada", f"Plantilla guardada en:\n{file_path}", parent=self)
        except RuntimeError as exc:
            messagebox.showerror("Dependencia faltante", str(exc), parent=self)
        except Exception:
            messagebox.showerror("Error", "No fue posible generar la plantilla Excel.", parent=self)

    def importar_excel(self) -> None:
        file_path = filedialog.askopenfilename(
            parent=self,
            title="Seleccionar archivo Excel",
            filetypes=[("Excel", "*.xlsx")],
        )
        if not file_path:
            return
        try:
            summary = excel_minutas.import_minutas(file_path)
            self.refresh()
            message = (
                f"Filas leídas no vacías: {summary.rows_processed}\n"
                f"Filas importadas: {summary.rows_imported}\n"
                f"Minutas creadas: {summary.minutas_created}\n"
                f"Filas actualizadas en minutas existentes: {summary.minutas_updated}\n"
                f"Alimentos detectados: {summary.foods_detected}\n"
                f"Alimentos cargados/actualizados: {summary.items_upserted}"
            )
            if summary.empty_food_rows:
                message += f"\n\nFilas con alimento vacío ignoradas: {summary.empty_food_rows}"
            if summary.unknown_foods:
                message += (
                    f"\n\nFilas con alimento no encontrado: {summary.unknown_food_rows}"
                    "\nAlimentos no encontrados en catálogo:\n- " + "\n- ".join(summary.unknown_foods)
                )
            messagebox.showinfo("Importación completada", message, parent=self)
        except RuntimeError as exc:
            messagebox.showerror("Dependencia faltante", str(exc), parent=self)
        except ValueError as exc:
            messagebox.showerror("Validación", str(exc), parent=self)
        except Exception:
            messagebox.showerror("Error", "No fue posible importar el archivo Excel.", parent=self)
