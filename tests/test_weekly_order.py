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


if __name__ == "__main__":
    unittest.main()
