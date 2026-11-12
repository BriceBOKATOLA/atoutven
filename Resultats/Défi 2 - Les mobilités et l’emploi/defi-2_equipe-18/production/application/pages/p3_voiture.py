"""
p3_voiture.py : station 3, « Comment ils vont travailler ».

Message : entre deux communes de banlieue, la voiture passe d'environ un trajet sur deux (lieu de travail avec
gare) à près de trois sur quatre (sans gare), quel que soit le métier. Ce n'est pas le métier qui met en
voiture, c'est l'absence de gare au lieu de travail.

Une seule mesure sur la page : la part de la voiture.
Visuel principal : barres-pilules (12/11). Barre pleine = sans gare, rond creux = avec gare : la forme distingue les
deux, pas seulement la couleur. Bande grise « Sans gare : 71 à 77 %, quel que soit le métier » sur les trois barres.
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

u.entete(FICHIER, 'Sans gare, <span style="color:#C0401A">près de 3 trajets sur 4</span> se font en voiture',   # espaces insécables : le « 4 » ne passe pas seul à la ligne
         "Entre deux communes de banlieue, la voiture fait environ un trajet sur deux quand le lieu de travail a une "
         "gare ; quand il n'en a pas, elle l'emporte quel que soit le métier, cadres compris.", retenir,
         u.panneau("Personnes concernées", u.fr(round(trajets_sans_gare, -3)),
                   "employés et ouvriers vont travailler, depuis une autre commune de banlieue, dans une commune sans gare",
                   "#E4572E", "#C0401A", "train_barre"))

# --- Visuel principal : barres-pilules (planche « Proposition p3 : barres-pilules », validée par Melvyn le 2026-11-12,
# dans le style du skill infographie-storytelling : formes larges, pastille ronde à la silhouette du métier).
#   - une barre par métier, remplie jusqu'à la part de voiture SANS gare (couleur vive du métier) ; la pastille au bout
#     porte la silhouette du métier ;
#   - un rond pâle posé sur la même piste marque la part AVEC gare, son chiffre au-dessus : l'écart se lit sur une ligne ;
#   - la bande grise verticale de la version précédente est gardée (demande de Melvyn) : elle couvre les 3 pastilles
#     « sans gare », avec la pastille « Sans gare : 71 à 77 %, quel que soit le métier ». Bornes calculées.
# Échelle de 0 à 100 % (honnêteté) ; formes différentes pour « avec » (rond creux) et « sans » (barre pleine) : le sens ne
# repose pas sur la couleur seule.
metiers = ["Cadres", "Employés", "Ouvriers"]
large = v.pivot(index="groupe", columns="commune_de_travail", values="part_voiture_pct").loc[metiers].reset_index()
large.columns = ["Métier", "avec", "sans"]
BAS, HAUT = round(large["sans"].min()), round(large["sans"].max())
PISTE_GRISE = "#E9EBE6"
# Colonnes : métier | piste | valeur, séparées de 16 px. Variables CSS (valeurs de l'ordinateur par défaut), réduites
# sur téléphone dans utils.py (classe jauges-p3). La largeur de la piste sert à placer la bande au bon endroit.
COLONNES = "var(--lib-p3, 150px) 1fr var(--val-p3, 70px)"
# Piste = largeur - colonne métier - écart après le métier - écart avant la valeur (16 px) - colonne valeur.
# Sur téléphone, le métier passe au-dessus de la barre : colonne et écart du métier à 0 (utils.py).
PISTE = "(100% - var(--lib-p3, 150px) - var(--ecart-lib, 16px) - 16px - var(--val-p3, 70px))"


def teinte(hexa: str, force: float) -> str:
    """Mélange une couleur avec le blanc (force 1 = couleur pleine) : contour du rond pâle « avec gare »."""
    r, g, b = (int(hexa[i:i + 2], 16) for i in (1, 3, 5))
    return "#" + "".join(f"{round(255 - (255 - c) * force):02X}" for c in (r, g, b))


def silhouette(metier: str) -> str:
    """Silhouette blanche du métier, reprise du rond de u.libelle_metier (même dessin dans toute l'application)."""
    rond = u.libelle_metier(metier)
    return rond[rond.find("<svg"):rond.find("</svg>") + 6]


def ligne_pilule(metier: str, avec: float, sans: float) -> str:
    """Une ligne : métier, piste grise, barre vive jusqu'à « sans gare » + pastille, rond pâle « avec gare », valeur."""
    c, texte = u.METIERS[metier]["donnee"], u.METIERS[metier]["texte"]
    return (f'<div role="img" aria-label="{metier} : {avec:.0f} % en voiture quand le lieu de travail a une gare, '
            f'{sans:.0f} % quand il n\'en a pas" class="ligne-p3" style="display:grid;grid-template-columns:{COLONNES};gap:16px;'
            f'align-items:center;padding:22px 0 18px;position:relative;z-index:1">{u.libelle_metier(metier)}'
            f'<div aria-hidden="true" style="position:relative;height:30px;border-radius:15px;background:{PISTE_GRISE}">'
            f'<div style="position:absolute;left:0;top:0;bottom:0;width:{sans:.1f}%;border-radius:15px;background:{c}"></div>'
            f'<span style="position:absolute;top:3px;left:calc({avec:.1f}% - 12px);width:24px;height:24px;border-radius:50%;'
            f'background:#FFFFFF;border:4px solid {teinte(c, .45)};box-sizing:border-box"></span>'
            f'<span style="position:absolute;top:-26px;left:calc({avec:.1f}% - 40px);width:80px;text-align:center;font-size:15px;'
            f'font-weight:700;color:#5E6475">{avec:.0f} %</span>'
            f'<span style="position:absolute;top:-5px;left:calc({sans:.1f}% - 20px);width:40px;height:40px;border-radius:50%;'
            f'background:{c};box-shadow:0 0 0 4px #FFFFFF;display:flex;align-items:center;justify-content:center">'
            f'{silhouette(metier)}</span></div>'
            f'<div aria-hidden="true" style="font-family:\'Barlow Semi Condensed\',sans-serif;font-weight:600;font-size:32px;'
            f'color:{texte};text-align:right">{sans:.0f} %</div></div>')


bande_gauche = f"calc(var(--lib-p3, 150px) + var(--ecart-lib, 16px) + {PISTE} * {BAS / 100:.2f} - 24px)"
bande_largeur = f"calc({PISTE} * {(HAUT - BAS) / 100:.2f} + 48px)"
legende = (f'<div style="display:flex;flex-wrap:wrap;gap:22px;font-size:15px;font-weight:700">'
           f'<span style="display:inline-flex;align-items:center;gap:8px">{u.badge_mode("train", 26)}'
           f'<span aria-hidden="true" style="width:18px;height:18px;border-radius:50%;border:4px solid #9BC7DB;'
           f'box-sizing:border-box;display:inline-block"></span>Le lieu de travail a une gare</span>'
           f'<span style="display:inline-flex;align-items:center;gap:8px">{u.badge_mode("train_barre", 26)}'
           f'<span aria-hidden="true" style="width:34px;height:14px;border-radius:7px;background:#3A8FB7;display:inline-block">'
           f'</span>Il n\'en a pas</span></div>')
st.markdown(f'<section class="defile-mobile jauges-p3" style="--largeur-mobile:290px;background:#FFFFFF;border:1px solid #E7EAE4;'
            f'border-radius:16px;padding:22px 28px;display:flex;flex-direction:column;gap:14px">'
            f'<h2 class="sous-titre" style="margin:0">Part des trajets faits en voiture, de banlieue à banlieue, selon le lieu '
            f'de travail</h2>{legende}'
            f'<div class="zone-jauges" style="position:relative;padding-top:52px">'
            f'<div aria-hidden="true" style="position:absolute;top:0;bottom:0;left:{bande_gauche};width:{bande_largeur};'
            f'background:#EEF0EC;border-radius:16px;z-index:0"></div>'
            f'<div class="conteneur-pastille" style="position:absolute;top:10px;left:{bande_gauche};width:{bande_largeur};'
            f'display:flex;justify-content:center;z-index:2"><span class="pastille-bande" style="white-space:nowrap;'
            f'background:#1B1F2A;color:#FFFFFF;border-radius:999px;padding:5px 14px;font-size:15px;font-weight:800">'
            f'Sans gare : {BAS} à {HAUT} %, quel que soit le métier</span></div>'
            + "".join(ligne_pilule(r.Métier, r.avec, r.sans) for r in large.itertuples()) + '</div>'
            f'<div aria-hidden="true" class="ligne-p3 axe-p3" style="display:grid;grid-template-columns:{COLONNES};gap:16px;'
            f'font-size:14px;color:#5E6475">'
            f'<span></span><div style="position:relative;height:22px;border-top:1px solid #DADDD6;padding-top:4px">'
            f'<span style="position:absolute;left:0">0 %</span>'
            f'<span class="axe-milieu" style="position:absolute;left:50%;transform:translateX(-50%)">50 %</span>'
            f'<span style="position:absolute;right:0">100 % en voiture</span></div><span></span></div></section>',
            unsafe_allow_html=True)
u.tableau(pd.DataFrame({"Métier": metiers,
                        "Lieu de travail avec gare (%)": [f"{a:.0f}" for a in large["avec"]],
                        "Lieu de travail sans gare (%)": [f"{s:.0f}" for s in large["sans"]]}))

u.encadres(retenir, "La catégorie INSEE « voiture » inclut camions et fourgonnettes (véhicules de travail possibles).")

with st.expander("Pour aller plus loin : la voiture selon la destination (habitants de grande couronne)"):
    m = u.lire("modes_par_destination_grande_couronne.csv")
    m = m[m["GS"].isin(metiers)].pivot(index="destination", columns="GS", values="part_voiture_pct")[metiers]
    st.dataframe(m.map(lambda val: f"{u.fr(val, 1)} %").reset_index().rename(columns={"destination": "Destination"}),
                 hide_index=True, width="stretch")
    # Paragraphe en gris foncé plutôt que st.caption, dont le gris clair n'a pas assez de contraste sur notre fond
    # (audit axe-core du 12/11) ; #5E6475 est le gris des notes de l'application
    st.markdown('<p style="margin:0;font-size:14px;color:#5E6475">Vers Paris, employés et cadres prennent aussi peu la '
                'voiture (16 %) ; entre banlieues, plus de 7 sur 10 la prennent.</p>', unsafe_allow_html=True)

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
