"""Reconstruct annual DEFM group series from local commune data.

Example (no download; output is required and replaces that file):
    python3 production/scripts/build_defm_series.py --output /tmp/series_defm.json

The CSV must contain ABC, Total sex, Total age, Brutes, T4 observations for
2015–2025. Sum all communes for IDF, code 75056 for Paris, each group's
communes for its series, and the complement of their union and Paris for
the remaining region. Do not apply the 300-person threshold used by the
separate 2016/2024 commune extract. Groups remain a prepared input: this
script does not reconstruct their spatial selection.

NOTE is copied verbatim from the retained series_defm_dares.json metadata.
It is historical documentation, not information inferred from the CSV.
Missing observations and duplicate commune/year keys are errors, never zero.
Compatibility exceptions: 93059 (Pierrefitte-sur-Seine, T11) and 91182
(Courcouronnes, T12) are absent from all years in the retained CSV, although
they appear in the prepared groups. Exclude them when absent from all years
to reproduce the snapshot. These historical series are incomplete; an
exclusion does not establish a zero count.
"""
import argparse
import csv
import json
from pathlib import Path
import re
import sys

DATASETS = Path(__file__).resolve().parents[1] / "datasets"
DEFAULT_SOURCE = DATASETS / "src/mobility-employment/idf-raw-sources/defm_communes_idf.csv"
DEFAULT_GROUPS = DATASETS / "clean/shared/groupes_lignes.json"
YEARS = list(range(2015, 2026))
HISTORICAL_EXCLUSIONS = {"T11 (2017)": {"93059"}, "T12 (2023)": {"91182"}}
NOTE = ("DEFM catégories ABC, 4e trimestre, données brutes. 2015 incomplet "
        "(rupture de série), 2025 gonflé par l'inscription automatique "
        "(loi pour le plein emploi) : comparaison retenue 2016-2024.")


def build_series(source, groups_path):
    """Return validated historical series, or fail before producing output."""
    values = {year: {} for year in YEARS}
    dimensions = {"categorie": "ABC", "sexe": "Total", "tranche_d_age": "Total",
                  "type_de_donnees": "Brutes"}
    required = {"date", "code_commune", "nombre_de_demandeurs_d_emploi", *dimensions}
    with Path(source).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter=";")
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Missing required CSV columns")
        for line, row in enumerate(reader, 2):
            if any(row[key] != expected for key, expected in dimensions.items()):
                raise ValueError(f"Unexpected dimensions on CSV line {line}")
            if not re.fullmatch(r"\d{4}-T4", row["date"] or ""):
                raise ValueError(f"Expected a T4 date on CSV line {line}")
            year = int(row["date"][:4])
            if year not in values:
                raise ValueError(f"Unexpected year on CSV line {line}: {year}")
            code = row["code_commune"]
            if not re.fullmatch(r"\d{5}", code or ""):
                raise ValueError(f"Invalid commune code on CSV line {line}")
            if code in values[year]:
                raise ValueError(f"Duplicate commune/year: {code}/{year}")
            raw = row["nombre_de_demandeurs_d_emploi"]
            if not re.fullmatch(r"\d+", raw or ""):
                raise ValueError(f"Missing or invalid count for {code}/{year}")
            values[year][code] = int(raw)

    communes = set().union(*(set(observations) for observations in values.values()))
    if not communes or "75056" not in communes:
        raise ValueError("Missing communes or Paris (75056)")
    for year, observations in values.items():
        missing = communes - observations.keys()
        if missing:
            raise ValueError(f"Missing commune observations for {year}: {', '.join(sorted(missing))}")

    groups = json.loads(Path(groups_path).read_text(encoding="utf-8"))
    if not isinstance(groups, dict) or not groups:
        raise ValueError("Expected a nonempty group dictionary")
    reserved = {"annees", "note", "IDF", "IDF hors desservies et Paris", "Paris"}
    group_codes = {}
    for name, group in groups.items():
        if name in reserved or not name:
            raise ValueError(f"Invalid group name: {name}")
        codes = group.get("codes") if isinstance(group, dict) else None
        if (not isinstance(codes, list) or not codes
                or any(not isinstance(code, str) for code in codes)):
            raise ValueError(f"Expected commune codes for group {name}")
        if len(codes) != len(set(codes)):
            raise ValueError(f"Duplicate commune in group {name}")
        missing = set(codes) - communes
        # The source omits this former commune in every year. Preserve the
        # snapshot's omission without silently accepting other missing codes.
        exclusions = HISTORICAL_EXCLUSIONS.get(name, set())
        missing -= exclusions
        if missing:
            raise ValueError(f"Missing communes for group {name}: {', '.join(sorted(missing))}")
        group_codes[name] = set(codes) & communes

    served = set().union(*group_codes.values())
    scopes = {"IDF": communes,
              "IDF hors desservies et Paris": communes - served - {"75056"},
              "Paris": {"75056"}, **group_codes}
    return {"annees": YEARS, "note": NOTE,
            **{name: [sum(values[year][code] for code in codes) for year in YEARS]
               for name, codes in scopes.items()}}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--groups", type=Path, default=DEFAULT_GROUPS)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve() in {args.source.resolve(), args.groups.resolve()}:
        parser.error("Output must differ from both input files")
    try:
        result = build_series(args.source, args.groups)
    except (ValueError, OSError) as error:
        parser.exit(1, f"Cannot reconstruct DEFM series: {error}\n")
    print("Warning: compatibility excludes 93059 from T11 (2017) and 91182 "
          "from T12 (2023) when absent from every source year. The retained "
          "source omits both; those historical series are incomplete.", file=sys.stderr)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
