"""Exercise the real snapshot and renderer, with exports isolated in /tmp."""

import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PathCollection
from PIL import Image

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))


class TransportExtensionsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        args = ["01_transport_extensions.py", "--output-dir", cls.temp.name]
        # Supply CLI arguments only. No map, data, renderer or output mocks.
        with patch.object(sys, "argv", args):
            cls.result = runpy.run_path(str(SCRIPTS / args[0]), run_name="__main__")
        cls.fig = cls.result["fig"]
        cls.addClassCleanup(plt.close, cls.fig)

    def test_default_exports_reach_project_pitch_from_another_working_directory(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as temp:
            root = Path(temp)
            scripts = root / "production/scripts"
            scripts.mkdir(parents=True)
            for name in ("01_transport_extensions.py", "export_paths.py"):
                shutil.copyfile(SCRIPTS / name, scripts / name)
            result = subprocess.run(
                [sys.executable, str(scripts / "01_transport_extensions.py"),
                 "--network-data", str(SCRIPTS.parent / "web/public/data/rail-network.json")],
                cwd="/tmp", capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((root / "production/pitch").exists())
            with Image.open(root / "pitch/png/01_reseau_transport_extens.png") as image:
                self.assertEqual(image.size, (5400, 3450))
            self.assertTrue((root / "pitch/PDF/01_reseau_transport_extens.pdf").read_bytes().startswith(b"%PDF-"))

    def test_real_plate_shows_web_totals(self):
        texts = {text.get_text() for text in self.fig.texts}
        self.assertIn("15", texts)
        self.assertIn("125", texts)
        self.assertIn("118 km", texts)
        self.assertEqual(self.result["data"]["summary"],
                         {"lines": 15, "stations": 125, "kilometres": 118})

    def test_openings_preserve_t14_m11_and_ter_rules(self):
        data = self.result["data"]
        openings = {opening["line"] for period in data["periods"] for opening in period["openings"]}
        self.assertEqual(len(openings), 15)
        self.assertNotIn("T14", openings)
        self.assertNotIn("TER", openings)
        self.assertIn("M11", openings)
        tracks = [track["name"] for period in data["periods"] for track in period["tracks"]]
        self.assertFalse(any(name.startswith("M11 ") for name in tracks))
        self.assertTrue(any(point["line"] == "M11" for period in data["periods"] for point in period["stations"]))
        texts = "\n".join(text.get_text() for text in self.fig.texts)
        self.assertIn("Le T14, renommé en 2025", texts)
        self.assertIn("métro 11 sont présents dans la source, mais non datés", texts)
        self.assertIn("ils sont exclus de cette carte et du total", texts)

    def test_map_preserves_window_station_symbols_and_annotation_positions(self):
        ax = self.fig.axes[0]
        self.assertEqual(ax.get_xlim(), (0, 73))
        self.assertEqual(ax.get_ylim(), (0, 60))
        stations = [collection for collection in ax.collections if isinstance(collection, PathCollection)]
        self.assertEqual([len(collection.get_offsets()) for collection in stations], [18, 33, 74])
        self.assertEqual([len(collection.get_paths()[0].vertices) for collection in stations], [26, 5, 5])
        data = self.result["data"]
        self.assertEqual([period["color"] for period in data["periods"]],
                         ["#009E73", "#0072B2", "#D55E00"])
        for point in data["labels"] + data["termini"] + data["departmentLabels"]:
            self.assertTrue(any(text.get_text() == point["name"] and text.get_position() == (point["x"], -point["y"])
                                for text in ax.texts), point["name"])

    def test_real_png_resolution_and_pdf(self):
        png = Path(self.temp.name) / "01_reseau_transport_extens.png"
        pdf = Path(self.temp.name) / "01_reseau_transport_extens.pdf"
        with Image.open(png) as image:
            self.assertEqual(image.size, (5400, 3450))
            for dpi in image.info["dpi"]:
                self.assertAlmostEqual(dpi, 300, delta=.01)
        content = pdf.read_bytes()
        self.assertTrue(content.startswith(b"%PDF-"))
        self.assertTrue(content.rstrip().endswith(b"%%EOF"))


if __name__ == "__main__":
    unittest.main()
