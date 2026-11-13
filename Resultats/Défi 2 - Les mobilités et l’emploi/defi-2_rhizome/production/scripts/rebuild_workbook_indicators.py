"""Reconstruct the six zone indicators from retained local raw files.

python3 production/scripts/rebuild_workbook_indicators.py --output /tmp/workbook-indicators.json

No workbook is created or modified. Output contains rebuilt values, cell-by-cell
comparison with Zones d’emploi, and coverage diagnostics. Blank Urssaf sector
cells are excluded from the sum of reported values and counted explicitly; a
matching historical total does not establish that these blanks mean zero.
Missing communes suppress a zone total. Commune values are rounded to one
decimal before zone aggregation, matching the retained communal preparation. RP 2016 uses C16_EMPLT (complementary
census), as the retained communal preparation does, rather than P16_EMPLT.
This reproduces local extracts; it does not recreate their upstream downloads.
"""
import argparse
from collections import defaultdict
import csv
import json
import math
from pathlib import Path
import posixpath
import re
import xml.etree.ElementTree as ET
import zipfile

SOURCE_ROOT = Path(__file__).resolve().parents[1] / "datasets/src"
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
RID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
YEARS = range(2015, 2026)


def read_workbook(path):
    """Read every sheet, including hidden/empty sheets, with cell references."""
    result = {}
    with zipfile.ZipFile(path) as archive:
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            strings = ["".join(n.itertext()) for n in ET.fromstring(archive.read("xl/sharedStrings.xml"))]
        relations = {r.get("Id"): r.get("Target") for r in ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))}
        for sheet in ET.fromstring(archive.read("xl/workbook.xml")).findall("m:sheets/m:sheet", NS):
            target = relations[sheet.get(RID)]
            target = target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/" + target)
            cells, formulas = {}, {}
            root = ET.fromstring(archive.read(target))
            for row_index, row in enumerate(root.findall("m:sheetData/m:row", NS), 1):
                for index, cell in enumerate(row.findall("m:c", NS), 1):
                    column, number = "", index
                    while number:
                        number, remainder = divmod(number - 1, 26)
                        column = chr(65 + remainder) + column
                    ref = cell.get("r", column + row.get("r", str(row_index)))
                    value = cell.find("m:v", NS)
                    inline = cell.find("m:is", NS)
                    text = value.text if value is not None else "".join(inline.itertext()) if inline is not None else ""
                    if cell.get("t") == "s":
                        text = strings[int(text)]
                    if text:
                        cells[ref] = text
                    formula = cell.find("m:f", NS)
                    if formula is not None:
                        formulas[ref] = formula.text
            result[sheet.get("name")] = {"cells": cells, "formulas": formulas,
                                             "state": sheet.get("state", "visible")}
    return result


def csv_rows(path, delimiter=","):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        yield from csv.DictReader(stream, delimiter=delimiter)


def number(value):
    if value in (None, ""):
        return None
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("Non-finite number")
    return value


def unique_rows(path, key, delimiter=","):
    result = {}
    for row in csv_rows(path, delimiter):
        code = row[key]
        if code in result:
            raise ValueError(f"Duplicate commune {code}: {path}")
        result[code] = row
    return result


