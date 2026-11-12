"""
p5_solutions.py : station 5, « Les solutions ».

Message : chaque territoire a sa solution. Le vélo là où les trajets en voiture sont courts (petite couronne),
des navettes là où les emplois sont loin des gares (grande couronne).

Version validée par Melvyn le 2026-11-11 (canevas « Proposition p5, version 2 »), inspirée de HAP Express :
  - titre avec les deux chiffres clés en pastille, chaque pourcentage dit sur quoi il porte (total écrit dessous) ;
  - chaque solution = une tuile (barre de couleur, pictogramme de mode, chiffre en Poppins, territoire où agir) ;
  - cartes lisibles d'un coup d'œil : 2 couleurs ou 2 tons, repères numérotés 1 à 5 qui renvoient au classement
    affiché à côté (preparation/preparer_cartes_solutions.py), titre-message et phrase « Lecture » ;
  - cartes cadrées par défaut sur la zone qui porte le message, interrupteur pour toute l'Île-de-France, zoom ;
  - recrutements jugés difficiles (script 10, enquête France Travail 2026) : une ligne dans la carte des navettes.
Écart avec la planche, signalé : les deux solutions sont l'une sous l'autre (pas côte à côte), car à 1 100 px de
large, une carte et son classement dans une demi-largeur seraient trop petits pour être lus.
"""

import html

import pandas as pd
import streamlit as st

import utils as u

FICHIER = "pages/p5_solutions.py"
NB_COMMUNES = 5          # communes du classement, numérotées comme les repères de la carte
ORANGE_TEXTE = "#C0401A"  # couleur du bloc vélo (texte, contraste 5,3:1)
ROSE = "#B23A86"          # couleur du bloc navettes (texte, contraste 5,6:1), demandée par Melvyn le 11/11

u.appliquer_style()
u.menu(FICHIER)

h16 = u.lire("h16_trajets_courts_voiture.csv").set_index("groupe")
h21 = u.lire("h21_emplois_sans_gare.csv").set_index("groupe")
territoires = u.lire("territoires.csv").set_index("couronne")          # script 10
compte = u.lire("cartes_solutions_compte.csv").iloc[0]
velo = u.lire("velo_par_commune.csv")                                   # preparer_velo_communes.py
communes = u.lire("emplois_sans_gare_par_commune.csv")
communes = communes[communes["emplois_sur_place"] >= 500].sort_values("emplois_sur_place", ascending=False)
courts, sans_gare = h16.loc["Ensemble"], h21.loc["Employés et ouvriers"]
pc, gc, paris = territoires.loc["Petite couronne"], territoires.loc["Grande couronne"], territoires.loc["Paris"]


def pct(x: float) -> str:
    """Pourcentage arrondi à l'unité, au format français."""
    return f"{u.fr(x)} %"


def pastille(texte: str, couleur: str) -> str:
    """Chiffre clé dans une pastille (HAP Express). Fine (peu de marge, texte gras mais pas extra-gras) : sur un titre
    de deux lignes, une pastille épaisse débordait sur la ligne voisine (remarque de Melvyn, 11/11)."""
    return (f'<span style="background:{couleur};color:#FFFFFF;border-radius:8px;padding:0 7px;font-weight:700;'
            f'white-space:nowrap">{texte}</span>')


retenir = ("Pour le défi : le vélo en petite couronne, où les trajets en voiture sont courts ; des navettes en grande "
           "couronne, où les emplois sont loin des gares et où les employeurs peinent le plus à recruter.")
# Interligne plus grand sur ce titre seulement : les pastilles ont besoin de place entre les deux lignes
u.entete(FICHIER,
         f'<span style="display:block;line-height:1.45">Le vélo pour '
         f'{pastille(pct(courts["part_moins_5km_pct"]), ORANGE_TEXTE)} des trajets en voiture, des navettes '
         f'pour les {pastille(pct(sans_gare["part_sans_gare_pct"]), ROSE)} d\'emplois sans gare</span>',
         # « les 20 % d'emplois sans gare » et non « 20 % des emplois sans gare », qui se lisait comme
         # « 20 % des emplois qui sont sans gare » (relecture du 12/11)
         "Chaque territoire a sa solution : le vélo là où les trajets en voiture sont courts, des navettes là où les "
         "emplois sont loin des gares.", retenir)

# Interrupteur commun aux deux cartes : vue cadrée (par défaut) ou toute l'Île-de-France
entiere = st.toggle("Voir toute l'Île-de-France sur les cartes", key="vue_entiere_solutions")


# Entrée de légende du repère numéroté : sans elle, on ne savait pas ce que désigne le rond noir à chiffre
NUMERO_LEGENDE = ("Rang de la commune dans le classement à droite",
                  f"width:16px;height:16px;border-radius:50%;background:{u.ENCRE};box-shadow:inset 0 0 0 3px {u.ENCRE}")


