"""
p4_nuit.py : station 4, « Les trajets de nuit ».

Message : la nuit (minuit-5h), il reste 8 % des passages de la pointe du matin, partout en Île-de-France.
Ce sont surtout les ouvriers qui en ont besoin : ils travaillent deux fois plus souvent la nuit que les cadres.

Une seule mesure dans le visuel principal : les passages prévus par heure (jour de semaine).
Limite affichée : les passages sont prévus, ils ne disent ni qui voyage ni pourquoi.
Données : donnees/offre_par_heure.csv (preparation/preparer_offre_horaire.py, même méthode que le script 05).
"""

import altair as alt
import pandas as pd
import streamlit as st

import utils as u

FICHIER = "pages/p4_nuit.py"
TRANCHES_NUIT = [24, 25, 26, 27, 4]   # minuit-5h (définition INSEE de la nuit), dans le découpage IDFM
TRANCHES_POINTE = [7, 8, 9]           # 7h-10h

# Horaires de travail des salariés, France entière, 2025 : au moins une fois dans les 4 dernières semaines.
# Source : INSEE Références, « Organisation du temps de travail », juillet 2026.
TRAVAIL_NUIT_PCT = {"Ouvriers": 15, "Cadres": 8}
TRAVAIL_DIMANCHE_PCT = {"Employés": 27, "Cadres": 19}

ROSE_NUIT = "#E58BC4"     # nuit sur fond nuit (contraste 6:1)
GRIS_JOUR = "#8E96B3"     # journée, en retrait

u.appliquer_style(nuit=True)
u.menu(FICHIER, nuit=True)

offre = u.lire("offre_par_heure.csv")
nuit = offre[offre["tranche_horaire"].isin(TRANCHES_NUIT)]["passages_semaine"].mean()
pointe = offre[offre["tranche_horaire"].isin(TRANCHES_POINTE)]["passages_semaine"].mean()
rapport = 100 * nuit / pointe
dimanche = 100 * offre["passages_dimanche"].sum() / offre["passages_semaine"].sum()

retenir = (f"Le réseau s'affaiblit la nuit partout, pas seulement là où travaillent les ouvriers. Ce qui change, c'est "
           f"qui en a besoin : les ouvriers, deux fois plus souvent de nuit que les cadres "
           f"({TRAVAIL_NUIT_PCT['Ouvriers']} % contre {TRAVAIL_NUIT_PCT['Cadres']} %).")
# « 13 fois moins » plutôt que « 8 % des passages » : le pourcentage a été mal compris par l'équipe (11/11)
u.entete(FICHIER, f'La nuit, <span style="color:{ROSE_NUIT}">{round(100 / rapport)} fois moins</span> de bus et de trains',
         f"Entre minuit et 5h, il passe {u.fr(rapport, 1)} % des bus et des trains de la pointe du matin. "
         "Il ne reste presque que des bus de nuit.", retenir,
         u.panneau("Travaillent la nuit", f"{TRAVAIL_NUIT_PCT['Ouvriers']} %",
                   f"des ouvriers (cadres : {TRAVAIL_NUIT_PCT['Cadres']} %), au moins une fois par mois", ROSE_NUIT,
                   "#FFFFFF", "lune", nuit=True), nuit=True)

# --- Visuel principal : passages par heure, de 5h à 4h du matin (la nuit regroupée à droite)
offre["ordre"] = (offre["heure"] - 5) % 24
offre["Heure"] = offre["heure"].map(lambda h: f"{h}h")
offre["Moment"] = offre["tranche_horaire"].map(lambda t: "Nuit (minuit-5h)" if t in TRANCHES_NUIT else "Journée")
offre["Passages par heure"] = offre["passages_semaine"].map(lambda v: u.fr(v))
ordre_heures = offre.sort_values("ordre")["Heure"].tolist()

