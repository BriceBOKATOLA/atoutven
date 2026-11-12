"""Rebuild the 2016/2024 jobseeker extract from the local Dares CSV."""
import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'datasets/src/mobility-employment/idf-raw-sources/defm_communes_idf.csv'


def build(source):
    values = {}
    with source.open(encoding='utf-8-sig', newline='') as stream:
        for row in csv.DictReader(stream, delimiter=';'):
            if (row['date'] not in ('2016-T4', '2024-T4') or
                (row['type_de_donnees'], row['categorie'], row['sexe'], row['tranche_d_age'])
                    != ('Brutes', 'ABC', 'Total', 'Total')):
                continue
            key = (row['code_commune'], row['date'])
            if key in values:
                raise ValueError(f'Duplicate record: {key}')
            value = row['nombre_de_demandeurs_d_emploi'].strip()
            values[key] = int(value) if value else None
    records = []
    codes = sorted(code for code, date in values if date == '2016-T4')
    for code in codes:
        first = values[code, '2016-T4']
        if first is None or first < 300:
            continue
        second = values.get((code, '2024-T4'))
        if second is None:
            raise ValueError(f'Missing 2024 value for {code}')
        records.append(f'{code}:{first}:{second}')
    if not records:
        raise ValueError('No qualifying records found')
    return ','.join(records) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=SOURCE)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve() == args.source.resolve():
        parser.error('Output must differ from the source file')
    result = build(args.source)
    args.output.write_text(result, encoding='utf-8')


if __name__ == '__main__':
    main()