def classement(lignes: list, maximum: float, unite: str, couleur: str) -> str:
    """Classement numéroté (1 à 5, comme les repères de la carte), barres-pastilles et valeur au bout."""
    return "".join(
        f'<div style="display:grid;grid-template-columns:24px 1fr 70px;gap:10px;align-items:center;font-size:15px">'
        f'<span aria-hidden="true" style="width:24px;height:24px;border-radius:50%;background:{u.ENCRE};color:#FFFFFF;'
        f'font-size:14px;font-weight:800;display:inline-flex;align-items:center;justify-content:center">{k + 1}</span>'
        f'<div><div style="font-weight:600;margin-bottom:4px">{html.escape(nom)}</div><div aria-hidden="true" '
        f'style="height:10px;border-radius:5px;background:#EEF0EC"><div style="height:10px;border-radius:5px;'
        f'background:{couleur};width:{valeur / maximum * 100:.0f}%"></div></div></div>'
        f'<div style="text-align:right;font-weight:700">{valeur_texte}{unite}</div></div>'
        for k, (nom, valeur, valeur_texte) in enumerate(lignes))


def legende(elements: list) -> str:
    """Légende courte : chaque couleur ou forme a son libellé écrit (jamais la couleur seule)."""
    return ('<div style="display:flex;flex-wrap:wrap;gap:6px;font-size:14px;font-weight:600">'
            + "".join(u.pastille_legende(libelle, style) for libelle, style in elements) + '</div>')


def bloc_solution(pictos, couleur_barre, couleur_texte, titre, territoire, chiffre, phrase, contexte, titre_carte,
                  carte, alt, elements_legende, titre_classement, lignes, maximum, unite, lecture) -> str:
    """Une solution : tuile (HAP Express), puis carte zoomable et classement côte à côte, puis la phrase « Lecture »."""
    nom_carte = f"{carte}{'' if entiere else '_cadree'}.svg"
    return (
        f'<div style="position:relative;padding-left:12px">'
        f'<span aria-hidden="true" style="position:absolute;left:-12px;top:4px;bottom:4px;width:5px;'
        f'border-radius:0 3px 3px 0;background:{couleur_barre}"></span>'
        f'<div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">'
        f'{"".join(u.badge_mode(p, 40) for p in pictos)}<h2 class="sous-titre" style="margin:0;font-size:20px">{titre}</h2>'
        f'<span style="margin-left:auto;border-radius:999px;padding:3px 12px;font-size:14px;font-weight:700;'
        f'background:#EEF0EC">{territoire}</span></div>'
        f'<div style="display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin-top:12px">'
        f'<span style="font-family:Poppins,sans-serif;font-weight:800;font-size:40px;line-height:1;color:{couleur_texte}">'
        f'{chiffre}</span><span style="font-size:16px;line-height:1.4">{phrase}</span></div>'
        f'<div style="font-size:14px;color:#4E5466;margin-top:4px">{contexte}</div>'
        f'<div style="font-family:Poppins,sans-serif;font-size:17px;font-weight:800;line-height:1.5;margin:16px 0 10px">'
        f'{titre_carte}</div>'
        f'<div class="pile-mobile" style="display:grid;grid-template-columns:minmax(0,1.4fr) minmax(0,1fr);gap:22px;'
        f'align-items:start">'
        f'<figure style="margin:0;display:flex;flex-direction:column;gap:8px"><div class="cadre-carte">'
        f'<img class="carte-zoomable" src="data:image/svg+xml;base64,{u.svg_base64(nom_carte)}" alt="{html.escape(alt)}" '
        f'style="width:100%;height:auto;display:block"></div>{legende(elements_legende)}</figure>'
        f'<div style="display:flex;flex-direction:column;gap:12px"><div style="font-size:15px;font-weight:700">'
        f'{titre_classement}</div>{classement(lignes, maximum, unite, couleur_barre)}</div></div>'
        f'<p style="margin:12px 0 0;font-size:14px;line-height:1.5;color:#4E5466"><strong style="color:{u.ENCRE}">'
        f'Lecture :</strong> {lecture}</p></div>')


