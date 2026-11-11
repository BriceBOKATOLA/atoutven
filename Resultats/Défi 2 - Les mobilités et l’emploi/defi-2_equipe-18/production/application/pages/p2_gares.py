"""
p2_gares.py : station 2, « Loin des gares ».

Message : hors de Paris, 1 emploi d'ouvrier sur 4 se trouve dans une commune sans gare (ni métro, ni RER,
ni train, ni tram), contre 1 emploi de cadre sur 8.

Visuel principal : barres horizontales, une par métier (couleur fixe par métier, valeur écrite au bout).
Données : script 07 (résultats copiés dans donnees/).
"""

import html

import pandas as pd
import streamlit as st

import utils as u

FICHIER = "pages/p2_gares.py"

u.appliquer_style()
u.menu(FICHIER)

h21 = u.lire("h21_emplois_sans_gare.csv").set_index("groupe")
sans_gare_sur_place = h21.loc["Employés et ouvriers", "emplois_sans_gare"]

# Formulations reprises des recommandations de Pierre THAI (captures annotées des maquettes, 11/11). « Presque deux fois » : le rapport réel est calculé
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

# --- Visuel principal : barres dessinées comme la maquette validée (maquettes_validees/Ou.dc.html) : rond du métier
# avec sa silhouette, barre sur fond gris clair (échelle de 0 à 30 %), valeur en gros chiffres. Valeurs calculées (script 07).
metiers = ["Cadres", "Employés", "Ouvriers"]


def ligne_barre(metier: str) -> str:
    """Une ligne du graphique : métier, barre, valeur ; décrite en mots pour les lecteurs d'écran."""
    v = h21.loc[metier, "part_sans_gare_pct"]
    return (f'<div role="img" aria-label="{metier} : {u.fr(v, 1)} % des emplois hors Paris dans une commune sans gare" '
            f'style="display:grid;grid-template-columns:170px 1fr 80px;gap:14px;align-items:center">'
            f'{u.libelle_metier(metier)}<div aria-hidden="true" style="height:22px;background:#EEF0EC;border-radius:11px;'
            f'overflow:hidden"><div style="height:22px;border-radius:11px;background:{u.METIERS[metier]["donnee"]};'
            f'width:{v / 30 * 100:.1f}%"></div></div><div style="text-align:right;font-family:\'Barlow Semi Condensed\','
            f'sans-serif;font-weight:600;font-size:28px">{u.fr(v, 1)} %</div></div>')


st.markdown(f'<section style="background:#FFFFFF;border:1px solid #E7EAE4;border-radius:16px;padding:22px 28px;'
            f'display:flex;flex-direction:column;gap:16px"><div style="display:flex;align-items:center;gap:10px">'
            f'{u.badge_mode("train_barre")}<h2 class="sous-titre" style="margin:0">Part des emplois hors Paris situés '
            f'dans une commune sans gare</h2></div>' + "".join(ligne_barre(m) for m in metiers)
            + '<p style="margin:0;font-size:14px;line-height:1.5;color:#5E6475">Emplois situés en Île-de-France hors '
              'Paris, quel que soit le lieu de résidence. Commune avec gare : au moins un arrêt de métro, de train, de RER '
              'ou de tramway (407 communes sur 1 266).</p></section>', unsafe_allow_html=True)
u.tableau(pd.DataFrame({
    "Métier": metiers,
    "Emplois hors Paris": [u.fr(round(h21.loc[m, "emplois"], -3)) for m in metiers],
    "Dont dans une commune sans gare": [u.fr(round(h21.loc[m, "emplois_sans_gare"], -3)) for m in metiers],
    "Part (%)": [u.fr(h21.loc[m, "part_sans_gare_pct"], 1) for m in metiers]}))

u.encadres(retenir, "On regarde la commune entière : une gare peut se trouver juste à côté, dans la commune voisine.",
           couleur="#B23A86", fond="#F7E8F1")

