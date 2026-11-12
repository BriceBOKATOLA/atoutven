"""
conclusion.py : terminus du récit.

Message : ce n'est pas le métier, c'est le lieu de travail qui décide. Le réseau mène à Paris, pas aux emplois de
banlieue.

Version validée par Melvyn le 2026-11-12 (canevas « Proposition conclusion : schéma compact et chiffré ») : la
conclusion CONCLUT au lieu de résumer les pages (l'ancien plan de ligne répétait tous leurs chiffres, « trop de
saturation »). Elle contient :
  - un schéma en aiguillage : les trois métiers arrivent au même aiguillage, le lieu de travail ; les chiffres sont sur
    les branches (avec gare / sans gare, tous métiers confondus) et la nuance du script 12 (une gare ne suffit pas) ;
  - « Ce que ça change pour IDFM » : 3 actions courtes, chacune avec une perspective « Et ensuite » ;
  - deux boutons (ma commune, retour à l'accueil) et la méthode en une ligne.
"""

import streamlit as st

import utils as u

FICHIER = "pages/conclusion.py"
ORANGE, BLEU_TC, GRIS = "#C0401A", "#1F6A8C", "#5E6475"

u.appliquer_style()
u.menu(FICHIER)

# --- Chiffres, tous calculés à partir des fichiers (aucun tapé à la main)
# Part de la voiture de banlieue à banlieue, tous métiers confondus (synthèse de la page 3, pondérée par les trajets)
v = u.lire("voiture_selon_gare_destination.csv")
part = {cas: (d["trajets"] * d["part_voiture_pct"]).sum() / d["trajets"].sum() for cas, d in v.groupby("commune_de_travail")}
# Constat exploratoire du script 12 : communes avec gare où au moins 2 actifs sur 3 viennent encore en voiture
g = u.lire("gare_ne_suffit_pas.csv")
gare = g[(g["groupe"] == "Ensemble") & (g["seuil_voiture_pct"] == 66.7)].iloc[0]


def en_mots(pct: float) -> str:
    """Part exprimée en fraction parlante, choisie d'après la valeur calculée (tolérance de 2 points)."""
    for fraction, mots in ((0.5, "1 trajet sur 2"), (0.75, "près de 3 trajets sur 4"), (2 / 3, "2 trajets sur 3")):
        if abs(pct / 100 - fraction) <= 0.02:
            return mots
    return f"{u.fr(pct)} %"


AVEC, SANS = en_mots(part["avec gare"]), en_mots(part["sans gare"])

u.entete(FICHIER, f'Ce n\'est pas le métier, c\'est le <span style="background:{ORANGE};color:#FFFFFF;border-radius:10px;'
                  f'padding:0 10px">lieu de travail</span> qui décide',
         "Le réseau mène à Paris, pas aux emplois de banlieue.")


# --- Schéma en aiguillage (SVG 800 x 252, mêmes silhouettes et couleurs que le reste de l'application)
def texte(x, y, contenu, taille=14, poids=700, couleur=u.ENCRE, ancre="start"):
    """Texte du schéma (14 px minimum, règle du projet)."""
    return (f'<text x="{x}" y="{y}" font-family="Plus Jakarta Sans, sans-serif" font-size="{taille}" font-weight="{poids}" '
            f'fill="{couleur}" text-anchor="{ancre}">{contenu}</text>')


def rond_icone(x, y, r, fond, nom_icone):
    """Pastille ronde avec une icône de l'application (u.ICONES, dessinée en 24 x 24), trait blanc."""
    t = r * 1.1
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fond}" stroke="#FFFFFF" stroke-width="4"/>'
            f'<g transform="translate({x - t / 2},{y - t / 2}) scale({t / 24})" fill="none" stroke="#FFFFFF" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round">{u.ICONES[nom_icone]}</g>')


def pastille_metier(metier, x, y, r):
    """Rond de la couleur du métier + silhouette blanche (même dessin que u.libelle_metier)."""
    rond = u.libelle_metier(metier)
    interieur = rond[rond.find(">", rond.find("<svg")) + 1:rond.find("</svg>")]
    t = r * 1.3
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{u.METIERS[metier]["donnee"]}" stroke="#FFFFFF" stroke-width="4"/>'
            f'<g transform="translate({x - t / 2},{y - t / 2}) scale({t / 24})">{interieur}</g>')


