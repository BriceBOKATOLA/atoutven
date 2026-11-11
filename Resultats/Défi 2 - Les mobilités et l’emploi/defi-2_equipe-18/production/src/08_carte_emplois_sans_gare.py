"""
08_carte_emplois_sans_gare.py : carte à cercles proportionnels des emplois
d'employés et d'ouvriers situés dans une commune sans gare (résultat de H21).

Méthode cartographique (inspirée de Boris Mericskay) : un NOMBRE se montre par
une TAILLE (cercle dont la surface est proportionnelle au nombre d'emplois),
jamais par une couleur. La couleur de fond sert seulement à distinguer les
communes avec ou sans gare (deux catégories, nommées dans la légende).

Entrées : mêmes données que le script 07 (recensement 2023, offre IDFM 2025,
          référentiel des arrêts) + data/brut/geo_communes_idf/ (contours, centres)
Sorties : resultats/08_cartes/carte_emplois_sans_gare.svg
          resultats/08_cartes/emplois_sans_gare_par_commune.csv (alternative en tableau)

Lancer depuis la racine du projet :
    .venv\\Scripts\\python.exe src\\08_carte_emplois_sans_gare.py
"""

import importlib.util
import json
import math
from pathlib import Path

import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
BRUT = RACINE / "data" / "brut"
SORTIE = RACINE / "resultats" / "08_cartes"

# Dimensions du dessin, en pixels SVG
LARGEUR_PX = 640
MARGE_PX = 10
DISTANCE_MIN_PX = 1.5        # simplification des contours : écart invisible à l'œil à cette taille

# Cercles : rayon du plus gros cercle, en pixels. La surface (pas le rayon) est
# proportionnelle au nombre d'emplois, sinon l'œil surestime les grandes valeurs.
RAYON_MAX_PX = 16
SEUIL_EMPLOIS_CERCLE = 500   # en dessous, cercle trop petit pour être lu : non dessiné
NB_ETIQUETTES = 5            # communes nommées sur la carte (les plus grosses)

# Couleurs de la charte
FOND_AVEC_GARE = "#CDD1C9"   # gris moyen : commune desservie par le train
FOND_SANS_GARE = "#F0F1EE"   # gris très clair : commune sans gare
TRAIT_COMMUNE = "#FFFFFF"
CERCLE = "#E4572E"           # orange des métiers sur place
CONTOUR_CERCLE = "#8E2A10"   # contour foncé : le cercle reste visible sur les deux fonds
ENCRE = "#1B1F2A"


def charger_module(nom_fichier: str):
    """Réutilise les fonctions d'un script numéroté (le nom commence par un chiffre : import classique impossible)."""
    spec = importlib.util.spec_from_file_location(nom_fichier, RACINE / "src" / nom_fichier)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def emplois_sur_place_par_commune() -> pd.DataFrame:
    """Emplois d'employés et d'ouvriers par commune de travail hors Paris, avec la présence d'une gare."""
    h21 = charger_module("07_tester_h21_emplois_gares.py")
    gares = h21.communes_avec_gare()
    emplois = h21.charger_emplois()
    sur_place = emplois[emplois["GS"].isin(["5", "6"])]
    table = sur_place.groupby("DCLT")["IPONDI"].sum().rename("emplois_sur_place").to_frame()
    table["avec_gare"] = table.index.isin(gares)
    return table


def projeteur(contours: dict):
    """Renvoie une fonction (lon, lat) -> (x, y) en pixels.

    Projection équirectangulaire corrigée par le cosinus de la latitude moyenne :
    à l'échelle de l'Île-de-France, la déformation est négligeable et le calcul
    reste explicable en une phrase (pas de bibliothèque de projection à installer).
    """
    lons, lats = [], []
    for f in contours["features"]:
        anneaux = f["geometry"]["coordinates"] if f["geometry"]["type"] == "Polygon" else \
            [a for poly in f["geometry"]["coordinates"] for a in poly]
        for anneau in anneaux:
            for lon, lat in anneau:
                lons.append(lon)
                lats.append(lat)
    lon_min, lon_max, lat_min, lat_max = min(lons), max(lons), min(lats), max(lats)
    facteur = math.cos(math.radians((lat_min + lat_max) / 2))
    echelle = (LARGEUR_PX - 2 * MARGE_PX) / ((lon_max - lon_min) * facteur)
    hauteur = (lat_max - lat_min) * echelle + 2 * MARGE_PX

    def projeter(lon, lat):
        return (MARGE_PX + (lon - lon_min) * facteur * echelle, MARGE_PX + (lat_max - lat) * echelle)
    return projeter, hauteur