# --- Graphique de flux « de banlieue à banlieue », validé le 2026-11-11 (canevas « Proposition p2 : un seul graphique
# de flux ») à la place de la carte en 5 nuances et des tableaux 8 x 8, jugés trop techniques. Trois domiciles (une
# maison par catégorie) vers trois lieux de travail ; épaisseur d'une branche = part de la catégorie (chaque maison =
# 100 %), donc les catégories se comparent même si leurs effectifs diffèrent. Cadres et ouvriers en couleur (les deux
# catégories que le message compare), employés en gris pâle, dessinés en dessous. Données :
# preparation/preparer_destinations_categories.py.
DESTINATIONS = ["Leur département", "Autre département", "Paris"]
FLUX_EP = 0.55               # épaisseur (unités SVG) pour 1 % : même échelle pour toutes les branches
FLUX_XD, FLUX_XT = 150, 760  # domiciles à gauche, lieux de travail à droite
FLUX_Y = [100, 250, 400]     # hauteur des domiciles et des lieux de travail
FLUX_ECART_BANDES, FLUX_ECART_ETIQUETTES = 6, 24
FLUX_STYLE = {"Cadres": ("#3A8FB7", "#1F6A8C"), "Employés": ("#C9CDD3", "#5E6475"), "Ouvriers": ("#B23A86", "#B23A86")}


def maison(x: float, y: float, fond: str) -> str:
    """Pictogramme du domicile : rond de la couleur de la catégorie, maison blanche."""
    return (f'<circle cx="{x}" cy="{y}" r="17" fill="{fond}" stroke="#1B1F2A" stroke-width="3"/>'
            f'<path d="M{x - 7},{y + 1} L{x},{y - 6} L{x + 7},{y + 1} M{x - 5},{y} L{x - 5},{y + 7} L{x + 5},{y + 7} '
            f'L{x + 5},{y}" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linejoin="round"/>')


def graphique_flux(dest_cat) -> str:
    """Graphique de flux en SVG : branches courbes empilées sur chaque lieu de travail, étiquettes espacées."""
    branches, dessus, etiquettes = "", "", ""
    for t, yt in enumerate(FLUX_Y):
        total = sum(dest_cat.loc[(c, DESTINATIONS[t])] * FLUX_EP for c in FLUX_STYLE) + 2 * FLUX_ECART_BANDES
        haut, y_etiquettes = yt - total / 2, []
        for k, (cat, (couleur, texte)) in enumerate(FLUX_STYLE.items()):
            part = dest_cat.loc[(cat, DESTINATIONS[t])]
            e = part * FLUX_EP
            y_arrivee = haut + e / 2
            haut += e + FLUX_ECART_BANDES
            trait = (f'<path d="M{FLUX_XD},{FLUX_Y[k]} C{FLUX_XD + 260},{FLUX_Y[k]} {FLUX_XT - 260},{y_arrivee:.1f} '
                     f'{FLUX_XT},{y_arrivee:.1f}" fill="none" stroke="{couleur}" stroke-width="{e:.1f}" '
                     f'opacity="{1 if cat == "Employés" else 0.9}"/>')
            # Employés dessinés en premier : les branches comparées (cadres, ouvriers) restent au premier plan
            if cat == "Employés":
                branches += trait
            else:
                dessus += trait
            # Étiquette au niveau de sa branche, poussée vers le bas si elle touche la précédente
            y_label = y_arrivee if not y_etiquettes else max(y_arrivee, y_etiquettes[-1] + FLUX_ECART_ETIQUETTES)
            y_etiquettes.append(y_label)
            etiquettes += (f'<text x="{FLUX_XT + 26}" y="{y_label + 7:.1f}" font-family="Barlow Semi Condensed, sans-serif" '
                           f'font-size="21" font-weight="600" fill="{texte}">{u.fr(part, 1)} %</text>')
        etiquettes += (f'<rect x="{FLUX_XT - 6}" y="{yt - total / 2 - 4:.1f}" width="12" height="{total + 8:.1f}" rx="6" '
                       f'fill="#FFFFFF" stroke="#1B1F2A" stroke-width="2.5"/><text x="{FLUX_XT + 90}" y="{yt + 7}" '
                       f'font-family="Plus Jakarta Sans, sans-serif" font-size="20" font-weight="700" fill="#1B1F2A">'
                       f'{DESTINATIONS[t]}</text>')
    domiciles = "".join(
        maison(FLUX_XD, y, couleur) + f'<text x="{FLUX_XD - 28}" y="{y + 7}" text-anchor="end" font-family="Poppins, '
        f'sans-serif" font-size="20" font-weight="800" fill="{texte}">{cat}</text>'
        for (cat, (couleur, texte)), y in zip(FLUX_STYLE.items(), FLUX_Y))
    description = " ; ".join(
        f"{cat} : " + ", ".join(f"{u.fr(dest_cat.loc[(cat, d)], 1)} % {d.lower()}" for d in DESTINATIONS)
        for cat in FLUX_STYLE)
    return (f'<svg role="img" aria-label="Où travaillent les actifs de banlieue. {html.escape(description)}" '
            f'viewBox="0 0 1100 500" style="width:100%;height:auto;display:block">{branches}{dessus}{domiciles}'
            f'{etiquettes}</svg>')