ys = {"Cadres": 40, "Employés": 92, "Ouvriers": 144}
dessin = ""
for m, y in ys.items():   # les voies des trois métiers se rejoignent avant l'aiguillage
    dessin += f'<path d="M95,{y} C150,{y} 160,92 200,92" fill="none" stroke="{u.METIERS[m]["donnee"]}" stroke-width="6" stroke-linecap="round"/>'
dessin += (f'<path d="M318,92 C350,92 360,40 400,40 L410,40" fill="none" stroke="{BLEU_TC}" stroke-width="6" stroke-linecap="round"/>'
           f'<path d="M318,92 C350,92 360,144 400,144 L410,144" fill="none" stroke="{ORANGE}" stroke-width="8" stroke-linecap="round"/>')
for m, y in ys.items():   # nom à gauche de la pastille : la voie ne le traverse pas
    dessin += pastille_metier(m, 95, y, 17) + texte(70, y + 5, m, 14, 800, u.METIERS[m]["texte"], "end")
dessin += (f'<rect x="200" y="70" width="118" height="44" rx="22" fill="{u.ENCRE}"/>'
           + texte(259, 89, "Lieu de", 14, 800, "#FFFFFF", "middle") + texte(259, 106, "travail", 14, 800, "#FFFFFF", "middle")
           # Branche « avec gare » : part de la voiture + nuance du script 12
           + rond_icone(430, 40, 20, BLEU_TC, "train")
           + f'<text x="460" y="36" font-family="Plus Jakarta Sans, sans-serif" font-size="15" fill="{u.ENCRE}">'
             f'<tspan font-weight="800" fill="{BLEU_TC}">Avec gare :</tspan> <tspan font-weight="800">{AVEC}</tspan> en voiture</text>'
           + f'<text x="460" y="57" font-family="Plus Jakarta Sans, sans-serif" font-size="14" fill="{GRIS}">mais dans '
             f'<tspan font-weight="800" fill="{u.ENCRE}">{int(gare.communes_au_dessus)} des {int(gare.communes_avec_gare)}</tspan> '
             f'communes avec gare,</text>'
           + f'<text x="460" y="75" font-family="Plus Jakarta Sans, sans-serif" font-size="14" fill="{GRIS}">'
             f'<tspan font-weight="800" fill="{u.ENCRE}">2 sur 3</tspan> ou plus viennent encore en voiture</text>'
           # Branche « sans gare » : part de la voiture + solutions reliées par une fourche en pointillé
           + rond_icone(430, 144, 20, ORANGE, "voiture")
           + f'<text x="460" y="140" font-family="Plus Jakarta Sans, sans-serif" font-size="15" fill="{u.ENCRE}">'
             f'<tspan font-weight="800" fill="{ORANGE}">Sans gare :</tspan> <tspan font-weight="800">{SANS}</tspan> en voiture</text>'
           + texte(460, 161, "quel que soit le métier", 14, 400, GRIS)
           + f'<path d="M430,166 L430,232 M430,196 L458,196 M430,232 L458,232" fill="none" stroke="{ORANGE}" stroke-width="2.5" '
             f'stroke-dasharray="4 4"/>'
           + rond_icone(474, 196, 14, u.ENCRE, "velo") + texte(496, 201, "vélo si c'est court", 14, 700)
           + rond_icone(474, 232, 14, u.ENCRE, "navette") + texte(496, 237, "navette sinon", 14, 700))
description_schema = (f"Schéma : cadres, employés et ouvriers arrivent au même aiguillage, le lieu de travail. Avec gare : "
                      f"{AVEC} en voiture, mais dans {int(gare.communes_au_dessus)} des {int(gare.communes_avec_gare)} communes "
                      f"avec gare, 2 sur 3 ou plus viennent encore en voiture. Sans gare : {SANS} en voiture, quel que soit le "
                      f"métier ; vélo si le trajet est court, navette sinon.")