barres = alt.Chart(offre).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
    x=alt.X("Heure:N", sort=ordre_heures, title=None,
            axis=alt.Axis(labelAngle=0, labelFontSize=13, labelColor="#C9CDD8", ticks=False, domainColor="#5A6386",
                          labelExpr="indexof(['5h','8h','11h','14h','17h','20h','23h','2h'], datum.value) >= 0 ? datum.value : ''")),
    y=alt.Y("passages_semaine:Q", title="Passages prévus par heure",
            axis=alt.Axis(labelFontSize=13, titleFontSize=13, labelColor="#C9CDD8", titleColor="#C9CDD8",
                          gridColor="#2E3756", domain=False, ticks=False,
                          # Milliers à la française (« 200 000 ») plutôt que la notation anglaise « 200k »
                          labelExpr="datum.value == 0 ? '0' : format(datum.value / 1000, 'd') + ' 000'")),
    color=alt.Color("Moment:N", scale=alt.Scale(domain=["Journée", "Nuit (minuit-5h)"], range=[GRIS_JOUR, ROSE_NUIT]),
                    legend=alt.Legend(orient="top", title=None, labelColor="#F1F2F6", labelFontSize=14, symbolType="square")),
    tooltip=[alt.Tooltip("Heure:N"), alt.Tooltip("Passages par heure:N"), alt.Tooltip("Moment:N")])
graphique = barres.properties(
    height=280, description=f"Passages prévus par heure, un jour de semaine, sur tout le réseau d'Île-de-France. De 7h à "
                            f"10h, environ {u.fr(round(pointe, -3))} par heure ; de minuit à 5h, environ "
                            f"{u.fr(round(nuit, -3))} par heure, soit {u.fr(rapport, 1)} % de la pointe."
).configure_view(strokeWidth=0).configure(background="transparent")

with st.container(border=True, key="carte_heures"):
    st.markdown(f'<div style="display:flex;align-items:center;gap:12px">{u.badge_mode("navette", nuit=True)}'
                f'<h2 class="sous-titre" style="margin:0">Bus, métros, trains et trams prévus chaque heure, un jour de '
                f'semaine</h2></div><div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:6px;font-size:15px">'
                f'<span style="border:2px solid #C9CDD8;border-radius:999px;padding:3px 12px">Pointe 7h-10h : '
                f'<b>{u.fr(round(pointe, -3))}</b> par heure</span><span style="border:2px solid {ROSE_NUIT};'
                f'border-radius:999px;padding:3px 12px;color:{ROSE_NUIT}">{u.icone("lune", 14, ROSE_NUIT)} Nuit '
                f'minuit-5h : <b>{u.fr(round(nuit, -3))}</b> par heure</span></div>', unsafe_allow_html=True)
    st.altair_chart(graphique, theme=None, width="stretch")
u.tableau(offre.sort_values("ordre")[["Heure", "Moment", "Passages par heure"]])

u.encadres(retenir, "On compte les bus et trains prévus, pas qui les prend ni pourquoi : tous les voyageurs de nuit ne "
           "vont pas travailler. Horaires de travail : chiffres France entière.", couleur=ROSE_NUIT, fond="#2A2140",
           nuit=True)

with st.expander("Pour aller plus loin : le dimanche"):
    st.markdown(f"Le dimanche, il passe **{u.fr(dimanche, 1)} %** des bus et trains d'un jour de semaine. "
                f"{TRAVAIL_DIMANCHE_PCT['Employés']} % des employés travaillent le dimanche au moins une fois par mois, "
                f"contre {TRAVAIL_DIMANCHE_PCT['Cadres']} % des cadres.")
    st.dataframe(pd.DataFrame({"Métier": list(TRAVAIL_NUIT_PCT) + list(TRAVAIL_DIMANCHE_PCT),
                               "Horaire": ["Nuit", "Nuit", "Dimanche", "Dimanche"],
                               "Salariés concernés (%)": list(TRAVAIL_NUIT_PCT.values()) + list(TRAVAIL_DIMANCHE_PCT.values())}),
                 hide_index=True, width="stretch")

u.navigation_bas(FICHIER)
u.sources("IDFM, offre hebdomadaire moyenne hors vacances 2025 (moyenne du mardi au jeudi) ; INSEE, enquête Emploi 2025, "
          "salariés, France entière.")