LEGENDE_FLUX = ('<div style="display:flex;flex-wrap:wrap;gap:22px;align-items:center;font-size:15px;font-weight:600;'
                'margin-bottom:6px"><span style="display:inline-flex;align-items:center;gap:8px">'
                '<svg aria-hidden="true" width="30" height="30" viewBox="0 0 40 40" style="flex-shrink:0">'
                '<circle cx="20" cy="20" r="16" fill="#1B1F2A"/><path d="M13,21 L20,14 L27,21 M15,20 L15,27 L25,27 '
                'L25,20" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linejoin="round"/></svg>Domicile en '
                'banlieue <span style="font-weight:500;color:#5E6475">(couleur de la catégorie)</span></span>'
                '<span style="display:inline-flex;align-items:center;gap:8px"><svg aria-hidden="true" width="14" '
                'height="30" viewBox="0 0 14 30" style="flex-shrink:0"><rect x="2" y="2" width="10" height="26" rx="5" '
                'fill="#FFFFFF" stroke="#1B1F2A" stroke-width="2.5"/></svg>Lieu de travail</span></div>')

dest_cat = u.lire("destinations_categories.csv").set_index(["categorie", "destination"])["part_pct"]
compte_bab = u.lire("banlieue_a_banlieue_compte.csv").iloc[0]
sur_dix = round(10 * compte_bab["communes_plus_de_la_moitie"] / compte_bab["communes"])
with st.expander("Pour aller plus loin : de banlieue à banlieue"):
    st.markdown(
        f'<h3 style="margin:4px 0 8px;font-family:Poppins,sans-serif;font-size:22px;font-weight:800;line-height:1.4">'
        f'Les ouvriers restent plus souvent <span style="color:#B23A86">dans leur département</span>, les cadres vont '
        f'plus souvent <span style="color:#1F6A8C">à Paris</span></h3>'
        f'<p style="margin:0 0 14px;font-size:16px;line-height:1.6;color:#4E5466">Dans <span style="background:#B23A86;'
        f'color:#FFFFFF;border-radius:8px;padding:0 7px;font-weight:700">{sur_dix} communes sur 10</span>, plus de la '
        f'moitié des employés et ouvriers travaillent dans une autre commune de banlieue.</p>'
        f'{LEGENDE_FLUX}{graphique_flux(dest_cat)}'
        f'<p style="margin:6px 0 0;font-size:13px;color:#5E6475">Chaque maison : les actifs de banlieue d\'une catégorie '
        f'(100 %), qui travaillent en Île-de-France. Épaisseur d\'une branche = part de la catégorie qui va à ce lieu de '
        f'travail. En couleur, les deux catégories comparées ; les employés en gris.</p>'
        # Une décimale, comme sur le graphique (sans elle, Python arrondit 24,5 à 24 : arrondi au chiffre pair)
        f'<p style="margin:12px 0 0;font-size:15px;line-height:1.5"><strong>Lecture :</strong> '
        f'{u.fr(dest_cat.loc[("Ouvriers", "Leur département")], 1)} % des ouvriers de banlieue travaillent dans leur '
        f'département, contre {u.fr(dest_cat.loc[("Cadres", "Leur département")], 1)} % des cadres ; à l\'inverse, '
        f'{u.fr(dest_cat.loc[("Cadres", "Paris")], 1)} % des cadres vont à Paris, contre '
        f'{u.fr(dest_cat.loc[("Ouvriers", "Paris")], 1)} % des ouvriers. Ces trajets de proximité, de banlieue à banlieue, '
        f'sont ceux que le réseau, tourné vers Paris, dessert le moins bien.</p>', unsafe_allow_html=True)
    st.dataframe(dest_cat.unstack()[DESTINATIONS].reset_index().rename(columns={"categorie": "Catégorie"})
                 .assign(**{d: lambda df, d=d: df[d].map(lambda x: f"{u.fr(x, 1)} %") for d in DESTINATIONS}),
                 hide_index=True, width="stretch")

