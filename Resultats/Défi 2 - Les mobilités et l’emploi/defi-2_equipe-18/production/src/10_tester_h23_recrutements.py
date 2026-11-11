"""
10_tester_h23_recrutements.py : test de H23 (recrutements jugés difficiles et territoire), selon le protocole écrit
dans hypotheses.md (section I) avant ce script.

Source : France Travail, enquête Besoins en main-d'œuvre 2026 (Licence Ouverte). Pour chaque bassin d'emploi et
chaque métier : « met » = projets de recrutement, « xmet » = projets jugés difficiles par les employeurs.
Les petites cases sont masquées par un « * » (secret statistique).

Ce que la donnée ne dit PAS : pourquoi le recrutement est difficile (salaire, pénibilité, manque de candidats,
transport…) ni à quelle heure on travaille. On décrit donc une coïncidence géographique, jamais une cause.

H23a : part des recrutements difficiles plus forte en grande couronne qu'à Paris (au moins 5 points).
H23b : plus forte pour les familles d'ouvriers que pour les fonctions d'encadrement (au moins 10 points).
Chaque critère doit tenir avec les DEUX méthodes :
  A : toutes les cases (un « * » compte pour 0 recrutement difficile : sous-estime la difficulté des petites cases) ;
  B : seulement les cases où les deux chiffres sont publiés (pas de biais de secret, mais moins de cases).

Le script calcule aussi, par couronne, deux indicateurs déjà établis par les scripts 06 et 07 (part des emplois
d'employés et d'ouvriers dans une commune sans gare ; part des trajets en voiture de moins de 5 km), pour le
tableau « trois territoires » de la page des solutions. Mêmes fonctions, mêmes définitions : rien n'est redéfini.

Entrées : production/data/brut/francetravail_bmo/ (script 00) + les données des scripts 06 et 07
Sorties : production/resultats/10_h23/ (trois tableaux CSV)

Lancer depuis le dossier production/ :
    python src/10_tester_h23_recrutements.py
"""

import importlib.util
from pathlib import Path

import pandas as pd

PRODUCTION = Path(__file__).resolve().parent.parent
SORTIE = PRODUCTION / "resultats" / "10_h23"
FICHIER_BMO = PRODUCTION / "data" / "brut" / "francetravail_bmo" / "Base-open-data-BMO-2026.xlsx"

# Critères fixés dans le protocole (hypotheses.md, section I), avant ce script
SEUIL_H23A_PTS = 5.0
SEUIL_H23B_PTS = 10.0
CODE_REGION_IDF = 11
COURONNES = {"75": "Paris", "92": "Petite couronne", "93": "Petite couronne", "94": "Petite couronne",
             "77": "Grande couronne", "78": "Grande couronne", "91": "Grande couronne", "95": "Grande couronne"}
# Familles de métiers telles que France Travail les publie (aucun classement fait à la main)
FAMILLES_OUVRIERS = ["Ouvriers des secteurs de l'industrie", "Ouvriers de la construction et du bâtiment"]
FAMILLE_ENCADREMENT = "Fonctions d'encadrement"


