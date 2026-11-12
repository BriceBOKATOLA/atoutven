"""Export the source map in Lambert-93 coordinates for the static web chart.

Run with production/.venv/bin/python production/scripts/export-network.py.
Requires the production Python dependencies.
"""
from pathlib import Path
from itertools import combinations
import json
import sys

import argparse


def arguments():
    parser = argparse.ArgumentParser(description="Export the rail network for the static web chart.")
    parser.add_argument('--production-dir', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--source-dir', type=Path, help='source GeoJSON directory (default: datasets/src)')
    parser.add_argument('--clean-dir', type=Path, help='shared clean data directory (default: datasets/clean/shared)')
    parser.add_argument('--output', type=Path, help='JSON destination (default: web/public/data/rail-network.json)')
    return parser.parse_args()


args = arguments()
production = args.production_dir.resolve()
sys.path.insert(0, str(production / 'scripts'))
from shapely.geometry import box
import map_utils

map_utils.BASE = args.source_dir or production / 'datasets/src'
map_utils.CLEAN = args.clean_dir or production / 'datasets/clean/shared'
load, short = map_utils.load, map_utils.short

com, dep, _, fer, gar = load()
window = box(619000, 6825000, 692000, 6885000)
stations = gar[(gar.an >= 2015) & (gar.an <= 2025)].copy()
# A commercial rename can date old infrastructure as recent (T14 in 2025).
# Match the source map's rule: require a recent station on the same line.
recent_tracks = fer.an.between(2015, 2025) & ~fer.res_com.str.contains("TER")
renamed_tracks = recent_tracks & ~fer.res_com.isin(stations.res_com)
old = fer[(fer.an < 2015) | renamed_tracks]
new = fer[recent_tracks & ~renamed_tracks].copy()
if renamed_tracks.any():
    print("Réseau ancien (aucune gare récente) : " + ", ".join(sorted(fer.loc[renamed_tracks, "res_com"].unique())))
new["line"] = new.res_com.map(short)
stations["line"] = stations.res_com.map(short)


def xy(x, y):
    # Local kilometre units retain the source's Lambert-93 aspect and scale.
    return [round((x - 619000) / 1000, 3), round((y - 6825000) / 1000, 3)]


def paths(geometry):
    """Highmaps SVG paths, using projected coordinates rather than lon/lat."""
    geometry = geometry.intersection(window).simplify(20, preserve_topology=True)
    if geometry.is_empty:
        return []
    if geometry.geom_type.startswith("Multi") or geometry.geom_type == "GeometryCollection":
        return [part for child in geometry.geoms for part in paths(child)]
    rings = [geometry.exterior, *geometry.interiors] if geometry.geom_type == "Polygon" else [geometry]
    result = []
    for ring in rings:
        coords = [xy(x, y) for x, y, *_ in ring.coords]
        if len(coords) < 2:
            continue
        path = []
        for index, (x, y) in enumerate(coords):
            path.extend(["M" if index == 0 else "L", x, -y])
        if geometry.geom_type == "Polygon":
            path.append("Z")
        result.append(" ".join(str(value) for value in path))
    return result


def features(frame, name_field=None):
    return [{"name": str(row[name_field]) if name_field else "", "path": path}
            for _, row in frame.iterrows() for path in paths(row.geometry)]


openings = sorted(set(zip(new.line, new.an.astype(int))) | set(zip(stations.line, stations.an.astype(int))), key=lambda item: (item[1], item[0]))
labels = []
termini = []
for line, year in openings:
    section = new[(new.line == line) & (new.an == year)]
    stops = stations[(stations.line == line) & (stations.an == year)]
    visible = (section if len(section) else stops).cx[619000:692000, 6825000:6885000]
    if len(visible):
        union = visible.geometry.union_all()
        point = union.interpolate(.5, normalized=True) if union.geom_type == "LineString" else union.centroid
        x, y = xy(point.x + 1200, point.y + 900)
        labels.append({"name": f"{line} | {year}" + ("*" if line == "M11" else ""), "x": x, "y": -y})
    points = list(stops.itertuples())
    pair = max(combinations(points, 2), key=lambda p: p[0].geometry.distance(p[1].geometry)) if len(points) > 1 else points
    for point in pair:
        if 620500 < point.geometry.x < 690500 and 6826500 < point.geometry.y < 6883500:
            x, y = xy(point.geometry.x, point.geometry.y)
            termini.append({"name": point.nom_gares, "x": x, "y": -y})

periods = []
for first, last, color in [(2015, 2018, "#009E73"), (2019, 2021, "#0072B2"), (2022, 2025, "#D55E00")]:
    frame = new[new.an.between(first, last)]
    stops = stations[stations.an.between(first, last)]
    periods.append({"name": f"{first} – {last}", "color": color,
                    "openings": [{"line": line, "year": year} for line, year in openings if first <= year <= last],
                    "tracks": [{"name": f"{row.line} ({int(row.an)})", "path": path} for _, row in frame.iterrows() for path in paths(row.geometry)],
                    "stations": [{"name": row.nom_gares, "line": row.line, "year": int(row.an), "x": xy(row.geometry.x, row.geometry.y)[0], "y": -xy(row.geometry.x, row.geometry.y)[1]} for row in stops.itertuples() if window.covers(row.geometry)]})

department_labels = []
for row in dep.itertuples():
    point = row.geometry.representative_point()
    if 623000 < point.x < 688000 and 6829000 < point.y < 6881000 and row.code != "75":
        x, y = xy(point.x, point.y)
        department_labels.append({"name": row.nom.upper(), "x": x, "y": -y})
x, y = xy(651800, 6862200)
department_labels.append({"name": "PARIS", "x": x, "y": -y})

payload = {"bounds": [0, 73, -60, 0], "summary": {"lines": len({line for line, _ in openings}), "stations": len(stations), "kilometres": round(new.length.sum() / 1000)},
           "communes": features(com, "nom"), "paris": features(com[com.code == "75056"]),
           "departments": features(dep), "existing": features(old), "periods": periods,
           "labels": labels, "termini": termini, "departmentLabels": department_labels,
           "sourceStationCount": len(stations)}
output = args.output or production / "web/public/data/rail-network.json"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"{output.name}: {output.stat().st_size:,} bytes, {len(stations)} gares, {payload['summary']['kilometres']} km")
