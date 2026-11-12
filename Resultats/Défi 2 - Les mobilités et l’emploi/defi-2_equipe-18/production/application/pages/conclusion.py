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

description = ("Les emplois des employés et ouvriers sont plus souvent dans des communes sans gare. Là, près de 3 trajets sur 4 se "
               "font en voiture, cadres compris. Ce n'est donc pas le métier qui éloigne du réseau, c'est le lieu "
               "de travail.")
u.entete(FICHIER, 'Le réseau mène à Paris, <span style="color:#C0401A">pas aux emplois de banlieue</span>', description)

# (icône, page, nom, chiffre, texte, correspondance)
stations = [
    ("personnes", "pages/p1_metiers.py", "Ceux qui ne télétravaillent pas",
     f"{(actifs['Employé'] + actifs['Ouvrier']) / 1e6:.0f} millions", "d'actifs ne peuvent presque pas télétravailler", False),
    ("repere", "pages/p2_gares.py", "Loin des gares", f"{h21.loc['Ouvriers', 'part_sans_gare_pct']:.0f} %",
     f"des emplois d'ouvriers hors Paris sont sans gare (cadres : {h21.loc['Cadres', 'part_sans_gare_pct']:.0f} %)", True),
    ("voiture", "pages/p3_voiture.py", "Comment ils vont travailler", f"{v[('Cadres', 'sans gare')]:.0f} %",
     "des cadres prennent la voiture quand leur lieu de travail n'a pas de gare", True),
    ("lune", "pages/p4_nuit.py", "Les trajets de nuit", f"{round(100 / u.part_nuit_pct())} fois moins",
     "de bus et de trains la nuit qu'entre 7h et 10h", False),
    ("velo", "pages/p5_solutions.py", "Les solutions", "2 solutions", "trajets courts pour le vélo, emplois sans gare pour les navettes", False),
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
# Bloc du bas repris de la maquette validée (maquettes_validees/Conclusion.dc.html) : une icône de mode devant
# chaque piste, une icône devant chaque titre, trois pastilles sous la méthode. Seul changement validé : 14 hypothèses.
communes_navettes = u.lire("emplois_sans_gare_par_commune.csv").sort_values("emplois_sur_place", ascending=False)["nom"].head(4)
pistes = [
    ("velo", f"Faciliter le vélo pour les {u.fr(round(h16.loc['Ensemble', 'dont_moins_5km'], -3))} trajets en voiture "
             f"de moins de 5 km entre communes de banlieue."),
    ("navette", "Relier par navette ou covoiturage organisé les communes d'emploi sans gare : "
                + ", ".join(communes_navettes) + "."),
    ("lune", "Mesurer les temps de trajet de nuit en bus, pour ceux qui travaillent entre minuit et 5h (piste à tester)."),
]
g, d = st.columns(2)
with g:
    st.markdown(f'<section aria-labelledby="titre-pistes" class="encadre" style="background:#FCEDE8;border-radius:16px;'
                f'padding:18px 22px;display:flex;flex-direction:column;gap:12px">'
                f'<h2 id="titre-pistes" style="margin:0;display:flex;align-items:center;gap:8px;font-size:16px;'
                f'font-weight:700;color:#C0401A">{u.icone("ampoule", 18, "#C0401A")}<span style="margin-left:8px">Pistes que suggèrent les données</span></h2>'
                + "".join(f'<div class="piste" style="display:flex;gap:12px;align-items:flex-start;font-size:15px;'
                          f'line-height:1.5">{u.badge_mode(ic)}<span>{texte}</span></div>' for ic, texte in pistes)
                + '</section>', unsafe_allow_html=True)
with d:
    pastille = ('padding:3px 12px;border-radius:999px;background:#E5EFF5;color:#1F6A8C;font-size:14px;font-weight:700')
    st.markdown(f'<section aria-labelledby="titre-methode" class="encadre" style="background:#FFFFFF;border:1px solid '
                f'#E7EAE4;border-radius:16px;padding:18px 22px;display:flex;flex-direction:column;gap:12px">'
                f'<h2 id="titre-methode" style="margin:0;display:flex;align-items:center;gap:8px;font-size:16px;'
                f'font-weight:700"><svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" '
                f'stroke="#1B1F2A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3 8-8"/>'
                f'<path d="M20 12v7a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h9"/></svg><span style="margin-left:8px">Notre méthode</span></h2>'
                f'<p style="margin:0;font-size:15px;line-height:1.55"><strong>15 hypothèses testées</strong>, dont '
                f'<strong>5 réfutées en tout ou en partie</strong>, toutes publiées avec leurs critères, écrits avant '
                f"d'ouvrir les données pour les tests principaux. Une erreur dans les données (gares sans code commune) "
                f'a été trouvée et corrigée.</p>'
                f'<div style="display:flex;flex-wrap:wrap;gap:6px"><span class="pastille" style="{pastille}">Données '
                f'ouvertes</span><span class="pastille" style="{pastille}">Code open source</span><span class="pastille" '
                f'style="{pastille}">Chaque chiffre vient d\'un script</span></div>'
                f'<p style="margin:0;font-size:14px;color:#4E5466">Code et données : <a style="color:#1B1F2A" '
                # Nouvel onglet : GitHub refuse de s'afficher dans le cadre de Streamlit Cloud ; l'ouverture est
                # annoncée dans le texte du lien (RGAA, critère 13.2)
                f'href="https://github.com/Melvy-hub/hackaviz_2026-equipe-18" target="_blank" rel="noopener noreferrer">'
                f'dépôt GitHub de l\'équipe (nouvel onglet)</a></p>'
                f'</section>', unsafe_allow_html=True)

u.navigation_bas(FICHIER)
u.sources("INSEE (recensement 2023, enquête Emploi 2025) ; Île-de-France Mobilités (offre 2025, référentiel des arrêts) ; "
          "geo.api.gouv.fr.")
