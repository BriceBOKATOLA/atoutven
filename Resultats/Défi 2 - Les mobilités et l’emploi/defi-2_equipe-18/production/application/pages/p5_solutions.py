"""
p5_solutions.py : station 5, « Les solutions ».

Message : deux cibles pour sortir de la voiture, deux réponses géographiques.
- le vélo pour les trajets courts en voiture entre communes de banlieue (script 06) ;
- navettes et covoiturage vers les emplois des communes sans gare (scripts 07 et 08).

Méthode cartographique : un nombre se montre par une taille (cercles proportionnels).
La carte du potentiel vélo (un pourcentage par commune, donc une couleur) est encore à produire.
"""

import pandas as pd
import streamlit as st

import utils as u

FICHIER = "pages/p5_solutions.py"
NB_COMMUNES = 5   # communes prioritaires listées sous chaque carte

u.appliquer_style()
u.menu(FICHIER)

h16 = u.lire("h16_trajets_courts_voiture.csv").set_index("groupe")
h21 = u.lire("h21_emplois_sans_gare.csv").set_index("groupe")
communes = u.lire("emplois_sans_gare_par_commune.csv").sort_values("emplois_sur_place", ascending=False)

retenir = (f"Les employés sont les plus concernés par le vélo : {h16.loc['Employés', 'part_moins_5km_pct']:.0f} % de "
           f"leurs trajets en voiture font moins de 5 km. Les navettes visent des zones précises : "
           + ", ".join(communes["nom"].head(3)) + ".")
u.entete(FICHIER, 'Deux cibles pour <span style="color:#C0401A">sortir de la voiture</span>',
         "Des trajets courts faisables à vélo, et des zones d'emploi sans gare à relier par navette ou covoiturage.",
         retenir)

gauche, droite = st.columns(2)
with gauche, st.container(border=True, key="carte_velo"):
    st.markdown(f'<div style="display:flex;align-items:center;gap:10px">{u.badge_mode("velo", 40)}'
                f'<h2 class="sous-titre" style="margin:0">Le vélo pour les trajets courts</h2></div>'
                f'<div style="display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;margin-top:12px">'
                f'<span class="chiffre" style="font-size:44px;color:#C0401A">'
                f'{u.fr(round(h16.loc["Ensemble", "dont_moins_5km"], -3))}</span><span>trajets en voiture de moins de '
                f'5 km ({h16.loc["Ensemble", "part_moins_5km_pct"]:.0f} % des trajets de banlieue à banlieue)</span></div>'
                f'<p style="font-size:14px;color:#5E6475">Carte du potentiel vélo par commune : en préparation.</p>',
                unsafe_allow_html=True)
    u.tableau(pd.DataFrame({
        "Métier": ["Cadres", "Employés", "Ouvriers"],
        "Trajets en voiture entre banlieues": [u.fr(round(h16.loc[m, "trajets_voiture"], -3)) for m in ["Cadres", "Employés", "Ouvriers"]],
        "Dont moins de 5 km (%)": [u.fr(h16.loc[m, "part_moins_5km_pct"], 1) for m in ["Cadres", "Employés", "Ouvriers"]]}),
        "Voir le tableau par métier")
with droite, st.container(border=True, key="carte_navette"):
    st.markdown(f'<div style="display:flex;align-items:center;gap:10px">{u.badge_mode("navette", 40)}'
                f'{u.badge_mode("voiture", 40)}<h2 class="sous-titre" style="margin:0">Navettes et covoiturage vers les '
                f'emplois sans gare</h2></div><div style="display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;'
                f'margin-top:12px"><span class="chiffre" style="font-size:44px;color:#C0401A">'
                f'{u.fr(round(h21.loc["Employés et ouvriers", "emplois_sans_gare"], -3))}</span><span>emplois '
                f'd\'employés et d\'ouvriers dans une commune sans gare</span></div>', unsafe_allow_html=True)
    st.image(str(u.DONNEES / "carte_emplois_sans_gare.svg"), width="stretch")
    # Nombre de cercles calculé depuis le tableau (arrondi à une décimale depuis la correction du script 08 : il compte
    # désormais autant de communes que la carte dessine de cercles)
    nb_cercles = int((communes["emplois_sur_place"] >= 500).sum())
    st.markdown(f'<p style="font-size:14px;color:#4E5466">Carte des communes d\'Île-de-France : taille du cercle = nombre '
                f'd\'emplois d\'employés et d\'ouvriers dans les communes sans gare ({nb_cercles} communes en comptent au '
                f'moins 500). Gris moyen : commune avec gare ; gris clair : sans gare.</p>', unsafe_allow_html=True)
    u.tableau(communes.head(NB_COMMUNES).assign(emplois_sur_place=lambda d: d["emplois_sur_place"].map(lambda x: u.fr(round(x, -2))))
              .rename(columns={"nom": "Commune", "emplois_sur_place": "Emplois sur place"})[["Commune", "Emplois sur place"]],
              f"Voir le tableau : les {NB_COMMUNES} communes sans gare qui en comptent le plus")

u.encadres(retenir, "Des potentiels, pas des prévisions. Distances à vol d'oiseau (plus courtes que par la route) ; une "
           "gare peut exister dans la commune voisine.")
u.navigation_bas(FICHIER)
u.sources("INSEE, recensement 2023 ; IDFM, offre hebdomadaire 2025 et référentiel des arrêts ; geo.api.gouv.fr ; seuil "
          "de 5 km des publications INSEE.")
