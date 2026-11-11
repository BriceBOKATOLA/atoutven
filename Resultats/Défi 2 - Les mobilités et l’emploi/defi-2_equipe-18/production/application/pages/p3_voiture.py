"""
p3_voiture.py : station 3, « Comment ils vont travailler ».

Message : entre deux communes de banlieue, la voiture passe d'environ un trajet sur deux (lieu de travail avec
gare) à près de trois sur quatre (sans gare), quel que soit le métier. Ce n'est pas le métier qui met en
voiture, c'est l'absence de gare au lieu de travail.

Une seule mesure sur la page : la part de la voiture.
Visuel principal : haltères. Rond creux = avec gare, rond plein = sans gare : la forme distingue les deux,
pas seulement la couleur.
"""

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

# --- Visuel principal : jauges de la proposition validée le 2026-11-11 (canevas « Proposition p3 : jauges »,
# inspirée de HAP Express : on met en avant l'information clé). Par rapport aux haltères de la maquette :
#   - barres épaisses et arrondies (14 px) au lieu d'un trait fin : l'écart entre les deux situations se voit ;
#   - le chiffre « sans gare » en gros, dans la couleur du métier ; le chiffre « avec gare » plus discret ;
#   - une bande grise verticale couvre les 3 ronds pleins, avec la pastille « Sans gare : 71 à 77 %, quel que soit le
#     métier » : c'est le message du titre, qu'on lit sans comparer les chiffres un à un. Bornes calculées.
# Rond creux = lieu de travail avec gare, rond plein = sans gare : la forme distingue les deux, pas seulement la couleur.
metiers = ["Cadres", "Employés", "Ouvriers"]
large = v.pivot(index="groupe", columns="commune_de_travail", values="part_voiture_pct").loc[metiers].reset_index()
large.columns = ["Métier", "avec", "sans"]
BAS, HAUT = round(large["sans"].min()), round(large["sans"].max())
LIBELLE_PX, MARGE_DROITE_PX = 184, 24   # colonne du métier (170 px + 14 d'écart) ; place pour « 100 % en voiture »
PISTE = f"(100% - {LIBELLE_PX + MARGE_DROITE_PX}px)"   # largeur de la piste, pour placer la bande au bon endroit


def ligne_jauge(metier: str, avec: float, sans: float) -> str:
    """Une ligne : métier, piste grise, segment pâle entre les deux valeurs, rond creux (avec gare), rond plein (sans)."""
    c, texte = u.METIERS[metier]["donnee"], u.METIERS[metier]["texte"]
    return (f'<div role="img" aria-label="{metier} : {avec:.0f} % en voiture quand le lieu de travail a une gare, '
            f'{sans:.0f} % quand il n\'en a pas" style="display:grid;grid-template-columns:170px 1fr {MARGE_DROITE_PX}px;'
            f'align-items:center;height:78px;position:relative">{u.libelle_metier(metier)}'
            f'<div aria-hidden="true" style="position:relative;height:78px;margin-left:14px">'
            f'<div style="position:absolute;left:0;right:0;top:44px;height:14px;border-radius:7px;background:#EEF0EC"></div>'
            f'<div style="position:absolute;top:44px;height:14px;border-radius:7px;background:{c};opacity:.35;'
            f'left:{avec:.1f}%;width:{sans - avec:.1f}%"></div>'
            f'<div style="position:absolute;top:10px;left:calc({avec:.1f}% - 40px);width:80px;text-align:center;'
            f'font-size:16px;font-weight:600;color:#5E6475">{avec:.0f} %</div>'
            f'<div style="position:absolute;top:2px;left:calc({sans:.1f}% - 40px);width:80px;text-align:center;'
            f'font-family:\'Barlow Semi Condensed\',sans-serif;font-weight:600;font-size:28px;line-height:1.1;color:{texte}">'
            f'{sans:.0f} %</div>'
            f'<span style="position:absolute;top:37px;left:calc({avec:.1f}% - 14px);width:28px;height:28px;border-radius:50%;'
            f'background:#FFFFFF;border:4px solid {c};box-sizing:border-box"></span>'
            f'<span style="position:absolute;top:35px;left:calc({sans:.1f}% - 16px);width:32px;height:32px;border-radius:50%;'
            f'background:{c};box-shadow:0 0 0 3px #FFFFFF"></span></div><span></span></div>')


bande_gauche = f"calc({LIBELLE_PX}px + {PISTE} * {BAS / 100:.2f} - 18px)"
bande_largeur = f"calc({PISTE} * {(HAUT - BAS) / 100:.2f} + 36px)"
st.markdown(f'<section style="background:#FFFFFF;border:1px solid #E7EAE4;border-radius:16px;padding:22px 28px;'
            f'display:flex;flex-direction:column;gap:10px"><h2 class="sous-titre" style="margin:0">Part des trajets faits '
            f'en voiture, de banlieue à banlieue, selon le lieu de travail</h2>'
            f'<div style="display:flex;flex-wrap:wrap;gap:22px;font-size:15px;font-weight:600">'
            f'<span style="display:inline-flex;align-items:center;gap:8px">{u.badge_mode("train")}'
            f'<span aria-hidden="true" style="width:18px;height:18px;border-radius:50%;border:3px solid #1B1F2A;'
            f'box-sizing:border-box;display:inline-block"></span>Le lieu de travail a une gare</span>'
            f'<span style="display:inline-flex;align-items:center;gap:8px">{u.badge_mode("train_barre")}'
            f'<span aria-hidden="true" style="width:20px;height:20px;border-radius:50%;background:#1B1F2A;'
            f'display:inline-block"></span>Il n\'en a pas</span></div>'
            f'<div style="position:relative;padding-top:44px">'
            f'<div aria-hidden="true" style="position:absolute;top:0;bottom:26px;left:{bande_gauche};width:{bande_largeur};'
            f'background:#EEF0EC;border-radius:14px"></div>'
            f'<div style="position:absolute;top:8px;left:{bande_gauche};width:{bande_largeur};display:flex;'
            f'justify-content:center"><span style="white-space:nowrap;background:#1B1F2A;color:#FFFFFF;border-radius:999px;'
            f'padding:4px 14px;font-size:14px;font-weight:700">Sans gare : {BAS} à {HAUT} %, quel que soit le métier</span></div>'
            f'<div style="position:relative">' + "".join(ligne_jauge(r.Métier, r.avec, r.sans) for r in large.itertuples())
            + f'</div><div aria-hidden="true" style="display:grid;grid-template-columns:170px 1fr {MARGE_DROITE_PX}px;'
              f'font-size:14px;color:#5E6475;padding-top:6px"><span></span><div style="position:relative;height:22px;'
              f'margin-left:14px;border-top:1px solid #DADDD6"><span style="position:absolute;left:0;top:4px">0 %</span>'
              f'<span style="position:absolute;left:50%;top:4px;transform:translateX(-50%)">50 %</span>'
              f'<span style="position:absolute;right:-24px;top:4px">100 % en voiture</span></div><span></span></div>'
              f'</div></section>', unsafe_allow_html=True)
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
