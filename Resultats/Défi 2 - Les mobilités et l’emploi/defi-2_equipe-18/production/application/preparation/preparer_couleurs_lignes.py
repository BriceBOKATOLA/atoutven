"""
preparer_couleurs_lignes.py : couleurs officielles des lignes ferrées, pour les pictogrammes de la page 6.

Source : IDFM, « Référentiel des lignes de transport en commun d'Île-de-France », téléchargé par l'API ouverte du
portail open data d'IDFM (pas de récupération sur un site web). Licence : ODbL, d'où la mention dans les sources de
la page 6 et dans le README ; le petit fichier produit ici (couleurs_lignes.csv) est lui aussi sous ODbL.

On ne récupère PAS les logos officiels : ils ne sont pas dans les données ouvertes (champ « picto » vide pour toutes
les lignes) et ce sont des marques. Nos pictogrammes suivent notre charte : carré encre du mode + pastille à la
couleur officielle de la ligne, en carré arrondi (le rond de couleur est réservé aux métiers).

Contrôles d'accessibilité calculés pour chaque ligne :
  - contraste du texte officiel (blanc, ou noir remplacé par notre encre) sur la couleur de la ligne. Les pastilles
    écrivent le texte en gras de 19 px (« grand texte ») : le seuil est 3:1. Sous ce seuil (CDG VAL, ORLYVAL,
    Transilien N), on garde la couleur officielle du fond et on prend le texte, blanc ou encre, le plus lisible ;
  - contraste de la pastille sur le fond blanc des cartes : sous 3:1 (seuil des éléments graphiques, WCAG 1.4.11),
    on ajoute un fin contour encre pour que la pastille reste visible.

Entrée  : API IDFM (copie gardée dans production/data/brut/idfm_referentiel_lignes/)
Sortie  : application/donnees/couleurs_lignes.csv

Lancer depuis le dossier application/ : python preparation/preparer_couleurs_lignes.py
"""

import urllib.request
from pathlib import Path

import pandas as pd

APPLICATION = Path(__file__).resolve().parents[1]
BRUT = APPLICATION.parent / "data" / "brut" / "idfm_referentiel_lignes"
FICHIER_BRUT = BRUT / "referentiel_lignes_ferrees.csv"
SORTIE = APPLICATION / "donnees" / "couleurs_lignes.csv"
URL = ("https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/referentiel-des-lignes/exports/csv"
       "?select=transportmode,transportsubmode,networkname,shortname_line,colourweb_hexa,textcolourweb_hexa,status"
       "&where=transportmode%20in%20(%22rail%22,%22metro%22,%22tram%22)&delimiter=%3B")
SEUIL_GRAPHIQUE = 3.0   # contraste minimal d'un élément graphique sur son fond (WCAG 1.4.11)
SEUIL_TEXTE_GRAS = 3.0  # contraste minimal d'un texte en gras de 19 px et plus (« grand texte », WCAG 1.4.3)
ENCRE = "1B1F2A"        # encre de notre charte, à la place du noir officiel (même rendu, palette cohérente)


def luminance(hexa: str) -> float:
    """Luminance relative d'une couleur (formule WCAG)."""
    canaux = [int(hexa[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    r, g, b = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canaux]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a: str, b: str) -> float:
    """Rapport de contraste entre deux couleurs hexadécimales (sans #)."""
    la, lb = sorted([luminance(a), luminance(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


def nom_usage(ligne) -> str:
    """Même nom que celui calculé par preparer_communes.py (« RER D », « Métro 7 », « Train H », « Tram T12 »)."""
    if ligne.transportmode == "metro":
        return f"Métro {ligne.shortname_line}"
    if ligne.transportmode == "tram":
        return f"Tram {ligne.shortname_line}"
    if ligne.networkname == "RER":
        return f"RER {ligne.shortname_line}"
    if ligne.networkname == "Transilien":
        return f"Train {ligne.shortname_line}"
    return ligne.shortname_line          # TER, CDG VAL, ORLYVAL


def main() -> None:
    """Télécharge le référentiel (une fois), puis écrit une ligne par nom d'usage avec ses couleurs et contrôles."""
    if not FICHIER_BRUT.exists():
        BRUT.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(URL, FICHIER_BRUT)
    lignes = pd.read_csv(FICHIER_BRUT, sep=";", dtype=str, encoding="utf-8-sig")
    lignes = lignes[lignes["status"] == "active"]
    lignes["ligne"] = [nom_usage(l) for l in lignes.itertuples()]
    # Les TER ont plusieurs entrées (une par région) de même couleur : on garde la première
    lignes = lignes.drop_duplicates("ligne")
    lignes["mode"] = lignes["transportmode"].map({"metro": "metro", "tram": "tram", "rail": "train"})
    lignes["court"] = lignes["shortname_line"].str.replace("Bis", "B")
    lignes["fond"] = "#" + lignes["colourweb_hexa"].str.upper()
    officiel = lignes["textcolourweb_hexa"].str.lower().map(lambda t: "FFFFFF" if t == "ffffff" else ENCRE)
    meilleur = [max(("FFFFFF", ENCRE), key=lambda t: contraste(f, t)) for f in lignes["colourweb_hexa"]]
    lignes["texte_modifie"] = [contraste(f, o) < SEUIL_TEXTE_GRAS for f, o in zip(lignes["colourweb_hexa"], officiel)]
    texte = [m if mod else o for o, m, mod in zip(officiel, meilleur, lignes["texte_modifie"])]
    lignes["texte"] = ["#" + x for x in texte]
    lignes["contraste_texte"] = [contraste(f, x) for f, x in zip(lignes["colourweb_hexa"], texte)]
    lignes["contraste_fond_blanc"] = [contraste(f, "ffffff") for f in lignes["colourweb_hexa"]]
    lignes["contour"] = lignes["contraste_fond_blanc"] < SEUIL_GRAPHIQUE
    sortie = lignes[["ligne", "mode", "court", "fond", "texte", "texte_modifie", "contour", "contraste_texte",
                     "contraste_fond_blanc"]]
    sortie.round(2).sort_values("ligne").to_csv(SORTIE, index=False, encoding="utf-8-sig")
    modifies = sortie[sortie["texte_modifie"]]
    print(f"{len(sortie)} lignes ; {int(sortie['contour'].sum())} avec contour ; texte changé pour : "
          f"{', '.join(modifies['ligne'])} ; contraste minimal du texte : {sortie['contraste_texte'].min():.2f}:1")


if __name__ == "__main__":
    main()
