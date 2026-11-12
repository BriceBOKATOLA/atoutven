#!/usr/bin/env python3
"""Extract the local GeoPackage and 2026 departmental indicators using only Python's standard library."""
import argparse
import ast
import csv
import json
import re
import sqlite3
import struct
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parents[1]
DEPARTMENT_SHEET = 'Par département 2ème&3ème trime'
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
DEPARTMENTS = [('75', 'Paris'), ('77', 'Seine-et-Marne'), ('78', 'Yvelines'), ('91', 'Essonne'), ('92', 'Hauts-de-Seine'), ('93', 'Seine-Saint-Denis'), ('94', 'Val-de-Marne'), ('95', 'Val-d’Oise')]

def geometry(blob):
    """Read 2D standard GeoPackage WKB, keeping EPSG:2154 coordinates rounded to the metre."""
    envelope = (blob[3] >> 1) & 7
    offset = 8 + {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}[envelope]
    def parse(pos):
        order = '<' if blob[pos] == 1 else '>'
        kind = struct.unpack_from(order + 'I', blob, pos + 1)[0]
        pos += 5
        def count():
            nonlocal pos
            value = struct.unpack_from(order + 'I', blob, pos)[0]
            pos += 4
            return value
        def point():
            nonlocal pos
            value = list(struct.unpack_from(order + 'dd', blob, pos))
            pos += 16
            return [round(value[0]), round(value[1])]
        if kind == 1:
            coordinates = point()
        elif kind == 2:
            coordinates = [point() for _ in range(count())]
        elif kind == 3:
            coordinates = [[point() for _ in range(count())] for _ in range(count())]
        elif kind in (4, 5, 6):
            coordinates = []
            for _ in range(count()):
                child, pos = parse(pos)
                coordinates.append(child['coordinates'])
        else:
            raise ValueError(f'Unsupported WKB geometry: {kind}')
        return {'type': {1:'Point', 2:'LineString', 3:'Polygon', 4:'MultiPoint', 5:'MultiLineString', 6:'MultiPolygon'}[kind], 'coordinates': coordinates}, pos
    result, end = parse(offset)
    if end != len(blob):
        raise ValueError('Unexpected bytes after WKB geometry')
    return result

def sheet_rows(path):
    with zipfile.ZipFile(path) as archive:
        strings = [''.join(item.itertext()) for item in ET.fromstring(archive.read('xl/sharedStrings.xml')).findall('m:si', NS)]
        workbook = ET.fromstring(archive.read('xl/workbook.xml'))
        sheet = next(s for s in workbook.findall('m:sheets/m:sheet', NS) if s.get('name') == DEPARTMENT_SHEET)
        relationship = sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        relations = ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))
        target = next(r.get('Target') for r in relations if r.get('Id') == relationship)
        xml = ET.fromstring(archive.read('xl/' + target.lstrip('/'))) if not target.startswith('/xl/') else ET.fromstring(archive.read(target[1:]))
        rows = {}
        for row in xml.findall('m:sheetData/m:row', NS):
            cells = {}
            for cell in row:
                value = cell.find('m:v', NS)
                text = value.text if value is not None else ''
                if cell.get('t') == 's': text = strings[int(text)]
                if cell.get('t') == 'inlineStr': text = ''.join(cell.find('m:is', NS).itertext())
                cells[re.sub(r'\d', '', cell.get('r'))] = text
            rows[int(row.get('r'))] = cells
        return rows

