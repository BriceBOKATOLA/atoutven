"""
11_tester_h24_ponctualite.py : test de H24 (ponctualité des lignes et emplois desservis), selon le protocole écrit
dans hypotheses.md (section J) avant ce script.

Question : les lignes de RER et Transilien qui desservent le plus d'emplois d'employés et d'ouvriers (hors Paris)
sont-elles moins ponctuelles que les autres ?

Données :
  - SNCF, « Régularité mensuelle Transilien » (licence ODbL) : part des voyageurs arrivés à l'heure, par mois et par
    ligne ; 13 lignes (RER A à E, Transilien H, J, K, L, N, P, R, U). Métro, tram, bus et ligne V ne sont pas publiés
    dans ce jeu : ils ne peuvent pas être comparés.
  - IDFM, offre 2025 : communes où chaque ligne a au moins un arrêt avec un passage dans la semaine (même correction
    des codes commune que le script 07, fonctions réutilisées).
  - INSEE, recensement 2023 : emplois d'employés et d'ouvriers par commune de travail, hors Paris (script 07).

Critère (protocole) : H24 confirmée si les 4 lignes qui desservent le plus de ces emplois ont une ponctualité
moyenne inférieure d'au moins 2 points à celle des 9 autres. 13 lignes : résultat descriptif, pas de test statistique.

Entrées : production/data/brut/sncf_ponctualite/ (script 00) + données des scripts 07
Sorties : production/resultats/11_h24/ponctualite_lignes.csv

Lancer depuis le dossier production/ :
    python src/11_tester_h24_ponctualite.py
"""

import importlib.util
from pathlib import Path

import pandas as pd

PRODUCTION = Path(__file__).resolve().parent.parent
SORTIE = PRODUCTION / "resultats" / "11_h24"
FICHIER_SNCF = PRODUCTION / "data" / "brut" / "sncf_ponctualite" / "ponctualite_mensuelle_transilien.csv"
NB_MOIS = 12              # moyenne des 12 derniers mois publiés : lisse les mois exceptionnels (grèves, travaux)
NB_LIGNES_HAUT = 4        # lignes qui desservent le plus d'emplois d'employés et d'ouvriers
SEUIL_PTS = 2.0           # écart minimal de ponctualité (protocole)
LETTRES_RER = {"A", "B", "C", "D", "E"}


def charger_module(chemin: Path):
    """Réutilise les fonctions d'un script numéroté (nom commençant par un chiffre : import classique impossible)."""
    spec = importlib.util.spec_from_file_location(chemin.stem, chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def nom_usage(service: str, ligne: str) -> str:
    """Nom commun aux deux sources et aux pictogrammes de l'application : « RER D », « Train P »."""
    return f"RER {ligne}" if service == "RER" or ligne in LETTRES_RER else f"Train {ligne}"


def ponctualite() -> pd.DataFrame:
    """Ponctualité moyenne de chaque ligne sur les 12 derniers mois publiés, avec la période couverte."""
    sncf = pd.read_csv(FICHIER_SNCF, sep=";", dtype=str, encoding="utf-8-sig")
    sncf["taux"] = pd.to_numeric(sncf["taux_de_ponctualite"], errors="coerce")
    mois = sorted(sncf["date"].unique())[-NB_MOIS:]
    recent = sncf[sncf["date"].isin(mois)]
    resultat = recent.groupby(["service", "ligne"]).agg(ponctualite_pct=("taux", "mean"), mois=("taux", "count"))
    resultat = resultat.reset_index()
    resultat["ligne_nom"] = [nom_usage(s, l) for s, l in zip(resultat["service"], resultat["ligne"])]
    print(f"Période : {mois[0]} à {mois[-1]} ({len(mois)} mois) ; {len(resultat)} lignes")
    return resultat.set_index("ligne_nom")


def emplois_desservis(s07) -> pd.Series:
    """Emplois d'employés et d'ouvriers hors Paris situés dans les communes où chaque ligne s'arrête."""
    colonnes = (["libelle_mode_ligne", "nom_ligne_commerciale", "code_commune", "id_zone_de_correspondance"]
                + [f"nb_courses_{j}" for j in s07.JOURS])
    offre = pd.read_csv(s07.BRUT / "idfm_offre_hebdo_2025" / "offre_hebdomadaire_moyenne_hors_vacances.csv", sep=";",
                        usecols=colonnes, dtype={"code_commune": str, "nom_ligne_commerciale": str}, encoding="utf-8-sig")
    train = offre[offre["libelle_mode_ligne"] == "Train"].copy()
    zones = pd.read_csv(s07.BRUT / "idfm_referentiel_arrets" / "zones-de-correspondance.csv", sep=";",
                        usecols=["zdcid", "zdcpostalregion"], dtype=str, encoding="utf-8-sig")
    # Même correction que le script 07 : code commune repris du référentiel des zones de correspondance
    id_zone = train["id_zone_de_correspondance"].dropna().astype("int64").astype(str)
    train["code_commune"] = train["code_commune"].fillna(id_zone.map(zones.set_index("zdcid")["zdcpostalregion"]))
    train = train[train[[f"nb_courses_{j}" for j in s07.JOURS]].sum(axis=1) > 0].dropna(subset=["code_commune"])
    train["ligne_nom"] = [nom_usage("", l) for l in train["nom_ligne_commerciale"].astype(str)]
    communes_par_ligne = train.groupby("ligne_nom")["code_commune"].agg(set)

    emplois = s07.charger_emplois()                      # emplois hors Paris (toute résidence)
    eo = emplois[emplois["GS"].isin(["5", "6"])].groupby("DCLT")["IPONDI"].sum()
    return communes_par_ligne.map(lambda communes: eo[eo.index.isin(communes)].sum()).rename("emplois_eo_desservis")


def main() -> None:
    """Calcule la ponctualité et les emplois desservis par ligne, puis applique le critère du protocole."""
    SORTIE.mkdir(parents=True, exist_ok=True)
    s07 = charger_module(PRODUCTION / "src" / "07_tester_h21_emplois_gares.py")
    lignes = ponctualite().join(emplois_desservis(s07), how="left")
    assert lignes["emplois_eo_desservis"].notna().all(), "une ligne SNCF sans arrêt retrouvé dans l'offre IDFM"
    lignes = lignes.sort_values("emplois_eo_desservis", ascending=False)
    lignes["rang_emplois"] = range(1, len(lignes) + 1)
    lignes["dessert_le_plus"] = lignes["rang_emplois"] <= NB_LIGNES_HAUT
    lignes.round(2).to_csv(SORTIE / "ponctualite_lignes.csv", encoding="utf-8-sig")

    haut = lignes.loc[lignes["dessert_le_plus"], "ponctualite_pct"].mean()
    autres = lignes.loc[~lignes["dessert_le_plus"], "ponctualite_pct"].mean()
    print(lignes[["ponctualite_pct", "emplois_eo_desservis", "dessert_le_plus"]].round(1).to_string())
    print(f"Moyenne des 13 lignes : {lignes['ponctualite_pct'].mean():.1f} %")
    verdict = "CONFIRMÉE" if autres - haut >= SEUIL_PTS else "NON CONFIRMÉE"
    print(f"H24 : 4 lignes qui desservent le plus {haut:.1f} % ; 9 autres {autres:.1f} % ; écart {autres - haut:+.1f} pts "
          f"(seuil {SEUIL_PTS}) -> {verdict}")


if __name__ == "__main__":
    main()
