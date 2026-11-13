"""Rebuild territories and coverage using Python's standard library and local sources.

Run from any working directory:
    python3 production/scripts/build_territories.py --output-dir /tmp/territories

The default output directory is production/datasets/src/jobseekers. --source-root
can select another datasets/src tree with the same relative source paths.
"""
from collections import defaultdict
from itertools import product
import re
import zipfile
import xml.etree.ElementTree as ET
import json
import math
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[1] / 'datasets/src'
DEFAULT_OUTPUT = SOURCE_ROOT / 'jobseekers'
DEPARTMENTS = {
    '75': 'Paris', '77': 'Seine-et-Marne', '78': 'Yvelines', '91': 'Essonne',
    '92': 'Hauts-de-Seine', '93': 'Seine-Saint-Denis', '94': 'Val-de-Marne',
    '95': "Val-d’Oise",
}


def numeric(value):
    """Keep missing values missing; refuse malformed numbers."""
    if value is None or value == '':
        return None
    if isinstance(value, bool):
        raise ValueError('Boolean is not an indicator value')
    value = float(value)
    if not math.isfinite(value):
        raise ValueError('Non-finite indicator value')
    return int(value) if value.is_integer() else value


def series(properties, prefix):
    result = {}
    for key, value in properties.items():
        if key.startswith(prefix) and key[len(prefix):].isdigit():
            number = numeric(value)
            if number is not None:
                result[key[len(prefix):]] = number
    return dict(sorted(result.items()))


def aggregate_communes(communes, field, coverage):
    values = [numeric(c['properties'].get(field)) for c in communes]
    missing = [c['properties']['code'] for c, value in zip(communes, values)
               if value is None]
    coverage[field] = {'communes_attendues': len(communes),
                       'communes_renseignees': len(communes) - len(missing),
                       'communes_absentes': missing}
    if missing or not communes:
        return None
    return numeric(round(math.fsum(values), 1))



def read_xlsx(path):
    """Read the sole worksheet; support sparse and inline/shared-string cells."""
    ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(path) as archive:
        strings = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            strings = [''.join(node.itertext())
                       for node in ET.fromstring(archive.read('xl/sharedStrings.xml'))]
        sheets = [name for name in archive.namelist()
                  if re.fullmatch(r'xl/worksheets/sheet\d+\.xml', name)]
        if len(sheets) != 1:
            raise ValueError(f'Expected one worksheet: {path}')
        rows = []
        for row in ET.fromstring(archive.read(sheets[0])).findall('.//s:row', ns):
            values = []
            for cell in row:
                if cell.tag != '{' + ns['s'] + '}c':
                    continue
                reference = cell.get('r')
                if reference:
                    column = re.match('[A-Z]+', reference).group()
                    index = 0
                    for letter in column:
                        index = index * 26 + ord(letter) - ord('A') + 1
                    while len(values) < index - 1:
                        values.append('')
                value = cell.find('s:v', ns)
                inline = cell.find('s:is', ns)
                if value is not None:
                    text = value.text or ''
                elif inline is not None:
                    text = ''.join(inline.itertext())
                else:
                    text = ''
                if cell.get('t') == 's':
                    text = strings[int(text)]
                values.append(text)
            if values:
                rows.append(values)
    if not rows or len(set(rows[0])) != len(rows[0]):
        raise ValueError(f'Missing or duplicate headers: {path}')
    header = rows[0]
    result = []
    for row in rows[1:]:
        if len(row) > len(header):
            raise ValueError(f'Too many columns: {path}')
        result.append(dict(zip(header, row + [''] * (len(header) - len(row)))))
    return result


DPAE_SECTORS = {
    'GSA1 Agriculture - Industrie', 'GSA2 Construction', 'GSA3 Commerce',
    'GSA4 Hôtellerie - Restauration', 'GSA5 Autres services',
}
DPAE_NATURES = {
    "CDD de moins d'un mois": "Contrat de moins d'un mois",
    "CDD de plus d'un mois": "Contrat de plus d'un mois",
    'CDI': "Contrat de plus d'un mois",
}


def complete_annual(groups, expected_slots):
    totals = {code: {} for code in DEPARTMENTS}
    coverage = {code: {} for code in DEPARTMENTS}
    for (code, year), cells in sorted(groups.items()):
        present = {slot for slot, value in cells.items() if value is not None}
        missing = expected_slots - present
        coverage[code][year] = {
            'cellules_attendues': len(expected_slots),
            'cellules_renseignees': len(present),
            'complet': not missing,
        }
        if not missing:
            totals[code][year] = numeric(math.fsum(cells.values()))
    return totals, coverage