with st.container(border=True, key="carte_velo"):
    st.markdown(bloc_solution(
        ["velo"], "#E4572E", ORANGE_TEXTE, "Le vélo pour les trajets courts", "Petite couronne",
        pct(pc["voiture_moins_5km_pct"]),
        f"des trajets en voiture font moins de 5 km en petite couronne (grande couronne : {pct(gc['voiture_moins_5km_pct'])})",
        f"Toute la banlieue : {pct(courts['part_moins_5km_pct'])} des trajets en voiture d'une commune de banlieue à une "
        f"autre, soit {u.fr(round(courts['dont_moins_5km'], -3))} sur {u.fr(round(courts['trajets_voiture'], -3))}",
        f'{pastille(str(compte["communes_velo_au_moins_un_tiers"]) + " communes", ORANGE_TEXTE)} où au moins 1 trajet en '
        f'voiture sur 3 fait moins de 5 km',
        "carte_velo_lisible",
        f"Carte des communes d'Île-de-France : {compte['communes_velo_au_moins_un_tiers']} communes où au moins 1 trajet "
        "en voiture sur 3 fait moins de 5 km, en anneau autour de Paris ; part des trajets en voiture de moins de 5 km "
        "par commune de résidence",
        [("Au moins 1 trajet sur 3", u.echantillon("#E4572E")), ("Moins de 1 sur 3", u.echantillon("#D9DCD5")),
         ("Paris ou effectif faible", u.echantillon("#EEF0EC", "#C9CDD3")), NUMERO_LEGENDE],
        "Les 5 communes où cette part est la plus forte",
        [(r.nom, r.part_moins_5km_pct, u.fr(r.part_moins_5km_pct)) for r in velo.head(NB_COMMUNES).itertuples()],
        60, " %",
        "les communes en orange forment un anneau autour de Paris : c'est là que le vélo peut remplacer le plus de "
        "trajets en voiture. Chaque numéro est le rang de la commune dans le classement à droite."), unsafe_allow_html=True)
    u.tableau(velo.head(20).assign(part=lambda d: d["part_moins_5km_pct"].map(lambda x: f"{u.fr(x)} %"))
              .rename(columns={"nom": "Commune", "part": "Trajets en voiture de moins de 5 km"})
              [["Commune", "Trajets en voiture de moins de 5 km"]],
              "Voir le tableau : les 20 communes où cette part est la plus forte")

with st.container(border=True, key="carte_navette"):
    st.markdown(bloc_solution(
        ["navette", "voiture"], ROSE, ROSE, "Des navettes vers les emplois sans gare", "Grande couronne",
        pct(gc["emplois_eo_sans_gare_pct"]),
        f"des postes d'employés et d'ouvriers sont sans gare en grande couronne (petite couronne : "
        f"{pct(pc['emplois_eo_sans_gare_pct'])})",
        f"Hors de Paris : {pct(sans_gare['part_sans_gare_pct'])}, soit {u.fr(round(sans_gare['emplois_sans_gare'], -3))} "
        f"emplois sur {u.fr(round(sans_gare['emplois'], -3))}. Les employeurs de grande couronne jugent "
        f"{pct(gc['part_A_pct'])} de leurs projets de recrutement difficiles (Paris : {pct(paris['part_A_pct'])}).",
        f'{pastille(str(compte["communes_sans_gare_500_emplois"]) + " communes", ROSE)} sans gare comptent au moins 500 '
        f'postes d\'employés et d\'ouvriers',
        "carte_navettes_lisible",
        f"Carte des communes d'Île-de-France : {compte['communes_sans_gare_500_emplois']} communes sans gare comptent au "
        f"moins 500 postes d'employés et d'ouvriers ; les plus grandes, en grande couronne près de la petite couronne, sont "
        + ", ".join(communes["nom"].head(4)) + " et " + communes["nom"].iloc[4],
        [("Les 5 communes qui en comptent le plus, numérotées comme le classement", "width:14px;height:14px;border-radius:50%;background:#1B1F2A"),
         ("Autres (taille = nombre d'emplois)", "width:14px;height:14px;border-radius:50%;background:#D9A6C7")],
        "Les 5 communes sans gare qui comptent le plus d'emplois",
        [(r.nom, r.emplois_sur_place, u.fr(round(r.emplois_sur_place, -2))) for r in communes.head(NB_COMMUNES).itertuples()],
        communes["emplois_sur_place"].max() * 1.1, "",
        "plus le cercle est grand, plus la commune compte d'emplois sans gare. Les communes qui en comptent le plus sont en "
        "grande couronne, près de la petite couronne : ce seraient les premiers arrêts d'une navette. Chaque numéro est le rang de la commune dans le classement à droite."),
        unsafe_allow_html=True)
    u.tableau(communes.head(20).assign(emplois=lambda d: d["emplois_sur_place"].map(lambda x: u.fr(round(x, -2))))
              .rename(columns={"nom": "Commune", "emplois": "Postes d'employés et d'ouvriers"})
              [["Commune", "Postes d'employés et d'ouvriers"]],
              "Voir le tableau : les 20 communes sans gare qui en comptent le plus")

u.encadres(retenir, "Des potentiels, pas des prévisions. Distances à vol d'oiseau ; une gare peut exister dans la commune "
           "voisine. Recrutements difficiles : ce que disent les employeurs (France Travail, 2026), sans que la cause "
           "soit connue.")
u.navigation_bas(FICHIER)
u.sources("INSEE, recensement 2023 ; IDFM, offre hebdomadaire 2025 et référentiel des arrêts ; France Travail, enquête "
          "Besoins en main-d'œuvre 2026 ; geo.api.gouv.fr ; seuil de 5 km de l'Insee Première n° 1835 (2021).")
