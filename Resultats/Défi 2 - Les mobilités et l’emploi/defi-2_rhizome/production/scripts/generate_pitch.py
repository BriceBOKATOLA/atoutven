"""Génère les cinq planches dans pitch/."""

import subprocess
import sys
from pathlib import Path


PRODUCTION = Path(__file__).resolve().parent.parent
SCRIPTS = [
    "01_transport_extensions.py",
    "02_employment_growth.py",
    "04_jobseekers.py",
    "05_transport_networks.py",
    "06_employment_centers.py",
]


def main():
    for script in SCRIPTS:
        print(f"Génération : {script}", flush=True)
        result = subprocess.run([sys.executable, str(PRODUCTION / "scripts" / script)])
        if result.returncode:
            print(f"Échec de {script} (code {result.returncode}).", file=sys.stderr)
            return result.returncode
    print("Les cinq planches sont disponibles dans production/pitch/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