def aggregate_dpae(rows):
    groups = defaultdict(dict)
    for row in rows:
        code = row['Code département']
        if row['Code région'] != '11' or code not in DEPARTMENTS:
            continue
        year = str(int(row['Année']))
        quarter = int(row['Trimestre'])
        sector = row["Grand secteur d'activité agrégé"]
        nature = row['Nature de contrat']
        if (quarter not in range(1, 5) or sector not in DPAE_SECTORS
                or nature not in DPAE_NATURES
                or row['Durée de contrat'] != DPAE_NATURES[nature]):
            raise ValueError(f'Unexpected DPAE dimensions: {code}, {year}')
        slot = (quarter, sector, nature)
        group = groups[(code, year)]
        if slot in group:
            raise ValueError(f'Duplicate DPAE cell: {code}, {year}, {slot}')
        group[slot] = numeric(row['DPAE (brut)'])
    expected = set(product(range(1, 5), DPAE_SECTORS, DPAE_NATURES))
    return complete_annual(groups, expected)


def aggregate_offres(rows):
    groups = defaultdict(dict)
    for row in rows:
        code = row['Code département']
        if (row['Code région'] != '11' or code not in DEPARTMENTS
                or row['Type de données'] != 'Brutes'
                or row["Type d'offre d'emploi"] != "Offres d'emploi collectées"
                or row["Type d'emploi"] != 'Total' or row['Qualification'] != 'Total'):
            continue
        match = re.fullmatch(r'(\d{4})-T([1-4])', row['Date'])
        if not match:
            raise ValueError(f"Invalid quarter: {row['Date']}")
        year, quarter = match.groups()
        group = groups[(code, year)]
        if quarter in group:
            raise ValueError(f'Duplicate offers quarter: {code}, {year}, {quarter}')
        group[quarter] = numeric(row["Nombre d'offres d'emploi"])
    return complete_annual(groups, set('1234'))

def build_dataset(root=SOURCE_ROOT):
    root = Path(root)
    zones_source = json.loads((root / 'jobseekers/territories_sources/map-data/zones_emploi.geojson').read_text(encoding="utf-8"))['features']
    communes = json.loads((root / 'jobseekers/communes.geojson').read_text(encoding="utf-8"))['features']
    zone_codes = {str(f['properties']['ze2020']) for f in zones_source}
    if len(zone_codes) != len(zones_source):
        raise ValueError('Duplicate zone code')
    commune_codes = [c['properties']['code'] for c in communes]
    if len(set(commune_codes)) != len(commune_codes):
        raise ValueError('Duplicate commune code')
    for commune in communes:
        prop = commune['properties']
        if str(prop['ze']) not in zone_codes or str(prop['dep']) not in DEPARTMENTS:
            raise ValueError(f"Unmapped commune: {prop['code']}")
    coverage = {'zones': {}, 'departements': {}}
    zones = []
    salary_fields = sorted({key for c in communes for key in c['properties']
                            if key.startswith('sal_') and key[4:].isdigit()})
    for feature in zones_source:
        prop = feature['properties']
        code = str(prop['ze2020'])
        members = [c for c in communes if str(c['properties']['ze']) == code]
        zone_coverage = {}
        jobs = {}
        active = {}
        for field in salary_fields:
            value = aggregate_communes(members, field, zone_coverage)
            if value is not None:
                jobs[field[4:]] = value
        for field, year in [('actocc_16', '2016'), ('actocc_21', '2021')]:
            value = aggregate_communes(members, field, zone_coverage)
            if value is not None:
                active[year] = value
        census_jobs = {}
        flores_posts = {}
        for field, year in [('emplt_14', '2014'), ('emplt_16', '2016'), ('emplt_20', '2020')]:
            value = aggregate_communes(members, field, zone_coverage)
            if value is not None:
                census_jobs[year] = value
        for year in range(2017, 2022):
            value = aggregate_communes(members, f'flo_{year}', zone_coverage)
            if value is not None:
                flores_posts[str(year)] = value
        zones.append({'code': code, 'nom': prop['libze2020'],
                      'geometry': feature['geometry'],
                      'indicateurs': {'chomage': series(prop, 'txcho_'),
                                      'demandeurs': series(prop, 'defmABC_'),
                                      'emplois': jobs, 'actifs_occupes': active,
                                      'emplois_rp': census_jobs, 'postes_flores': flores_posts}})
        coverage['zones'][code] = zone_coverage
    dpae, dpae_coverage = aggregate_dpae(read_xlsx(
        root / 'mobility-employment/idf-raw-sources/dpae-par-departement-x-grand-secteur.xlsx'))
    offres, offres_coverage = aggregate_offres(read_xlsx(
        root / 'mobility-employment/idf-raw-sources/dares_offres_collectees_satisfaites_france_travail_brutes_trim.xlsx'))
    departments = []
    for code, name in DEPARTMENTS.items():
        geometries = [c['geometry'] for c in communes if str(c['properties']['dep']) == code]
        if not geometries:
            raise ValueError(f'Missing department geometries: {code}')
        departments.append({'code': code, 'nom': name,
                            'geometry': {'type': 'GeometryCollection', 'geometries': geometries},
                            'indicateurs': {'dpae': dpae[code], 'offres': offres[code]}})
        coverage['departements'][code] = {
            'communes_geometrie': len(geometries),
            'dpae': dpae_coverage[code], 'offres': offres_coverage[code]}
    return {'zones': zones, 'departements': departments}, coverage


