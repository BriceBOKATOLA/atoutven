"""
preparer_communes.py : données de la page 6 « Chercher ma commune ».

Pour chaque commune d'Île-de-France (commune de résidence), on calcule, pour ses cadres, ses employés et ses
ouvriers qui ont un emploi (recensement 2023, mobilités professionnelles), séparément pour chaque catégorie :
  - combien ils sont ;
  - combien travaillent dans la commune même, combien à Paris, combien dans une commune sans gare ;
  - combien travaillent dans chacune de leurs communes de travail (carte et liste « principales communes ») ;
et, pour la commune elle-même : a-t-elle une gare, et quelles lignes (métro, RER, train, tram) s'y arrêtent.

Filtre par catégorie (demande de l'équipe, 2026-11-12 : les cadres manquaient, chacun doit pouvoir choisir sa catégorie).
La page laisse allumer une ou plusieurs catégories ; elle additionne alors leurs EFFECTIFS puis calcule les parts.
On stocke donc des effectifs (pondérés, arrondis au dixième) et non des parts : deux parts ne s'additionnent pas.

Choix :
  - Paris compte pour une seule commune : le recensement code le lieu de résidence « 75056 » (Paris entier)
    mais le lieu de travail par arrondissement (75101 à 75120). On regroupe les arrondissements pour comparer.
  - Même définition de la gare que les pages 2 et 3 (script 07) : au moins un arrêt de métro, RER, train ou tram
    avec un passage dans la semaine. On réutilise ses fonctions et sa correction (90 % des arrêts de train
    n'ont pas de code commune dans le fichier d'offre : on le reprend du référentiel des zones de correspondance).
  - Une commune de travail n'est gardée dans le fichier des destinations que si elle pèse au moins 0,25 % des
    emplois de la commune de résidence pour AU MOINS UNE catégorie (on garde alors les trois effectifs). C'est le seuil
    de la légende de la maquette (en dessous, commune non colorée), et cela garde le fichier léger. Ce choix rend les
    parts exactes pour toute combinaison de catégories : si une combinaison atteint 0,25 %, au moins une de ses
    catégories l'atteint seule (une part d'une somme est toujours comprise entre les parts de ses morceaux).
  - Fichier frugal : une colonne d'effectifs par catégorie (C, E, O) ; le nom et la gare de la commune de travail ne
    sont pas répétés à chaque ligne, la page les reprend du fichier des communes.
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
# GS du recensement (varmod_mobpro_2023.csv) : 3 = cadres, 5 = employés, 6 = ouvriers ; lettre courte pour les colonnes
CATEGORIES = {"3": "C", "5": "E", "6": "O"}
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

    # Cadres, employés et ouvriers qui habitent en Île-de-France, où qu'ils travaillent (même hors de la région)
    actifs = pd.read_parquet(BRUT / "insee_mobpro_2023" / "RP2023_mobpro.parquet",
                             columns=["COMMUNE", "DCLT", "REGION", "GS", "IPONDI"],
                             filters=[("REGION", "==", "11")])
    actifs = actifs[actifs["GS"].isin(CATEGORIES)].copy()
    actifs["cat"] = actifs["GS"].map(CATEGORIES)
    actifs["DCLT"] = actifs["DCLT"].where(~actifs["DCLT"].str.startswith("751"), CODE_PARIS)

    contours = json.load(open(BRUT / "geo_communes_idf" / "communes_idf_contours.geojson", encoding="utf-8"))
    centres = json.load(open(BRUT / "geo_communes_idf" / "communes_idf_centres.json", encoding="utf-8"))
    infos = pd.DataFrame([{"code": c["code"], "nom": c["nom"], "departement": c["codeDepartement"]} for c in centres])

    # Flux : une ligne par (commune de résidence, commune de travail), une colonne d'effectifs par catégorie
    flux = actifs.pivot_table(index=["COMMUNE", "DCLT"], columns="cat", values="IPONDI", aggfunc="sum", fill_value=0)
    flux = flux.reindex(columns=list(CATEGORIES.values()), fill_value=0)
    total = flux.groupby(level="COMMUNE").transform("sum")          # effectif de chaque catégorie dans la commune
    code_res = flux.index.get_level_values("COMMUNE")
    code_trav = pd.Series(flux.index.get_level_values("DCLT"), index=flux.index)

    # Communes de résidence : effectifs par catégorie (total, même commune, Paris, commune de travail sans gare)
    residence = infos.set_index("code")
    for c in CATEGORIES.values():
        par_commune = lambda masque: flux.loc[masque, c].groupby(level="COMMUNE").sum()
        residence[f"actifs_{c}"] = flux[c].groupby(level="COMMUNE").sum()
        residence[f"meme_commune_{c}"] = par_commune(code_res == code_trav.values)
        residence[f"paris_{c}"] = par_commune((code_trav == CODE_PARIS).values)
        residence[f"sans_gare_{c}"] = par_commune((~code_trav.isin(gares)).values)
    residence = residence.fillna(0)
    residence["gare"] = residence.index.isin(gares)
    residence["lignes"] = residence.index.map(lignes_par_commune(s07)).fillna("")
    residence.index.name = "code"
    residence.round(1).reset_index().to_csv(DONNEES / "communes_residence.csv", index=False, encoding="utf-8-sig")

    # Destinations : gardées si au moins une catégorie dépasse 0,25 % (voir l'en-tête : parts exactes pour toute combinaison)
    garder = ((flux / total.where(total > 0)) * 100 >= SEUIL_DESTINATION_PCT).any(axis=1)
    destinations = flux[garder].round(1).reset_index().rename(columns={"COMMUNE": "code_residence", "DCLT": "code_travail"})
    destinations.to_csv(DONNEES / "communes_destinations.csv", index=False, encoding="utf-8-sig")

    # Contours projetés et simplifiés, une seule fois (même projection que les cartes du script 08)
    projeter, hauteur = s08.projeteur(contours)
    chemins = {f["properties"]["code"]: s08.chemin_svg(f["geometry"], projeter) for f in contours["features"]}
    json.dump({"largeur": s08.LARGEUR_PX, "hauteur": round(hauteur, 1), "chemins": chemins},
              open(DONNEES / "contours_communes.json", "w", encoding="utf-8"), ensure_ascii=False)

    # Contrôle : Évry-Courcouronnes, employés + ouvriers, doit redonner les chiffres d'avant (14 700, 29 %, 13 %, 19 %)
    e = residence.loc["91228"]
    eo = e["actifs_E"] + e["actifs_O"]
    print(f"Évry, employés et ouvriers : {eo:.0f} actifs, même commune {100 * (e['meme_commune_E'] + e['meme_commune_O']) / eo:.2f} %, "
          f"Paris {100 * (e['paris_E'] + e['paris_O']) / eo:.2f} %, sans gare {100 * (e['sans_gare_E'] + e['sans_gare_O']) / eo:.2f} %")
    print(f"Évry, cadres : {e['actifs_C']:.0f} actifs, même commune {100 * e['meme_commune_C'] / e['actifs_C']:.2f} %")
    print(f"{len(residence)} communes, {len(destinations)} lignes de destinations, fichiers "
          f"{(DONNEES / 'communes_residence.csv').stat().st_size / 1024:.0f} Ko et "
          f"{(DONNEES / 'communes_destinations.csv').stat().st_size / 1024:.0f} Ko")


if __name__ == "__main__":
    main()
