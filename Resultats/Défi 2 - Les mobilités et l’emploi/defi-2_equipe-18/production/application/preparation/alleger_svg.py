"""
alleger_svg.py : allège les cartes SVG de l'application sans changer leur dessin.

Pourquoi : en ligne (Streamlit Community Cloud), les cartes sont envoyées dans la page à chaque affichage. La page des
solutions en contient deux (1,5 Mo) et l'Accueil une (2,2 Mo) : 7 secondes avant d'afficher le titre de l'Accueil,
et de la latence à chaque clic sur la page des solutions (mesuré le 2026-11-12).

Ce que fait le script (le dessin reste exactement le même) :
  1. Les contours des communes sont écrits en coordonnées ABSOLUES (« L275.8,161.1 » : 12 caractères par point).
     On les réécrit en ÉCARTS RELATIFS au point précédent (« l4-.1 » : 5 à 6 caractères). Les écarts sont calculés
     en dixièmes entiers : aucun arrondi ne s'accumule, chaque point retombe exactement au même endroit.
  2. Les cercles vides « <circle ...></circle> » deviennent « <circle .../> » (même élément, écriture plus courte).
Les cercles ne sont pas fusionnés en un seul tracé : avec la transparence, les zones denses changeraient d'aspect.

À lancer APRÈS les scripts qui produisent les cartes (preparer_*.py), car eux réécrivent les fichiers complets.
Entrée/sortie : les cartes de donnees/ utilisées par l'application (réécrites sur place).
"""

import re
from pathlib import Path

DONNEES = Path(__file__).resolve().parents[1] / "donnees"
# Cartes affichées par l'application (Accueil, nuit, solutions) ; carte_nuit.svg sert d'entrée à un autre script
CARTES = ["carte_points_accueil.svg", "carte_nuit_2couleurs.svg", "carte_velo_lisible.svg",
          "carte_velo_lisible_cadree.svg", "carte_navettes_lisible.svg", "carte_navettes_lisible_cadree.svg"]
# Un tracé « simple » : uniquement des commandes M, L, Z absolues et des nombres à une décimale au plus
TRACE_SIMPLE = re.compile(r"^[MLZ0-9.,\- ]+$")


def en_dixiemes(nombre: str) -> int:
    """« 275.8 » -> 2758 : on travaille en entiers pour que les écarts soient exacts."""
    return round(float(nombre) * 10)


def ecrire(dixiemes: int) -> str:
    """2758 -> « 275.8 », 40 -> « 4 », -1 -> « -.1 » : l'écriture la plus courte d'un nombre à une décimale."""
    signe = "-" if dixiemes < 0 else ""
    entier, decimale = divmod(abs(dixiemes), 10)
    texte = str(entier) if decimale == 0 else (f"{entier}.{decimale}" if entier else f".{decimale}")
    return signe + texte


def joindre(nombres: list[str]) -> str:
    """Colle les nombres d'une commande ; le séparateur est inutile devant un « - » ou après un nombre à virgule
    suivi d'un « . » (règle de lecture des tracés SVG). Par prudence, on ne supprime que celui devant « - »."""
    sortie = nombres[0]
    for n in nombres[1:]:
        sortie += n if n.startswith("-") else " " + n
    return sortie


def relatif(d: str) -> str:
    """Réécrit un tracé M/L/Z absolu en tracé relatif équivalent ; renvoie le tracé tel quel s'il n'est pas simple."""
    if not TRACE_SIMPLE.match(d):
        return d
    jetons = re.findall(r"[MLZ]|-?\d*\.?\d+", d)
    sortie, i = [], 0
    x = y = depart_x = depart_y = None
    while i < len(jetons):
        commande = jetons[i]
        if commande == "Z":
            sortie.append("z")
            x, y = depart_x, depart_y          # après Z, le point courant revient au début du sous-tracé
            i += 1
            continue
        if commande not in ("M", "L"):
            return d                            # forme inattendue : on ne touche à rien
        i += 1
        points = []
        while i < len(jetons) and jetons[i] not in ("M", "L", "Z"):
            points.append((en_dixiemes(jetons[i]), en_dixiemes(jetons[i + 1])))
            i += 2
        if commande == "M":
            # Premier point en absolu (M) ; les points suivants d'un M sont des « lignes vers » en relatif
            (px, py), suite = points[0], points[1:]
            sortie.append("M" + ecrire(px) + "," + ecrire(py))
            x, y, depart_x, depart_y = px, py, px, py
        else:
            suite = points
        if suite:
            morceaux = []
            for px, py in suite:
                morceaux += [ecrire(px - x), ecrire(py - y)]
                x, y = px, py
            sortie.append("l" + joindre(morceaux))
    return "".join(sortie)


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
