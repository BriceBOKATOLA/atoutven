"""Check the actual export statements with a real Matplotlib figure.

Map data and layout are excluded here; full map generation is a separate check.
"""

import ast
import tempfile
import unittest
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


class PlateResolutionTest(unittest.TestCase):
    def test_each_plate_exports_a_300_dpi_png_and_a_pdf(self):
        for script in sorted(SCRIPTS.glob("0[1-6]_*.py")):
            with self.subTest(script=script.name), tempfile.TemporaryDirectory() as temp:
                tree = ast.parse(script.read_text())
                exports = [
                    statement for statement in ast.walk(tree)
                    if isinstance(statement, ast.Expr)
                    and isinstance(statement.value, ast.Call)
                    and isinstance(statement.value.func, ast.Attribute)
                    and isinstance(statement.value.func.value, ast.Name)
                    and statement.value.func.value.id == "fig"
                    and statement.value.func.attr == "savefig"
                ]
                self.assertEqual(len(exports), 2)
                png, pdf = Path(temp) / "plate.png", Path(temp) / "plate.pdf"
                fig = plt.figure(figsize=(18, 11.5))
                try:
                    code = compile(ast.Module(body=exports, type_ignores=[]), str(script), "exec")
                    exec(code, {"fig": fig, "PNG": png, "PDF": pdf, "NIGHT": "#FFFFFF"})
                    with Image.open(png) as image:
                        self.assertEqual(image.size, (5400, 3450))
                        for dpi in image.info["dpi"]:
                            self.assertAlmostEqual(dpi, 300, delta=0.01)
                    self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"))
                finally:
                    plt.close(fig)


if __name__ == "__main__":
    unittest.main()