def simplifier(points: list) -> list:
    """Garde un point seulement s'il est à au moins DISTANCE_MIN_PX du dernier point gardé.

    Les contours officiels ont des milliers de points par commune, invisibles à
    cette échelle : sans simplification, le fichier SVG pèse plus de 3 Mo.
    """
    gardes = [points[0]]
    for x, y in points[1:]:
        if math.hypot(x - gardes[-1][0], y - gardes[-1][1]) >= DISTANCE_MIN_PX:
            gardes.append((x, y))
    return gardes


def chemin_svg(geometrie: dict, projeter) -> str:
    """Convertit un polygone GeoJSON en attribut d du SVG (points simplifiés, coordonnées arrondies)."""
    polygones = [geometrie["coordinates"]] if geometrie["type"] == "Polygon" else geometrie["coordinates"]
    morceaux = []
    for poly in polygones:
        for anneau in poly:
            points = simplifier([projeter(lon, lat) for lon, lat in anneau])
            if len(points) >= 3:   # un anneau réduit à 2 points ne dessine rien
                morceaux.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in points) + "Z")
    return "".join(morceaux)


def main() -> None:
    """Calcule les emplois par commune, dessine la carte et enregistre le tableau qui l'accompagne."""
    SORTIE.mkdir(parents=True, exist_ok=True)
    table = emplois_sur_place_par_commune()

    contours = json.load(open(BRUT / "geo_communes_idf" / "communes_idf_contours.geojson", encoding="utf-8"))
    centres = {c["code"]: c for c in json.load(open(BRUT / "geo_communes_idf" / "communes_idf_centres.json",
                                                    encoding="utf-8"))}
    projeter, hauteur = projeteur(contours)

    # Fond : communes avec gare en gris moyen, sans gare en gris clair. Paris compte comme desservie.
    fonds = []
    for f in contours["features"]:
        code = f["properties"]["code"]
        avec_gare = code.startswith("75") or bool(table["avec_gare"].get(code, False))
        couleur = FOND_AVEC_GARE if avec_gare else FOND_SANS_GARE
        fonds.append(f'<path d="{chemin_svg(f["geometry"], projeter)}" fill="{couleur}" '
                     f'stroke="{TRAIT_COMMUNE}" stroke-width="0.4"/>')

    # Cercles : seulement les communes sans gare, les plus gros dessinés en premier
    # pour que les petits restent visibles par-dessus
    sans_gare = table[~table["avec_gare"]].sort_values("emplois_sur_place", ascending=False)
    sans_gare["nom"] = [centres[c]["nom"] if c in centres else c for c in sans_gare.index]
    valeur_max = sans_gare["emplois_sur_place"].max()
    cercles, etiquettes = [], []
    for rang, (code, ligne) in enumerate(sans_gare.iterrows()):
        if ligne["emplois_sur_place"] < SEUIL_EMPLOIS_CERCLE or code not in centres:
            continue
        lon, lat = centres[code]["centre"]["coordinates"]
        x, y = projeter(lon, lat)
        rayon = RAYON_MAX_PX * math.sqrt(ligne["emplois_sur_place"] / valeur_max)
        cercles.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rayon:.1f}" fill="{CERCLE}" fill-opacity="0.8" '
                       f'stroke="{CONTOUR_CERCLE}" stroke-width="0.8"/>')
        if rang < NB_ETIQUETTES:
            # Contour blanc autour du texte (paint-order) : lisible sur n'importe quel fond
            etiquettes.append(f'<text x="{x + rayon + 3:.1f}" y="{y + 4:.1f}" font-family="Plus Jakarta Sans, sans-serif" '
                              f'font-size="12" font-weight="700" fill="{ENCRE}" stroke="#FFFFFF" stroke-width="3" '
                              f'paint-order="stroke">{ligne["nom"]}</text>')

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LARGEUR_PX} {hauteur:.0f}" '
           f'width="{LARGEUR_PX}" height="{hauteur:.0f}">' + "".join(fonds) + "".join(cercles)
           + "".join(etiquettes) + "</svg>")
    (SORTIE / "carte_emplois_sans_gare.svg").write_text(svg, encoding="utf-8")

    # Arrondi à une décimale, pas à l'unité : arrondie à l'unité, une commune à 499,6 emplois passait à 500 dans le
    # tableau alors que la carte (seuil de 500, calculé avant l'arrondi) ne la dessine pas : 155 lignes contre 154 cercles.
    sans_gare[["nom", "emplois_sur_place"]].round(1).to_csv(SORTIE / "emplois_sans_gare_par_commune.csv",
                                                           encoding="utf-8-sig")
    print(f"Communes sans gare avec au moins {SEUIL_EMPLOIS_CERCLE} emplois sur place (cercles) : {len(cercles)}")
    print(f"Plus gros cercle : {sans_gare['nom'].iloc[0]} ({valeur_max:,.0f} emplois)".replace(",", " "))
    print(f"Carte : {SORTIE / 'carte_emplois_sans_gare.svg'} ({len(svg) / 1024:.0f} Ko)")


if __name__ == "__main__":
    main()
