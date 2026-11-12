import importlib.util
from pathlib import Path
import unittest
import tempfile
import copy

PRODUCTION = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("rebuild_workbook_indicators", PRODUCTION / "scripts/rebuild_workbook_indicators.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class WorkbookReconstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = module.reconstruct(PRODUCTION / "datasets/src")
        cls.workbook = PRODUCTION / "datasets/src/jobseekers/Recap_mobilites_emploi_IDF.xlsx"

    def test_reconstruct_real_zone_unemployment_and_claimants(self):
        result = self.result
        self.assertEqual(result["zones"]["1101"]["Taux de chômage localisé"]["2015"], 8.7)
        self.assertEqual(result["zones"]["1101"]["Demandeurs ABC"]["2025"], 53480)
        self.assertEqual(result["zones"]["1101"]["Emplois au lieu de travail"]["2016"], 188766.9)

    def test_all_exported_zone_cells_match_real_workbook(self):
        comparisons = module.compare(self.result, self.workbook)
        self.assertEqual(len(comparisons), 1080)
        self.assertTrue(all(row["matches"] for row in comparisons))
        self.assertEqual(len(self.result["zones"]), 15)

    def test_blank_and_missing_salary_data_are_reported(self):
        self.assertIsNone(self.result["zones"]["1103"]["Salariés privés"]["2025"])
        self.assertIsNone(self.result["zones"]["1115"]["Salariés privés"]["2025"])
        self.assertIn({"metric": "Salariés privés", "zone": "1103", "missing_communes": ["91526"]}, self.result["coverage"])
        self.assertIn({"metric": "Salariés privés", "zone": "1115", "missing_communes": ["78606"]}, self.result["coverage"])
        blank_counts = next(row["blank_sector_cells_by_year"] for row in self.result["coverage"] if "blank_sector_cells_by_year" in row)
        self.assertEqual(blank_counts["2015"], 49218)
        self.assertEqual(blank_counts["2025"], 47014)

    def test_comparison_exposes_changed_value(self):
        altered = copy.deepcopy(self.result)
        altered["zones"]["1101"]["Demandeurs ABC"]["2025"] = 0
        failures = [row for row in module.compare(altered, self.workbook) if not row["matches"]]
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0]["cell"], "O7")
        self.assertEqual(failures[0]["workbook"], 53480)

    def test_duplicate_communes_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "communes.csv"
            source.write_text("code,value\n75056,1\n75056,2\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate commune 75056"):
                module.unique_rows(source, "code")

    def test_department_workbook_has_three_sheets_and_empty_third(self):
        source = PRODUCTION / "datasets/src/employment-centers/indicateurs-departementaux-2025-2026.xlsx"
        sheets = module.read_workbook(source)
        self.assertEqual(list(sheets), ["Par département 2ème&3ème trime", "Sheet3", "Sheet2"])
        self.assertEqual(sheets["Sheet2"]["cells"], {})
        self.assertEqual(sheets["Sheet3"]["cells"]["H4"], "28022.0")
        self.assertFalse(any(sheet["formulas"] for sheet in sheets.values()))

if __name__ == "__main__":
    unittest.main()
