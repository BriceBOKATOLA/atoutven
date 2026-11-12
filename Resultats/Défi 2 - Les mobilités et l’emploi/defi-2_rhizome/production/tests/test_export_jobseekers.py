"""Check the public employment-zone export against the local sources."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PRODUCTION = Path(__file__).resolve().parents[1]

class JobseekersExportTest(unittest.TestCase):
    def test_jobseeker_period_and_snapshot(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "export.json"
            subprocess.run([sys.executable, str(PRODUCTION / "scripts/export-jobseekers.py"), "--output", str(output)], check=True, capture_output=True, text=True)
            data = json.loads(output.read_text())
        metric = next(m for m in data["metrics"] if m["name"] == "Demandeurs ABC")
        self.assertEqual(metric["scope"], "4e trimestre ; rupture 2025")
        snapshot = json.loads((PRODUCTION / "web/public/data/jobseekers-employment-zones.json").read_text())
        self.assertEqual(data, snapshot)

if __name__ == "__main__":
    unittest.main()
