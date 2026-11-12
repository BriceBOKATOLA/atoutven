#!/usr/bin/env python3
"""Prépare les données de la carte à partir des fichiers locaux du projet."""
import argparse
import json
import heapq
import math
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parents[1]


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--production-dir', type=Path, default=PRODUCTION)
    parser.add_argument('--source-dir', type=Path, help='source data directory (default: datasets/src)')
    parser.add_argument('--workbook', type=Path, help='employment-zone indicator workbook')
    parser.add_argument('--geography', type=Path, help='employment-zone territories JSON')
    parser.add_argument('--communes', type=Path, help='communes GeoJSON')
    parser.add_argument('--traces', type=Path, help='dated rail sections GeoJSON')
    parser.add_argument('--output', type=Path, help='JSON destination (default: web/public/data/jobseekers-employment-zones.json)')
    return parser.parse_args()


# Cadrage de la planche, avec une marge pour les géométries aux bords.
MAP_BOUNDS = (1.78, 48.49, 3.02, 49.09)
LON_SCALE = math.cos(math.radians(48.8))
METRE_IN_DEGREES = 1 / 111_000

def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))

def rounded_to_metre(coordinates):
    if isinstance(coordinates[0], (int, float)):
        return [round(coordinates[0], 5), round(coordinates[1], 5)]
    parts = [rounded_to_metre(part) for part in coordinates]
    if isinstance(parts[0][0], (int, float)):
        return [point for index, point in enumerate(parts) if index == 0 or point != parts[index - 1]]
    return parts

def douglas_peucker(path, tolerance):
    keep = {0, len(path) - 1}
    spans = [(0, len(path) - 1)]
    while spans:
        first, last = spans.pop()
        ax, ay = path[first][0] * LON_SCALE, path[first][1]
        dx, dy = path[last][0] * LON_SCALE - ax, path[last][1] - ay
        squared_length = dx * dx + dy * dy
        farthest, index = tolerance, None
        for i in range(first + 1, last):
            px, py = path[i][0] * LON_SCALE - ax, path[i][1] - ay
            along = max(0, min(1, (px * dx + py * dy) / squared_length)) if squared_length else 0
            distance = math.hypot(px - along * dx, py - along * dy)
            if distance > farthest:
                farthest, index = distance, i
        if index is not None:
            keep.add(index)
            spans += [(first, index), (index, last)]
    return [path[i] for i in sorted(keep)]

def feature(geometry, properties, tolerance=None):
    coordinates = geometry['coordinates']
    if tolerance:
        coordinates = douglas_peucker(coordinates, tolerance)
    return {'type': 'Feature', 'geometry': {'type': geometry['type'], 'coordinates': rounded_to_metre(coordinates)}, 'properties': properties}

def intersects_map(geometry):
    """Conserve les objets dont l'enveloppe touche le cadrage, même à cheval sur son bord."""
    def points(coordinates):
        if isinstance(coordinates[0], (int, float)):
            yield coordinates
        else:
            for part in coordinates:
                yield from points(part)
    coordinates = list(points(geometry['coordinates']))
    west, south, east, north = MAP_BOUNDS
    return (min(point[0] for point in coordinates) <= east and
            max(point[0] for point in coordinates) >= west and
            min(point[1] for point in coordinates) <= north and
            max(point[1] for point in coordinates) >= south)

def inside_ring(point, ring):
    x, y = point
    inside = False
    previous = ring[-1]
    for current in ring:
        x1, y1 = previous
        x2, y2 = current
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
        previous = current
    return inside

def center(geometry):
    """Point intérieur éloigné des limites, calculé dans un plan local."""
    polygons = [geometry['coordinates']] if geometry['type'] == 'Polygon' else geometry['coordinates']
    # Corrige la différence d'échelle entre longitude et latitude en Île-de-France.
    scale = LON_SCALE
    polygon = max(polygons, key=lambda p: abs(sum(a[0]*b[1]-b[0]*a[1] for a, b in zip(p[0], p[0][1:]+p[0][:1]))))
    rings = [[(x * scale, y) for x, y in ring] for ring in polygon]
    xmin, xmax = min(x for x, y in rings[0]), max(x for x, y in rings[0])
    ymin, ymax = min(y for x, y in rings[0]), max(y for x, y in rings[0])

    def distance(x, y):
        inside = inside_ring((x, y), rings[0]) and not any(inside_ring((x, y), ring) for ring in rings[1:])
        minimum = math.inf
        for ring in rings:
            for (ax, ay), (bx, by) in zip(ring, ring[1:] + ring[:1]):
                dx, dy = bx - ax, by - ay
                t = max(0, min(1, ((x-ax)*dx + (y-ay)*dy) / (dx*dx + dy*dy))) if dx or dy else 0
                minimum = min(minimum, (x-ax-t*dx)**2 + (y-ay-t*dy)**2)
        return math.sqrt(minimum) * (1 if inside else -1)

    # Subdivise les cellules susceptibles d'améliorer le meilleur point.
    queue = []
    def add(x, y, half):
        d = distance(x, y)
        heapq.heappush(queue, (-(d + half * math.sqrt(2)), x, y, half, d))
        return d
    half = max(xmax-xmin, ymax-ymin) / 2
    x, y = (xmin+xmax)/2, (ymin+ymax)/2
    best = (add(x, y, half), x, y)
    while queue:
        upper, x, y, half, d = heapq.heappop(queue)
        if d > best[0]:
            best = (d, x, y)
        if -upper - best[0] <= 0.001:
            continue
        half /= 2
        for dx in (-half, half):
            for dy in (-half, half):
                add(x+dx, y+dy, half)
    return [best[1] / scale, best[2]]

