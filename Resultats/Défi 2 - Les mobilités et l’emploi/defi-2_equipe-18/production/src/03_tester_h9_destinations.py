"""
03_tester_h9_destinations.py : test de l'hypothèse H9 (première partie, sans itinéraire).

H9 : les métiers "sur place" font plus de trajets de banlieue à banlieue,
     qui obligent souvent à passer par Paris, donc plus longs.

Ce script teste la première moitié : OÙ vont travailler les actifs, selon
leur métier et leur lieu de résidence. La durée des trajets (seconde moitié)
demandera un calcul d'itinéraire, plus tard.

Il teste aussi la piste ouverte par H2 : en grande couronne, les ouvriers
prennent-ils la voiture à cause de leur MÉTIER ou à cause de leur DESTINATION ?
Pour le savoir, on compare les modes à destination égale. Si un ouvrier qui
va à Paris prend autant les transports en commun qu'un cadre qui va à Paris,
c'est la destination qui compte, pas le métier.

Entrée  : data/brut/insee_mobpro_2023/
Sorties : console + CSV dans resultats/03_h9/

Lancer depuis la racine du projet :
    .venv\\Scripts\\python.exe src\\03_tester_h9_destinations.py
"""

# importlib : réutilise les fonctions des étapes 01 et 02 (noms de fichiers
# commençant par un chiffre, donc non importables avec un simple "import")
import importlib
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
etape_01 = importlib.import_module("01_explorer_mobpro")
etape_02 = importlib.import_module("02_tester_h2_mode_par_metier")

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

RACINE = etape_01.RACINE
ANNEE = etape_02.ANNEE
CODE_IDF = etape_01.CODE_IDF
COURONNES = etape_02.COURONNES

# Groupes comparés : les cadres (référence, souvent en télétravail possible)
# face aux employés et ouvriers (métiers majoritairement sur place).
GS_COMPARES = {"3": "Cadres", "5": "Employés", "6": "Ouvriers"}

# Ordre d'affichage des destinations, du plus proche au plus lointain
ORDRE_DESTINATIONS = ["Même commune", "Paris", "Petite couronne",
                      "Grande couronne (autre commune)", "Hors Île-de-France"]

# Nombre de communes de destination affichées dans le classement
NB_TOP_DESTINATIONS = 10


# ---------------------------------------------------------------------------
# Fonctions
# ---------------------------------------------------------------------------

def charger_donnees() -> pd.DataFrame:
    """Charge les résidents d'IDF des trois groupes comparés, avec leur destination.

    DCLT = commune du lieu de travail ; REGLT = région du lieu de travail.
    """
    chemin = RACINE / "data" / "brut" / f"insee_mobpro_{ANNEE}" / f"RP{ANNEE}_mobpro.parquet"
    donnees = pd.read_parquet(
        chemin,
        columns=["COMMUNE", "DCLT", "REGION", "REGLT", "IPONDI", "TRANS", "GS"],
        filters=[("REGION", "==", CODE_IDF)],
    )
    donnees = etape_01.normaliser_codes(donnees)
    donnees = donnees[donnees["GS"].isin(GS_COMPARES)].copy()
    donnees["couronne"] = donnees["COMMUNE"].str[:2].map(COURONNES)
    donnees["destination"] = classer_destination(donnees)
    return donnees


def classer_destination(donnees: pd.DataFrame) -> pd.Series:
    """Range chaque trajet dans une catégorie de destination.

    L'ordre des tests compte : on regarde d'abord si la personne travaille
    hors d'Île-de-France, puis dans sa propre commune, puis on classe la
    commune de travail selon sa couronne (via les 2 premiers caractères).
    """
    destination = donnees["DCLT"].str[:2].map(COURONNES).replace(
        {"Grande couronne": "Grande couronne (autre commune)"}
    )
    destination = destination.mask(donnees["COMMUNE"] == donnees["DCLT"], "Même commune")
    destination = destination.mask(donnees["REGLT"] != CODE_IDF, "Hors Île-de-France")
    return destination


