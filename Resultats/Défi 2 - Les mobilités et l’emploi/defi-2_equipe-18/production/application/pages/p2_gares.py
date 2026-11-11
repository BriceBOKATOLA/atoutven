"""
p2_gares.py : station 2, « Loin des gares ».

Message : hors de Paris, 1 emploi d'ouvrier sur 4 se trouve dans une commune sans gare (ni métro, ni RER,
ni train, ni tram), contre 1 emploi de cadre sur 8.

Visuel principal : barres horizontales, une par métier (couleur fixe par métier, valeur écrite au bout).
Données : script 07 (résultats copiés dans donnees/).
"""

import altair as alt
import pandas as pd
import streamlit as st

import utils as u

FICHIER = "pages/p2_gares.py"

u.appliquer_style()
u.menu(FICHIER)

h21 = u.lire("h21_emplois_sans_gare.csv").set_index("groupe")
dest = u.lire("destinations_par_gs_et_couronne.csv")
gc = dest[dest["couronne"] == "Grande couronne"].set_index("GS")["Grande couronne (autre commune)"]
sans_gare_sur_place = h21.loc["Employés et ouvriers", "emplois_sans_gare"]

retenir = (f"Leurs emplois sont en banlieue, souvent là où le train ne va pas. En grande couronne, "
           f"{gc['Ouvriers']:.0f} % des ouvriers travaillent dans une autre commune de banlieue, contre "
           f"{gc['Cadres']:.0f} % des cadres.")
u.entete(FICHIER, 'Leurs emplois sont <span style="color:#B23A86">loin des gares</span>',
         f"Hors de Paris, 1 emploi d'ouvrier sur 4 se trouve dans une commune sans gare (ni métro, ni RER, ni train, "
         f"ni tram), contre 1 emploi de cadre sur 8.", retenir,
         u.panneau("Emplois sans gare", u.fr(round(sans_gare_sur_place, -3)), "d'employés et d'ouvriers, hors Paris",
                   "#B23A86", "#B23A86", "train_barre"))

# --- Visuel principal : barres
metiers = ["Cadres", "Employés", "Ouvriers"]
donnees = pd.DataFrame({"Métier": metiers, "part": [h21.loc[m, "part_sans_gare_pct"] for m in metiers]})
donnees["étiquette"] = donnees["part"].map(lambda v: f"{u.fr(v, 1)} %")
echelle = alt.Scale(domain=metiers, range=[u.METIERS[m]["donnee"] for m in metiers])
base = alt.Chart(donnees).encode(
    y=alt.Y("Métier:N", sort=metiers, title=None, axis=alt.Axis(labelFontSize=16, labelFontWeight="bold",
                                                               labelColor=u.ENCRE, labelPadding=12, ticks=False, domain=False)),
    x=alt.X("part:Q", title=None, scale=alt.Scale(domain=[0, 30]), axis=None))
barres = base.mark_bar(cornerRadiusEnd=6, height=30).encode(color=alt.Color("Métier:N", scale=echelle, legend=None))
valeurs = base.mark_text(align="left", dx=8, fontSize=18, fontWeight="bold", color=u.ENCRE).encode(text="étiquette:N")
graphique = (barres + valeurs).properties(
    height=190, description="Part des emplois hors Paris situés dans une commune sans gare : "
    + ", ".join(f"{m.lower()} {e}" for m, e in zip(metiers, donnees["étiquette"])) + ".").configure_view(strokeWidth=0).configure(background="transparent")

# Titre, graphique et légende dans une même carte blanche (style des conteneurs « carte_ » dans utils)
with st.container(border=True, key="carte_barres"):
    # Icône et titre dans un conteneur à part : Streamlit impose son propre style aux h2, l'écart y serait perdu
    st.markdown(f'<div style="display:flex;align-items:center;gap:12px">{u.badge_mode("train_barre")}'
                f'<h2 class="sous-titre" style="margin:0">Part des emplois hors Paris situés dans une commune sans gare'
                f'</h2></div>', unsafe_allow_html=True)
    st.altair_chart(graphique, theme=None, width="stretch")
    st.markdown('<p style="font-size:14px;color:#5E6475">Emplois situés en Île-de-France hors Paris, quel que soit le '
                'lieu de résidence. Commune avec gare : au moins un arrêt de métro, de train, de RER ou de tramway '
                '(407 communes sur 1 266).</p>', unsafe_allow_html=True)
u.tableau(pd.DataFrame({
    "Métier": metiers,
    "Emplois hors Paris": [u.fr(round(h21.loc[m, "emplois"], -3)) for m in metiers],
    "Dont dans une commune sans gare": [u.fr(round(h21.loc[m, "emplois_sans_gare"], -3)) for m in metiers],
    "Part (%)": [u.fr(h21.loc[m, "part_sans_gare_pct"], 1) for m in metiers]}))

u.encadres(retenir, "On regarde la commune entière : une gare peut se trouver juste à côté, dans la commune voisine.",
           couleur="#B23A86", fond="#F7E8F1")

with st.expander("Pour aller plus loin : où travaillent les actifs de grande couronne, selon leur métier"):
    lieux = ["Même commune", "Paris", "Petite couronne", "Grande couronne (autre commune)", "Hors Île-de-France"]
    vue = dest[dest["couronne"] == "Grande couronne"][["GS"] + lieux].rename(columns={"GS": "Métier"})
    for col in lieux:
        vue[col] = vue[col].map(lambda v: f"{u.fr(v, 1)} %")
    st.dataframe(vue, hide_index=True, width="stretch")
    st.caption("Lecture : 51,2 % des ouvriers qui habitent en grande couronne travaillent dans une autre commune "
               "de grande couronne.")

u.navigation_bas(FICHIER)
u.sources("INSEE, recensement 2023, mobilités professionnelles ; IDFM, offre hebdomadaire 2025 et référentiel des "
          "arrêts.")
