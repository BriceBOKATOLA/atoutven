"""
12_gare_ne_suffit_pas.py : constat EXPLORATOIRE (trouvé le 2026-11-12, pas une hypothèse au critère écrit d'avance).

Question : quand la commune de travail a une gare, les actifs qui y viennent d'une autre commune de banlieue
laissent-ils la voiture ? Ou bien, dans une partie de ces communes, la voiture domine-t-elle autant que sans gare ?

Pourquoi : la page 3 compare « lieu de travail avec gare » et « sans gare » en moyenne. En détaillant par commune, des
communes avec gare (Roissy-en-France, Rungis…) gardent une voiture très forte. Ce constat sert la perspective de la
conclusion : une gare dans la commune ne suffit pas ; il faudrait mesurer la distance réelle entre emplois et gare.

Ce que la donnée permet de dire, et pas plus :
  - la présence d'une gare est connue à l'échelle de la COMMUNE (script 07) ; on ne sait pas si les emplois sont près
    de la gare, ni si les horaires ou les directions desservies conviennent : le script ne dit pas POURQUOI ;
  - « voiture » = catégorie INSEE (TRANS = 5), qui inclut camions et fourgonnettes. Contrôle : le constat est calculé
    aussi pour les cadres et les employés, qui utilisent peu de véhicules de travail.

Définitions reprises du script 07 (fonctions réutilisées, mêmes résultats) :
  - commune avec gare : au moins un arrêt de métro, RER, train ou tram avec un passage dans l'offre IDFM 2025 ;
  - trajets de banlieue à banlieue : résidence et travail en Île-de-France hors Paris, dans deux communes différentes.
Seuils :
  - au moins 200 trajets par commune et par groupe : en dessous, l'INSEE déconseille de commenter les écarts
    (fiche de précision du recensement), même convention que la page 6 ;
  - « au moins 2 sur 3 en voiture » : seuil choisi par l'équipe, aucune source ne le définit. Sensibilité à 60 % et 70 %.

Entrées : données des scripts 00 et 07 (recensement 2023, offre IDFM 2025, référentiel des arrêts)
Sorties : production/resultats/12_gare/par_commune.csv (détail), production/resultats/12_gare/synthese.csv
          (une ligne par groupe et par seuil ; la ligne « Ensemble » au seuil 2 sur 3 alimente la conclusion de l'application)

Lancer depuis le dossier production/ :
    python src/12_gare_ne_suffit_pas.py
"""

import importlib.util
from pathlib import Path

import pandas as pd

PRODUCTION = Path(__file__).resolve().parent.parent
SORTIE = PRODUCTION / "resultats" / "12_gare"
SEUIL_TRAJETS = 200                                   # prudence INSEE (voir l'en-tête)
SEUIL_PRINCIPAL = 2 / 3                               # « au moins 2 sur 3 en voiture » (choix de l'équipe)
SEUILS_SENSIBILITE = [0.60, SEUIL_PRINCIPAL, 0.70]
GROUPES = {"Cadres": ["3"], "Employés": ["5"], "Ouvriers": ["6"], "Ensemble": ["3", "5", "6"]}
CODE_VOITURE = "5"                                    # variable TRANS du recensement
NB_EXEMPLES = 3                                       # communes citées dans la conclusion


def charger_module(chemin: Path):
    """Réutilise les fonctions d'un script numéroté (nom commençant par un chiffre : import classique impossible)."""
    spec = importlib.util.spec_from_file_location(chemin.stem, chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def trajets_banlieue(s07) -> pd.DataFrame:
    """Trajets de banlieue à banlieue (même filtre que voiture_selon_gare du script 07), avec la gare au lieu de travail."""
    gares = s07.communes_avec_gare()
    emplois = s07.charger_emplois()
    emplois["travail_avec_gare"] = emplois["DCLT"].isin(gares)
    banlieue = emplois[(emplois["REGION"] == "11") & ~emplois["COMMUNE"].str.startswith("75")
                       & (emplois["COMMUNE"] != emplois["DCLT"])].copy()
    banlieue["voiture"] = (banlieue["TRANS"] == CODE_VOITURE) * banlieue["IPONDI"]
    return banlieue


def par_commune(banlieue: pd.DataFrame, codes_gs: list[str]) -> pd.DataFrame:
    """Trajets et part de la voiture par commune de travail, pour un groupe de catégories."""
    sous = banlieue[banlieue["GS"].isin(codes_gs)]
    t = sous.groupby(["DCLT", "travail_avec_gare"]).agg(trajets=("IPONDI", "sum"), voiture=("voiture", "sum")).reset_index()
    t["part_voiture"] = t["voiture"] / t["trajets"]
    return t


def main() -> None:
    """Calcule le constat par groupe et par seuil, contrôle la cohérence avec le script 07, écrit les résultats."""
    SORTIE.mkdir(parents=True, exist_ok=True)
    s07 = charger_module(PRODUCTION / "src" / "07_tester_h21_emplois_gares.py")
    banlieue = trajets_banlieue(s07)
    noms = (pd.read_csv(PRODUCTION / "application" / "donnees" / "communes_residence.csv", encoding="utf-8-sig",
                        dtype={"code": str}).set_index("code")["nom"])
    synthese, details = [], []
    for groupe, codes in GROUPES.items():
        t = par_commune(banlieue, codes)
        # Contrôle de cohérence : sans filtre, on doit retrouver les parts du script 07 (affichées en page 3)
        for avec in (True, False):
            d = t[t["travail_avec_gare"] == avec]
            print(f"{groupe:9} {'avec' if avec else 'sans'} gare, toutes communes : {100 * d.voiture.sum() / d.trajets.sum():.1f} %")
        fiables = t[t["trajets"] >= SEUIL_TRAJETS]
        avec_gare = fiables[fiables["travail_avec_gare"]]
        sans_gare = fiables[~fiables["travail_avec_gare"]]
        for seuil in SEUILS_SENSIBILITE:
            haut = avec_gare[avec_gare["part_voiture"] >= seuil].sort_values("trajets", ascending=False)
            synthese.append({
                # Seuil en pourcentage à une décimale (60 ; 66,7 ; 70) : lisible, et sans ambiguïté après arrondi
                "groupe": groupe, "seuil_voiture_pct": round(100 * seuil, 1),
                "communes_avec_gare": len(avec_gare), "communes_au_dessus": len(haut),
                "part_communes_pct": 100 * len(haut) / len(avec_gare),
                "part_trajets_pct": 100 * haut["trajets"].sum() / avec_gare["trajets"].sum(),
                "voiture_avec_gare_pct": 100 * avec_gare["voiture"].sum() / avec_gare["trajets"].sum(),
                "voiture_sans_gare_pct": 100 * sans_gare["voiture"].sum() / sans_gare["trajets"].sum(),
                "exemples": ", ".join(noms.get(c, c) for c in haut["DCLT"].head(NB_EXEMPLES)),
            })
        details.append(avec_gare.assign(groupe=groupe, nom=avec_gare["DCLT"].map(noms)))
    synthese = pd.DataFrame(synthese)
    synthese.round(2).to_csv(SORTIE / "synthese.csv", index=False, encoding="utf-8-sig")
    pd.concat(details).round(4).to_csv(SORTIE / "par_commune.csv", index=False, encoding="utf-8-sig")
    print(synthese.round(1).to_string(index=False))


if __name__ == "__main__":
    main()