# defile-mobile : sur téléphone, le schéma garde 800 px (textes à 14 px) et défile de côté dans son cadre
st.markdown(f'<div class="carte defile-mobile" style="--largeur-mobile:800px;padding:18px 0 10px">'
            f'<svg viewBox="0 0 800 252" role="img" aria-label="{description_schema}" style="width:100%;height:auto;display:block">'
            f'{dessin}</svg></div>', unsafe_allow_html=True)

# --- Ce que ça change pour IDFM : 3 actions courtes, chacune avec sa perspective « Et ensuite » (sans chiffre :
# les chiffres sont sur les pages 4 et 5 et sur le schéma)
ACTIONS = [  # (icône, couleur de la page d'origine, action, et ensuite)
    ("velo", "#E4572E", "Le vélo, en petite couronne", "mesurer les trajets réels à vélo, pas à vol d'oiseau"),
    ("navette", "#B23A86", "Des navettes vers les emplois sans gare", "les tester avec les employeurs qui peinent à recruter"),
    ("lune", "#CF5CA6", "Penser aux horaires de nuit", "mesurer les temps de trajet en bus de nuit"),
]
actions = "".join(
    f'<div class="piste" style="display:flex;gap:16px;align-items:center;padding:12px 0;border-top:1px solid #E1E4DE">'
    f'<span aria-hidden="true" style="flex-shrink:0;width:42px;height:42px;border-radius:50%;background:{c};display:flex;'
    f'align-items:center;justify-content:center">{u.icone(ic, 20, "#FFFFFF")}</span><div><div style="font-size:17px;'
    f'font-weight:800">{action}</div><div style="font-size:15px;color:#4E5466;margin-top:2px"><b style="color:{ORANGE}">'
    f'Et ensuite :</b> {ensuite}</div></div></div>' for ic, c, action, ensuite in ACTIONS)
bouton = 'display:inline-flex;align-items:center;gap:8px;padding:12px 22px;border-radius:999px;font-size:16px;font-weight:800;text-decoration:none'
st.markdown(f'<section aria-labelledby="titre-changements" style="margin-top:8px">'
            f'<h2 id="titre-changements" style="margin:0 0 2px;font-size:20px;font-weight:800">Ce que ça change pour '
            f'Île-de-France Mobilités</h2>{actions}</section>'
            # Liens relatifs (comme le menu) : ils fonctionnent dans le cadre de Streamlit Cloud
            f'<div style="margin-top:22px;display:flex;gap:12px;flex-wrap:wrap">'
            f'<a href="p6_commune" target="_self" style="{bouton};background:{u.ENCRE};color:#FFFFFF">Et votre commune ? →</a>'
            f'<a href="./" target="_self" style="{bouton};border:2px solid {u.ENCRE};color:{u.ENCRE}">Revenir à l\'accueil ↺</a></div>'
            f'<p style="margin:22px 0 0;font-size:14px;color:{GRIS}"><b style="color:#4E5466">15 hypothèses</b> testées, dont '
            f'<b style="color:#4E5466">5 réfutées</b>, critères écrits avant d\'ouvrir les données · '
            # Nouvel onglet : GitHub refuse de s'afficher dans le cadre de Streamlit Cloud (annoncé : RGAA, critère 13.2)
            f'<a style="color:#4E5466" href="https://github.com/Melvy-hub/hackaviz_2026-equipe-18" target="_blank" '
            f'rel="noopener noreferrer">code et données sur GitHub (nouvel onglet)</a></p>', unsafe_allow_html=True)

# Pas de navigation_bas : les deux boutons ci-dessus la remplacent (« ← Chercher ma commune » aurait fait doublon)
u.sources("INSEE (recensement 2023, enquête Emploi 2025) ; Île-de-France Mobilités (offre 2025, référentiel des arrêts) ; "
          "France Travail (Besoins en main-d'œuvre 2026) ; geo.api.gouv.fr. Constat « une gare ne suffit pas » : "
          "src/12_gare_ne_suffit_pas.py (exploratoire ; seuil « 2 sur 3 » choisi par l'équipe, au moins 200 trajets par commune).")
