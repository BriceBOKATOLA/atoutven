"""
preparer_carte_nuit_2couleurs.py : carte de la nuit lisible d'un coup d'œil (page 4, changement validé le 2026-11-11).

La carte validée (donnees/carte_nuit.svg) a 6 nuances : l'œil ne les distingue pas et il faut chercher dans la
légende. Le message de la page est « la plupart des communes n'ont plus rien la nuit » : on garde exactement le
même dessin et les mêmes communes, mais en 2 couleurs seulement :
  - « aucun passage de minuit à 5h » (couleur de fond nuit #262E48 dans la carte d'origine) -> bleu-gris ;
  - « au moins un passage » (les 5 autres nuances) -> rose de la page.
Le seuil n'est pas un choix arbitraire : c'est la classe « Aucun passage » de la carte d'origine.

On compte aussi les communes de chaque classe, pour écrire le chiffre du titre de la carte (« 6 communes sur 10 »)
à partir de la carte elle-même, jamais à la main. Les tracés #1B2238 (hors classes, couleur du fond de carte)
ne sont pas comptés.

Entrée  : application/donnees/carte_nuit.svg
Sorties : application/donnees/carte_nuit_2couleurs.svg, application/donnees/carte_nuit_compte.csv

Lancer depuis le dossier application/ : python preparation/preparer_carte_nuit_2couleurs.py
"""

from pathlib import Path

import pandas as pd

DONNEES = Path(__file__).resolve().parents[1] / "donnees"
AUCUN_ORIGINE = "#262E48"                                              # classe « Aucun passage » de la carte d'origine
DESSERVIE_ORIGINE = ["#4a5478", "#747c98", "#9ea3b7", "#c7cad6", "#f1f2f6"]   # les 5 classes « au moins un passage »
AUCUN, DESSERVIE = "#3A4368", "#E58BC4"   # bleu-gris visible sur le fond nuit (contour clair) ; rose de la page 4


def main() -> None:
    """Recolorie la carte d'origine en 2 classes, ajoute le nom de Paris, et compte les communes de chaque classe."""
    svg = (DONNEES / "carte_nuit.svg").read_text(encoding="utf-8")
    aucun = svg.count(f'fill="{AUCUN_ORIGINE}"')
    desservies = sum(svg.count(f'fill="{c}"') for c in DESSERVIE_ORIGINE)
    for c in DESSERVIE_ORIGINE:
        svg = svg.replace(f'fill="{c}"', f'fill="{DESSERVIE}"')
    svg = svg.replace(f'fill="{AUCUN_ORIGINE}"', f'fill="{AUCUN}"')
    # Repère : Paris écrit sur la carte (position du centre de Paris dans la projection des cartes, 640 x 515)
    svg = svg.replace("</svg>", '<text x="272" y="182" text-anchor="middle" font-family="Plus Jakarta Sans, sans-serif" '
                                'font-size="13" font-weight="800" fill="#141A2E">Paris</text></svg>')
    (DONNEES / "carte_nuit_2couleurs.svg").write_text(svg, encoding="utf-8")
    pd.DataFrame([{"communes_aucun_passage": aucun, "communes_au_moins_un": desservies,
                   "communes_total": aucun + desservies}]).to_csv(DONNEES / "carte_nuit_compte.csv", index=False,
                                                                  encoding="utf-8-sig")
    print(f"Aucun passage : {aucun} communes sur {aucun + desservies} ({100 * aucun / (aucun + desservies):.0f} %)")


if __name__ == "__main__":
    main()
