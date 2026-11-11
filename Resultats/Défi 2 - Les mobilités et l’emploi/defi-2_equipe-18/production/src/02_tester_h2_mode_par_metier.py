"""
02_tester_h2_mode_par_metier.py : test de l'hypothèse H2 (et de la contre-hypothèse C3).

H2 : les métiers "sur place" (employés, ouvriers) prennent plus les transports
     en commun et moins la voiture que les cadres.
C3 : à l'inverse, ces métiers utilisent surtout la voiture.

Méthode :
  1. Part de chaque mode de transport par groupe socioprofessionnel (GS),
     pour tous les actifs résidant en Île-de-France.
  2. Même calcul À LIEU DE RÉSIDENCE ÉGAL (Paris / petite couronne / grande
     couronne). Pourquoi : les cadres habitent plus souvent à Paris, où presque
     tout le monde prend les transports en commun. Sans ce contrôle, on
     risquerait d'attribuer au métier un effet qui vient du lieu de résidence.

Entrée  : data/brut/insee_mobpro_2023/ (recensement 2023, source principale)
Sorties : console + CSV dans resultats/02_h2/

Lancer depuis la racine du projet :
    .venv\\Scripts\\python.exe src\\02_tester_h2_mode_par_metier.py
"""

# importlib : nécessaire pour réutiliser les fonctions de 01_explorer_mobpro.py,
# car un nom de fichier qui commence par un chiffre ne peut pas être importé
# avec un simple "import". On réutilise plutôt que de copier le code.
import importlib
import sys
from pathlib import Path

import pandas as pd

# On ajoute src/ au chemin de recherche des modules pour trouver 01_explorer_mobpro
sys.path.insert(0, str(Path(__file__).resolve().parent))
etape_01 = importlib.import_module("01_explorer_mobpro")

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

RACINE = etape_01.RACINE
ANNEE = "2023"  # source principale (voir journal_des_choix.md)
CODE_IDF = etape_01.CODE_IDF
SEUIL_PRUDENCE_INSEE = etape_01.SEUIL_PRUDENCE_INSEE

# Les deux premiers caractères du code commune donnent le département.
# Découpage classique de l'Île-de-France en trois couronnes.
COURONNES = {
    "75": "Paris",
    "92": "Petite couronne", "93": "Petite couronne", "94": "Petite couronne",
    "77": "Grande couronne", "78": "Grande couronne",
    "91": "Grande couronne", "95": "Grande couronne",
}

# Codes TRANS (dictionnaire INSEE) des deux modes au coeur de H2 et C3
CODE_TRANSPORTS_COMMUN = "6"
CODE_VOITURE = "5"

# Agriculteurs (GS = 1) écartés : environ 5 000 personnes en Île-de-France,
# trop peu pour être comparés, surtout une fois découpés par couronne.
GS_ECARTES = ["1"]


# ---------------------------------------------------------------------------
# Fonctions
# ---------------------------------------------------------------------------

def charger_donnees() -> pd.DataFrame:
    """Charge les résidents d'Île-de-France avec leur couronne de résidence.

    On lit COMMUNE en plus des colonnes de l'étape 01, pour en déduire
    la couronne. Les codes sont convertis en texte comme à l'étape 01.
    """
    chemin = RACINE / "data" / "brut" / f"insee_mobpro_{ANNEE}" / f"RP{ANNEE}_mobpro.parquet"
    donnees = pd.read_parquet(
        chemin,
        columns=["COMMUNE", "REGION", "IPONDI", "TRANS", "GS"],
        filters=[("REGION", "==", CODE_IDF)],
    )
    donnees = etape_01.normaliser_codes(donnees)
    donnees["couronne"] = donnees["COMMUNE"].str[:2].map(COURONNES)
    # Contrôle : toute commune d'Île-de-France doit avoir une couronne.
    # Si ce n'est pas le cas, on s'arrête plutôt que de perdre des lignes en silence.
    sans_couronne = donnees["couronne"].isna().sum()
    if sans_couronne:
        raise ValueError(f"{sans_couronne} lignes sans couronne : code département inattendu")
    return donnees[~donnees["GS"].isin(GS_ECARTES)]


