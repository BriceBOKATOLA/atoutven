import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parents[1]
SCRIPT = PRODUCTION / 'scripts/build_defm.py'
SOURCE = PRODUCTION / 'datasets/src/mobility-employment/idf-raw-sources/defm_communes_idf.csv'
EXPECTED = PRODUCTION / 'datasets/src/defm_2016_2024.txt'


class BuildDefmTest(unittest.TestCase):
    def test_local_source_reproduces_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'defm.txt'
            subprocess.run([sys.executable, str(SCRIPT), '--source', str(SOURCE),
                            '--output', str(output)], check=True)
            self.assertEqual(output.read_bytes(), EXPECTED.read_bytes())

    def test_threshold_applies_to_2016_only(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source.csv'
            output = Path(directory) / 'out.txt'
            source.write_text(
                'date;code_commune;type_de_donnees;categorie;sexe;tranche_d_age;nombre_de_demandeurs_d_emploi\n'
                '2016-T4;95480;Brutes;ABC;Total;Total;305\n'
                '2024-T4;95480;Brutes;ABC;Total;Total;275\n'
                '2016-T4;77001;Brutes;ABC;Total;Total;295\n'
                '2024-T4;77001;Brutes;ABC;Total;Total;500\n', encoding='utf-8')
            subprocess.run([sys.executable, str(SCRIPT), '--source', str(source),
                            '--output', str(output)], check=True)
            self.assertEqual(output.read_text(encoding="utf-8"), '95480:305:275\n')

    def test_duplicate_matching_record_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source.csv'
            fields = ['date', 'code_commune', 'type_de_donnees', 'categorie',
                      'sexe', 'tranche_d_age', 'nombre_de_demandeurs_d_emploi']
            row = dict(zip(fields, ['2016-T4', '77014', 'Brutes', 'ABC', 'Total', 'Total', '1000']))
            with source.open('w', encoding='utf-8', newline='') as stream:
                writer = csv.DictWriter(stream, fields, delimiter=';')
                writer.writeheader()
                writer.writerows([row, row])
            result = subprocess.run([sys.executable, str(SCRIPT), '--source', str(source),
                                     '--output', str(Path(directory) / 'out')], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b'duplicate', result.stderr.lower())

    def test_missing_2024_does_not_replace_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source.csv'
            output = Path(directory) / 'out.txt'
            source.write_text(
                'date;code_commune;type_de_donnees;categorie;sexe;tranche_d_age;nombre_de_demandeurs_d_emploi\n'
                '2016-T4;77014;Brutes;ABC;Total;Total;1000\n', encoding='utf-8')
            output.write_text('original', encoding='utf-8')
            result = subprocess.run([sys.executable, str(SCRIPT), '--source', str(source),
                                     '--output', str(output)], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b'Missing 2024', result.stderr)
            self.assertEqual(output.read_text(encoding="utf-8"), 'original')


if __name__ == '__main__':
    unittest.main()
