"""
07_tester_h21_emplois_gares.py : test de H21, selon le protocole écrit dans
hypotheses.md (section G) AVANT l'ouverture des données.

H21 : hors de Paris, les emplois des employés et des ouvriers sont plus souvent
      que ceux des cadres dans des communes sans gare (métro, train/RER, tramway).

Indicateur complémentaire (sans verdict) : part de la voiture dans les trajets
de banlieue à banlieue, selon que la commune de travail a une gare ou non.

Entrées : data/brut/insee_mobpro_2023/RP2023_mobpro.parquet
          data/brut/idfm_offre_hebdo_2025/offre_hebdomadaire_moyenne_hors_vacances.csv
Sorties : console + CSV dans resultats/07_h21/

Lancer depuis la racine du projet :
    .venv\\Scripts\\python.exe src\\07_tester_h21_emplois_gares.py
"""

from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Constantes : toutes viennent du protocole (hypotheses.md, section G)
# ---------------------------------------------------------------------------

RACINE = Path(__file__).resolve().parent.parent
BRUT = RACINE / "data" / "brut"
SORTIE = RACINE / "resultats" / "07_h21"

# Modes qui font d'une commune une "commune avec gare". Le bus est exclu car il
# dessert presque toutes les communes ; le funiculaire (Montmartre) aussi.
MODES_FERRES = {"Métro", "Train", "Tramway"}
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

SEUIL_CONFIRMEE_PTS = 5.0   # écart minimal pour "confirmée"
SEUIL_NUANCEE_PTS = 2.0     # écart minimal pour "nuancée"

CODE_VOITURE = "5"          # variable TRANS du recensement
GS_NOMS = {"3": "Cadres", "5": "Employés", "6": "Ouvriers"}


# ---------------------------------------------------------------------------
# Fonctions
# ---------------------------------------------------------------------------

def communes_avec_gare() -> set:
    """Codes INSEE des communes ayant au moins un arrêt ferré avec un passage dans la semaine.

    On lit seulement les colonnes utiles : le fichier compte 1,3 million de lignes.
    """
    colonnes = ["libelle_mode_ligne", "code_commune"] + [f"nb_courses_{j}" for j in JOURS]
    offre = pd.read_csv(BRUT / "idfm_offre_hebdo_2025" / "offre_hebdomadaire_moyenne_hors_vacances.csv",
                        sep=";", usecols=colonnes, dtype={"code_commune": str}, encoding="utf-8-sig")
    ferre = offre[offre["libelle_mode_ligne"].isin(MODES_FERRES)]
    # Un arrêt compte s'il a au moins un passage dans la semaine (somme des 7 jours)
    ferre = ferre[ferre[[f"nb_courses_{j}" for j in JOURS]].sum(axis=1) > 0]
    return set(ferre["code_commune"].dropna())


def charger_emplois() -> pd.DataFrame:
    """Personnes qui travaillent en Île-de-France hors Paris (toute résidence), recensement 2023."""
    actifs = pd.read_parquet(BRUT / "insee_mobpro_2023" / "RP2023_mobpro.parquet",
                             columns=["COMMUNE", "DCLT", "REGION", "REGLT", "TRANS", "GS", "IPONDI"],
                             filters=[("REGLT", "==", "11")])
    return actifs[~actifs["DCLT"].str.startswith("75")].copy()


def tester_h21(emplois: pd.DataFrame, gares: set) -> pd.DataFrame:
    """Part des emplois situés dans une commune sans gare, par métier."""
    emplois["travail_avec_gare"] = emplois["DCLT"].isin(gares)
    lignes = []
    groupes = [("Cadres", emplois["GS"] == "3"), ("Employés", emplois["GS"] == "5"),
               ("Ouvriers", emplois["GS"] == "6"), ("Employés et ouvriers", emplois["GS"].isin(["5", "6"]))]
    for nom, masque in groupes:
        sous = emplois[masque]
        sans_gare = sous.loc[~sous["travail_avec_gare"], "IPONDI"].sum()
        lignes.append({"groupe": nom, "emplois": sous["IPONDI"].sum(), "emplois_sans_gare": sans_gare,
                       "part_sans_gare_pct": 100 * sans_gare / sous["IPONDI"].sum()})
    return pd.DataFrame(lignes)


def voiture_selon_gare(emplois: pd.DataFrame) -> pd.DataFrame:
    """Part de la voiture, trajets de banlieue à banlieue, selon la présence d'une gare au lieu de travail."""
    banlieue = emplois[(emplois["REGION"] == "11") & ~emplois["COMMUNE"].str.startswith("75")
                       & (emplois["COMMUNE"] != emplois["DCLT"])]
    lignes = []
    for code, nom in GS_NOMS.items():
        for avec_gare in (True, False):
            sous = banlieue[(banlieue["GS"] == code) & (banlieue["travail_avec_gare"] == avec_gare)]
            voiture = sous.loc[sous["TRANS"] == CODE_VOITURE, "IPONDI"].sum()
            lignes.append({"groupe": nom, "commune_de_travail": "avec gare" if avec_gare else "sans gare",
                           "trajets": sous["IPONDI"].sum(), "part_voiture_pct": 100 * voiture / sous["IPONDI"].sum()})
    return pd.DataFrame(lignes)


def main() -> None:
    """Calcule H21, applique les critères du protocole et enregistre les résultats."""
    SORTIE.mkdir(parents=True, exist_ok=True)
    gares = communes_avec_gare()
    print(f"Communes d'IDF avec au moins une gare (métro, train/RER, tram) : {len(gares)}")

    emplois = charger_emplois()
    resultat = tester_h21(emplois, gares)
    print("\nH21 : emplois hors Paris situés dans une commune sans gare")
    print(resultat.round(1).to_string(index=False))

    ecart = (resultat.loc[resultat["groupe"] == "Employés et ouvriers", "part_sans_gare_pct"].iloc[0]
             - resultat.loc[resultat["groupe"] == "Cadres", "part_sans_gare_pct"].iloc[0])
    verdict = ("confirmée" if ecart >= SEUIL_CONFIRMEE_PTS
               else "nuancée" if ecart >= SEUIL_NUANCEE_PTS else "réfutée")
    print(f"\nÉcart employés et ouvriers - cadres : {ecart:.1f} points -> H21 {verdict}")

    voiture = voiture_selon_gare(emplois)
    print("\nPart de la voiture, banlieue à banlieue, selon la commune de travail")
    print(voiture.round(1).to_string(index=False))

    resultat.to_csv(SORTIE / "h21_emplois_sans_gare.csv", index=False, encoding="utf-8-sig")
    voiture.to_csv(SORTIE / "voiture_selon_gare_destination.csv", index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    main()