def repartition_destinations(donnees: pd.DataFrame) -> pd.DataFrame:
    """Part (en %) de chaque destination, par couronne de résidence et métier (pondérée)."""
    effectifs = donnees.groupby(["couronne", "GS", "destination"])["IPONDI"].sum()
    # Division par le total de chaque couple (couronne, métier) : chaque ligne fait 100 %
    parts = 100 * effectifs / effectifs.groupby(["couronne", "GS"]).transform("sum")
    tableau = parts.unstack("destination")[ORDRE_DESTINATIONS].reset_index()
    tableau["GS"] = tableau["GS"].map(GS_COMPARES)
    return tableau


def top_destinations(donnees: pd.DataFrame, libelles_dclt: dict) -> pd.DataFrame:
    """Communes de travail les plus fréquentes, par métier, pour les résidents de grande couronne."""
    lignes = []
    for code_gs, nom_gs in GS_COMPARES.items():
        sous_ensemble = donnees[(donnees["couronne"] == "Grande couronne") & (donnees["GS"] == code_gs)]
        total = sous_ensemble["IPONDI"].sum()
        top = sous_ensemble.groupby("DCLT")["IPONDI"].sum().nlargest(NB_TOP_DESTINATIONS)
        for rang, (code, effectif) in enumerate(top.items(), start=1):
            lignes.append({"GS": nom_gs, "rang": rang, "commune": libelles_dclt.get(code, code),
                           "effectif_pondere": effectif, "part_pct": 100 * effectif / total})
    return pd.DataFrame(lignes)


def main() -> None:
    """Destinations par métier, puis modes de transport à destination égale."""
    libelles = etape_01.charger_libelles(
        RACINE / "data" / "brut" / f"insee_mobpro_{ANNEE}" / f"varmod_mobpro_{ANNEE}.csv"
    )
    donnees = charger_donnees()
    dossier_sortie = RACINE / "resultats" / "03_h9"
    dossier_sortie.mkdir(parents=True, exist_ok=True)
    format_nombre = lambda x: f"{x:,.1f}"  # noqa: E731 (format d'affichage court)

    # 1. Où vont-ils travailler ?
    destinations = repartition_destinations(donnees)
    print(f"=== H9, recensement {ANNEE} : destination du trajet (% de chaque groupe) ===")
    print(destinations.to_string(index=False, float_format=format_nombre))
    destinations.to_csv(dossier_sortie / "destinations_par_gs_et_couronne.csv",
                        index=False, encoding="utf-8-sig")

    # 2. En grande couronne : mode de transport À DESTINATION ÉGALE
    grande_couronne = donnees[donnees["couronne"] == "Grande couronne"]
    modes = etape_02.parts_modales(grande_couronne, ["destination", "GS"])
    modes["GS"] = modes["GS"].map(GS_COMPARES)
    modes.to_csv(dossier_sortie / "modes_par_destination_grande_couronne.csv",
                 index=False, encoding="utf-8-sig")
    for colonne, titre in [("part_tc_pct", "Transports en commun"), ("part_voiture_pct", "Voiture")]:
        tableau = modes.pivot(index="destination", columns="GS", values=colonne).loc[ORDRE_DESTINATIONS]
        print(f"\n--- Résidents de grande couronne : {titre} (%), à destination égale ---")
        print(tableau.round(1).to_string())
    print(f"\nCases sous le seuil de prudence INSEE : {int(modes['prudence'].sum())}")

    # 3. Les communes de travail les plus fréquentes
    top = top_destinations(donnees, libelles["DCLT"])
    print(f"\n=== Résidents de grande couronne : {NB_TOP_DESTINATIONS} premières communes de travail ===")
    for nom_gs, groupe in top.groupby("GS", sort=False):
        print(f"\n{nom_gs} :")
        print(groupe[["rang", "commune", "part_pct"]].to_string(index=False, float_format=format_nombre))
    top.to_csv(dossier_sortie / "top_destinations_grande_couronne.csv", index=False, encoding="utf-8-sig")

    print(f"\nCSV enregistrés dans : {dossier_sortie}")


if __name__ == "__main__":
    main()
