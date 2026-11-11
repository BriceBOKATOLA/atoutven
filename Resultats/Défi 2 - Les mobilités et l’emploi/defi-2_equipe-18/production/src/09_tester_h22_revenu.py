"""
09_tester_h22_revenu.py : test de H22 (revenu et choix de la voiture), selon le protocole écrit
AVANT de télécharger les données de revenu (hypotheses.md, section H).

Test A (hypothèse proposée par l'équipe) : les actifs des communes modestes prennent-ils moins la voiture
             (la voiture comme « luxe ») ? Employés et ouvriers, trajets de banlieue à banlieue.
Test B (contrôle du résultat principal) : à revenu de commune égal, l'absence de gare au lieu de travail
             fait-elle toujours monter la part de la voiture ?

Revenu = niveau de vie médian de la commune de RÉSIDENCE (INSEE, Filosofi 2023, variable MED_SL).
Classes = quartiles pondérés par le nombre d'actifs : chaque quart regroupe environ autant de trajets.

Entrées : production/data/brut/insee_filosofi_2023/DS_FILOSOFI_CC_2023_data.csv
          + les données du script 07 (recensement 2023, offre IDFM, référentiel des arrêts)
Sorties : production/resultats/09_h22/ (deux tableaux CSV)

Lancer depuis le dossier production/ :
    python src/09_tester_h22_revenu.py
"""

import importlib.util
import sys
from pathlib import Path

import pandas as pd

# Emplacement du dossier production/ : en argument (avant intégration au dépôt), sinon le parent de src/
PRODUCTION = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
# Dossier de sortie : en second argument si besoin (par exemple hors du dépôt), sinon resultats/09_h22
SORTIE = Path(sys.argv[2]) if len(sys.argv) > 2 else PRODUCTION / "resultats" / "09_h22"

# Critères fixés dans le protocole, avant de regarder les données
SEUIL_TEST_A_PTS = 5.0     # écart minimal (en points) entre le quart le plus aisé et le plus modeste
SEUIL_TEST_B_PTS = 10.0    # écart minimal sans gare / avec gare, dans chaque quartile
CODE_VOITURE = "5"
NOMS_QUARTILES = ["1 - plus modestes", "2", "3", "4 - plus aisées"]


