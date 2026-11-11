"""
conclusion.py : terminus du récit.

Message : le réseau mène à Paris, pas aux emplois de banlieue. Ce n'est pas le métier qui éloigne du réseau,
c'est le lieu de travail.

Visuel : plan de ligne. Les stations 2 et 3 sont des « correspondances » (double rond, chiffre plus grand) :
elles portent le résultat central. Chaque station est un lien vers sa page.
"""

import streamlit as st

import utils as u

FICHIER = "pages/conclusion.py"

u.appliquer_style()
u.menu(FICHIER)

actifs = u.lire("parts_modales_par_gs.csv").set_index("GS")["effectif_pondere"]
h21 = u.lire("h21_emplois_sans_gare.csv").set_index("groupe")
v = u.lire("voiture_selon_gare_destination.csv").set_index(["groupe", "commune_de_travail"])["part_voiture_pct"]
h16 = u.lire("h16_trajets_courts_voiture.csv").set_index("groupe")

description = ("Les emplois des métiers sur place sont plus souvent dans des communes sans gare. Là, tout le monde "
               "prend la voiture, cadres compris. Ce n'est donc pas le métier qui éloigne du réseau, c'est le lieu "
               "de travail.")
u.entete(FICHIER, 'Le réseau mène à Paris, <span style="color:#C0401A">pas aux emplois de banlieue</span>', description)

# (icône, page, nom, chiffre, texte, correspondance)
stations = [
    ("personnes", "pages/p1_metiers.py", "Ceux qui ne télétravaillent pas",
     f"{(actifs['Employé'] + actifs['Ouvrier']) / 1e6:.0f} millions", "d'actifs exercent un métier qui se fait sur place", False),
    ("repere", "pages/p2_gares.py", "Loin des gares", f"{h21.loc['Ouvriers', 'part_sans_gare_pct']:.0f} %",
     f"des emplois d'ouvriers hors Paris sont sans gare (cadres : {h21.loc['Cadres', 'part_sans_gare_pct']:.0f} %)", True),
    ("voiture", "pages/p3_voiture.py", "Comment ils vont travailler", f"{v[('Cadres', 'sans gare')]:.0f} %",
     "des cadres prennent la voiture quand leur lieu de travail n'a pas de gare", True),
    ("lune", "pages/p4_nuit.py", "Les trajets de nuit", f"{round(100 / u.part_nuit_pct())} fois moins",
     "de bus et de trains la nuit qu'à l'heure de pointe", False),
    ("velo", "pages/p5_solutions.py", "Les solutions", "2 cibles", "trajets courts pour le vélo, emplois sans gare pour les navettes", False),
]


def station_html(numero: int, icone: str, nom: str, chiffre: str, texte: str, coeur: bool) -> str:
    """Une station du plan de ligne : icône de la page, rond (double si correspondance), nom, chiffre, phrase."""
    rond = ("width:38px;height:38px;border:4px solid #1B1F2A;box-shadow:0 0 0 4px #fff,0 0 0 8px #1B1F2A"
            if coeur else "width:32px;height:32px;border:4px solid #1B1F2A")
    taille, couleur = ("38px", "#C0401A") if coeur else ("26px", u.ENCRE)
    return (f'<li style="display:flex;flex-direction:column;align-items:center;gap:8px;text-align:center">'
            f'{u.badge_mode(icone)}<span aria-hidden="true" style="height:44px;display:flex;align-items:center">'
            f'<span style="{rond};border-radius:50%;background:#fff;box-sizing:border-box;display:flex;align-items:center;'
            f'justify-content:center;font-weight:800;font-size:14px">{numero}</span></span>'
            f'<span style="font-size:15px;font-weight:700;color:#4E5466">{nom}</span>'
            f'<span style="font-family:Poppins,sans-serif;font-weight:800;font-size:{taille};color:{couleur};line-height:1.1">'
            f'{chiffre}</span><span style="font-size:14px;line-height:1.4">{texte}</span></li>')


st.markdown('<div class="carte"><div style="display:flex;justify-content:space-between;align-items:center">'
            '<h2 class="sous-titre">Le voyage en cinq stations</h2><span style="display:inline-flex;align-items:center;'
            f'gap:6px;font-size:14px;font-weight:700;color:#3F4555">{u.icone("drapeau", 16, u.ENCRE)}Terminus : vous êtes ici'
            '</span></div><div style="position:relative"><div class="trait-ligne" aria-hidden="true" style="position:absolute;left:10%;right:14px;'
            'top:59px;height:6px;background:#1B1F2A;border-radius:3px"></div><div class="trait-ligne" aria-hidden="true" style="position:absolute;'
            'left:30%;width:20%;top:55px;height:14px;background:#1B1F2A;border-radius:7px"></div><div class="trait-ligne" aria-hidden="true" '
            'style="position:absolute;right:0;top:52px;border-left:18px solid #1B1F2A;border-top:10px solid transparent;'
            'border-bottom:10px solid transparent"></div><ol style="list-style:none;margin:0;padding:0;position:relative;'
            'display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:14px">'
            + "".join(station_html(i + 1, ic, nom, ch, tx, cc) for i, (ic, _, nom, ch, tx, cc) in enumerate(stations))
            + '</ol><div style="display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:14px;margin-top:12px"><div '
              'style="grid-column:2 / span 2;border-top:3px solid #C0401A;padding-top:6px;text-align:center;font-size:14px;'
              'font-weight:700;color:#C0401A">Le cœur du résultat : c\'est le lieu de travail qui décide</div></div></div></div>',
            unsafe_allow_html=True)

# Les stations du dessin ne sont pas cliquables : le menu latéral sert de navigation, au clavier aussi.
g, d = st.columns(2)
with g:
    st.markdown(f'<div class="encadre" style="background:#FCEDE8"><div style="font-weight:700;color:#C0401A;margin-bottom:6px">'
                f'Pistes que suggèrent les données</div>'
                f'<p style="margin:0 0 6px">Vélo : {u.fr(round(h16.loc["Ensemble", "dont_moins_5km"], -3))} trajets en voiture '
                f'de moins de 5 km entre communes de banlieue.</p>'
                f'<p style="margin:0 0 6px">Navettes ou covoiturage organisé vers les zones d\'emploi sans gare.</p>'
                f'<p style="margin:0">Mesurer les temps de trajet de nuit en bus (piste à tester).</p></div>',
                unsafe_allow_html=True)
with d:
    st.markdown('<div class="encadre" style="background:#FFFFFF;border:1px solid #E7EAE4"><div style="font-weight:700;'
                'margin-bottom:6px">Notre méthode</div><p style="margin:0">13 hypothèses testées, dont 5 réfutées en tout '
                'ou en partie, avec un critère écrit avant d\'ouvrir les données. Une erreur dans les données (gares sans '
                'code commune) a été trouvée et corrigée. Données ouvertes, code open source, chaque chiffre vient d\'un '
                'script.</p></div>', unsafe_allow_html=True)

u.navigation_bas(FICHIER)
u.sources("INSEE (recensement 2023, enquête Emploi 2025) ; Île-de-France Mobilités (offre 2025, référentiel des arrêts) ; "
          "geo.api.gouv.fr.")
