"""
alleger_svg.py : allège les cartes SVG de l'application sans changer leur dessin.

Pourquoi : en ligne (Streamlit Community Cloud), les cartes sont envoyées dans la page à chaque affichage. La page des
solutions en contient deux (1,5 Mo) et l'Accueil une (2,2 Mo) : 7 secondes avant d'afficher le titre de l'Accueil,
et de la latence à chaque clic sur la page des solutions (mesuré le 2026-11-12).

Ce que fait le script (le dessin reste exactement le même) :
  1. Les contours des communes passent de coordonnées absolues à des écarts relatifs (svg_leger.relatif).
  2. Les cercles vides « <circle ...></circle> » deviennent « <circle .../> » (même élément, écriture plus courte).
Les cercles ne sont pas fusionnés en un seul tracé : avec la transparence, les zones denses changeraient d'aspect.
Contrôle fait le 2026-11-12 : géométrie identique point par point ; au rendu, au plus 26 pixels sur 1,8 million
diffèrent de plus de 8/255 (lissage des bords).

À lancer APRÈS les scripts qui produisent les cartes (preparer_*.py), car eux réécrivent les fichiers complets.
Entrée/sortie : les cartes de donnees/ utilisées par l'application (réécrites sur place).
"""

import re
import sys
from pathlib import Path

APPLICATION = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APPLICATION))   # pour importer svg_leger.py, partagé avec la page 6
from svg_leger import relatif  # noqa: E402

DONNEES = APPLICATION / "donnees"
# Cartes affichées par l'application (Accueil, nuit, solutions) ; carte_nuit.svg sert d'entrée à un autre script
CARTES = ["carte_points_accueil.svg", "carte_nuit_2couleurs.svg", "carte_velo_lisible.svg",
          "carte_velo_lisible_cadree.svg", "carte_navettes_lisible.svg", "carte_navettes_lisible_cadree.svg"]


def alleger(chemin: Path) -> tuple[int, int]:
    """Réécrit un fichier SVG sur place ; renvoie les tailles avant et après (en octets)."""
    texte = chemin.read_text(encoding="utf-8")
    avant = len(texte.encode("utf-8"))
    texte = re.sub(r' d="([^"]*)"', lambda m: f' d="{relatif(m.group(1))}"', texte)
    texte = re.sub(r"(<circle [^>]*?)></circle>", r"\1/>", texte)
    chemin.write_text(texte, encoding="utf-8")
    return avant, len(texte.encode("utf-8"))


if __name__ == "__main__":
    for nom in CARTES:
        a, b = alleger(DONNEES / nom)
        print(f"{nom:36} {a / 1024:7.0f} Ko -> {b / 1024:6.0f} Ko ({100 * (a - b) / a:.0f} % de moins)")
