"""
p1_metiers.py : station 1, « Ceux qui ne télétravaillent pas ».

Message : employés et ouvriers (2 millions d'actifs en Île-de-France) ne peuvent presque pas télétravailler :
chaque jour travaillé est un trajet.

Visuel principal : trois silhouettes-jauges. Le remplissage est calculé sur la SURFACE de la silhouette,
pas sur sa hauteur (le corps est plus large que la tête : remplir 52 % de la hauteur couvrirait environ 65 %
de la surface, ce qui exagérerait l'écart).
"""

import math

import pandas as pd
import streamlit as st

import utils as u

FICHIER = "pages/p1_metiers.py"

# Télétravail au moins un jour par semaine, salariés, France entière, 2025.
# Source : INSEE Références, « Organisation du temps de travail », juillet 2026, figure 3a.
TELETRAVAIL_PCT = {"Cadres": 52, "Employés": 8, "Ouvriers": 0}

# Silhouette d'un seul tenant (tête et épaules reliées par le cou), dans un cadre de 120 x 200
SILHOUETTE = "M60 8A24 24 0 0 1 74 51.5C90 56 102 80 102 116V200H18V116C18 80 30 56 46 51.5A24 24 0 0 1 60 8Z"


def largeur(y: float) -> float:
    """Largeur de la silhouette à la hauteur y (tête = cercle, épaules = courbe, corps = rectangle de 84)."""
    if y < 8:
        return 0.0
    if y < 51.5:
        return 2 * math.sqrt(max(0.0, 24 ** 2 - (y - 32) ** 2))
    if y < 116:
        # Épaules : courbe de Bézier de (74 ; 51,5) à (102 ; 116), approchée point par point
        t = min(range(401), key=lambda k: abs(_bezier(k / 400)[1] - y)) / 400
        return 2 * (_bezier(t)[0] - 60)
    return 84.0


def _bezier(t: float) -> tuple:
    """Point de la courbe des épaules (côté droit) pour t entre 0 et 1."""
    pts = [(74, 51.5), (90, 56), (102, 80), (102, 116)]
    return tuple((1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t ** 2 * c + t ** 3 * d
                 for a, b, c, d in zip(*pts))


@st.cache_data
def niveau_remplissage(part_pct: float) -> float:
    """Hauteur y (dans le cadre 120 x 200) où s'arrête le remplissage pour couvrir part_pct % de la SURFACE.

    On additionne la largeur de la silhouette tranche par tranche, du bas vers le haut, jusqu'à la part voulue.
    """
    pas = 0.25
    tranches = [(200 - k * pas, largeur(200 - k * pas) * pas) for k in range(int(192 / pas))]
    total = sum(s for _, s in tranches)
    cumul = 0.0
    for y, s in tranches:
        if cumul >= total * part_pct / 100:
            return y
        cumul += s
    return 8.0


def silhouette(metier: str, part: int) -> str:
    """Une silhouette-jauge : fond gris, partie remplie dans la couleur du métier, valeur écrite en dessous."""
    c = u.METIERS[metier]
    y = niveau_remplissage(part)
    signe = {"Cadres": '<path d="M55 64h10l3 13-8 44-8-44z" fill="#1B1F2A"/>',
             "Employés": '<rect x="68" y="98" width="20" height="13" rx="3" fill="#FFFFFF" stroke="#1B1F2A" stroke-width="2"/>',
             "Ouvriers": '<path d="M33 24a27 23 0 0 1 54 0z" fill="#1B1F2A"/><rect x="27" y="22" width="66" height="7" rx="3.5" fill="#1B1F2A"/>'}[metier]
    ident = "s" + metier[:3].lower()
    return (f'<figure role="img" aria-label="{metier} : {part} % télétravaillent au moins un jour par semaine" '
            f'style="margin:0;display:flex;flex-direction:column;align-items:center;gap:8px">'
            f'<svg aria-hidden="true" width="132" height="210" viewBox="0 0 120 200"><defs><clipPath id="{ident}">'
            f'<path d="{SILHOUETTE}"/></clipPath></defs>'
            f'<rect width="120" height="200" fill="#E6E9E3" clip-path="url(#{ident})"/>'
            f'<rect y="{y:.1f}" width="120" height="{200 - y:.1f}" fill="{c["donnee"]}" clip-path="url(#{ident})"/>'
            f'{signe}<line x1="6" x2="114" y1="{y:.1f}" y2="{y:.1f}" stroke="{c["texte"]}" stroke-width="2" '
            f'stroke-dasharray="4 3"/></svg>'
            f'<span style="padding:2px 14px;border-radius:999px;background:{c["texte"]};color:#fff;font-weight:700;'
            f'font-size:20px">{part} %</span><figcaption style="font-weight:700;font-size:16px;color:{c["texte"]}">'
            f'{metier}</figcaption></figure>')


# --- Page
u.appliquer_style()
u.menu(FICHIER)

actifs = u.lire("parts_modales_par_gs.csv").set_index("GS")["effectif_pondere"]
sur_place = actifs["Employé"] + actifs["Ouvrier"]
# Formulations reprises des remarques de l'équipe (11/11)
retenir = "Sans télétravail, chaque journée travaillée commence par un trajet."

# « Surtout » et non « réservé » : 48 % des cadres ne télétravaillent pas ; titre affirmatif plutôt qu'une question
u.entete(FICHIER, 'Le télétravail, <span style="color:#C0401A">surtout pour les cadres</span>',
         "Pour de nombreux employés et ouvriers, la mobilité n'est pas une option : c'est une condition d'accès à "
         "l'emploi.", retenir,
         u.panneau("Sans télétravail possible", f"{sur_place / 1e6:.0f} millions".replace(".", ","),
                   "d'actifs en Île-de-France (employés et ouvriers)", "#E4572E", "#C0401A"))

st.markdown('<div class="carte"><h2 class="sous-titre">Télétravail selon la catégorie socioprofessionnelle : part des salariés qui '
            'télétravaillent au moins un jour par semaine</h2><div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px">'
            + "".join(silhouette(m, p) for m, p in TELETRAVAIL_PCT.items())
            + '</div><p style="font-size:14px;color:#5E6475;margin:12px 0 0">Le niveau de remplissage indique la part de '
              'télétravailleurs dans chaque catégorie (calculé sur la surface de la silhouette). Groupe « employés » de l\'INSEE : aides-soignants, agents d\'accueil, vendeurs, employés '
              'administratifs, agents de sécurité…</p></div>', unsafe_allow_html=True)
u.tableau(pd.DataFrame({"Métier": list(TELETRAVAIL_PCT),
                        "Télétravail au moins 1 jour par semaine (%)": list(TELETRAVAIL_PCT.values()),
                        "Actifs résidant en Île-de-France": [u.fr(actifs[m.rstrip("s") if m != "Cadres" else m]) for m in TELETRAVAIL_PCT]}))

# Limite fidèle au calcul : les deux sources sont affichées côte à côte, jamais multipliées entre elles
u.encadres(retenir, "Parts de télétravail nationales (INSEE, enquête Emploi 2025) et nombre d'actifs franciliens "
           "(INSEE, recensement 2023) : deux sources distinctes, non combinées.")
u.navigation_bas(FICHIER)
u.sources("INSEE, enquête Emploi 2025 (Insee Références, juillet 2026) ; INSEE, recensement 2023, actifs résidant "
          "en Île-de-France.")