def charger_module(chemin: Path):
    """Réutilise les fonctions d'un script numéroté (nom commençant par un chiffre : import classique impossible)."""
    spec = importlib.util.spec_from_file_location(chemin.stem, chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def revenu_par_commune() -> pd.Series:
    """Niveau de vie médian 2023 de chaque commune (euros par an et par unité de consommation)."""
    filosofi = pd.read_csv(PRODUCTION / "data" / "brut" / "insee_filosofi_2023" / "DS_FILOSOFI_CC_2023_data.csv",
                           sep=";", dtype={"GEO": str}, encoding="utf-8-sig")
    communes = filosofi[(filosofi["GEO_OBJECT"] == "COM") & (filosofi["FILOSOFI_MEASURE"] == "MED_SL")]
    return communes.dropna(subset=["OBS_VALUE"]).set_index("GEO")["OBS_VALUE"].astype(float)


def quartiles_ponderes(trajets: pd.DataFrame) -> pd.Series:
    """Quartile de revenu de chaque trajet, pondéré par IPONDI.

    On classe les communes de la plus modeste à la plus aisée, on cumule leur nombre d'actifs, et chaque
    commune entière va dans le quart où se trouve le milieu de son effectif : une commune n'est jamais coupée en deux.
    """
    par_commune = trajets.groupby("COMMUNE").agg(revenu=("revenu", "first"), poids=("IPONDI", "sum")).sort_values("revenu")
    cumul = par_commune["poids"].cumsum()
    milieu = (cumul - par_commune["poids"] / 2) / par_commune["poids"].sum()
    quart = pd.cut(milieu, bins=[0, 0.25, 0.5, 0.75, 1.0], labels=NOMS_QUARTILES, include_lowest=True)
    return trajets["COMMUNE"].map(quart)


def part_voiture(d: pd.DataFrame) -> float:
    """Part des trajets faits en voiture, en %, pondérée."""
    return 100 * d.loc[d["TRANS"] == CODE_VOITURE, "IPONDI"].sum() / d["IPONDI"].sum()


def main() -> None:
    """Prépare la population, applique les deux tests et les critères du protocole, enregistre les tableaux."""
    h21 = charger_module(PRODUCTION / "src" / "07_tester_h21_emplois_gares.py")
    gares = h21.communes_avec_gare()
    emplois = h21.charger_emplois()

    # Même population que l'analyse « voiture selon la gare » : de banlieue à banlieue, deux communes différentes
    trajets = emplois[(emplois["REGION"] == "11") & ~emplois["COMMUNE"].str.startswith("75")
                      & (emplois["COMMUNE"] != emplois["DCLT"])].copy()
    trajets["gare_au_travail"] = trajets["DCLT"].isin(gares)
    revenus = revenu_par_commune()
    trajets["revenu"] = trajets["COMMUNE"].map(revenus)
    sans_revenu = trajets["revenu"].isna()
    print(f"Trajets écartés faute de revenu de commune (secret statistique) : "
          f"{100 * trajets.loc[sans_revenu, 'IPONDI'].sum() / trajets['IPONDI'].sum():.1f} %")
    trajets = trajets[~sans_revenu].copy()
    trajets["quartile"] = quartiles_ponderes(trajets)

    # --- Test A : employés et ouvriers, voiture selon le revenu de la commune de résidence
    sur_place = trajets[trajets["GS"].isin(["5", "6"])]
    test_a = pd.DataFrame([{
        "quartile_revenu": q, "niveau_de_vie_median_min": round(d["revenu"].min()),
        "niveau_de_vie_median_max": round(d["revenu"].max()), "trajets": round(d["IPONDI"].sum()),
        "part_voiture_pct": round(part_voiture(d), 1)} for q, d in sur_place.groupby("quartile", observed=True)])
    ecart_a = test_a["part_voiture_pct"].iloc[-1] - test_a["part_voiture_pct"].iloc[0]   # aisés - modestes
    verdict_a = ("confirmée" if ecart_a >= SEUIL_TEST_A_PTS else "réfutée" if ecart_a <= 0 else "nuancée")
    print("\nTest A : part de la voiture (employés et ouvriers) selon le revenu de la commune de résidence")
    print(test_a.to_string(index=False))
    print(f"Écart aisées - modestes : {ecart_a:+.1f} points -> H22 {verdict_a}")

    # --- Test B : tous métiers, sans gare / avec gare au lieu de travail, dans chaque quartile
    lignes = []
    for q, d in trajets.groupby("quartile", observed=True):
        avec, sans = d[d["gare_au_travail"]], d[~d["gare_au_travail"]]
        lignes.append({"quartile_revenu": q, "voiture_avec_gare_pct": round(part_voiture(avec), 1),
                       "voiture_sans_gare_pct": round(part_voiture(sans), 1),
                       "ecart_points": round(part_voiture(sans) - part_voiture(avec), 1),
                       "trajets_sans_gare": round(sans["IPONDI"].sum())})
    test_b = pd.DataFrame(lignes)
    nb_ok = int((test_b["ecart_points"] >= SEUIL_TEST_B_PTS).sum())
    verdict_b = "maintenu" if nb_ok == 4 else "nuancé" if nb_ok >= 2 else "remis en cause"
    print("\nTest B : part de la voiture selon la gare au lieu de travail, dans chaque quartile de revenu")
    print(test_b.to_string(index=False))
    print(f"Quartiles où l'écart atteint {SEUIL_TEST_B_PTS:.0f} points : {nb_ok} sur 4 -> résultat principal {verdict_b}")

    SORTIE.mkdir(parents=True, exist_ok=True)
    test_a.to_csv(SORTIE / "voiture_selon_revenu_employes_ouvriers.csv", index=False, encoding="utf-8-sig")
    test_b.to_csv(SORTIE / "effet_gare_a_revenu_egal.csv", index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    main()
