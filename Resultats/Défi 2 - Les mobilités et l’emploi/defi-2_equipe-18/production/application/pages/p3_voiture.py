"""
p3_voiture.py : station 3, « Comment ils vont travailler ».

Message : entre deux communes de banlieue, la voiture passe d'environ un trajet sur deux (lieu de travail avec
gare) à près de trois sur quatre (sans gare), quel que soit le métier. Ce n'est pas le métier qui met en
voiture, c'est l'absence de gare au lieu de travail.

Une seule mesure sur la page : la part de la voiture.
Visuel principal : haltères. Rond creux = avec gare, rond plein = sans gare : la forme distingue les deux,
pas seulement la couleur.
"""

import altair as alt
import pandas as pd
import streamlit as st

import utils as u

FICHIER = "pages/p3_voiture.py"

u.appliquer_style()
u.menu(FICHIER)

v = u.lire("voiture_selon_gare_destination.csv")
trajets_sans_gare = v[(v["commune_de_travail"] == "sans gare") & v["groupe"].isin(["Employés", "Ouvriers"])]["trajets"].sum()
retenir = ("Ce n'est pas le métier qui met en voiture, c'est l'absence de gare au lieu de travail. Les employés et ouvriers "
           "en souffrent plus, parce que leurs emplois sont plus souvent sans gare.")

u.entete(FICHIER, 'Sans gare, <span style="color:#C0401A">tout le monde</span> prend la voiture',
         "Entre deux communes de banlieue, la voiture passe d'environ un trajet sur deux quand le lieu de travail a "
         "une gare à près de trois sur quatre quand il n'en a pas, quel que soit le métier.", retenir,
         u.panneau("Personnes concernées", u.fr(round(trajets_sans_gare, -3)),
                   "employés et ouvriers vont travailler, depuis une autre commune de banlieue, dans une commune sans gare",
                   "#E4572E", "#C0401A", "train_barre"))

# --- Visuel principal : haltères
metiers = ["Cadres", "Employés", "Ouvriers"]
large = v.pivot(index="groupe", columns="commune_de_travail", values="part_voiture_pct").loc[metiers].reset_index()
large.columns = ["Métier", "avec", "sans"]
long = v.rename(columns={"groupe": "Métier", "commune_de_travail": "Lieu de travail", "part_voiture_pct": "part"})
long["Lieu de travail"] = long["Lieu de travail"].map({"avec gare": "a une gare", "sans gare": "n'a pas de gare"})
long["étiquette"] = long["part"].map(lambda x: f"{x:.0f} %")

echelle = alt.Scale(domain=metiers, range=[u.METIERS[m]["donnee"] for m in metiers])
y = alt.Y("Métier:N", sort=metiers, title=None, axis=alt.Axis(labelFontSize=16, labelFontWeight="bold",
                                                              labelColor=u.ENCRE, labelPadding=12, ticks=False, domain=False))
x = alt.X("part:Q", title="Part des trajets faits en voiture (%)", scale=alt.Scale(domain=[0, 100]),
          axis=alt.Axis(values=[0, 25, 50, 75, 100], labelFontSize=14, titleFontSize=14, grid=True,
                        gridColor="#EEF0EC", titleColor=u.GRIS_TEXTE, labelColor=u.GRIS_TEXTE))
trait = alt.Chart(large).mark_rule(strokeWidth=6).encode(
    y=y, x=alt.X("avec:Q", scale=alt.Scale(domain=[0, 100])), x2="sans:Q",
    color=alt.Color("Métier:N", scale=echelle, legend=None))
points = alt.Chart(long).mark_point(size=420, strokeWidth=4, opacity=1).encode(
    y=y, x=x, color=alt.Color("Métier:N", scale=echelle, legend=None),
    fill=alt.condition("datum['Lieu de travail'] == \"n'a pas de gare\"", alt.Color("Métier:N", scale=echelle),
                       alt.value("#FFFFFF")),
    shape=alt.value("circle"),
    tooltip=[alt.Tooltip("Métier:N"), alt.Tooltip("Lieu de travail:N"), alt.Tooltip("étiquette:N", title="En voiture")])
etiquettes = alt.Chart(long).mark_text(dy=-24, fontSize=16, fontWeight="bold", color=u.ENCRE).encode(
    y=y, x="part:Q", text="étiquette:N")
