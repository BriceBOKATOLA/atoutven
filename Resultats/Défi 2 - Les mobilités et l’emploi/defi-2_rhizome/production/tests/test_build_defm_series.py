"""Verify DEFM reconstruction through its CLI and actual local inputs."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PRODUCTION = Path(__file__).resolve().parents[1]
SCRIPT = PRODUCTION / "scripts/build_defm_series.py"
SOURCE = PRODUCTION / "datasets/src/mobility-employment/idf-raw-sources/defm_communes_idf.csv"
SNAPSHOT = PRODUCTION / "datasets/clean/shared/series_defm_dares.json"
GROUPS = PRODUCTION / "datasets/clean/shared/groupes_lignes.json"


class DefmSeriesTest(unittest.TestCase):
    def run_changed_source(self, transform, expected_error):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "source.csv"
            output = Path(temp) / "series.json"
            source.write_text(transform(SOURCE.read_text(encoding="utf-8-sig")), encoding="utf-8")
            output.write_text("preserved output", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--source", str(source),
                 "--output", str(output)], capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(expected_error, result.stderr)
            self.assertEqual(output.read_text(encoding="utf-8"), "preserved output")

    def test_duplicate_observation_is_rejected(self):
        self.run_changed_source(lambda text: text + text.splitlines()[1] + "\n", "Duplicate commune/year")

    def test_missing_year_observation_is_rejected(self):
        self.run_changed_source(lambda text: "\n".join(text.splitlines()[:1] + text.splitlines()[2:]), "Missing commune observations")

    def test_empty_count_is_rejected(self):
        def empty_count(text):
            lines = text.splitlines()
            fields = lines[1].split(";")
            fields[-1] = ""
            lines[1] = ";".join(fields)
            return "\n".join(lines)
        self.run_changed_source(empty_count, "Missing or invalid count")

    def test_unexpected_dimension_is_rejected(self):
        self.run_changed_source(lambda text: text.replace(";ABC;", ";A;", 1), "Unexpected dimensions")

    def test_historical_exclusion_does_not_allow_partial_year_coverage(self):
        def add_one_observation(text):
            row = text.splitlines()[1].split(";")
            row[5] = "93059"
            return text + ";".join(row) + "\n"
        self.run_changed_source(add_one_observation, "Missing commune observations")

    def test_group_errors_preserve_existing_output(self):
        for kind in ("missing", "duplicate"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temp:
                groups = json.loads(GROUPS.read_text(encoding="utf-8"))
                codes = groups["T11 (2017)"]["codes"]
                codes.append("99999" if kind == "missing" else codes[0])
                group_path = Path(temp) / "groups.json"
                group_path.write_text(json.dumps(groups), encoding="utf-8")
                output = Path(temp) / "series.json"
                output.write_text("preserved output", encoding="utf-8")
                result = subprocess.run(
                    [sys.executable, "-B", str(SCRIPT), "--groups", str(group_path),
                     "--output", str(output)], capture_output=True, text=True,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Missing communes" if kind == "missing" else "Duplicate commune", result.stderr)
                self.assertEqual(output.read_text(encoding="utf-8"), "preserved output")

    def test_local_source_reproduces_snapshot(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "series.json"
            result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--output", str(output)],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(data, json.loads(SNAPSHOT.read_text(encoding="utf-8")))
            # These groups retain historical omissions, not invented zeros.
            self.assertIn("93059", result.stderr)
            self.assertIn("91182", result.stderr)
            self.assertIn("incomplete", result.stderr)
            self.assertEqual(data["T11 (2017)"][1], 22780)
            self.assertEqual(data["T12 (2023)"][1], 24370)


if __name__ == "__main__":
    unittest.main()
