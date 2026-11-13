"""
preparer_cartes_solutions.py : les deux cartes de la page 5 (« Les solutions »), dessinées pour être lues d'un coup d'œil.

Même méthode que les cartes de la nuit et de « Chercher ma commune », validée par l'équipe le 2026-11-11 : on ne
colore que ce qui porte le message, et des repères numérotés (1 à 5) placés sur la carte renvoient au classement
affiché à côté. Les numéros remplacent les noms écrits sur la carte : en petite couronne, les communes sont si
petites que les noms se chevaucheraient.

Carte du vélo : part des trajets en voiture de banlieue à banlieue qui font moins de 5 km, par commune de
résidence (preparer_velo_communes.py, même méthode que le script 06). Deux classes seulement :
  - « au moins 1 trajet sur 3 » (seuil lisible : un tiers), en orange ;
  - « moins de 1 sur 3 », en gris clair ; communes à effectif faible (moins de 200 trajets) en gris plus pâle.
Carte des navettes : communes sans gare d'au moins 500 emplois d'employés et d'ouvriers (script 08), en cercles
proportionnels (un nombre = une taille) ; les 5 plus grandes en encre, les autres en violet pâle.

Projection et simplification des contours : fonctions du script 08 (mêmes cartes que le reste de l'application).

Entrées : production/data/brut/geo_communes_idf/, application/donnees/velo_par_commune.csv,
          application/donnees/emplois_sans_gare_par_commune.csv
Chaque carte est écrite deux fois : en entier, et cadrée sur la zone qui porte le message (comme la carte de
« Chercher ma commune ») : Paris et la petite couronne pour le vélo, les plus grands pôles d'emploi pour les navettes.
La page s'ouvre sur la vue cadrée ; un interrupteur montre toute l'Île-de-France.

Sorties : application/donnees/carte_velo_lisible.svg (+ _cadree), carte_navettes_lisible.svg (+ _cadree),
          cartes_solutions_compte.csv

Lancer depuis le dossier application/ : python preparation/preparer_cartes_solutions.py
"""

import importlib.util
import json
import math
from pathlib import Path

import pandas as pd

APPLICATION = Path(__file__).resolve().parents[1]
PRODUCTION = APPLICATION.parent
DONNEES = APPLICATION / "donnees"
BRUT = PRODUCTION / "data" / "brut" / "geo_communes_idf"
SEUIL_TIERS_PCT = 100 / 3          # « au moins 1 trajet en voiture sur 3 fait moins de 5 km »
NB_REPERES = 5                     # repères numérotés, comme le classement affiché à côté de la carte
ORANGE, GRIS, GRIS_PALE, ENCRE, VIOLET_PALE = "#E4572E", "#D9DCD5", "#EEF0EC", "#1B1F2A", "#D9A6C7"
SEUIL_EMPLOIS = 500               # même seuil que la carte validée et le script 08 (« au moins 500 emplois »)
ECART_REPERES_PX = 20             # deux repères plus proches que cela sont écartés (communes voisines)
DEPARTEMENTS_VELO = ("75", "92", "93", "94")   # cadrage du vélo : Paris et petite couronne, où se trouve l'anneau
NB_POLES_CADRAGE = 15             # cadrage des navettes : les 15 plus grands pôles sans gare (avec 25, un pôle isolé
                                  # au sud laissait un grand vide en bas de la carte)
MARGE_CADRAGE_PX = 14
RAYON_MAX_PX = 16                  # rayon du plus grand cercle (Gonesse), les autres proportionnels à la surface


