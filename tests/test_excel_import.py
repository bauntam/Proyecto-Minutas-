from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import db
import excel_minutas
import models
import seed


class ExcelImportTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        db.DATA_DIR = Path(self._tmpdir.name)
        db.DB_PATH = db.DATA_DIR / "test_minutas.db"
        db.init_db()
        seed.seed_if_empty()

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def _build_workbook(self, rows: list[list[object]]) -> Path:
        try:
            from openpyxl import Workbook
        except ModuleNotFoundError as exc:
            self.skipTest(f"openpyxl no disponible: {exc}")

        output = Path(self._tmpdir.name) / "minutas_test.xlsx"
        wb = Workbook()
        ws = wb.active
        ws.title = "Minutas"
        ws.append(excel_minutas.HEADERS)
        for row in rows:
            ws.append(row)
        wb.save(output)
        return output

    def test_seed_contains_complete_required_food_catalog(self) -> None:
        expected = {models.normalize_food_name(name) for name in seed.INITIAL_FOODS}
        in_db = {models.normalize_food_name(row["nombre"]) for row in models.list_alimentos()}

        self.assertEqual(len(expected), len(seed.INITIAL_FOODS))
        self.assertEqual(expected, in_db)

    def test_import_detects_accents_and_spacing_variants(self) -> None:
        xlsx = self._build_workbook(
            [
                ["Minuta 1", "  Pimenton  ", 10, 15],
                ["Minuta 1", "Limon", 5, 5],
                ["Minuta 1", "Pasta  spaguetti", 20, 30],
                ["Minuta 1", "Banano comun, maduro", 8, 9],
            ]
        )

        summary = excel_minutas.import_minutas(xlsx)

        self.assertEqual(summary.rows_processed, 4)
        self.assertEqual(summary.rows_imported, 4)
        self.assertEqual(summary.items_upserted, 4)
        self.assertEqual(summary.foods_detected, 4)
        self.assertEqual(summary.unknown_foods, [])

        minuta_id = models.list_minutas()[0]["id"]
        imported_items = {row["alimento_nombre"] for row in models.list_minuta_items(minuta_id)}
        self.assertIn("Pimentón", imported_items)
        self.assertIn("Limón", imported_items)
        self.assertIn("Pasta spaguetti", imported_items)
        self.assertIn("Banano común, maduro", imported_items)

    def test_import_reports_unknown_foods_and_keeps_valid_rows(self) -> None:
        xlsx = self._build_workbook(
            [
                ["Minuta X", "Arroz", 10, 10],
                ["Minuta X", "No existe", 5, 5],
                ["Minuta X", "", 7, 7],
                ["Minuta X", "No existe", 8, 8],
            ]
        )

        summary = excel_minutas.import_minutas(xlsx)

        self.assertEqual(summary.rows_processed, 4)
        self.assertEqual(summary.rows_imported, 1)
        self.assertEqual(summary.unknown_food_rows, 2)
        self.assertEqual(summary.empty_food_rows, 1)
        self.assertEqual(summary.unknown_foods, ["No existe"])

    def test_import_fails_with_missing_headers(self) -> None:
        try:
            from openpyxl import Workbook
        except ModuleNotFoundError as exc:
            self.skipTest(f"openpyxl no disponible: {exc}")

        output = Path(self._tmpdir.name) / "headers_invalid.xlsx"
        wb = Workbook()
        ws = wb.active
        ws.title = "Minutas"
        ws.append(["minuta", "alimento", "gramos_grupo_1"])
        ws.append(["M", "Arroz", 10])
        wb.save(output)

        with self.assertRaisesRegex(ValueError, "Faltan: gramos_grupo_2"):
            excel_minutas.import_minutas(output)


if __name__ == "__main__":
    unittest.main()