def reconstruct(source_root=SOURCE_ROOT):
    root = Path(source_root)
    raw = root / "mobility-employment/idf-raw-sources"
    membership = unique_rows(raw / "zones_emploi_communes.csv", "codgeo", ";")
    members = defaultdict(list)
    for code, row in membership.items():
        members[row["ze2020"]].append(code)
    zones = {code: {} for code in sorted(members)}
    coverage = []

    # Quarter, category and population dimensions are selected explicitly.
    claims = {}
    for row in csv_rows(raw / "defm_ze_idf.csv", ";"):
        if (row["code_region"] != "11" or row["categorie"] != "ABC"
            or any(row[k] != "Total" for k in ("sexe", "tranche_d_age", "anciennete"))
            or row["type_de_donnees"] != "Brutes" or not row["date"].endswith("-T4")):
            continue
        code, year = row["code_zone_d_emploi"], row["date"][:4]
        if code not in zones or int(year) not in YEARS:
            continue
        key = code, year
        if key in claims:
            raise ValueError(f"Duplicate DEFM observation: {key}")
        claims[key] = number(row["nombre_de_demandeurs_d_emploi"])
    for code in zones:
        zones[code]["Demandeurs ABC"] = {str(y): claims.get((code, str(y))) for y in YEARS}

    unemployment = read_workbook(raw / "chomage-zone-2003-2025.xlsx")["txcho_ze"]["cells"]
    source_rows = {value: int(ref[1:]) for ref, value in unemployment.items() if re.fullmatch(r"A\d+", ref) and value in zones}
    headers = {value: re.sub(r"\d", "", ref) for ref, value in unemployment.items() if re.fullmatch(r"[A-Z]+5", ref) and value.isdigit()}
    for code in zones:
        zones[code]["Taux de chômage localisé"] = {
            str(y): number(unemployment.get(headers[str(y)] + str(source_rows[code]))) for y in YEARS}

    # Aggregate the actual raw sector observations, keeping blank-cell evidence.
    salaries = defaultdict(lambda: defaultdict(list))
    blanks = defaultdict(int)
    observed = set()
    for row in csv_rows(raw / "urssaf_effectifs_communes_idf.csv"):
        if row["code_region"] != "11":
            continue
        code = row["com"]
        observed.add(code)
        for year in YEARS:
            value = number(row[f"effectifs_salaries_{year}"])
            if value is None:
                blanks[str(year)] += 1
            else:
                salaries[code][str(year)].append(value)
    for code, communes in members.items():
        missing = sorted(set(communes) - observed)
        zones[code]["Salariés privés"] = {
            str(y): None if missing else round(math.fsum(v for c in communes for v in salaries[c][str(y)]), 1)
            for y in YEARS}
        if missing:
            coverage.append({"metric": "Salariés privés", "zone": code, "missing_communes": missing})
    coverage.append({"metric": "Salariés privés", "blank_sector_cells_by_year": dict(blanks),
                     "meaning": "Sum of reported values; blank sector cells are not established zeros"})

    def communal(metric, year, rows, field):
        for code, communes in members.items():
            missing = [c for c in communes if c not in rows or number(rows[c].get(field)) is None]
            value = None if missing else round(math.fsum(round(number(rows[c][field]), 1) for c in communes), 1)
            zones[code].setdefault(metric, {})[str(year)] = value
            if missing:
                coverage.append({"metric": metric, "year": str(year), "zone": code, "missing_communes": missing})

    census = unique_rows(raw / "actifs_emplois_2016_com.csv", "CODGEO")
    communal("Actifs occupés résidents", 2016, census, "P16_ACTOCC1564")
    communal("Emplois au lieu de travail", 2016, census, "C16_EMPLT")
    communal("Actifs occupés résidents", 2021, unique_rows(raw / "actifs_2021_com.csv", ""), "P21_ACTOCC1564")
    comparator = unique_rows(raw / "comparateur_territoires_idf.csv", "codgeo", ";")
    # The comparator gives Paris arrondissements, whereas the zone map uses Paris.
    paris = [row for code, row in comparator.items() if re.fullmatch(r"751(?:0[1-9]|1[0-9]|20)", code)]
    if "75056" not in comparator and len(paris) == 20:
        comparator["75056"] = {
            field: str(math.fsum(number(row[field]) for row in paris))
            for field in ("p14_emplt", "p20_emplt")}
    for year in (2014, 2020):
        communal("Emplois au lieu de travail", year, comparator, f"p{str(year)[2:]}_emplt")
    for year in range(2017, 2022):
        communal("Postes salariés Flores", year,
                  unique_rows(raw / f"flores/flores_{year}_na17_com_idf.csv", "com"), "EFF_TOT")
    return {"zones": zones, "coverage": coverage}


def compare(result, workbook):
    cells = read_workbook(workbook)["Zones d’emploi"]["cells"]
    comparisons = []
    years = {re.sub(r"\d", "", ref): value for ref, value in cells.items()
             if re.fullmatch(r"[D-O]5", ref)}
    for ref, code in cells.items():
        if not re.fullmatch(r"A\d+", ref) or code not in result["zones"]:
            continue
        row = ref[1:]
        metric = cells["C" + row]
        rebuilt = result["zones"][code].get(metric, {})
        for column, year in years.items():
            expected = number(cells.get(column + row))
            actual = rebuilt.get(year)
            same = expected == actual or (expected is not None and actual is not None and abs(expected-actual) < 0.000001)
            comparisons.append({"cell": column + row, "zone": code, "metric": metric,
                                "year": year, "workbook": expected, "rebuilt": actual,
                                "matches": same})
    return comparisons


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source-root", type=Path, default=SOURCE_ROOT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.suffix.lower() != ".json":
        parser.error("Output must be a JSON report, never a source workbook")
    if args.output.resolve().is_relative_to(args.source_root.resolve()):
        parser.error("Output must be outside the source tree")
    result = reconstruct(args.source_root)
    workbook = args.source_root / "jobseekers/Recap_mobilites_emploi_IDF.xlsx"
    comparisons = compare(result, workbook)
    result["comparison"] = comparisons
    result["summary"] = {"compared_cells": len(comparisons), "mismatches": sum(not c["matches"] for c in comparisons)}
    result["workbook_inventory"] = {
        str(path.relative_to(args.source_root)): read_workbook(path)
        for path in [workbook, args.source_root / "employment-centers/indicateurs-departementaux-2025-2026.xlsx"]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"]))


if __name__ == "__main__":
    main()