# Détail par département (tableaux 8 x 8 de la maquette) retiré le 2026-11-11 : jugé trop technique par Melvyn.
# À sa place, validé le même jour (canevas « Proposition p2 : ligne « plus on s'éloigne » + tableau des départs ») :
# une ligne de métro de Paris vers l'extérieur, trois stations de plus en plus marquées, et pour chacune 10 voitures
# dont autant de pleines que de dixièmes de trajets faits en voiture. Données : preparation/preparer_liaisons_banlieue.py.
VOITURE_SVG = ('<path d="M5 17h14v-5l-2-5H7l-2 5z"/><path d="M5 12h14"/><circle cx="8" cy="17" r="2"/>'
               '<circle cx="16" cy="17" r="2"/>')
ROUGE_VOITURE, GRIS_VOITURE = "#C0401A", "#C9CDD3"
STATIONS = [("petite", "Entre deux communes de", "petite couronne", 24, 4),
            ("mixte", "De la petite à la", "grande couronne", 34, 7),
            ("grande", "Entre deux communes de", "grande couronne", 46, 10)]   # (type, texte, gras, diamètre, contour)


def voiture(pleine: bool, taille: int = 26) -> str:
    """Pictogramme de voiture : plein (trajet en voiture) ou vide (trajet fait autrement)."""
    couleur = ROUGE_VOITURE if pleine else GRIS_VOITURE
    return (f'<svg aria-hidden="true" width="{taille}" height="{taille}" viewBox="0 0 24 24" '
            f'fill="{couleur if pleine else "none"}" stroke="{couleur}" stroke-width="1.8" stroke-linecap="round" '
            f'stroke-linejoin="round">{VOITURE_SVG}</svg>')


liaisons = u.lire("liaisons_banlieue.csv").set_index("type")["voiture_pct"]
stations_html = "".join(
    f'<div style="display:flex;flex-direction:column;align-items:center;gap:10px;text-align:center">'
    f'<div style="height:46px;display:flex;align-items:center"><span style="width:{d}px;height:{d}px;border-radius:50%;'
    f'background:#FFFFFF;border:{c}px solid #1B1F2A;box-sizing:border-box;position:relative;z-index:1"></span></div>'
    f'<div style="font-size:15px;line-height:1.35;color:#4E5466">{texte}<br><strong style="color:#1B1F2A">{gras}</strong></div>'
    f'<div role="img" aria-label="{u.fr(liaisons[k])} % des trajets en voiture" style="display:grid;'
    f'grid-template-columns:repeat(5,26px);gap:4px">'
    + "".join(voiture(i < round(liaisons[k] / 10)) for i in range(10))
    + f'</div><div style="font-family:Poppins,sans-serif;font-weight:800;font-size:30px;color:{ROUGE_VOITURE};'
      f'line-height:1">{u.fr(liaisons[k])} %</div><div style="font-size:14px;color:#4E5466">des trajets en voiture</div>'
      f'</div>'
    for k, texte, gras, d, c in STATIONS)