def charger_module(chemin: Path):
    """Réutilise les fonctions d'un script numéroté (nom commençant par un chiffre, donc non importable)."""
    spec = importlib.util.spec_from_file_location(chemin.stem, chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def repere(x: float, y: float, numero: int, k: float = 1.0) -> str:
    """Repère numéroté : rond encre cerné de blanc, numéro blanc (lisible sur toutes les couleurs de la carte).

    k = échelle du repère. La vue cadrée agrandit toute la carte (environ 2,5 fois) : on y dessine des repères plus
    petits pour qu'ils gardent à l'écran une taille proche de la vue entière (remarque de l'équipe, 11/11 : repères
    « extrêmement gros » en vue cadrée).
    """
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{9 * k:.2f}" fill="{ENCRE}" stroke="#FFFFFF" stroke-width="{2 * k:.2f}"/>'
            f'<text x="{x:.1f}" y="{y + 4 * k:.1f}" text-anchor="middle" font-family="Plus Jakarta Sans, sans-serif" '
            f'font-size="{11 * k:.2f}" font-weight="800" fill="#FFFFFF">{numero}</text>')


def placer(x: float, y: float, places: list, k: float = 1.0) -> tuple:
    """Décale un repère vers le haut à droite tant qu'il touche un repère déjà posé (communes voisines)."""
    while any(math.hypot(x - a, y - b) < ECART_REPERES_PX * k for a, b in places):
        x, y = x + 12 * k, y - 12 * k
    places.append((x, y))
    return x, y


def boite(chemin: str) -> tuple:
    """Rectangle englobant d'un tracé SVG (x min, y min, x max, y max)."""
    import re
    nombres = [float(v) for v in re.findall(r"-?\d+\.?\d*", chemin)]
    return min(nombres[0::2]), min(nombres[1::2]), max(nombres[0::2]), max(nombres[1::2])


AGRANDISSEMENT_REPERES = 1.3    # en vue cadrée, repères 1,3 fois plus grands à l'écran qu'en vue entière (pas 2,5)


def ecrire(nom: str, entete_entier: str, largeur_entiere: float, cadre: tuple, contenu: str, reperes) -> None:
    """Écrit la carte entière et la carte cadrée (même dessin, seule la fenêtre affichée change).

    reperes(k) dessine les repères à l'échelle k : 1 pour la vue entière ; pour la vue cadrée, k compense
    l'agrandissement du cadrage.
    """
    x0, y0, x1, y1 = cadre
    k_cadre = (x1 - x0) / largeur_entiere * AGRANDISSEMENT_REPERES
    (DONNEES / f"{nom}.svg").write_text(entete_entier + contenu + reperes(1.0) + "</svg>", encoding="utf-8")
    (DONNEES / f"{nom}_cadree.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.1f} {y0:.1f} {x1 - x0:.1f} {y1 - y0:.1f}">'
        + contenu + reperes(k_cadre) + "</svg>", encoding="utf-8")


def englobant(boites: list) -> tuple:
    """Rectangle qui contient toutes les boîtes, avec une marge."""
    return (min(b[0] for b in boites) - MARGE_CADRAGE_PX, min(b[1] for b in boites) - MARGE_CADRAGE_PX,
            max(b[2] for b in boites) + MARGE_CADRAGE_PX, max(b[3] for b in boites) + MARGE_CADRAGE_PX)