def main():
    import argparse
    import hashlib

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, default=SOURCE_ROOT,
                        help='Root of the source datasets (default: production/datasets/src)')
    parser.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT,
                        help='Directory for territoires.json and couverture.json')
    args = parser.parse_args()
    data, coverage = build_dataset(args.source_root)
    source_files = [
        'jobseekers/territories_sources/map-data/zones_emploi.geojson', 'jobseekers/communes.geojson',
        'mobility-employment/idf-raw-sources/dpae-par-departement-x-grand-secteur.xlsx',
        'mobility-employment/idf-raw-sources/dares_offres_collectees_satisfaites_france_travail_brutes_trim.xlsx',
    ]
    coverage['sources_sha256'] = {
        name: hashlib.sha256((args.source_root / name).read_bytes()).hexdigest()
        for name in source_files
    }
    coverage['regles'] = {
        'valeurs_absentes': 'Années absentes du JSON ; aucune imputation à zéro.',
        'emplois': 'Somme sal_ communale seulement si toutes les communes sont renseignées.',
        'actifs_occupes': 'Somme actocc_16 et actocc_21 ; années 2016 et 2021 uniquement.',
        'emplois_rp': 'Somme emplt_14, emplt_16, emplt_20 ; années 2014, 2016, 2020 uniquement.',
        'postes_flores': 'Somme flo_2017 à flo_2021 ; aucune extrapolation.',
        'chomage_demandeurs': 'Valeurs txcho_ et defmABC_ des zones, sans agrégation des taux.',
        'dpae': 'Brut ; 4 trimestres × 5 grands secteurs × 3 natures de contrat ; 60 cellules par année.',
        'offres': 'Brutes, collectées, type emploi Total, qualification Total, département individuel ; 4 trimestres.',
        'geometries': 'Contours locaux : 15 zones et 8 collections de communes, sans fusion géométrique.',
    }
    coverage['limites'] = [
        'Emplois = effectifs salariés privés Urssaf des données préparées, pas ensemble des emplois.',
        'Les cellules sal_ renseignées sont des agrégats existants. Leur exhaustivité par rapport aux cellules annuelles manquantes du CSV Urssaf brut ne peut pas être démontrée.',
        'Les communes 78606 et 91526 ne figurent pas dans le CSV Urssaf brut. Les totaux emplois des zones 1115 et 1103 sont omis, pour toutes les années.',
        'Le fichier Urssaf brut est limité au code région 11. Aucun total de zone entière hors de ce périmètre ne peut être inféré.',
        'Les géométries départementales conservent les limites communales ; les propriétés indicateurs ne contiennent aucune donnée départementale affectée à une zone.',
        'Les offres Dares sont fournies en multiples de 100 dans ce fichier ; la somme annuelle conserve la précision du fichier.',
    ]
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    for filename, content in [('territoires.json', data), ('couverture.json', coverage)]:
        destination = output / filename
        temporary = destination.with_suffix('.json.tmp')
        temporary.write_text(json.dumps(content, ensure_ascii=False, allow_nan=False,
                                        separators=(',', ':')) + '\n', encoding='utf-8')
        temporary.replace(destination)
    print(f"Generated {output / 'territoires.json'}: {len(data['zones'])} zones, "
          f"{len(data['departements'])} départements")


if __name__ == '__main__':
    main()