def interior_center(geom):
    """Midpoint of an interior scanline segment; remains inside the source polygon."""
    polygons = [geom['coordinates']] if geom['type'] == 'Polygon' else geom['coordinates']
    candidates = []
    for rings in polygons:
        ys = [p[1] for p in rings[0]]
        y = (min(ys) + max(ys)) / 2
        crossings = []
        for ring in rings:
            for a, b in zip(ring, ring[1:] + ring[:1]):
                if (a[1] > y) != (b[1] > y):
                    crossings.append(a[0] + (y-a[1]) * (b[0]-a[0]) / (b[1]-a[1]))
        crossings.sort()
        for left, right in zip(crossings[::2], crossings[1::2]):
            candidates.append((right-left, [round((left+right)/2), round(y)]))
    return max(candidates)[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--production-dir', type=Path, default=PRODUCTION)
    parser.add_argument('--workbook', type=Path, help='departmental floral indicator workbook (2026 departmental tab)')
    parser.add_argument('--source', type=Path, help='folder of the plate 06 GeoPackage and CSV')
    parser.add_argument('--plate-script', type=Path, help='plate 06 script holding the regional constants')
    parser.add_argument('--indicators', type=Path, help='four-petal indicator configuration JSON')
    parser.add_argument('--output', type=Path, help='JSON destination (default: web/public/data/employment-centers-departments.json)')
    args = parser.parse_args()
    local = args.production_dir / 'datasets/src/employment-centers'
    args.workbook = args.workbook or local / 'Représention Florale  (1).xlsx'
    args.source = args.source or args.production_dir / 'datasets/clean/06_employment_centers_2015_2025'
    args.plate_script = args.plate_script or args.production_dir / 'scripts/06_employment_centers.py'
    args.indicators = args.indicators or local / 'indicateurs.json'
    args.output = args.output or args.production_dir / 'web/public/data/employment-centers-departments.json'
    rows = sheet_rows(args.workbook)
    config = json.loads(args.indicators.read_text(encoding='utf-8'))
    assert len(config) == 4, 'Exactly four petals are required'
    connection = sqlite3.connect(f'file:{args.source / "06_poles_emploi.gpkg"}?mode=ro', uri=True)
    connection.row_factory = sqlite3.Row
    def layer(name, columns):
        records = []
        for row in connection.execute(f'SELECT geom,{columns} FROM "{name}"'):
            record = dict(row)
            record['geometry'] = geometry(record.pop('geom'))
            records.append(record)
        return records
    communes = layer('communes_emploi', 'code,nom,emploi_2015,emploi_2025,densite_2025,km2')
    poles = layer('poles_2025', 'code,nom,emploi_2015,emploi_2025,nouveau_pole')
    lines = layer('reseau_2025', 'res_com,mode,an')
    departments = layer('departements', 'code,nom')
    values = {}
    for index, (code, name) in enumerate(DEPARTMENTS, 5):
        assert rows[index]['A'].strip(), f'Missing department at row {index}'
        values[code] = {}
        for metric in config:
            raw = rows[index].get(metric['column'], '').strip()
            values[code][metric['id']] = float(raw.replace(',', '.')) if raw else None
    for department in departments:
        department['indicators'] = values[department['code']]
        department['center'] = interior_center(department['geometry'])
    # Exact extents of the source's departmental geometries. Northing becomes SVG -y.
    def points(coords):
        if isinstance(coords[0], (int,float)): yield coords
        else:
            for child in coords: yield from points(child)
    coordinates = [p for d in departments for p in points(d['geometry']['coordinates'])]
    bounds = [min(p[0] for p in coordinates), min(p[1] for p in coordinates), max(p[0] for p in coordinates), max(p[1] for p in coordinates)]
    data = {'crs': 'EPSG:2154', 'bounds': bounds, 'communes': communes, 'poles': poles, 'lines': lines, 'departments': departments, 'metrics': config, 'sourceWorkbook': args.workbook.name, 'totalEmployment': sum(c['emploi_2025'] or 0 for c in communes)}
    # Preserve the regional figures of the original panel. INSEE regional totals
    # in the plate 06 script are not the sum of the available communal records.
    constants = {}
    for node in ast.parse(args.plate_script.read_text()).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in {'INSEE', 'DEFM'}:
            constants[node.targets[0].id] = ast.literal_eval(node.value)
    ae_rows = list(csv.DictReader((args.source / 'auto_entrepreneurs_par_departement_urssaf.csv').open(encoding='utf-8-sig'), delimiter=';'))
    def comparison(label, start, end, years, source):
        return dict(label=label, start=start, end=end, years=years, source=source)
    # Producer and period as printed on plate 06; file names stay in the README.
    data['comparison'] = {
        'poleCount2015': sum(c['emploi_2015'] >= 10000 for c in communes),
        'newPoleCount': sum(bool(p['nouveau_pole']) for p in poles),
        'rows': [
            comparison('Emplois salariés privés', sum(c['emploi_2015'] for c in communes), data['totalEmployment'], 'fin 2015 à fin 2025', 'Urssaf'),
            comparison('Emploi total (public compris)', constants['INSEE']['2017'][0], constants['INSEE']['2023'][0], 'recensement 2017 à 2023', 'Insee'),
            comparison('Dont non-salariés', constants['INSEE']['2017'][1], constants['INSEE']['2023'][1], 'recensement 2017 à 2023', 'Insee'),
            comparison('Auto-entrepreneurs inscrits', sum(int(r['ae_adm_actifs_2015']) for r in ae_rows), sum(int(r['ae_adm_actifs_2025']) for r in ae_rows), 'fin 2015 à fin 2025', 'Urssaf'),
            comparison('Demandeurs d’emploi (A, B, C)', *constants['DEFM'], 'moyennes du 4e trimestre 2016 et 2024', 'France Travail et Dares')
        ],
        'topPoles': sorted((dict(code=c['code'], nom=c['nom'], start=c['emploi_2015'], end=c['emploi_2025']) for c in communes if c['code'] != '75056'), key=lambda c: c['end'], reverse=True)[:6]
    }
    assert len(poles) == 87 and all(p['emploi_2025'] >= 10000 for p in poles)
    assert len(departments) == 8 and set(values) == {d['code'] for d in departments}
    connection.close()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(f'{len(communes)} communes, {len(poles)} pôles, {len(lines)} tronçons, {len(departments)} départements; EPSG:2154 {bounds}')

if __name__ == '__main__':
    main()
