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
    def test_exports_departmental_values_from_real_workbook(self):
        with tempfile.TemporaryDirectory() as temp:
            data = export_data(Path(temp) / "export.json")
        expected = {
            "75": [1980.2, 38.7, 28022, 5220],
            "77": [517.2, 16.1, 6121, 2130],
            "78": [531.0, 6.3, 6878, 1190],
            "91": [498.8, 9.8, 5827, 1350],
            "92": [1169.2, 16.9, 8960, 1680],
            "93": [677.4, 9.2, 9542, 2560],
            "94": [554.9, 7.0, 7675, 1370],
            "95": [419.5, 10.5, 6193, 1040],
        }
        actual = {
            row["code"]: [row["indicators"][key] for key in
                          ("salarie", "interim", "creations", "defaillances")]
            for row in data["departments"]
        }
        self.assertEqual(actual, expected)
        self.assertEqual([metric["period"] for metric in data["metrics"]], [
            "2e trimestre 2025", "2e trimestre 2025", "3e trimestre 2025",
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
                             if item.get("name") == "Sheet3")
                relation_id = sheet.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
                relation = next(item for item in relations if item.get("Id") == relation_id)
                old_path = "xl/" + relation.get("Target")
                relation.set("Target", "worksheets/renamed-departments.xml")
                xml = ET.fromstring(source.read(old_path))
                for row in xml.findall("m:sheetData/m:row", ns):
                    for cell in list(row):
                        if cell.get("r") == "B4":
                            for child in list(cell):
                                cell.remove(child)
                            cell.attrib.pop("t", None)
                        elif cell.get("r") == "H5":
                            cell.find("m:v", ns).text = "0"
                        elif cell.get("r") == "H6":
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
            self.assertIsNone(departments["78"]["creations"])
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
        snapshot = json.loads((PRODUCTION / "web/public/data/employment-centers-departments.json").read_text(encoding="utf-8"))
        self.assertEqual(data, snapshot)


if __name__ == "__main__":
    unittest.main()
