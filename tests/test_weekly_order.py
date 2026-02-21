from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import db
import models


class WeeklyOrderUnionTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        db.DATA_DIR = Path(self._tmpdir.name)
        db.DB_PATH = db.DATA_DIR / "test_minutas.db"
        db.init_db()

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_includes_food_present_in_only_one_selected_minuta(self) -> None:
        arroz_id = models.create_alimento("Arroz")
        ahuyama_id = models.create_alimento("Ahuyama")

        m1_id = models.create_minuta("M1")
        m2_id = models.create_minuta("M2")
        m3_id = models.create_minuta("M3")

        models.add_or_update_item(m1_id, arroz_id, 50, 70)
        models.add_or_update_item(m2_id, arroz_id, 25, 30)
        models.add_or_update_item(m1_id, ahuyama_id, 100, 120)

        resumen = models.calculate_weekly_order([m1_id, m2_id, m3_id], 10, 5)
        by_name = {row["alimento_nombre"]: row for row in resumen}

        self.assertIn("Ahuyama", by_name)
        self.assertEqual(by_name["Ahuyama"]["suma_gramos_g1"], 100)
        self.assertEqual(by_name["Ahuyama"]["suma_gramos_g2"], 120)
        self.assertEqual(by_name["Ahuyama"]["total_g1"], 1000)
        self.assertEqual(by_name["Ahuyama"]["total_g2"], 600)
        self.assertEqual(by_name["Ahuyama"]["total_general"], 1600)

        self.assertIn("Arroz", by_name)
        self.assertEqual(by_name["Arroz"]["suma_gramos_g1"], 75)
        self.assertEqual(by_name["Arroz"]["suma_gramos_g2"], 100)

    def test_results_are_sorted_and_recalculate_totals_by_children(self) -> None:
        frijol_id = models.create_alimento("Frijol")
        arroz_id = models.create_alimento("Arroz")

        m1_id = models.create_minuta("M1")
        m2_id = models.create_minuta("M2")

        models.add_or_update_item(m1_id, frijol_id, 20, 10)
        models.add_or_update_item(m2_id, arroz_id, 30, 5)

        resumen_1 = models.calculate_weekly_order([m1_id, m2_id], 2, 3)
        nombres = [row["alimento_nombre"] for row in resumen_1]
        self.assertEqual(nombres, ["Arroz", "Frijol"])

        by_name_1 = {row["alimento_nombre"]: row for row in resumen_1}
        self.assertEqual(by_name_1["Arroz"]["total_general"], (30 * 2) + (5 * 3))
        self.assertEqual(by_name_1["Frijol"]["total_general"], (20 * 2) + (10 * 3))

        resumen_2 = models.calculate_weekly_order([m1_id, m2_id], 4, 0)
        by_name_2 = {row["alimento_nombre"]: row for row in resumen_2}
        self.assertEqual(by_name_2["Arroz"]["total_general"], 30 * 4)
        self.assertEqual(by_name_2["Frijol"]["total_general"], 20 * 4)


if __name__ == "__main__":
    unittest.main()