avant, apres = round(liaisons["petite"] / 10), round(liaisons["grande"] / 10)
with st.expander("Pour aller plus loin : travailler dans un autre département de banlieue"):
    st.markdown(
        f'<h3 style="margin:4px 0 10px;font-family:Poppins,sans-serif;font-size:22px;font-weight:800;line-height:1.5">'
        f'Plus on s\'éloigne de Paris, plus la voiture s\'impose : de <span style="background:{ROUGE_VOITURE};'
        f'color:#FFFFFF;border-radius:8px;padding:0 7px;font-weight:700;white-space:nowrap">1 trajet sur '
        f'{round(10 / avant)}</span> à <span style="background:{ROUGE_VOITURE};color:#FFFFFF;border-radius:8px;'
        f'padding:0 7px;font-weight:700;white-space:nowrap">{apres} sur 10</span></h3>'
        f'<div style="display:flex;flex-wrap:wrap;gap:24px;font-size:14px;font-weight:600;margin-bottom:6px">'
        f'<span style="display:inline-flex;align-items:center;gap:8px">{voiture(True, 24)}1 trajet sur 10 fait en '
        f'voiture</span><span style="display:inline-flex;align-items:center;gap:8px">{voiture(False, 24)}1 trajet sur '
        f'10 fait autrement (transports en commun, vélo, marche…)</span></div>'
        f'<div style="position:relative;padding:28px 10px 0">'
        f'<div aria-hidden="true" style="position:absolute;left:10px;right:10px;top:47px;height:8px;border-radius:4px;'
        f'background:#1B1F2A"></div><div aria-hidden="true" style="position:absolute;left:10px;top:0;font-size:13px;'
        f'font-weight:700;color:#5E6475">◂ Paris</div><div aria-hidden="true" style="position:absolute;right:10px;'
        f'top:0;font-size:13px;font-weight:700;color:#5E6475">vers l\'extérieur ▸</div>'
        f'<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px">{stations_html}</div></div>'
        f'<p style="margin:14px 0 0;font-size:14px;line-height:1.5;color:#4E5466"><strong style="color:#1B1F2A">'
        f'Lecture :</strong> employés et ouvriers qui travaillent dans un autre département de banlieue que le leur. '
        f'Chaque voiture pleine = 1 trajet sur 10 fait en voiture. Petite couronne : Hauts-de-Seine, Seine-Saint-Denis, '
        f'Val-de-Marne ; grande couronne : Seine-et-Marne, Yvelines, Essonne, Val-d\'Oise.</p>', unsafe_allow_html=True)

# --- Ponctualité des lignes (idée et premier travail de Maroua Zoubir ; script 11). Tableau des départs validé le
# 2026-11-11 (canevas « Proposition p2 : ligne « plus on s'éloigne » + tableau des départs ») à la place des points
# alignés : fond sombre, pastille de chaque ligne à sa couleur officielle, part de voyageurs à l'heure (avec le signe %,
# demandé par Melvyn) et « en retard : 1 sur X ». Chiffres en Barlow, la police des chiffres de la charte.
# « Dessert le plus de postes » : notre classement (4 premières lignes par postes desservis), pas une catégorie officielle.
ponct = u.lire("ponctualite_lignes.csv").set_index("ligne_nom").sort_values("ponctualite_pct")
couleurs_lignes = u.lire("couleurs_lignes.csv").set_index("ligne")
AMBRE, FOND_PANNEAU = "#FFC93C", "#141A2E"
COLONNES_PANNEAU = "48px 82px 96px minmax(0,1fr)"   # largeurs pour la page (plus étroite que la maquette)


def ligne_panneau(nom: str, r) -> str:
    """Une ligne du panneau : pastille de la ligne, part à l'heure, « 1 sur X » en retard, étiquette éventuelle."""
    c = couleurs_lignes.loc[nom]
    sur = round(100 / (100 - r["ponctualite_pct"]))      # 17,5 % de voyageurs en retard -> 1 sur 6
    etiquette = ('<span style="font-size:12px;font-weight:800;color:#141A2E;background:#E58BC4;border-radius:999px;'
                 'padding:3px 8px;display:inline-block;line-height:1.15;text-align:center;max-width:120px">DESSERT LE PLUS DE '
                 'POSTES</span>') if r["dessert_le_plus"] else ""
    # (étiquette sur deux lignes si besoin : elle ne déborde plus sur la colonne voisine)
    return (f'<div role="row" aria-label="{nom} : {u.fr(r["ponctualite_pct"], 1)} % des voyageurs à l\'heure, 1 sur {sur} '
            f'en retard" style="display:grid;grid-template-columns:{COLONNES_PANNEAU};gap:12px;align-items:center;'
            f'padding:7px 0;border-bottom:1px solid #262E48">'
            f'<span aria-hidden="true" style="width:30px;height:30px;border-radius:8px;background:{c["fond"]};'
            f'color:{c["texte"]};display:flex;align-items:center;justify-content:center;font-weight:800;font-size:16px">'
            f'{c["court"]}</span>'
            f'<span style="font-family:\'Barlow Semi Condensed\',sans-serif;font-weight:600;font-size:24px;color:{AMBRE}">'
            f'{u.fr(r["ponctualite_pct"], 1)} %</span>'
            f'<span style="font-family:\'Barlow Semi Condensed\',sans-serif;font-weight:600;font-size:20px;color:#F1F2F6">'
            f'1 sur <span style="color:{AMBRE};font-size:24px">{sur}</span></span><span>{etiquette}</span></div>')