def charger_module(chemin: Path):
    """Réutilise les fonctions d'un script numéroté (nom commençant par un chiffre : import classique impossible)."""
    spec = importlib.util.spec_from_file_location(chemin.stem, chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def charger_bmo() -> pd.DataFrame:
    """Lignes de l'enquête pour l'Île-de-France, avec les chiffres en nombres et la couronne du département.

    Un « * » (secret statistique) devient une valeur manquante : on le garde visible au lieu de le remplacer en douce.
    """
    bmo = pd.read_excel(FICHIER_BMO, sheet_name="BMO_2026_open_data")
    bmo = bmo[bmo["REG"] == CODE_REGION_IDF].copy()
    for colonne in ["met", "xmet"]:
        bmo[colonne] = pd.to_numeric(bmo[colonne], errors="coerce")
    bmo["Dept"] = bmo["Dept"].astype(str)
    bmo["couronne"] = bmo["Dept"].map(COURONNES)
    bmo["cases_completes"] = bmo["met"].notna() & bmo["xmet"].notna()
    return bmo


def part_difficile(bmo: pd.DataFrame, par: str) -> pd.DataFrame:
    """Part des projets jugés difficiles par groupe, avec les deux méthodes (A : toutes les cases ; B : cases complètes)."""
    a = bmo.groupby(par).agg(projets=("met", "sum"), difficiles=("xmet", "sum"))
    a["part_A_pct"] = 100 * a["difficiles"] / a["projets"]
    complet = bmo[bmo["cases_completes"]]
    b = complet.groupby(par).agg(projets_B=("met", "sum"), difficiles_B=("xmet", "sum"))
    b["part_B_pct"] = 100 * b["difficiles_B"] / b["projets_B"]
    return a.join(b)


def indicateurs_transport() -> pd.DataFrame:
    """Par couronne : part des emplois d'employés et d'ouvriers sans gare (script 07, lieu de travail) et part des
    trajets en voiture de moins de 5 km (script 06, trajets de banlieue à banlieue, lieu de résidence)."""
    s07 = charger_module(PRODUCTION / "src" / "07_tester_h21_emplois_gares.py")
    s06 = charger_module(PRODUCTION / "src" / "06_tester_h16_h17_solutions.py")
    gares = s07.communes_avec_gare()
    emplois = s07.charger_emplois()                     # emplois hors Paris (toute résidence), recensement 2023
    eo = emplois[emplois["GS"].isin(["5", "6"])].copy()
    eo["couronne"] = eo["DCLT"].str[:2].map(COURONNES)
    eo["sans_gare"] = ~eo["DCLT"].isin(gares)
    sans_gare = eo.groupby("couronne").apply(
        lambda d: 100 * d.loc[d["sans_gare"], "IPONDI"].sum() / d["IPONDI"].sum(), include_groups=False)

    centres = s06.charger_centres_communes()
    trajets = s06.charger_trajets_banlieue()
    voiture = trajets[(trajets["COMMUNE"] != trajets["DCLT"]) & (trajets["TRANS"] == s06.CODE_VOITURE)].copy()
    travail = centres[["lat", "lon"]].rename(columns={"lat": "lat_t", "lon": "lon_t"})
    voiture = voiture.join(centres[["lat", "lon"]], on="COMMUNE").join(travail, on="DCLT").dropna(subset=["lat", "lat_t"])
    voiture["court"] = s06.distance_vol_oiseau_km(voiture["lat"], voiture["lon"], voiture["lat_t"], voiture["lon_t"]) \
        < s06.SEUIL_DISTANCE_KM
    voiture["couronne"] = voiture["COMMUNE"].str[:2].map(COURONNES)
    courts = voiture.groupby("couronne").apply(
        lambda d: 100 * d.loc[d["court"], "IPONDI"].sum() / d["IPONDI"].sum(), include_groups=False)
    return pd.DataFrame({"emplois_eo_sans_gare_pct": sans_gare, "voiture_moins_5km_pct": courts})


def main() -> None:
    """Calcule, contrôle et enregistre les résultats de H23, puis affiche le verdict selon le protocole."""
    SORTIE.mkdir(parents=True, exist_ok=True)
    bmo = charger_bmo()
    print(f"Île-de-France : {len(bmo)} cases, dont {100 * (~bmo['cases_completes']).mean():.0f} % avec un chiffre masqué")

    # Contrôle : la somme des départements redonne le total régional (aucune ligne perdue par le regroupement)
    par_dep = part_difficile(bmo, "Dept")
    assert abs(par_dep["projets"].sum() - bmo["met"].sum()) < 1e-6, "les départements ne redonnent pas le total"
    assert bmo["couronne"].notna().all(), "un département hors des 8 d'Île-de-France"

    couronnes = part_difficile(bmo, "couronne").reindex(["Paris", "Petite couronne", "Grande couronne"])
    familles = part_difficile(bmo, "Lbl_fam_met").sort_values("part_A_pct")
    metiers = part_difficile(bmo, "Nom métier BMO").sort_values("difficiles", ascending=False)

    # H23a : grande couronne contre Paris, avec les deux méthodes
    ecart_a = {m: couronnes.loc["Grande couronne", f"part_{m}_pct"] - couronnes.loc["Paris", f"part_{m}_pct"]
               for m in "AB"}
    # H23b : familles d'ouvriers (ensemble) contre fonctions d'encadrement
    ouvriers = bmo[bmo["Lbl_fam_met"].isin(FAMILLES_OUVRIERS)].assign(groupe="Ouvriers")
    encadrement = bmo[bmo["Lbl_fam_met"] == FAMILLE_ENCADREMENT].assign(groupe="Encadrement")
    comparaison = part_difficile(pd.concat([ouvriers, encadrement]), "groupe")
    ecart_b = {m: comparaison.loc["Ouvriers", f"part_{m}_pct"] - comparaison.loc["Encadrement", f"part_{m}_pct"]
               for m in "AB"}

    territoires = couronnes[["projets", "difficiles", "part_A_pct", "part_B_pct"]].join(indicateurs_transport())
    territoires.round(2).to_csv(SORTIE / "territoires.csv", encoding="utf-8-sig")
    familles.round(2).to_csv(SORTIE / "familles_de_metiers.csv", encoding="utf-8-sig")
    metiers.round(2).to_csv(SORTIE / "metiers.csv", encoding="utf-8-sig")
    par_dep.round(2).to_csv(SORTIE / "departements.csv", encoding="utf-8-sig")

    print(territoires.round(1).to_string())
    print(familles[["part_A_pct", "part_B_pct"]].round(1).to_string())
    for nom, ecart, seuil in [("H23a (grande couronne - Paris)", ecart_a, SEUIL_H23A_PTS),
                              ("H23b (ouvriers - encadrement)", ecart_b, SEUIL_H23B_PTS)]:
        verdict = "CONFIRMÉE" if all(v >= seuil for v in ecart.values()) else "NON CONFIRMÉE"
        print(f"{nom} : méthode A {ecart['A']:+.1f} pts, méthode B {ecart['B']:+.1f} pts (seuil {seuil}) -> {verdict}")


if __name__ == "__main__":
    main()
