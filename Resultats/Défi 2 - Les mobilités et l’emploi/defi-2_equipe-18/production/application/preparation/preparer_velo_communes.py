"""
preparer_velo_communes.py : part des trajets en voiture de moins de 5 km, par commune de résidence (page 5).

Même population et même méthode que le script 06 (trajets de banlieue à banlieue en voiture, distance à vol
d'oiseau entre les centres des communes, seuil de 5 km). On réutilise ses fonctions plutôt que de les réécrire.
Les communes avec moins de 200 trajets en voiture sont écartées (seuil de prudence de l'INSEE) : ce sont les
communes « effectif faible » de la carte.

La maquette validée avait la liste des 5 premières communes écrite en dur ; ce script la recalcule.

Entrées : production/data/brut/ (recensement 2023, centres des communes)
Sortie  : application/donnees/velo_par_commune.csv

Lancer depuis le dossier application/ : python preparation/preparer_velo_communes.py
"""

import importlib.util
from pathlib import Path

import pandas as pd

APPLICATION = Path(__file__).resolve().parents[1]
PRODUCTION = APPLICATION.parent
SORTIE = APPLICATION / "donnees" / "velo_par_commune.csv"
SEUIL_EFFECTIF = 200   # trajets en voiture minimum pour afficher une commune (seuil de prudence de l'INSEE)


def charger_module(chemin: Path):
    """Réutilise les fonctions d'un script numéroté (nom commençant par un chiffre)."""
    spec = importlib.util.spec_from_file_location(chemin.stem, chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    """Calcule, pour chaque commune de résidence, la part des trajets en voiture de moins de 5 km."""
    s06 = charger_module(PRODUCTION / "src" / "06_tester_h16_h17_solutions.py")
    centres = s06.charger_centres_communes()
    trajets = s06.charger_trajets_banlieue()
    autre = trajets[(trajets["COMMUNE"] != trajets["DCLT"]) & (trajets["TRANS"] == s06.CODE_VOITURE)].copy()
    travail = centres[["lat", "lon"]].rename(columns={"lat": "lat_travail", "lon": "lon_travail"})
    autre = autre.join(centres[["lat", "lon", "nom"]], on="COMMUNE").join(travail, on="DCLT").dropna(subset=["lat", "lat_travail"])
    autre["court"] = s06.distance_vol_oiseau_km(autre["lat"], autre["lon"], autre["lat_travail"], autre["lon_travail"]) \
        < s06.SEUIL_DISTANCE_KM
    par_commune = autre.groupby(["COMMUNE", "nom"]).apply(
        lambda d: pd.Series({"trajets_voiture": d["IPONDI"].sum(),
                             "part_moins_5km_pct": 100 * d.loc[d["court"], "IPONDI"].sum() / d["IPONDI"].sum()}),
        include_groups=False).reset_index()
    par_commune = par_commune[par_commune["trajets_voiture"] >= SEUIL_EFFECTIF]
    par_commune = par_commune.sort_values("part_moins_5km_pct", ascending=False).round({"trajets_voiture": 0,
                                                                                          "part_moins_5km_pct": 2})
    par_commune.rename(columns={"COMMUNE": "code_commune"}).to_csv(SORTIE, index=False, encoding="utf-8-sig")
    print(par_commune.head(6).to_string(index=False))


if __name__ == "__main__":
    main()
