"""
05_tester_h4b_h10_offre.py : test du volet (2) de H4b (nuit) et H10 (dimanche),
selon le protocole écrit dans hypotheses.md AVANT l'ouverture des données.

H4b : là où travaillent beaucoup d'ouvriers, l'offre de transport la nuit
      (minuit-5h) est encore plus faible qu'ailleurs, par rapport à la journée.
H10 : là où travaillent beaucoup d'employés, l'offre du dimanche est encore
      plus faible qu'ailleurs, par rapport à la semaine.

Source de l'offre : IDFM, « Offre hebdomadaire moyenne hors vacances » 2025
(nombre moyen de passages par arrêt, ligne, heure et jour de la semaine).

Entrées : data/brut/idfm_offre_hebdo_2025/, data/brut/insee_mobpro_2023/
Sorties : console + CSV dans resultats/05_h4b_h10/

Lancer depuis la racine du projet :
    .venv\\Scripts\\python.exe src\\05_tester_h4b_h10_offre.py
"""

from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Constantes : toutes viennent du protocole (hypotheses.md)
# ---------------------------------------------------------------------------

RACINE = Path(__file__).resolve().parent.parent
BRUT = RACINE / "data" / "brut"

# Journée d'exploitation IDFM : 4h à 3h59. Les tranches 24 à 27 = minuit à 3h59.
TRANCHES_NUIT = [24, 25, 26, 27, 4]   # minuit-5h (définition INSEE de la nuit)
TRANCHES_POINTE = [7, 8, 9]           # 7h-10h (pointe du matin, Institut Paris Région)
JOURS_SEMAINE = ["nb_courses_mardi", "nb_courses_mercredi", "nb_courses_jeudi"]
JOUR_DIMANCHE = "nb_courses_dimanche"

SEUIL_EMPLOIS_MIN = 1000      # communes plus petites écartées (trop sensibles à quelques bus)
SEUIL_SPEARMAN = -0.3         # critère 1 : lien négatif d'au moins cette force
SEUIL_ECART_RELATIF = 0.25    # critère 2 : quart le plus concerné au moins 25 % plus bas
SEUIL_NUIT_REGION = 0.50      # volet 1 : H4b réfutée si nuit >= 50 % de la pointe
SEUIL_DIMANCHE_REGION = 0.90  # volet 1 : H10 réfutée si dimanche >= 90 % de la semaine

CODE_EMPLOYES, CODE_OUVRIERS = "5", "6"   # variable GS du recensement
CODE_PARIS = "75056"  # IDFM code Paris en une seule commune


# ---------------------------------------------------------------------------
# Offre de transport par commune
# ---------------------------------------------------------------------------

def charger_offre() -> pd.DataFrame:
    """Lit l'offre IDFM et ne garde que les colonnes utiles.

    dtype=str pour le code commune : "01001" doit garder son zéro initial.
    Les lignes sans code commune sont comptées puis écartées, pour savoir
    quelle part de l'offre on perd.
    """
    colonnes = ["code_commune", "tranche_horaire"] + JOURS_SEMAINE + [JOUR_DIMANCHE]
    offre = pd.read_csv(BRUT / "idfm_offre_hebdo_2025" / "offre_hebdomadaire_moyenne_hors_vacances.csv",
                        sep=";", encoding="utf-8-sig", usecols=colonnes, dtype={"code_commune": str})
    sans_commune = offre["code_commune"].isna()
    part_perdue = 100 * offre.loc[sans_commune, JOURS_SEMAINE].sum().sum() / offre[JOURS_SEMAINE].sum().sum()
    print(f"Offre IDFM : {len(offre):,} lignes, dont {sans_commune.sum():,} sans code commune "
          f"({part_perdue:.2f} % des passages de semaine, écartés)".replace(",", " "))
    return offre[~sans_commune]


def indicateurs_offre(offre: pd.DataFrame, groupe: list) -> pd.DataFrame:
    """Calcule les deux rapports d'offre pour chaque groupe (commune, ou région si groupe vide).

    - nuit_par_heure / pointe_par_heure : on divise par le nombre d'heures
      (5 la nuit, 3 en pointe) pour comparer à durée égale.
    - Moyenne du mardi au jeudi pour un jour ordinaire de semaine.
    """
    offre = offre.copy()
    offre["semaine"] = offre[JOURS_SEMAINE].mean(axis=1)  # passages d'un jour ordinaire
    cles = groupe if groupe else (lambda _: "Île-de-France")  # tout regrouper si pas de groupe
    nuit = offre[offre["tranche_horaire"].isin(TRANCHES_NUIT)].groupby(cles)["semaine"].sum() / len(TRANCHES_NUIT)
    pointe = offre[offre["tranche_horaire"].isin(TRANCHES_POINTE)].groupby(cles)["semaine"].sum() / len(TRANCHES_POINTE)
    jour_total = offre.groupby(cles)["semaine"].sum()
    dimanche_total = offre.groupby(cles)[JOUR_DIMANCHE].sum()
    resultat = pd.DataFrame({"nuit_par_heure": nuit, "pointe_par_heure": pointe,
                             "passages_jour_semaine": jour_total, "passages_dimanche": dimanche_total})
    # Une commune sans aucun passage la nuit a une offre de nuit de 0, pas une valeur manquante
    resultat["nuit_par_heure"] = resultat["nuit_par_heure"].fillna(0)
    resultat["offre_nuit_relative"] = resultat["nuit_par_heure"] / resultat["pointe_par_heure"]
    resultat["offre_dimanche_relative"] = resultat["passages_dimanche"] / resultat["passages_jour_semaine"]
    return resultat


