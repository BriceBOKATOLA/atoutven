"""Exercise the exporter with the local workbook and GeoPackage."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile


PRODUCTION = Path(__file__).resolve().parents[1]
SCRIPT = PRODUCTION / "scripts/export-employment-centers.py"


def export_data(output, *arguments):
    subprocess.run(
        [sys.executable, str(SCRIPT), "--output", str(output), *map(str, arguments)],
        check=True, capture_output=True, text=True,
    )
    return json.loads(output.read_text(encoding="utf-8"))


class EmploymentCentersExportTest(unittest.TestCase):
    def test_exports_all_2026_departmental_values_from_real_workbook(self):
        with tempfile.TemporaryDirectory() as temp:
            data = export_data(Path(temp) / "export.json")
        expected = {
            "75": [1984.7, 37.0, 33800, 5220],
            "77": [517.7, 15.8, 7680, 2130],
            "78": [527.8, 5.6, 7740, 1190],
            "91": [499.3, 9.1, 6720, 1350],
            "92": [1165.8, 17.5, 9840, 1680],
            "93": [678.8, 9.0, 11560, 2560],
            "94": [552.6, 7.0, 9090, 1370],
            "95": [422.7, 10.8, 7390, 1040],
        }
        actual = {
            row["code"]: [row["indicators"][key] for key in
                          ("salarie", "interim", "creations", "defaillances")]
            for row in data["departments"]
        }
        self.assertEqual(actual, expected)
        self.assertEqual([metric["period"] for metric in data["metrics"]], [
            "2e trimestre 2026", "2e trimestre 2026", "3e trimestre 2026",
            "Août 2026 — cumul des 12 derniers mois",
        ])
        self.assertEqual([metric["scale"] for metric in data["metrics"]], [1000, 1000, 1, 1])


    def test_resolves_named_tab_and_preserves_missing_values_and_zero_on_reload(self):
        # Modify only a temporary copy of the real workbook. The source file is unchanged.
        workbook = next((PRODUCTION / "datasets/src/employment-centers").glob("*.xlsx"))
        ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        with tempfile.TemporaryDirectory() as temp:
            modified = Path(temp) / workbook.name
            with zipfile.ZipFile(workbook) as source, zipfile.ZipFile(modified, "w") as target:
                relations = ET.fromstring(source.read("xl/_rels/workbook.xml.rels"))
                sheets = ET.fromstring(source.read("xl/workbook.xml"))
                sheet = next(item for item in sheets.findall("m:sheets/m:sheet", ns)
                             if item.get("name") == "Par département 2ème&3ème trime")
                relation_id = sheet.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
                relation = next(item for item in relations if item.get("Id") == relation_id)
                old_path = "xl/" + relation.get("Target")
                relation.set("Target", "worksheets/renamed-departments.xml")
                xml = ET.fromstring(source.read(old_path))
                for row in xml.findall("m:sheetData/m:row", ns):
                    for cell in list(row):
                        if cell.get("r") == "B5":
                            for child in list(cell):
                                cell.remove(child)
                            cell.attrib.pop("t", None)
                        elif cell.get("r") == "H6":
                            cell.find("m:v", ns).text = "0"
                        elif cell.get("r") == "I7":
                            row.remove(cell)
                for item in source.infolist():
                    if item.filename == old_path:
                        target.writestr("xl/worksheets/renamed-departments.xml", ET.tostring(xml))
                    elif item.filename == "xl/_rels/workbook.xml.rels":
                        target.writestr(item, ET.tostring(relations))
                    else:
                        target.writestr(item, source.read(item.filename))
            output = Path(temp) / "export.json"
            first = export_data(output, "--workbook", modified)
            second = export_data(output, "--workbook", modified)
            self.assertEqual(first, second)
            departments = {row["code"]: row["indicators"] for row in second["departments"]}
            self.assertIsNone(departments["75"]["salarie"])
            self.assertEqual(departments["77"]["creations"], 0)
            self.assertIsNone(departments["78"]["defaillances"])
            self.assertEqual(departments["95"]["defaillances"], 1040)

    def test_jobseeker_comparison_describes_quarterly_averages(self):
        with tempfile.TemporaryDirectory() as temp:
            data = export_data(Path(temp) / "export.json")
        row = next(row for row in data["comparison"]["rows"] if row["label"].startswith("Demandeurs"))
        self.assertEqual(row["years"], "moyennes du 4e trimestre 2016 et 2024")
        self.assertEqual((row["start"], row["end"]), (972835, 1015850))

    def test_regenerated_data_matches_web_snapshot(self):
        with tempfile.TemporaryDirectory() as temp:
            data = export_data(Path(temp) / "export.json")
        snapshot = json.loads((PRODUCTION / "web/public/data/employment-centers-departments.json").read_text())
        self.assertEqual(data, snapshot)


if __name__ == "__main__":
    unittest.main()