def parts_modales(donnees: pd.DataFrame, groupes: list) -> pd.DataFrame:
    """Part (en %) des transports en commun et de la voiture, par groupe.

    Pondéré par IPONDI (une ligne représente plusieurs personnes).
    Renvoie aussi le nombre de réponses réelles et un indicateur de prudence
    pour juger la fiabilité de chaque case.
    """
    total = donnees.groupby(groupes)["IPONDI"].agg(effectif_pondere="sum", nb_lignes="size")
    tc = donnees[donnees["TRANS"] == CODE_TRANSPORTS_COMMUN].groupby(groupes)["IPONDI"].sum()
    voiture = donnees[donnees["TRANS"] == CODE_VOITURE].groupby(groupes)["IPONDI"].sum()
    resultat = total.copy()
    resultat["part_tc_pct"] = 100 * tc / total["effectif_pondere"]
    resultat["part_voiture_pct"] = 100 * voiture / total["effectif_pondere"]
    resultat["prudence"] = resultat["effectif_pondere"] < SEUIL_PRUDENCE_INSEE
    return resultat.reset_index()


def ajouter_libelles_gs(tableau: pd.DataFrame, libelles: dict) -> pd.DataFrame:
    """Remplace les codes GS par leur libellé lu dans le dictionnaire INSEE."""
    tableau["GS"] = tableau["GS"].map(libelles["GS"])
    return tableau


def main() -> None:
    """Calcule les parts modales par métier, sans puis avec contrôle du lieu."""
    libelles = etape_01.charger_libelles(
        RACINE / "data" / "brut" / f"insee_mobpro_{ANNEE}" / f"varmod_mobpro_{ANNEE}.csv"
    )
    donnees = charger_donnees()
    dossier_sortie = RACINE / "resultats" / "02_h2"
    dossier_sortie.mkdir(parents=True, exist_ok=True)

    # 1. Sans contrôle du lieu de résidence
    global_gs = ajouter_libelles_gs(parts_modales(donnees, ["GS"]), libelles)
    print(f"=== H2, recensement {ANNEE} : part des modes par métier (résidents IDF) ===")
    print(global_gs.sort_values("part_tc_pct", ascending=False)
          .to_string(index=False, float_format=lambda x: f"{x:,.1f}"))
    global_gs.to_csv(dossier_sortie / "parts_modales_par_gs.csv", index=False, encoding="utf-8-sig")

    # 2. À lieu de résidence égal : un tableau métier x couronne pour chaque mode
    par_couronne = ajouter_libelles_gs(parts_modales(donnees, ["couronne", "GS"]), libelles)
    par_couronne.to_csv(dossier_sortie / "parts_modales_par_gs_et_couronne.csv",
                        index=False, encoding="utf-8-sig")
    ordre_couronnes = ["Paris", "Petite couronne", "Grande couronne"]
    for colonne, titre in [("part_tc_pct", "Transports en commun"), ("part_voiture_pct", "Voiture")]:
        tableau = par_couronne.pivot(index="GS", columns="couronne", values=colonne)[ordre_couronnes]
        print(f"\n--- {titre} (%), à lieu de résidence égal ---")
        print(tableau.round(1).to_string())

    # Signalement des cases peu fiables (aucune attendue avec ces grands groupes)
    nb_prudence = int(par_couronne["prudence"].sum())
    print(f"\nCases sous le seuil de prudence INSEE ({SEUIL_PRUDENCE_INSEE}) : {nb_prudence}")
    print(f"CSV enregistrés dans : {dossier_sortie}")


if __name__ == "__main__":
    main()
