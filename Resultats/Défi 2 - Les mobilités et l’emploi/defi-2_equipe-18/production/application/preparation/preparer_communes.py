"""
preparer_communes.py : données de la page 6 « Chercher ma commune ».

Pour chaque commune d'Île-de-France (commune de résidence), on calcule, pour ses employés et ouvriers qui ont un
emploi (recensement 2023, mobilités professionnelles) :
  - combien ils sont ;
  - la part qui travaille dans la commune même, et la part qui travaille à Paris ;
  - leurs communes de travail (part de chacune), pour la carte et la liste « principales communes de travail » ;
  - la part de leurs emplois situés dans une commune sans gare ;
et, pour la commune elle-même : a-t-elle une gare, et quelles lignes (métro, RER, train, tram) s'y arrêtent.

Choix :
  - Paris compte pour une seule commune : le recensement code le lieu de résidence « 75056 » (Paris entier)
    mais le lieu de travail par arrondissement (75101 à 75120). On regroupe les arrondissements pour comparer.
  - Même définition de la gare que les pages 2 et 3 (script 07) : au moins un arrêt de métro, RER, train ou tram
    avec un passage dans la semaine. On réutilise ses fonctions et sa correction (90 % des arrêts de train
    n'ont pas de code commune dans le fichier d'offre : on le reprend du référentiel des zones de correspondance).
  - Une commune de travail n'est gardée dans le fichier des destinations que si elle pèse au moins 0,25 % des
    emplois de la commune de résidence : c'est le seuil de la légende de la maquette (en dessous, commune non
    colorée), et cela garde le fichier léger (l'application en ligne doit rester frugale).
  - Les contours des communes sont projetés et simplifiés une fois pour toutes (fonctions du script 08), pour que
    la page dessine la carte sans bibliothèque cartographique.

Entrées : production/data/brut/ (recensement 2023, offre IDFM 2025, référentiel des arrêts, contours des communes)
Sorties : application/donnees/communes_residence.csv, communes_destinations.csv, contours_communes.json

Lancer depuis le dossier application/ : python preparation/preparer_communes.py
"""

import importlib.util
import json
from pathlib import Path

import pandas as pd

APPLICATION = Path(__file__).resolve().parents[1]
PRODUCTION = APPLICATION.parent
BRUT = PRODUCTION / "data" / "brut"
DONNEES = APPLICATION / "donnees"
METIERS_EO = ["5", "6"]          # GS du recensement : 5 = employés, 6 = ouvriers
SEUIL_DESTINATION_PCT = 0.25     # en dessous, la commune de travail n'est pas colorée (légende de la maquette)
CODE_PARIS = "75056"
# Noms des lignes ferrées tels que les voyageurs les connaissent (le fichier IDFM classe le RER dans « Train »)
LETTRES_RER = {"A", "B", "C", "D", "E"}


