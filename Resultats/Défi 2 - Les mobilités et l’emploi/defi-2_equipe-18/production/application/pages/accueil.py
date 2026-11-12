"""
accueil.py : page d'accueil, reprise de la maquette validée (maquettes_validees/Accueil.dc.html).

Mise en page de la maquette : texte, quatre chiffres et boutons à gauche ; carte à points à droite (image
d'origine de la maquette), avec sa légende et ses sources. Fond nuit.
Changements validés depuis la maquette (journal des choix, 11/11) : titre, description et libellés des chiffres
proposés par l'équipe ; « 13 fois moins » au lieu de « 7,6 % » ; nom de l'application.
"""

import streamlit as st

import utils as u

FICHIER = "pages/accueil.py"

u.appliquer_style(nuit=True)
u.menu(FICHIER, nuit=True)

actifs = u.lire("parts_modales_par_gs.csv").set_index("GS")["effectif_pondere"]
h21 = u.lire("h21_emplois_sans_gare.csv").set_index("groupe")
dest = u.lire("destinations_par_gs_et_couronne.csv")
gc_ouvriers = dest[(dest["couronne"] == "Grande couronne") & (dest["GS"] == "Ouvriers")]["Grande couronne (autre commune)"].iloc[0]

# Texte validé (retours de l'équipe, 11/11) ; « par nécessité » retiré : la donnée montre l'usage, pas la contrainte
message = ("En Île-de-France, de nombreux employés et ouvriers travaillent dans des communes éloignées du réseau "
           "ferroviaire. Pour rejoindre leur lieu de travail, notamment de banlieue à banlieue, la voiture s'impose "
           "souvent. L'enjeu n'est pas tant le métier exercé que l'accessibilité du lieu d'emploi.")
fois_moins_nuit = round(100 / u.part_nuit_pct())   # même chiffre que 7,6 %, compris sans explication
chiffres = [
    (f"{(actifs['Employé'] + actifs['Ouvrier']) / 1e6:.0f} millions",
     "d'actifs ne peuvent presque pas télétravailler (employés et ouvriers)", "#E4572E"),
    (u.fr(round(h21.loc['Employés et ouvriers', 'emplois_sans_gare'], -3)),
     "ouvriers et employés travaillent dans une commune sans gare", "#B23A86"),
    (f"{gc_ouvriers:.0f} %", "des ouvriers de grande couronne vont de banlieue à banlieue", "#B23A86"),
    (f"{fois_moins_nuit} fois moins", "de bus et de trains la nuit qu'entre 7h et 10h", "#F1F2F6"),
]

# Deux colonnes centrées verticalement, proportions de la maquette (1 / 1,05)
gauche, droite = st.columns([1, 1.05], gap="large", vertical_alignment="center")
with gauche:
    st.markdown(f'<div class="surtitre" style="color:#F28B6B"><span aria-hidden="true" style="width:26px;height:26px;'
                f'border-radius:50%;background:#E4572E;display:inline-flex;align-items:center;justify-content:center">'
                f'<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.4" '
                f'stroke-linecap="round" stroke-linejoin="round"><path d="M3 12h18"/><path d="M13 5l7 7-7 7"/></svg></span>'
                f'Mobilités et emploi en Île-de-France</div>', unsafe_allow_html=True)
    # Titre et formulation des chiffres repris des recommandations de Pierre THAI (captures annotées des maquettes, 11/11)
    u.bouton_ecouter("Quand le lieu de travail impose la voiture. " + message, nuit=True)
    st.markdown(f'<h1 class="titre" style="font-size:46px;line-height:1.1;color:#F1F2F6">Quand le lieu de travail '
                f'<span style="color:#F28B6B">impose la voiture</span></h1>'
                f'<p class="description" style="line-height:1.6">{message}</p>', unsafe_allow_html=True)
    st.markdown('<div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:6px">'
                + "".join(f'<div style="position:relative;background:#1B2238;border:1px solid #262E48;border-radius:16px;'
                          f'padding:12px 16px 12px 22px"><span aria-hidden="true" style="position:absolute;left:0;top:12px;'
                          f'bottom:12px;width:5px;border-radius:0 3px 3px 0;background:{c}"></span>'
                          f'<div style="font-family:Poppins,sans-serif;font-weight:800;font-size:28px;line-height:1.2;'
                          f'color:#F1F2F6">{v}</div><div style="font-size:14px;color:#C9CDD8">{t}</div></div>'
                          for v, t, c in chiffres)
                + '</div>', unsafe_allow_html=True)
    # Boutons de la maquette : un bouton principal plein (clair sur fond nuit) et un lien simple.
    # De vrais liens <a> vers l'adresse de chaque page : atteignables au clavier (contour visible, voir utils).
    # Adresses relatives, comme dans le menu : sur Streamlit Cloud, l'application tourne dans un cadre (voir utils.menu)
    st.markdown('<div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;margin-top:8px">'
                '<a class="bouton-principal" href="p1_metiers" target="_self" style="display:inline-flex;'
                'align-items:center;gap:10px;padding:14px 26px;background:#F1F2F6;border-radius:999px;font-weight:800;'
                'font-size:16px;color:#141A2E;text-decoration:none">Commencer le voyage →</a>'
                '<a href="p6_commune" target="_self" style="font-size:15px;font-weight:600;color:#8FC3DE">'
                'Aller directement à ma commune</a></div>', unsafe_allow_html=True)

with droite:
    # Image d'origine de la maquette (maquettes_validees/cartes/accueil_points.svg), légende et sources d'origine
    st.markdown(f'<figure style="margin:0;display:flex;flex-direction:column;gap:10px">'
                f'<div class="cadre-carte"><img class="carte-zoomable" '
                f'src="data:image/svg+xml;base64,{u.svg_base64("carte_points_accueil.svg")}" '
                f'alt="Carte à points de l\'Île-de-France : environ 10 000 points, chacun représentant 200 employés ou '
                f'ouvriers selon leur commune de résidence" style="width:100%;height:auto;display:block"></div>'
                f'<figcaption style="display:flex;align-items:center;gap:8px;font-size:14px;color:#C9CDD8">'
                f'<span aria-hidden="true" style="width:8px;height:8px;border-radius:50%;background:#F28B6B;flex-shrink:0">'
                f'</span>Chaque point = 200 employés ou ouvriers, placé au hasard dans leur commune de résidence '
                f'(2 millions au total).</figcaption>'
                f'<div style="font-size:14px;color:#9AA0B2">Sources : INSEE, recensement 2023 ; contours des communes, '
                f'geo.api.gouv.fr.</div></figure>', unsafe_allow_html=True)
