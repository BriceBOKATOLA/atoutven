import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
OUTPUTS = {
    "01_transport_extensions.py": ("01_reseau", "01_reseau_transport_extens"),
    "02_employment_growth.py": ("02_emploi", "02_emploi_progress"),
    "03_employment_comparison.py": ("03_avant_apres", "03_avant_apres"),
    "04_jobseekers.py": ("04_demandeurs", "04_demandeurs_emplois"),
    "05_transport_networks.py": ("05_tous_reseaux", "05_tous_reseaux_2015_2025"),
    "06_employment_centers.py": ("06_poles_emploi", "06_poles_emploi_2015_2025"),
}


class GeneratePitchTest(unittest.TestCase):
    def test_generates_all_exports_and_stops_on_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            scripts = root / "scripts"
            scripts.mkdir()
            (scripts / "generate_pitch.py").write_text((SCRIPTS / "generate_pitch.py").read_text())
            for name, (_, target) in OUTPUTS.items():
                (scripts / name).write_text(
                    "from pathlib import Path\n"
                    "root = Path(__file__).resolve().parent.parent / 'pitch'\n"
                    "for ext, folder in (('png', 'png'), ('pdf', 'PDF')):\n"
                    "    dest = root / folder\n"
                    "    dest.mkdir(parents=True, exist_ok=True)\n"
                    f"    (dest / '{target}.{{}}'.format(ext)).write_text('{name}')\n"
                )
            runner = scripts / "generate_pitch.py"
            result = subprocess.run([sys.executable, str(runner)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            for name, (_, target) in OUTPUTS.items():
                for ext in ("png", "pdf"):
                    self.assertEqual((root / "pitch" / ("PDF" if ext == "pdf" else "png") / f"{target}.{ext}").read_text(), name)
            self.assertFalse((root / "out").exists())
            (scripts / "03_employment_comparison.py").write_text("raise SystemExit(7)\n")
            result = subprocess.run([sys.executable, str(runner)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("03_employment_comparison.py", result.stderr)


if __name__ == "__main__":
    unittest.main()
