"""
06_tester_h16_h17_solutions.py : test de H16 (potentiel du vélo) et H17 (pôles
d'emploi sans desserte de nuit), selon le protocole écrit dans hypotheses.md
AVANT l'ouverture des données.

H16 : une part importante des trajets de banlieue à banlieue faits en voiture
      font moins de 5 km (à vol d'oiseau), donc seraient faisables à vélo.
H17 : il existe des pôles d'emploi des métiers sur place (au moins 2 000
      emplois d'employés et d'ouvriers) sans aucun passage entre minuit et 5h.

Entrées : data/brut/insee_mobpro_2023/, data/brut/geo_communes_idf/,
          resultats/05_h4b_h10/offre_relative_par_commune.csv (sortie du script 05,
          à lancer avant celui-ci)
Sorties : console + CSV dans resultats/06_h16_h17/

Lancer depuis la racine du projet :
    .venv\\Scripts\\python.exe src\\06_tester_h16_h17_solutions.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Constantes : toutes viennent du protocole (hypotheses.md)
# ---------------------------------------------------------------------------

RACINE = Path(__file__).resolve().parent.parent
BRUT = RACINE / "data" / "brut"

# H16
SEUIL_DISTANCE_KM = 5.0         # trajets "courts" (seuil des publications INSEE)
SEUIL_PART_COURTS_PCT = 20.0    # critère 1 : au moins 20 % des trajets en voiture
SEUIL_PERSONNES = 100_000       # critère 2 : au moins 100 000 personnes concernées
RAYON_TERRE_KM = 6371.0         # rayon moyen de la Terre, pour la distance à vol d'oiseau

# H17
SEUIL_EMPLOIS_SUR_PLACE = 2000  # emplois d'employés + ouvriers pour parler de "pôle"
SEUIL_NB_COMMUNES = 5           # confirmée à partir de 5 communes

CODE_VOITURE = "5"              # variable TRANS du recensement
GS_NOMS = {"3": "Cadres", "5": "Employés", "6": "Ouvriers"}


# ---------------------------------------------------------------------------
# Fonctions
# ---------------------------------------------------------------------------

def charger_centres_communes() -> pd.DataFrame:
    """Coordonnées du centre de chaque commune d'Île-de-France (geo.api.gouv.fr).

    Le fichier donne [longitude, latitude] : on les sépare en deux colonnes
    nommées, pour ne pas les inverser par erreur.
    """
    with open(BRUT / "geo_communes_idf" / "communes_idf_centres.json", encoding="utf-8") as f:
        communes = json.load(f)
    return pd.DataFrame([{"code_commune": c["code"], "nom": c["nom"],
                          "lon": c["centre"]["coordinates"][0], "lat": c["centre"]["coordinates"][1]}
                         for c in communes]).set_index("code_commune")


def distance_vol_oiseau_km(lat1, lon1, lat2, lon2):
    """Distance à vol d'oiseau en km (formule de haversine), sur des colonnes entières.

    Pourquoi haversine : elle tient compte de la courbure de la Terre. À
    l'échelle de l'Île-de-France l'écart avec une formule plane est faible,
    mais celle-ci est la formule de référence et reste juste partout.
    """
    lat1, lon1, lat2, lon2 = (np.radians(x) for x in (lat1, lon1, lat2, lon2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 2 * RAYON_TERRE_KM * np.arcsin(np.sqrt(a))


def charger_trajets_banlieue() -> pd.DataFrame:
    """Trajets des actifs qui habitent et travaillent en IDF, hors Paris des deux côtés."""
    actifs = pd.read_parquet(BRUT / "insee_mobpro_2023" / "RP2023_mobpro.parquet",
                             columns=["COMMUNE", "DCLT", "REGION", "REGLT", "TRANS", "GS", "IPONDI"],
                             filters=[("REGION", "==", "11"), ("REGLT", "==", "11")])
    hors_paris = ~actifs["COMMUNE"].str.startswith("75") & ~actifs["DCLT"].str.startswith("75")
    return actifs[hors_paris].copy()


def tester_h16(trajets: pd.DataFrame, centres: pd.DataFrame) -> pd.DataFrame:
    """Part des trajets de banlieue à banlieue en voiture qui font moins de 5 km, par métier."""
    autre_commune = trajets[trajets["COMMUNE"] != trajets["DCLT"]].copy()
    # Ajout des coordonnées du domicile puis du lieu de travail
    # Les colonnes du lieu de travail sont renommées avant la jointure, pour ne
    # pas dépendre de l'option rsuffix (bientôt supprimée par pandas)
    centres_travail = centres[["lat", "lon"]].rename(columns={"lat": "lat_travail", "lon": "lon_travail"})
    autre_commune = autre_commune.join(centres[["lat", "lon"]], on="COMMUNE").join(centres_travail, on="DCLT")
    sans_coordonnees = autre_commune["lat"].isna() | autre_commune["lat_travail"].isna()
    if sans_coordonnees.any():
        print(f"Attention : {sans_coordonnees.sum()} lignes sans coordonnées, écartées")
        autre_commune = autre_commune[~sans_coordonnees]
    autre_commune["distance_km"] = distance_vol_oiseau_km(autre_commune["lat"], autre_commune["lon"],
                                                          autre_commune["lat_travail"], autre_commune["lon_travail"])

    en_voiture = autre_commune[autre_commune["TRANS"] == CODE_VOITURE]
    lignes = []
    # "Ensemble" d'abord (c'est lui qui donne le verdict), puis le détail par métier
    for nom, sous_ensemble in [("Ensemble", en_voiture)] + [
            (GS_NOMS[code], en_voiture[en_voiture["GS"] == code]) for code in GS_NOMS]:
        courts = sous_ensemble["distance_km"] < SEUIL_DISTANCE_KM
        lignes.append({"groupe": nom,
                       "trajets_voiture": sous_ensemble["IPONDI"].sum(),
                       "dont_moins_5km": sous_ensemble.loc[courts, "IPONDI"].sum(),
                       "part_moins_5km_pct": 100 * sous_ensemble.loc[courts, "IPONDI"].sum() / sous_ensemble["IPONDI"].sum(),
                       "distance_mediane_km": sous_ensemble["distance_km"].median()})
    return pd.DataFrame(lignes)


def tester_h17(centres: pd.DataFrame) -> pd.DataFrame:
    """Communes d'au moins 2 000 emplois d'employés et d'ouvriers, avec leur offre de nuit."""
    communes = pd.read_csv(RACINE / "resultats" / "05_h4b_h10" / "offre_relative_par_commune.csv",
                           dtype={"code_commune": str}, encoding="utf-8-sig").set_index("code_commune")
    communes["emplois_sur_place"] = communes["emplois"] * (communes["part_ouvriers_pct"]
                                                          + communes["part_employes_pct"]) / 100
    poles = communes[communes["emplois_sur_place"] >= SEUIL_EMPLOIS_SUR_PLACE].copy()
    poles["nom"] = centres["nom"].reindex(poles.index)
    poles.loc[poles.index == "75056", "nom"] = "Paris"
    return poles.sort_values("emplois_sur_place", ascending=False)


