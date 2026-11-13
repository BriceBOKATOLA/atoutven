"""
01_explorer_mobpro.py : première exploration du fichier INSEE des trajets domicile-travail.

But : connaître les données AVANT de tester la moindre hypothèse.
On garde les actifs qui habitent en Île-de-France, puis on regarde :
  - combien de personnes ils représentent (après pondération) ;
  - comment ils vont au travail (TRANS) ;
  - leur groupe socioprofessionnel (GS) ;
  - leur type de contrat (EMPL), pour savoir si les alternants sont repérables.

Entrée  : data/brut/insee_mobpro_<ANNEE>/RP<ANNEE>_mobpro.parquet (+ son dictionnaire varmod)
Sorties : affichage console + un CSV par variable dans resultats/01_exploration/<ANNEE>/

Lancer depuis la racine du projet :
    .venv\\Scripts\\python.exe src\\01_explorer_mobpro.py --annee 2023
"""

# argparse : permet de choisir l'année en ligne de commande, sans modifier le code
import argparse
# Path : construit des chemins qui marchent sous Windows comme sous Mac/Linux
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Constantes (aucune valeur "magique" au milieu du code)
# ---------------------------------------------------------------------------

# Racine du projet = dossier parent de src/. Ainsi le script fonctionne
# quel que soit le dossier depuis lequel on le lance.
RACINE = Path(__file__).resolve().parent.parent

# Code INSEE de la région Île-de-France (variable REGION = région de résidence)
CODE_IDF = "11"

# Seuil de prudence donné par l'INSEE : en dessous de 200 personnes
# (après pondération), un effectif est peu fiable car il repose sur trop
# peu de réponses réelles. On le signale au lieu de le cacher.
SEUIL_PRUDENCE_INSEE = 200

# Variables explorées ici, avec la raison de chacune
VARIABLES_A_EXPLORER = [
    "TRANS",  # mode de transport principal : coeur du sujet mobilité
    "GS",     # groupe socioprofessionnel : distinguer cadres et métiers sur place
    "EMPL",   # condition d'emploi : les alternants sont-ils repérables ?
]

# Colonnes lues dans le fichier. On ne lit que celles-ci (le fichier en a 32)
# pour aller plus vite et consommer moins de mémoire.
COLONNES_UTILES = ["REGION", "REGLT", "IPONDI"] + VARIABLES_A_EXPLORER


# ---------------------------------------------------------------------------
# Fonctions
# ---------------------------------------------------------------------------

def charger_libelles(chemin_varmod: Path) -> dict:
    """Lit le dictionnaire INSEE et renvoie {variable: {code: libellé}}.

    Pourquoi : le fichier de données ne contient que des codes ("6", "101"...).
    Le dictionnaire (varmod) donne leur signification. On le lit plutôt que
    d'écrire les libellés à la main : si l'INSEE change une catégorie
    (ce qui est arrivé pour EMPL entre 2022 et 2023), le script reste juste.
    """
    # dtype=str : les codes comme "011" doivent rester du texte,
    # sinon pandas les transformerait en nombre 11 et perdrait le zéro.
    varmod = pd.read_csv(chemin_varmod, sep=";", dtype=str, encoding="utf-8")
    libelles = {}
    for variable, groupe in varmod.groupby("COD_VAR"):
        libelles[variable] = dict(zip(groupe["COD_MOD"], groupe["LIB_MOD"]))
    return libelles


def charger_residents_idf(chemin_parquet: Path) -> pd.DataFrame:
    """Charge uniquement les actifs qui habitent en Île-de-France.

    Pourquoi filtrer sur la résidence (et pas sur le lieu de travail) :
    notre sujet part des personnes et de leur trajet depuis chez elles.
    Le filtre est appliqué pendant la lecture (option filters), donc les
    lignes des autres régions ne sont jamais chargées en mémoire.
    """
    donnees = pd.read_parquet(
        chemin_parquet,
        columns=COLONNES_UTILES,
        filters=[("REGION", "==", CODE_IDF)],
    )
    return normaliser_codes(donnees)


