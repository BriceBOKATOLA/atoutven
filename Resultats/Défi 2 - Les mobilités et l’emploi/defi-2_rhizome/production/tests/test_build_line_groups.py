"""Verify spatial line groups using real geometries and retained local inputs."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import geopandas as gpd
from shapely.geometry import Point, box

PRODUCTION = Path(__file__).resolve().parents[1]
SCRIPT = PRODUCTION / "scripts/build_line_groups.py"
SNAPSHOT = PRODUCTION / "datasets/clean/shared/groupes_lignes.json"


def load_builder():
    sys.path.insert(0, str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("build_line_groups", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LineGroupsTest(unittest.TestCase):
    def test_selection_names_duplicates_and_sorting(self):
        communes = gpd.GeoDataFrame(
            {"code": ["92002", "75056", "92001"], "nom": ["Alpha", "Paris", "Old name"]},
            geometry=[box(10, 0, 20, 10), box(20, 0, 30, 10), box(0, 0, 10, 10)], crs=2154,
        )
        stations = gpd.GeoDataFrame(
            {"res_com": ["METRO 4"] * 4 + ["METRO 99"] + ["METRO 4"] * 4 + ["TRAM 1", "METRO 77"],
             "date_mise": ["2015-01-01", "2015-01-01", "2015-12-31", "2015-01-01",
                           "2015-01-01", "2014-12-31", "2026-01-01", None, "bad date", "2025-12-31", "2020-01-01"]},
            geometry=[Point(1, 1), Point(1, 1), Point(11, 1), Point(21, 1), Point(10, 1),
                      Point(1, 1), Point(1, 1), Point(1, 1), Point(1, 1), Point(1, 1), Point(50, 1)], crs=2154,
        )
        result = load_builder().reconstruct_groups(stations, communes, {"92001": "Zulu’ town\u200b"})
        self.assertEqual(result, {
            "M4 (2015)": {"line": "M4", "an": 2015, "codes": ["92001", "92002"],
                          "communes": ["Alpha", "Zulu' town"]},
            "T1 (2025)": {"line": "T1", "an": 2025, "codes": ["92001"], "communes": ["Zulu' town"]},
        })
        self.assertEqual(list(result), ["M4 (2015)", "T1 (2025)"])

    def test_local_sources_reproduce_complete_snapshot(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "groups.json"
            result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--output", str(output)],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            actual = json.loads(output.read_text(encoding="utf-8"))
            expected = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
            self.assertEqual(actual, expected)
            self.assertEqual(len(actual), 15)
            self.assertEqual(list(actual), sorted(expected))
            for group in actual.values():
                self.assertEqual(group["codes"], sorted(group["codes"]))
                self.assertEqual(group["communes"], sorted(group["communes"]))

    def test_invalid_inputs_fail_before_replacing_output(self):
        with tempfile.TemporaryDirectory() as temp:
            stations = Path(temp) / "stations.geojson"
            communes = Path(temp) / "communes.geojson"
            names = Path(temp) / "names.json"
            output = Path(temp) / "groups.json"
            gpd.GeoDataFrame(
                {"res_com": [None], "date_mise": ["2020-01-01"]},
                geometry=[Point(1, 1)], crs=2154,
            ).to_file(stations, driver="GeoJSON")
            gpd.GeoDataFrame(
                {"code": ["91001"], "nom": ["Town"]},
                geometry=[box(0, 0, 10, 10)], crs=2154,
            ).to_file(communes, driver="GeoJSON")
            names.write_text("{}", encoding="utf-8")
            output.write_text("keep existing result", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--stations", str(stations),
                 "--communes", str(communes), "--official-names", str(names), "--output", str(output)],
                capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing or invalid station line", result.stderr)
            self.assertEqual(output.read_text(encoding="utf-8"), "keep existing result")

    def test_output_cannot_replace_any_input(self):
        for option in ("--stations", "--communes", "--official-names"):
            with self.subTest(option=option), tempfile.TemporaryDirectory() as temp:
                source = Path(temp) / "source.json"
                source.write_text("preserve source", encoding="utf-8")
                result = subprocess.run(
                    [sys.executable, "-B", str(SCRIPT), option, str(source),
                     "--output", str(source.parent / "." / source.name)],
                    capture_output=True, text=True,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Output must differ from all input files", result.stderr)
                self.assertEqual(source.read_text(encoding="utf-8"), "preserve source")

    def test_output_is_required(self):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--output", result.stderr)

    def test_overlapping_communes_keep_every_match(self):
        communes = gpd.GeoDataFrame(
            {"code": ["91001", "91002"], "nom": ["Former", "Merged"]},
            geometry=[box(0, 0, 10, 10), box(0, 0, 20, 20)], crs=2154,
        )
        stations = gpd.GeoDataFrame(
            {"res_com": ["TRAM 12"], "date_mise": ["2023-01-01"]},
            geometry=[Point(1, 1)], crs=2154,
        )
        group = load_builder().reconstruct_groups(stations.to_crs(4326), communes, {})["T12 (2023)"]
        self.assertEqual(group["codes"], ["91001", "91002"])


if __name__ == "__main__":
    unittest.main()