def charger_module(chemin: Path):
    """Réutilise les fonctions d'un script numéroté (nom commençant par un chiffre, donc non importable)."""
    spec = importlib.util.spec_from_file_location(chemin.stem, chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def nom_ligne(mode: str, ligne: str) -> str:
    """Nom d'usage d'une ligne : « RER D », « Train R », « Métro 7 », « Tram T1 », « TER »."""
    if mode == "Train":
        if ligne in LETTRES_RER:
            return f"RER {ligne}"
        return "TER" if ligne.startswith("TER") else f"Train {ligne}"
    if mode == "Métro":
        return f"Métro {ligne}"
    # Tramway : « T1 » devient « Tram T1 » ; les navettes automatiques (CDG VAL, ORLYVAL) gardent leur nom
    return f"Tram {ligne}" if ligne[:1] == "T" and ligne[1:2].isdigit() else ligne


def lignes_par_commune(s07) -> pd.Series:
    """Lignes ferrées (avec au moins un passage dans la semaine) qui s'arrêtent dans chaque commune."""
    colonnes = (["libelle_mode_ligne", "nom_ligne_commerciale", "code_commune", "id_zone_de_correspondance"]
                + [f"nb_courses_{j}" for j in s07.JOURS])
    offre = pd.read_csv(BRUT / "idfm_offre_hebdo_2025" / "offre_hebdomadaire_moyenne_hors_vacances.csv", sep=";",
                        usecols=colonnes, dtype={"code_commune": str, "nom_ligne_commerciale": str}, encoding="utf-8-sig")
    ferre = offre[offre["libelle_mode_ligne"].isin(s07.MODES_FERRES)].copy()
    zones = pd.read_csv(BRUT / "idfm_referentiel_arrets" / "zones-de-correspondance.csv", sep=";",
                        usecols=["zdcid", "zdcpostalregion"], dtype=str, encoding="utf-8-sig")
    # Même correction que le script 07 : code commune repris du référentiel quand il manque
    id_zone = ferre["id_zone_de_correspondance"].dropna().astype("int64").astype(str)
    ferre["code_commune"] = ferre["code_commune"].fillna(id_zone.map(zones.set_index("zdcid")["zdcpostalregion"]))
    ferre = ferre[ferre[[f"nb_courses_{j}" for j in s07.JOURS]].sum(axis=1) > 0].dropna(subset=["code_commune"])
    ferre["code_commune"] = ferre["code_commune"].where(~ferre["code_commune"].str.startswith("751"), CODE_PARIS)
    ferre["ligne"] = [nom_ligne(m, str(n)) for m, n in zip(ferre["libelle_mode_ligne"], ferre["nom_ligne_commerciale"])]
    # Ordre d'affichage : RER, métro, train, tram (les plus fréquentés d'abord), puis ordre alphabétique
    rang = {"RER": 0, "Métro": 1, "Train": 2, "TER": 3}
    return ferre.groupby("code_commune")["ligne"].agg(
        lambda s: ", ".join(sorted(set(s), key=lambda x: (rang.get(x.split()[0], 4), len(x), x))))


def main() -> None:
    """Calcule les trois fichiers de la page 6 et affiche les chiffres d'Évry-Courcouronnes pour contrôle."""
    s07 = charger_module(PRODUCTION / "src" / "07_tester_h21_emplois_gares.py")
    s08 = charger_module(PRODUCTION / "src" / "08_carte_emplois_sans_gare.py")
    gares = s07.communes_avec_gare()
    gares = {CODE_PARIS if c.startswith("751") else c for c in gares}

    # Employés et ouvriers qui habitent en Île-de-France, où qu'ils travaillent (même hors de la région)
    actifs = pd.read_parquet(BRUT / "insee_mobpro_2023" / "RP2023_mobpro.parquet",
                             columns=["COMMUNE", "DCLT", "REGION", "GS", "IPONDI"],
                             filters=[("REGION", "==", "11")])
    actifs = actifs[actifs["GS"].isin(METIERS_EO)].copy()
    actifs["DCLT"] = actifs["DCLT"].where(~actifs["DCLT"].str.startswith("751"), CODE_PARIS)

    contours = json.load(open(BRUT / "geo_communes_idf" / "communes_idf_contours.geojson", encoding="utf-8"))
    centres = json.load(open(BRUT / "geo_communes_idf" / "communes_idf_centres.json", encoding="utf-8"))
    infos = pd.DataFrame([{"code": c["code"], "nom": c["nom"], "departement": c["codeDepartement"]} for c in centres])
    noms = infos.set_index("code")["nom"]

    # Destinations : part de chaque commune de travail dans les emplois des habitants
    flux = actifs.groupby(["COMMUNE", "DCLT"])["IPONDI"].sum().rename("actifs").reset_index()
    flux["part_pct"] = 100 * flux["actifs"] / flux.groupby("COMMUNE")["actifs"].transform("sum")
    flux["travail_avec_gare"] = flux["DCLT"].isin(gares)

    residence = flux.groupby("COMMUNE").agg(employes_ouvriers=("actifs", "sum")).join(
        flux[flux["COMMUNE"] == flux["DCLT"]].set_index("COMMUNE")["part_pct"].rename("part_meme_commune_pct")).join(
        flux[flux["DCLT"] == CODE_PARIS].set_index("COMMUNE")["part_pct"].rename("part_paris_pct")).join(
        flux[~flux["travail_avec_gare"]].groupby("COMMUNE")["part_pct"].sum().rename("part_emplois_sans_gare_pct")).join(
        flux[flux["part_pct"] >= SEUIL_DESTINATION_PCT].groupby("COMMUNE").size().rename("communes_au_moins_0_25_pct"))
    residence = residence.fillna(0)
    residence = infos.set_index("code").join(residence, how="inner")
    residence["gare"] = residence.index.isin(gares)
    residence["lignes"] = residence.index.map(lignes_par_commune(s07)).fillna("")
    residence.index.name = "code"
    residence.round(2).reset_index().to_csv(DONNEES / "communes_residence.csv", index=False, encoding="utf-8-sig")

    destinations = flux[flux["part_pct"] >= SEUIL_DESTINATION_PCT].rename(
        columns={"COMMUNE": "code_residence", "DCLT": "code_travail"})
    # Une destination hors Île-de-France n'a pas de nom dans le fichier des communes : on l'indique
    destinations["nom_travail"] = destinations["code_travail"].map(noms).fillna("Hors Île-de-France")
    destinations[["code_residence", "code_travail", "nom_travail", "part_pct", "travail_avec_gare"]].round(
        {"part_pct": 2}).to_csv(DONNEES / "communes_destinations.csv", index=False, encoding="utf-8-sig")

    # Contours projetés et simplifiés, une seule fois (même projection que les cartes du script 08)
    projeter, hauteur = s08.projeteur(contours)
    chemins = {f["properties"]["code"]: s08.chemin_svg(f["geometry"], projeter) for f in contours["features"]}
    json.dump({"largeur": s08.LARGEUR_PX, "hauteur": round(hauteur, 1), "chemins": chemins},
              open(DONNEES / "contours_communes.json", "w", encoding="utf-8"), ensure_ascii=False)

    evry = residence.loc["91228"]
    print(evry.to_string())
    print(destinations[destinations["code_residence"] == "91228"].nlargest(6, "part_pct").to_string(index=False))
    print(f"{len(residence)} communes, {len(destinations)} lignes de destinations, "
          f"contours {(DONNEES / 'contours_communes.json').stat().st_size / 1024:.0f} Ko")


if __name__ == "__main__":
    main()
