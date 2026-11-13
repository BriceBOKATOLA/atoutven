import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
OUTPUTS = {
    "01_transport_extensions.py": ("01_reseau", "01_reseau_transport_extens"),
    "02_employment_growth.py": ("02_emploi", "02_emploi_progress"),
    "04_jobseekers.py": ("04_demandeurs", "04_demandeurs_emplois"),
    "05_transport_networks.py": ("05_tous_reseaux", "05_tous_reseaux_2015_2025"),
    "06_employment_centers.py": ("06_poles_emploi", "06_poles_emploi_2015_2025"),
}


class GeneratePitchTest(unittest.TestCase):
    def test_generates_all_exports_and_stops_on_failure(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as temp:
            root = Path(temp)
            scripts = root / "production" / "scripts"
            scripts.mkdir(parents=True)
            (scripts / "generate_pitch.py").write_text((SCRIPTS / "generate_pitch.py").read_text(encoding="utf-8"), encoding="utf-8")
            (scripts / "export_paths.py").write_text((SCRIPTS / "export_paths.py").read_text(encoding="utf-8"), encoding="utf-8")
            for name, (_, target) in OUTPUTS.items():
                (scripts / name).write_text(
                    "from export_paths import export_paths\n"
                    f"for dest in export_paths('{target}'):\n"
                    f"    dest.write_text('{name}', encoding='utf-8')\n",
                    encoding="utf-8",
                )
            runner = scripts / "generate_pitch.py"
            result = subprocess.run([sys.executable, str(runner)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            for name, (_, target) in OUTPUTS.items():
                for ext in ("png", "pdf"):
                    self.assertEqual((root / "pitch" / ("PDF" if ext == "pdf" else "png") / f"{target}.{ext}").read_text(encoding="utf-8"), name)
            self.assertFalse((root / "production" / "pitch").exists())
            self.assertIn("disponibles dans pitch/", result.stdout)
            for output in (root / "pitch").glob("*/*"):
                output.unlink()
            (scripts / "04_jobseekers.py").write_text("raise SystemExit(7)\n", encoding="utf-8")
            result = subprocess.run([sys.executable, str(runner)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 7)
            self.assertFalse((root / "pitch/png/05_tous_reseaux_2015_2025.png").exists())
            self.assertFalse((root / "pitch/png/06_poles_emploi_2015_2025.png").exists())
            self.assertIn("04_jobseekers.py", result.stderr)


if __name__ == "__main__":
    unittest.main()
