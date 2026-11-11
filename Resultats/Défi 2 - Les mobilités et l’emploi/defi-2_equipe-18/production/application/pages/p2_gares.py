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

# Formulations reprises des remarques de l'équipe (11/11). « Presque deux fois » : le rapport réel est calculé
# (23,4 % / 13,0 % = 1,8) ; « 1 sur 4 contre 1 sur 8 » laissait croire à un rapport de 2 exactement.
rapport = h21.loc["Ouvriers", "part_sans_gare_pct"] / h21.loc["Cadres", "part_sans_gare_pct"]
combien = "presque deux fois" if 1.7 <= rapport < 2 else f"{u.fr(rapport, 1)} fois"
# « Sans gare » et non « hors des axes de transport » : on mesure les gares, pas les bus, qui passent presque partout.
# Pas de lien de cause affirmé ici : la voiture est montrée à la station suivante.
retenir = ("Les emplois d'ouvriers sont plus souvent dans des communes sans gare. Pour s'y rendre, de banlieue à "
           "banlieue, la voiture devient souvent la solution (station suivante).")
u.entete(FICHIER, 'Leurs emplois sont <span style="color:#B23A86">loin des gares</span>',
         f"Hors de Paris, les ouvriers travaillent {combien} plus souvent que les cadres dans une commune sans gare "
         f"(ni métro, ni RER, ni train, ni tram).", retenir,
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
    # Chiffre déplacé ici depuis le « À retenir » (une seule idée par encadré) ; calculé, plus écrit à la main
    st.caption(f"Lecture : en grande couronne, {u.fr(gc['Ouvriers'], 1)} % des ouvriers travaillent dans une autre "
               f"commune de grande couronne, contre {u.fr(gc['Cadres'], 1)} % des cadres.")

u.navigation_bas(FICHIER)
u.sources("INSEE, recensement 2023, mobilités professionnelles ; IDFM, offre hebdomadaire 2025 et référentiel des "
          "arrêts.")