# ---------------------------------------------------------------------------
# Emplois par commune (recensement 2023)
# ---------------------------------------------------------------------------

def emplois_par_commune() -> pd.DataFrame:
    """Nombre d'emplois et parts d'employés et d'ouvriers, par commune de travail.

    On garde les personnes qui travaillent en Île-de-France (REGLT = 11).
    Les arrondissements de Paris (751xx) sont regroupés en 75056, car l'offre
    IDFM ne distingue pas les arrondissements.
    """
    actifs = pd.read_parquet(BRUT / "insee_mobpro_2023" / "RP2023_mobpro.parquet",
                             columns=["DCLT", "REGLT", "GS", "IPONDI"], filters=[("REGLT", "==", "11")])
    actifs["code_commune"] = actifs["DCLT"].where(~actifs["DCLT"].str.startswith("751"), CODE_PARIS)
    total = actifs.groupby("code_commune")["IPONDI"].sum()
    par_gs = actifs.pivot_table(index="code_commune", columns="GS", values="IPONDI", aggfunc="sum", fill_value=0)
    return pd.DataFrame({
        "emplois": total,
        "part_ouvriers_pct": 100 * par_gs[CODE_OUVRIERS] / total,
        "part_employes_pct": 100 * par_gs[CODE_EMPLOYES] / total,
    })


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def evaluer(communes: pd.DataFrame, variable: str, indicateur: str) -> dict:
    """Applique les deux critères du protocole.

    Spearman = corrélation sur les rangs (calculée sans scipy, comme à l'étape 04).
    Écart relatif = 1 - (moyenne du quart le plus concerné / moyenne du quart le moins concerné).
    Exemple : 0,02 contre 0,04 donne un écart relatif de 50 %.
    """
    spearman = communes[variable].rank().corr(communes[indicateur].rank())
    quartile = pd.qcut(communes[variable], 4, labels=["Q1", "Q2", "Q3", "Q4"])
    moyennes = communes.groupby(quartile, observed=True)[indicateur].mean()
    ecart_relatif = 1 - moyennes["Q4"] / moyennes["Q1"]
    # int() sur chaque critère avant l'addition (piège des booléens numpy, voir étape 04)
    criteres = int(spearman <= SEUIL_SPEARMAN) + int(ecart_relatif >= SEUIL_ECART_RELATIF)
    return {"indicateur": indicateur, "variable": variable, "spearman": spearman,
            "moyenne_Q1_moins_concerne": moyennes["Q1"], "moyenne_Q4_plus_concerne": moyennes["Q4"],
            "ecart_relatif_pct": 100 * ecart_relatif,
            "verdict": {2: "CONFIRMÉE", 1: "NUANCÉE", 0: "RÉFUTÉE"}[criteres]}


def main() -> None:
    """Volet 1 (constat régional), puis volet 2 (comparaison entre communes)."""
    offre = charger_offre()

    # Volet 1 : constat sur toute l'Île-de-France
    region = indicateurs_offre(offre, []).iloc[0]
    print("\n=== Volet 1 : constat régional ===")
    print(f"Offre de nuit relative     : {100 * region['offre_nuit_relative']:.1f} % de la pointe 7h-10h "
          f"-> H4b {'RÉFUTÉE' if region['offre_nuit_relative'] >= SEUIL_NUIT_REGION else 'confirmée'}")
    print(f"Offre du dimanche relative : {100 * region['offre_dimanche_relative']:.1f} % d'un jour de semaine "
          f"-> H10 {'RÉFUTÉE' if region['offre_dimanche_relative'] >= SEUIL_DIMANCHE_REGION else 'confirmée'}")

    # Volet 2 : comparaison entre communes
    communes = emplois_par_commune().join(indicateurs_offre(offre, ["code_commune"]), how="left")
    communes = communes[communes["emplois"] >= SEUIL_EMPLOIS_MIN]
    sans_pointe = communes["pointe_par_heure"].isna() | (communes["pointe_par_heure"] == 0)
    print(f"\nCommunes d'au moins {SEUIL_EMPLOIS_MIN} emplois : {len(communes)}, dont {sans_pointe.sum()} "
          f"sans aucun passage entre 7h et 10h (écartées) : {sorted(communes.index[sans_pointe])[:15]}")
    communes = communes[~sans_pointe]
    print(f"Communes retenues : {len(communes)}")
    print(f"Communes sans aucun passage la nuit : {(communes['nuit_par_heure'] == 0).sum()}")

    evaluations = pd.DataFrame([
        evaluer(communes, "part_ouvriers_pct", "offre_nuit_relative"),
        evaluer(communes, "part_employes_pct", "offre_dimanche_relative"),
    ])
    print("\n=== Volet 2 : verdict selon les critères fixés d'avance ===")
    print(evaluations.to_string(index=False, float_format=lambda x: f"{x:.3f}"))

    dossier_sortie = RACINE / "resultats" / "05_h4b_h10"
    dossier_sortie.mkdir(parents=True, exist_ok=True)
    communes.to_csv(dossier_sortie / "offre_relative_par_commune.csv", encoding="utf-8-sig")
    evaluations.to_csv(dossier_sortie / "verdict_h4b_h10.csv", index=False, encoding="utf-8-sig")
    print(f"\nCSV enregistrés dans : {dossier_sortie}")


if __name__ == "__main__":
    main()