graphique = (trait + points + etiquettes).properties(
    height=260, description="Part des trajets en voiture entre communes de banlieue, avec puis sans gare au lieu "
    "de travail. " + " ".join(f"{r.Métier} : {r.avec:.0f} % et {r.sans:.0f} %." for r in large.itertuples())
).configure_view(strokeWidth=0).configure(background="transparent")

# Titre, légende et graphique dans une même carte blanche (style des conteneurs « carte_ » dans utils)
with st.container(border=True, key="carte_halteres"):
    st.markdown(f'<h2 class="sous-titre">Part des trajets faits en voiture, de banlieue à banlieue, selon le lieu de '
                f'travail</h2><div style="display:flex;flex-wrap:wrap;gap:22px;font-size:15px;font-weight:600">'
                f'<span style="display:inline-flex;align-items:center;gap:8px">{u.badge_mode("train")}'
                f'<span aria-hidden="true" style="width:18px;height:18px;border-radius:50%;border:4px solid #1B1F2A;'
                f'box-sizing:border-box;display:inline-block"></span>Le lieu de travail a une gare</span>'
                f'<span style="display:inline-flex;align-items:center;gap:8px">{u.badge_mode("train_barre")}'
                f'<span aria-hidden="true" style="width:18px;height:18px;border-radius:50%;background:#1B1F2A;'
                f'display:inline-block"></span>Il n\'en a pas</span></div>', unsafe_allow_html=True)
    st.altair_chart(graphique, theme=None, width="stretch")
u.tableau(pd.DataFrame({"Métier": metiers,
                        "Lieu de travail avec gare (%)": [f"{a:.0f}" for a in large["avec"]],
                        "Lieu de travail sans gare (%)": [f"{s:.0f}" for s in large["sans"]]}))

u.encadres(retenir, "La catégorie INSEE « voiture » inclut camions et fourgonnettes (véhicules de travail possibles).")

with st.expander("Pour aller plus loin : la voiture selon la destination (habitants de grande couronne)"):
    m = u.lire("modes_par_destination_grande_couronne.csv")
    m = m[m["GS"].isin(metiers)].pivot(index="destination", columns="GS", values="part_voiture_pct")[metiers]
    st.dataframe(m.map(lambda val: f"{u.fr(val, 1)} %").reset_index().rename(columns={"destination": "Destination"}),
                 hide_index=True, width="stretch")
    st.caption("Vers Paris, employés et cadres prennent aussi peu la voiture (16 %) ; entre banlieues, tous la prennent.")

# Contrôle du résultat principal par le revenu (script 09) : réponse à « et si c'était une question d'argent ? »
with st.expander("Et si c'était simplement une question de revenu ? Le contrôle"):
    r = u.lire("effet_gare_a_revenu_egal.csv")
    st.markdown(f"On a classé les trajets selon le **niveau de vie médian de la commune de résidence**, en quatre parts "
                f"égales. Dans chacune, l'absence de gare au lieu de travail fait monter la voiture de "
                f"**{r['ecart_points'].min():.0f} à {r['ecart_points'].max():.0f} points**. Le résultat ne s'explique donc "
                f"pas par le revenu.")
    st.dataframe(pd.DataFrame({
        "Communes de résidence": ["Les plus modestes", "Plutôt modestes", "Plutôt aisées", "Les plus aisées"],
        "Voiture, lieu de travail avec gare (%)": [u.fr(x, 1) for x in r["voiture_avec_gare_pct"]],
        "Voiture, lieu de travail sans gare (%)": [u.fr(x, 1) for x in r["voiture_sans_gare_pct"]],
        "Écart (points)": [f"+{u.fr(x, 1)}" for x in r["ecart_points"]]}), hide_index=True, width="stretch")
    st.caption("Revenu : INSEE, Filosofi 2023 (niveau de vie médian par commune). Trajets de banlieue à banlieue, "
               "tous métiers. Le revenu est celui de la commune, pas de la personne.")

u.navigation_bas(FICHIER)
u.sources("INSEE, recensement 2023, mobilités professionnelles ; INSEE, Filosofi 2023 ; IDFM, offre hebdomadaire 2025 et "
          "référentiel des arrêts.")