def main() -> None:
    """Lance H16 puis H17 et affiche leur verdict."""
    centres = charger_centres_communes()
    dossier_sortie = RACINE / "resultats" / "06_h16_h17"
    dossier_sortie.mkdir(parents=True, exist_ok=True)

    # --- H16 ---
    trajets = charger_trajets_banlieue()
    meme_commune_voiture = trajets[(trajets["COMMUNE"] == trajets["DCLT"]) & (trajets["TRANS"] == CODE_VOITURE)]
    h16 = tester_h16(trajets, centres)
    print("=== H16 : trajets de banlieue à banlieue (deux communes différentes) faits en voiture ===")
    print(h16.to_string(index=False, float_format=lambda x: f"{x:,.1f}"))
    ensemble = h16.iloc[0]
    criteres = int(ensemble["part_moins_5km_pct"] >= SEUIL_PART_COURTS_PCT) + int(ensemble["dont_moins_5km"] >= SEUIL_PERSONNES)
    print(f"Verdict H16 : {['RÉFUTÉE', 'NUANCÉE', 'CONFIRMÉE'][criteres]}")
    print(f"À part : {meme_commune_voiture['IPONDI'].sum():,.0f} personnes vont en voiture "
          f"travailler dans leur propre commune (hors Paris)".replace(",", " "))
    h16.to_csv(dossier_sortie / "h16_trajets_courts_voiture.csv", index=False, encoding="utf-8-sig")

    # --- H17 ---
    poles = tester_h17(centres)
    sans_nuit = poles[poles["nuit_par_heure"] == 0]
    nb = len(sans_nuit)
    verdict = "CONFIRMÉE" if nb >= SEUIL_NB_COMMUNES else ("NUANCÉE" if nb >= 1 else "RÉFUTÉE")
    print(f"\n=== H17 : pôles d'emploi des métiers sur place (>= {SEUIL_EMPLOIS_SUR_PLACE} emplois "
          f"d'employés et d'ouvriers) ===")
    print(f"Pôles : {len(poles)} | sans aucun passage entre minuit et 5h : {nb} -> Verdict H17 : {verdict}")
    colonnes = ["nom", "emplois_sur_place", "part_ouvriers_pct", "nuit_par_heure", "offre_nuit_relative"]
    print("\nPôles sans desserte de nuit, du plus grand au plus petit :")
    print(sans_nuit[colonnes].to_string(float_format=lambda x: f"{x:,.1f}"))
    print("\nPour comparaison, les 10 plus grands pôles :")
    print(poles.head(10)[colonnes].to_string(float_format=lambda x: f"{x:,.2f}"))
    poles.to_csv(dossier_sortie / "h17_poles_emploi_sur_place.csv", encoding="utf-8-sig")
    print(f"\nCSV enregistrés dans : {dossier_sortie}")


if __name__ == "__main__":
    main()