def main() -> None:
    """Dessine les deux cartes et enregistre les comptes qui serviront aux titres (jamais écrits à la main)."""
    s08 = charger_module(PRODUCTION / "src" / "08_carte_emplois_sans_gare.py")
    contours = json.load(open(BRUT / "communes_idf_contours.geojson", encoding="utf-8"))
    centres = {c["code"]: c["centre"]["coordinates"] for c in
               json.load(open(BRUT / "communes_idf_centres.json", encoding="utf-8"))}
    projeter, hauteur = s08.projeteur(contours)
    chemins = {f["properties"]["code"]: s08.chemin_svg(f["geometry"], projeter) for f in contours["features"]}
    entete = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {s08.LARGEUR_PX} {hauteur:.0f}">'

    # --- Vélo : 2 classes autour du seuil d'un tiers, 5 repères sur les communes du classement ---
    velo = pd.read_csv(DONNEES / "velo_par_commune.csv", encoding="utf-8-sig", dtype={"code_commune": str})
    part = velo.set_index("code_commune")["part_moins_5km_pct"]
    fonds = "".join(
        f'<path d="{d}" fill="{(ORANGE if part[c] >= SEUIL_TIERS_PCT else GRIS) if c in part.index else GRIS_PALE}" '
        f'stroke="#FFFFFF" stroke-width="0.35"/>' for c, d in chemins.items())
    def reperes_velo(k: float) -> str:
        """Les 5 repères du classement, écartés si deux communes voisines se touchent."""
        places = []
        return "".join(repere(*placer(*projeter(*centres[c]), places, k), i + 1, k)
                       for i, c in enumerate(velo["code_commune"].head(NB_REPERES)))
    # Le cadre contient Paris, la petite couronne ET les 5 communes du classement (Neuville-sur-Oise est dans le 95)
    codes_cadre = {c for c in chemins if c[:2] in DEPARTEMENTS_VELO} | set(velo["code_commune"].head(NB_REPERES))
    cadre_velo = englobant([boite(chemins[c]) for c in codes_cadre])
    ecrire("carte_velo_lisible", entete, s08.LARGEUR_PX, cadre_velo, fonds, reperes_velo)

    # --- Navettes : cercles proportionnels, les 5 plus grands en encre et numérotés ---
    sans = pd.read_csv(DONNEES / "emplois_sans_gare_par_commune.csv", encoding="utf-8-sig", dtype={"DCLT": str})
    # Le fichier compte toutes les communes sans gare : on garde celles d'au moins 500 emplois, comme la carte validée
    sans = sans[sans["emplois_sur_place"] >= SEUIL_EMPLOIS]
    sans = sans.sort_values("emplois_sur_place", ascending=False).reset_index(drop=True)
    fonds = "".join(f'<path d="{d}" fill="{GRIS_PALE}" stroke="#FFFFFF" stroke-width="0.35"/>' for d in chemins.values())
    plus_grand = sans["emplois_sur_place"].max()
    cercles, boites_poles, positions = "", [], []
    # Du plus petit au plus grand : les grands cercles passent au-dessus et restent visibles
    for i in reversed(range(len(sans))):
        r = sans.loc[i]
        x, y = projeter(*centres[r["DCLT"]])
        rayon = RAYON_MAX_PX * math.sqrt(r["emplois_sur_place"] / plus_grand)   # surface proportionnelle au nombre
        haut = i < NB_REPERES
        if i < NB_POLES_CADRAGE:
            boites_poles.append((x - rayon, y - rayon, x + rayon, y + rayon))
        cercles += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rayon:.1f}" fill="{ENCRE if haut else VIOLET_PALE}" '
                    f'fill-opacity="{1 if haut else 0.85}" stroke="#FFFFFF" stroke-width="0.8"/>')
        if haut:
            positions.append((x, y, rayon, i + 1))

    def reperes_navettes(k: float) -> str:
        """Numéro écrit DANS chacun des 5 plus grands cercles (remarque de l'équipe, 11/11) : un petit repère posé à côté
        faisait deux objets pour une seule commune, et on ne comprenait pas le lien. Taille du chiffre proportionnelle
        au cercle, sans plafond : le chiffre remplit le rond aux trois quarts."""
        return "".join(
            f'<text x="{x:.1f}" y="{y + rayon * 0.75 * 0.36:.1f}" text-anchor="middle" '
            f'font-family="Plus Jakarta Sans, sans-serif" font-size="{rayon * 0.75:.2f}" font-weight="800" '
            f'fill="#FFFFFF">{n}</text>' for x, y, rayon, n in positions)
    ecrire("carte_navettes_lisible", entete, s08.LARGEUR_PX, englobant(boites_poles), fonds + cercles, reperes_navettes)

    compte = {"communes_velo_au_moins_un_tiers": int((part >= SEUIL_TIERS_PCT).sum()),
              "communes_velo_avec_donnees": int(len(part)),
              "communes_sans_gare_500_emplois": int(len(sans))}
    pd.DataFrame([compte]).to_csv(DONNEES / "cartes_solutions_compte.csv", index=False, encoding="utf-8-sig")
    print(compte)


if __name__ == "__main__":
    main()