def main():
    args = arguments()
    sources = args.source_dir or args.production_dir / 'datasets/src'
    local = sources / 'jobseekers'
    workbook_path = args.workbook or local / 'Recap_mobilites_emploi_IDF.xlsx'
    geography_path = args.geography or local / 'territoires.json'
    communes_path = args.communes or local / 'communes.geojson'
    traces_path = args.traces or local / 'traces.geojson'
    output = args.output or args.production_dir / 'web/public/data/jobseekers-employment-zones.json'
    from openpyxl import load_workbook
    workbook = load_workbook(workbook_path, data_only=True, read_only=True)
    rows = list(workbook['Zones d’emploi'].values)
    workbook.close()
    header = rows[4]
    years = [(i, str(value)) for i, value in enumerate(header) if isinstance(value, int)]
    metrics = []
    values = {}
    for row in rows[5:]:
        code, name, metric = row[:3]
        if not code:
            continue
        if not any(m['name'] == metric for m in metrics):
            # The source workbook says ‘Fin T4’; the zone methodology does not establish an end-of-quarter count.
            scope = '4e trimestre ; rupture 2025' if metric == 'Demandeurs ABC' else row[17]
            metrics.append({'name': metric, 'unit': row[15], 'source': row[16], 'scope': scope})
        values.setdefault(str(code), {})[metric] = {year: row[i] for i, year in years}
    geography = read_json(geography_path)
    zones = []
    for zone in geography['zones']:
        code = zone['code']
        if code not in values:
            raise ValueError(f'Zone absente du classeur : {code}')
        zones.append(feature(zone['geometry'], {'code': code, 'nom': zone['nom'], 'indicators': values[code], 'center': rounded_to_metre(center(zone['geometry']))}))
    records = {}
    for record in (sources / 'defm_2016_2024.txt').read_text(encoding='utf-8').strip().split(','):
        code, a, b = record.split(':')
        records[code] = (int(a), int(b))
    communes = []
    for source in read_json(communes_path)['features']:
        if not intersects_map(source['geometry']):
            continue
        props = source['properties']
        a, b = records.get(props['code'], (None, None))
        evolution = (b / a - 1) * 100 if a and b is not None else None
        communes.append(feature(source['geometry'], {'code': props['code'], 'nom': props['nom'], 'defm2016': a, 'defm2024': b, 'evolution': evolution}))
    stations = []
    recent_stations = {}
    for source in read_json(sources / 'gares_idf.geojson')['features']:
        props = source['properties']
        date = props.get('date_mise') or ''
        if date[:4].isdigit() and 2015 <= int(date[:4]) <= 2025 and source.get('geometry'):
            recent_stations.setdefault(props.get('res_com'), []).append((source['geometry']['coordinates'], int(date[:4])))
            if intersects_map(source['geometry']):
                stations.append(feature(source['geometry'], {'nom': props.get('nom_gares')}))

    def year_of_recent_station_at_an_end(line, path):
        gap, year = min(((math.hypot((end[0] - at[0]) * LON_SCALE, end[1] - at[1]), year) for end in (path[0], path[-1]) for at, year in recent_stations.get(line, [])), default=(math.inf, None))
        return year if gap < 60 * METRE_IN_DEGREES else None

    lines, renamed_without_new_station, undated_attached_to_an_opening = [], {}, {}
    for source in read_json(traces_path)['features']:
        props = source['properties']
        name, year = props.get('res_com') or '', props.get('annee_mes')
        if isinstance(year, (float, int)) and 2015 <= year <= 2025 and 'TER' not in name and intersects_map(source['geometry']):
            if name in recent_stations:
                lines.append(feature(source['geometry'], {'nom': name, 'annee': year}))
            else:
                renamed_without_new_station.setdefault(name, []).append(feature(source['geometry'], {}, 2 * METRE_IN_DEGREES))
    old_lines = []
    for source in read_json(sources / 'reseau_ferre_idf.geojson')['features']:
        props = source['properties']
        name, date = props.get('res_com') or '', props.get('date_mes') or ''
        if not intersects_map(source['geometry']):
            continue
        if date[:4].isdigit():
            if int(date[:4]) < 2015:
                old_lines.append(feature(source['geometry'], {}, 2 * METRE_IN_DEGREES))
        elif 'TER' not in name:
            year = year_of_recent_station_at_an_end(name, source['geometry']['coordinates'])
            if year is not None:
                lines.append(feature(source['geometry'], {'nom': name, 'annee': year}))
                undated_attached_to_an_opening[name] = undated_attached_to_an_opening.get(name, 0) + 1
    for sections in renamed_without_new_station.values():
        old_lines += sections
    data = {'oldLines': {'type': 'FeatureCollection', 'features': old_lines}, 'stations': {'type': 'FeatureCollection', 'features': stations}, 'communes': {'type': 'FeatureCollection', 'features': communes}, 'zones': {'type': 'FeatureCollection', 'features': zones}, 'metrics': metrics, 'lines': {'type': 'FeatureCollection', 'features': lines}}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(f'{len(communes)} communes, {len(zones)} zones, {len(metrics)} indicateurs, {len(lines)} tronçons')
    print('Tronçons non datés rattachés à une ouverture :', undated_attached_to_an_opening or 'aucun')
    print('Lignes datées de 2015 à 2025 sans station nouvelle, dessinées avec le réseau ancien :', {name: len(sections) for name, sections in renamed_without_new_station.items()} or 'aucune')

if __name__ == '__main__':
    main()