def normaliser_codes(donnees: pd.DataFrame) -> pd.DataFrame:
    """Convertit en texte les colonnes de codes que l'INSEE a stockées en nombres.

    Pourquoi : dans le fichier 2022, TRANS, GS ou EMPL sont des nombres
    décimaux (6.0), alors que le dictionnaire les écrit en texte ("6").
    Sans cette conversion, aucun code ne trouverait son libellé.
    Le fichier 2023, lui, est déjà en texte : il n'est pas modifié.
    """
    # On ne traite que les variables réellement chargées : les étapes suivantes
    # (ex. 02) réutilisent cette fonction avec d'autres colonnes.
    for variable in [v for v in VARIABLES_A_EXPLORER if v in donnees.columns]:
        if pd.api.types.is_numeric_dtype(donnees[variable]):
            # Int64 (avec majuscule) : entier qui accepte les valeurs manquantes.
            # On passe par l'entier pour obtenir "6" et non "6.0".
            donnees[variable] = donnees[variable].astype("Int64").astype(str)
    return donnees


def repartition_ponderee(donnees: pd.DataFrame, variable: str, libelles: dict) -> pd.DataFrame:
    """Calcule la répartition d'une variable, pondérée par IPONDI.

    Pourquoi pondérer : le recensement est un échantillon. Chaque ligne
    représente IPONDI personnes (par exemple 4,9). Compter les lignes
    donnerait un résultat faux ; on additionne donc les poids.

    Colonnes renvoyées :
      - nb_lignes        : nombre de réponses réelles (sert à juger la fiabilité)
      - effectif_pondere : nombre de personnes représentées
      - part_pct         : part en % de l'ensemble
      - prudence         : True si l'effectif est sous le seuil INSEE
    """
    tableau = (
        donnees.groupby(variable)
        .agg(nb_lignes=("IPONDI", "size"), effectif_pondere=("IPONDI", "sum"))
        .reset_index()
        .rename(columns={variable: "code"})
    )
    # On ajoute le libellé lisible à côté du code ; "?" signale un code
    # absent du dictionnaire (ce serait une anomalie à investiguer).
    tableau.insert(1, "libelle", tableau["code"].map(libelles.get(variable, {})).fillna("?"))
    tableau["part_pct"] = 100 * tableau["effectif_pondere"] / tableau["effectif_pondere"].sum()
    tableau["prudence"] = tableau["effectif_pondere"] < SEUIL_PRUDENCE_INSEE
    # Tri du plus grand au plus petit groupe : on lit d'abord l'essentiel
    return tableau.sort_values("effectif_pondere", ascending=False)


def main() -> None:
    """Enchaîne les étapes : lecture, contrôles, répartitions, export CSV."""
    parser = argparse.ArgumentParser(description="Exploration du fichier INSEE domicile-travail")
    # 2023 par défaut : c'est le recensement le plus récent (publié en juin 2026)
    parser.add_argument("--annee", default="2023", help="millésime du recensement (2022 ou 2023)")
    annee = parser.parse_args().annee

    dossier = RACINE / "data" / "brut" / f"insee_mobpro_{annee}"
    libelles = charger_libelles(dossier / f"varmod_mobpro_{annee}.csv")
    donnees = charger_residents_idf(dossier / f"RP{annee}_mobpro.parquet")

    # --- Contrôles de base : on vérifie avant de calculer ---
    print(f"=== Recensement {annee} : actifs résidant en Île-de-France ===")
    print(f"Lignes (réponses réelles)       : {len(donnees):,}".replace(",", " "))
    print(f"Personnes représentées (IPONDI) : {donnees['IPONDI'].sum():,.0f}".replace(",", " "))
    # Valeurs manquantes : s'il y en a, les parts calculées seraient biaisées
    print(f"Valeurs manquantes par colonne  : {donnees.isna().sum().to_dict()}")
    # Part des résidents qui travaillent aussi en Île-de-France (REGLT = région de travail)
    part_travail_idf = 100 * donnees.loc[donnees["REGLT"] == CODE_IDF, "IPONDI"].sum() / donnees["IPONDI"].sum()
    print(f"Travaillent aussi en IDF        : {part_travail_idf:.1f} %")

    # --- Répartitions, affichées et sauvegardées ---
    dossier_sortie = RACINE / "resultats" / "01_exploration" / annee
    dossier_sortie.mkdir(parents=True, exist_ok=True)
    for variable in VARIABLES_A_EXPLORER:
        tableau = repartition_ponderee(donnees, variable, libelles)
        print(f"\n--- {variable} ---")
        print(tableau.to_string(index=False, float_format=lambda x: f"{x:,.1f}"))
        # utf-8-sig : le CSV s'ouvre avec les accents corrects dans Excel
        tableau.to_csv(dossier_sortie / f"repartition_{variable}.csv", index=False, encoding="utf-8-sig")

    print(f"\nCSV enregistrés dans : {dossier_sortie}")


# Ce bloc ne s'exécute que si on lance le fichier directement
# (pas si une autre partie du code importe ses fonctions).
if __name__ == "__main__":
    main()