entete_panneau = (f'<div aria-hidden="true" style="display:grid;grid-template-columns:{COLONNES_PANNEAU};gap:12px;'
                  f'font-size:12px;font-weight:800;letter-spacing:0.08em;color:#9AA0B2;padding-bottom:6px;'
                  f'border-bottom:2px solid #3A4368"><span>LIGNE</span><span>À L\'HEURE</span><span>EN RETARD</span>'
                  f'<span></span></div>')
lignes_triees = list(ponct.iterrows())
moitie = (len(lignes_triees) + 1) // 2           # deux colonnes : 7 lignes puis 6
colonne = lambda lignes: entete_panneau + "".join(ligne_panneau(nom, r) for nom, r in lignes)
haut = ponct.loc[ponct["dessert_le_plus"], "ponctualite_pct"].mean()
autres = ponct.loc[~ponct["dessert_le_plus"], "ponctualite_pct"].mean()
with st.expander("Pour aller plus loin : la ponctualité des lignes de RER et de train"):
    st.markdown(
        f'<h3 style="margin:4px 0 12px;font-family:Poppins,sans-serif;font-size:21px;font-weight:800">Près d\'une gare, '
        f'encore faut-il que le train soit à l\'heure</h3>'
        f'<div role="table" aria-label="Ponctualité des 13 lignes de RER et de train" style="background:{FOND_PANNEAU};'
        f'border-radius:14px;padding:16px 20px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 34px;'
        f'color:#F1F2F6"><div>{colonne(lignes_triees[:moitie])}</div><div>{colonne(lignes_triees[moitie:])}</div></div>'
        f'<p style="margin:12px 0 0;font-size:15px;line-height:1.5"><strong>Lecture :</strong> lignes classées de la '
        f'moins ponctuelle à la plus ponctuelle (12 derniers mois). « En retard : 1 sur 6 » = un voyageur sur six arrive '
        f'en retard. « Dessert le plus de postes » : les 4 lignes qui desservent le plus de postes d\'employés et '
        f'd\'ouvriers hors de Paris ; elles sont à {u.fr(haut, 1)} % à l\'heure, les 9 autres à {u.fr(autres, 1)} %. Ce '
        f'sont surtout des RER, moins ponctuels que les Transilien.</p>'
        f'<p style="margin:8px 0 0;font-size:14px;line-height:1.5;color:#5E6475">Limite : 13 lignes seulement '
        f'(RER A à E, Transilien H, J, K, L, N, P, R, U). Le métro, le tram, le bus et la ligne V ne sont pas publiés '
        f'dans ce jeu de données de la SNCF. La ponctualité ne dit pas qui voyage. Idée et premier travail : Maroua '
        f'Zoubir.</p>', unsafe_allow_html=True)
    # Tableau affiché directement : Streamlit n'accepte pas un bloc à déplier (u.tableau) dans un autre
    st.dataframe(ponct.reset_index().assign(
        Ligne=lambda d: d["ligne_nom"], **{"À l'heure (%)": lambda d: d["ponctualite_pct"].map(lambda x: u.fr(x, 1)),
                                           "Postes d'employés et d'ouvriers desservis (hors Paris)":
                                               lambda d: d["emplois_eo_desservis"].map(lambda x: u.fr(round(x, -3)))})
                 [["Ligne", "À l'heure (%)", "Postes d'employés et d'ouvriers desservis (hors Paris)"]],
                 hide_index=True, width="stretch")


u.navigation_bas(FICHIER)
u.sources("INSEE, recensement 2023, mobilités professionnelles ; IDFM, offre hebdomadaire 2025 et référentiel des "
          "arrêts ; SNCF, régularité mensuelle Transilien (licence ODbL).")
