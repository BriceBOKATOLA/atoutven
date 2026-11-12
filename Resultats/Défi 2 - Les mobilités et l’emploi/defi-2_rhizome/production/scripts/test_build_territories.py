import unittest
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from build_territories import (
    SOURCE_ROOT, aggregate_dpae, aggregate_offres, build_dataset, read_xlsx,
)


class ReproductionTests(unittest.TestCase):
    def test_cli_reproduces_production_snapshot_and_source_hashes(self):
        production = Path(__file__).resolve().parents[1]
        snapshot = production / 'datasets/src/jobseekers/territoires.json'
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'generated'
            subprocess.run(
                [sys.executable, '-B', str(production / 'scripts/build_territories.py'),
                 '--output-dir', str(output)],
                cwd=temporary, check=True, capture_output=True, text=True,
            )
            self.assertEqual((output / 'territoires.json').read_bytes(),
                             snapshot.read_bytes())
            coverage = json.loads((output / 'couverture.json').read_text(encoding="utf-8"))
            expected_sources = [
                'jobseekers/territories_sources/map-data/zones_emploi.geojson',
                'jobseekers/communes.geojson',
                'mobility-employment/idf-raw-sources/dpae-par-departement-x-grand-secteur.xlsx',
                'mobility-employment/idf-raw-sources/dares_offres_collectees_satisfaites_france_travail_brutes_trim.xlsx',
            ]
            self.assertEqual(coverage['sources_sha256'], {
                name: hashlib.sha256((SOURCE_ROOT / name).read_bytes()).hexdigest()
                for name in expected_sources
            })
            self.assertEqual(list(output.glob('*.tmp')), [])


    def test_missing_sources_preserve_existing_outputs(self):
        production = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / 'output'
            output.mkdir()
            for filename in ['territoires.json', 'couverture.json']:
                (output / filename).write_bytes(b'existing output')
            result = subprocess.run(
                [sys.executable, '-B', str(production / 'scripts/build_territories.py'),
                 '--source-root', str(root / 'missing-sources'),
                 '--output-dir', str(output)],
                cwd=temporary, capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('FileNotFoundError', result.stderr)
            for filename in ['territoires.json', 'couverture.json']:
                self.assertEqual((output / filename).read_bytes(), b'existing output')
            self.assertEqual(list(output.glob('*.tmp')), [])


class RealSourcesTests(unittest.TestCase):
    def test_geographical_contract(self):
        data, coverage = build_dataset()
        self.assertEqual(set(data), {"zones", "departements"})
        self.assertEqual(len(data["zones"]), 15)
        self.assertEqual(len(data["departements"]), 8)
        for zone in data["zones"]:
            self.assertIsInstance(zone["code"], str)
            self.assertEqual(set(zone["indicateurs"]),
                             {"chomage", "demandeurs", "emplois", "actifs_occupes",
                              "emplois_rp", "postes_flores"})
        for dep in data["departements"]:
            self.assertEqual(dep["geometry"]["type"], "GeometryCollection")
            self.assertTrue(dep["geometry"]["geometries"])
            self.assertEqual(set(dep["indicateurs"]), {"dpae", "offres"})

    def test_complete_annual_department_totals(self):
        data, coverage = build_dataset()
        deps = {dep["code"]: dep for dep in data["departements"]}
        self.assertEqual(deps["75"]["indicateurs"]["dpae"]["2025"], 3564964)
        self.assertEqual(sum(d["indicateurs"]["dpae"]["2025"] for d in deps.values()),
                         8514056)
        for dep in deps.values():
            self.assertNotIn("2026", dep["indicateurs"]["dpae"])
            self.assertNotIn("2026", dep["indicateurs"]["offres"])
        self.assertEqual(set(deps["75"]["indicateurs"]["dpae"]),
                         {str(year) for year in range(2015, 2026)})

    def test_zone_values_and_missing_coverage(self):
        data, coverage = build_dataset()
        zones = {zone["code"]: zone for zone in data["zones"]}
        self.assertEqual(zones["1109"]["indicateurs"]["emplois"]["2025"], 3558039)
        self.assertEqual(zones["1109"]["indicateurs"]["actifs_occupes"],
                         {"2016": 2968980, "2021": 3050718.9})
        self.assertEqual(set(zones["1109"]["indicateurs"]["emplois_rp"]),
                         {"2014", "2016", "2020"})
        self.assertEqual(set(zones["1109"]["indicateurs"]["postes_flores"]),
                         {str(year) for year in range(2017, 2022)})
        self.assertEqual(zones["1101"]["indicateurs"]["chomage"]["2015"], 8.7)
        self.assertEqual(zones["1101"]["indicateurs"]["demandeurs"]["2015"], 46700)
        for code, commune in [("1103", "91526"), ("1115", "78606")]:
            self.assertEqual(zones[code]["indicateurs"]["emplois"], {})
            self.assertEqual(coverage["zones"][code]["sal_2025"]["communes_absentes"],
                             [commune])

    def test_real_offers_total_uses_only_total_employment_type(self):
        data, coverage = build_dataset()
        paris = next(dep for dep in data["departements"] if dep["code"] == "75")
        self.assertEqual(paris["indicateurs"]["offres"]["2025"], 43500)
        self.assertEqual(set(paris["indicateurs"]["offres"]),
                         {str(year) for year in range(1996, 2026)})
        self.assertEqual(coverage["departements"]["75"]["offres"]["2026"]
                         ["cellules_renseignees"], 3)


class IncompleteSourcesTests(unittest.TestCase):
    """Alter copies of real rows to exercise failure behavior, never source files."""
    @classmethod
    def setUpClass(cls):
        cls.dpae = read_xlsx(SOURCE_ROOT / 'mobility-employment/idf-raw-sources/dpae-par-departement-x-grand-secteur.xlsx')
        cls.offres = read_xlsx(SOURCE_ROOT / 'mobility-employment/idf-raw-sources/dares_offres_collectees_satisfaites_france_travail_brutes_trim.xlsx')

    def test_dpae_missing_cell_omits_annual_total(self):
        rows = [row for row in self.dpae if row['Code département'] == '75'
                and row['Année'] == '2025']
        self.assertEqual(len(rows), 60)
        totals, coverage = aggregate_dpae(rows[:-1])
        self.assertNotIn('2025', totals['75'])
        self.assertEqual(coverage['75']['2025']['cellules_renseignees'], 59)
        rows[-1] = {**rows[-1], 'DPAE (brut)': ''}
        self.assertNotIn('2025', aggregate_dpae(rows)[0]['75'])

    def test_duplicate_dpae_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate DPAE'):
            aggregate_dpae(self.dpae + [self.dpae[0]])

    def test_offers_missing_quarter_omits_annual_total_and_zero_is_valid(self):
        rows = [row for row in self.offres if row['Code département'] == '75'
                and row['Date'].startswith('2025-') and row["Type d'emploi"] == 'Total']
        self.assertEqual(len(rows), 4)
        self.assertNotIn('2025', aggregate_offres(rows[:-1])[0]['75'])
        zero_rows = [{**row, "Nombre d'offres d'emploi": '0'} for row in rows]
        self.assertEqual(aggregate_offres(zero_rows)[0]['75']['2025'], 0)
        zero_rows[-1] = {**zero_rows[-1], "Nombre d'offres d'emploi": ''}
        self.assertNotIn('2025', aggregate_offres(zero_rows)[0]['75'])

    def test_duplicate_offers_is_rejected(self):
        row = next(row for row in self.offres if row['Code département'] == '75'
                   and row["Type d'emploi"] == 'Total')
        with self.assertRaisesRegex(ValueError, 'Duplicate offers'):
            aggregate_offres(self.offres + [row])


if __name__ == "__main__":
    unittest.main()
