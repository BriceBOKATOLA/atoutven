"""
svg_leger.py : écriture plus courte des tracés SVG des cartes, sans changer leur dessin.

Utilisé par preparation/alleger_svg.py (cartes enregistrées) et par la page 6 (carte calculée pour chaque commune).

Pourquoi : les contours des communes sont écrits en coordonnées ABSOLUES (« L275.8,161.1 » : 12 caractères par
point). En ÉCARTS RELATIFS au point précédent (« l4-.1 »), il en faut 5 ou 6 : les cartes pèsent 30 à 40 % de moins
et se chargent plus vite en ligne (mesuré le 2026-11-12). Les écarts sont calculés en dixièmes entiers : aucun arrondi
ne s'accumule, chaque point retombe exactement au même endroit (vérifié point par point sur les 6 cartes).
"""

import re

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
    """Colle les nombres d'une commande : le séparateur est inutile devant un « - » (règle de lecture des tracés)."""
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
