"""Reconstruct retained line/year groups from local station and commune geometry.

Run with an explicit output, for example:
    python production/scripts/build_line_groups.py --output /tmp/groupes_lignes.json

Reproject both sources to EPSG:2154. Select station opening years 2015–2025
inclusive, then join with ``within``. Points on polygon boundaries or outside
all polygons are excluded. Keep every match in overlapping polygons, including
historical communes; do not choose a nearest commune or merge historical codes.
Exclude Paris (75056). Repeated stations/matches count a commune only once in
each line/year group. Invalid or missing dates do not select a station.

Use map_utils.short for line labels and map_utils.clean for commune names.
The local official-name dictionary overrides polygon names, with polygon names
as fallback. Sort group keys, codes and names independently by Python string
order (not locale order); names and codes are not positional pairs. These are
historical source geometries and names, not a claim about current boundaries.
The output path is required and must differ from each input file.
"""
import argparse
import json
from pathlib import Path
import sys

import geopandas as gpd
import pandas as pd

from map_utils import clean, short

DATASETS = Path(__file__).resolve().parents[1] / "datasets"
DEFAULT_STATIONS = DATASETS / "src/gares_idf.geojson"
DEFAULT_COMMUNES = DATASETS / "clean/shared/hackathon_emploi.gpkg"
DEFAULT_NAMES = DATASETS / "src/noms_officiels.json"


def reconstruct_groups(stations, communes, official_names):
    """Return line/year groups; inputs are GeoDataFrames and a name dictionary."""
    stations = stations.to_crs(2154).copy()
    communes = communes.to_crs(2154).copy()
    years = pd.to_datetime(stations["date_mise"], errors="coerce", utc=True).dt.year
    stations = stations.loc[years.between(2015, 2025), ["res_com", "geometry"]].copy()
    stations["an"] = years.loc[stations.index].astype(int)
    if not stations["res_com"].map(lambda value: isinstance(value, str) and bool(value.strip())).all():
        raise ValueError("Missing or invalid station line")
    stations["line"] = stations["res_com"].map(short)
    communes["nom"] = [clean(official_names.get(code, name))
                       for code, name in zip(communes["code"], communes["nom"])]
    matches = gpd.sjoin(stations, communes[["code", "nom", "geometry"]], how="inner", predicate="within")
    matches = matches.loc[matches["code"] != "75056"]
    groups = {}
    for (line, year), matched in matches.groupby(["line", "an"], sort=True):
        groups[f"{line} ({year})"] = {
            "line": line, "an": int(year),
            "codes": sorted(set(matched["code"])),
            "communes": sorted(set(matched["nom"])),
        }
    return dict(sorted(groups.items()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stations", type=Path, default=DEFAULT_STATIONS)
    parser.add_argument("--communes", type=Path, default=DEFAULT_COMMUNES)
    parser.add_argument("--official-names", type=Path, default=DEFAULT_NAMES)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    for source in (args.stations, args.communes, args.official_names):
        same_path = args.output.resolve() == source.resolve()
        same_file = args.output.exists() and source.exists() and args.output.samefile(source)
        if same_path or same_file:
            parser.error("Output must differ from all input files")
    groups = reconstruct_groups(
        gpd.read_file(args.stations), gpd.read_file(args.communes),
        json.loads(args.official_names.read_text(encoding="utf-8")),
    )
    args.output.write_text(json.dumps(groups, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Wrote {len(groups)} line/year groups to {args.output}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
