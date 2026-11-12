"""
p4_nuit.py : station 4, « Les trajets de nuit ».

Message : la nuit (minuit-5h), il reste 8 % des passages de 7h-10h, sur l'ensemble de l'Île-de-France.
Ce sont surtout les ouvriers qui en ont besoin : ils travaillent deux fois plus souvent la nuit que les cadres.

Une seule mesure dans le visuel principal : les passages prévus par heure (jour de semaine).
Limite affichée : les passages sont prévus, ils ne disent ni qui voyage ni pourquoi.
Données : donnees/offre_par_heure.csv (preparation/preparer_offre_horaire.py, même méthode que le script 05).
"""

import html

import pandas as pd
import streamlit as st

import utils as u

FICHIER = "pages/p4_nuit.py"
TRANCHES_NUIT = [24, 25, 26, 27, 4]   # minuit-5h (définition INSEE de la nuit), dans le découpage IDFM
TRANCHES_POINTE = [7, 8, 9]           # 7h-10h (notre choix de comparaison, pas une définition officielle)
DEBUT_SOIR = 20                       # soir de 20h à minuit selon l'INSEE (enquête Emploi)

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

# Vocabulaire « offre de transport de nuit » (demande de Melvyn, 11/11) : plus juste que « bus et trains », car on
# compte tous les passages prévus (bus, métros, trains, trams)
retenir = (f"L'offre de transport de nuit s'affaiblit sur l'ensemble de l'Île-de-France, pas seulement là où travaillent "
           f"les ouvriers. Ce qui "
           f"change, c'est qui en a besoin : les ouvriers, deux fois plus souvent de nuit que les cadres.")
# Commentaire de la page (texte validé le 2026-11-12) ; la partie « graphique » sert aussi de description de la courbe
description = (f"Entre minuit et 5h, l'offre de transport tombe à {u.fr(rapport, 1)} % de celle de 7h à 10h "
               ": il ne reste presque que des bus de nuit.")
graphique = (f"La courbe suit les passages prévus heure par heure, un jour de semaine, dans toute l'Île-de-France. Elle "
             f"culmine vers 8 heures et vers 18 heures, autour de {u.fr(round(pointe, -3))} passages par heure aux heures "
             f"de pointe, baisse le soir, puis tombe à environ {u.fr(round(nuit, -3))} passages par heure entre minuit et "
             f"5 heures.")
commentaire = u.commentaire_page(
    FICHIER, f"la nuit, une offre de transport {round(100 / rapport)} fois moins importante",
    description.replace("minuit et 5h", "minuit et 5 heures").replace("7h à 10h", "7 heures à 10 heures"), graphique,
    f"{TRAVAIL_NUIT_PCT['Ouvriers']} % des ouvriers travaillent la nuit au moins une fois par mois, contre "
    f"{TRAVAIL_NUIT_PCT['Cadres']} % des cadres.",
    u.a_retenir(retenir),
    "Limite : on compte l'offre prévue, pas qui la prend ni pourquoi.",
    a_deplier=("la carte de la nuit et le dimanche",))
# « 13 fois moins » plutôt que « 8 % des passages » : le pourcentage avait été mal compris (remarque de Pierre THAI, 11/11)
u.entete(FICHIER, f'La nuit, une offre de transport <span style="color:{ROSE_NUIT}">{round(100 / rapport)} fois moins'
                  f'</span> importante',
         # « Heures de pointe » plutôt que « pointe » (mot jugé incompréhensible par Melvyn, 11/11)
         description, retenir,
         u.panneau("Travaillent la nuit", f"{TRAVAIL_NUIT_PCT['Ouvriers']} %",
                   f"des ouvriers (cadres : {TRAVAIL_NUIT_PCT['Cadres']} %), au moins une fois par mois", ROSE_NUIT,
                   "#FFFFFF", "lune", nuit=True), nuit=True, commentaire=commentaire)

# --- Visuel principal : variante A (courbe) validée le 2026-11-11 (canevas « Proposition p4, variante A »,
# inspirée de HAP Express : on éclaire l'information clé et on efface le reste). Par rapport aux 24 barres de la maquette :
#   - une courbe lisse de 5h à 4h du matin (la nuit regroupée à droite), journée en gris clair, nuit en rose avec un
#     point par heure ;
#   - deux zones nommées en fond : « Pointe 7h-10h » et « Nuit 0h-5h » ;
#   - le niveau moyen de la pointe prolongé en pointillés jusqu'à la nuit, puis une flèche qui descend au niveau de la
#     nuit avec la pastille « 13 fois moins » : on voit la chute au lieu de la calculer.
# Valeurs calculées (moyenne du mardi au jeudi, comme le script 05) ; dessin en SVG écrit ici, sans bibliothèque.
offre["ordre"] = (offre["heure"] - 5) % 24
offre = offre.sort_values("ordre")
offre["Heure"] = offre["heure"].map(lambda h: f"{h}h")
# Mêmes plages que la courbe : soir et nuit selon l'INSEE, le reste nommé par ses heures (aucune source ne le nomme)
offre["Moment"] = [("Nuit (minuit-5h)" if t in TRANCHES_NUIT else "Soir (20h-minuit)" if h >= DEBUT_SOIR else "De 5h à 20h")
                   for t, h in zip(offre["tranche_horaire"], offre["heure"])]
offre["Passages par heure"] = offre["passages_semaine"].map(lambda v: u.fr(v))
valeurs = offre["passages_semaine"].tolist()
heures = offre["heure"].tolist()
I_POINTE = [i for i, t in enumerate(offre["tranche_horaire"]) if t in TRANCHES_POINTE]   # 7h, 8h, 9h
I_NUIT = [i for i, t in enumerate(offre["tranche_horaire"]) if t in TRANCHES_NUIT]       # 0h à 4h
LARGEUR, X0, LONGUEUR, Y0, HAUTEUR = 1000, 30, 940, 70, 220   # repère du dessin (viewBox), en unités SVG
BASE = Y0 + HAUTEUR
PAS = LONGUEUR / 23


def px(i: int) -> float:
    """Abscisse de la i-ème heure (5h = 0)."""
    return X0 + i * PAS


def py(x: float) -> float:
    """Ordonnée d'un nombre de passages (0 en bas, le maximum en haut)."""
    return BASE - x / max(valeurs) * HAUTEUR


def lisse(points: list) -> str:
    """Chemin SVG d'une courbe lisse passant par chaque point (Catmull-Rom converti en courbes de Bézier).

    La courbe passe exactement par les valeurs réelles ; les points de contrôle sont bloqués à l'axe pour qu'elle ne
    descende jamais sous zéro (un nombre de passages négatif n'aurait pas de sens).
    """
    d = f"M{points[0][0]:.1f},{points[0][1]:.1f}"
    for k in range(len(points) - 1):
        p0, p1, p2, p3 = points[max(k - 1, 0)], points[k], points[k + 1], points[min(k + 2, len(points) - 1)]
        d += (f"C{p1[0] + (p2[0] - p0[0]) / 6:.1f},{min(BASE, p1[1] + (p2[1] - p0[1]) / 6):.1f} "
              f"{p2[0] - (p3[0] - p1[0]) / 6:.1f},{min(BASE, p2[1] - (p3[1] - p1[1]) / 6):.1f} {p2[0]:.1f},{p2[1]:.1f}")
    return d


pts = [(px(i), py(x)) for i, x in enumerate(valeurs)]
n0 = I_NUIT[0]
# Soir selon l'INSEE (enquête Emploi) : de 20h à minuit (validé par Melvyn le 11/11, planche « journée, soir et nuit »)
s0 = heures.index(DEBUT_SOIR)
SOIR = "#A58BC9"     # mauve, entre le gris du reste de la journée et le rose de la nuit
xs0 = px(s0) - PAS / 2
xn0, xn1 = px(I_NUIT[0]) - PAS / 2, px(I_NUIT[-1]) + PAS / 2
xp0, xp1 = px(I_POINTE[0]) - PAS / 2, px(I_POINTE[-1]) + PAS / 2
xm, yp, yn = (xn0 + xn1) / 2, py(pointe), py(nuit)
ym = (yp + yn) / 2 + 20
fois = round(100 / rapport)
svg = (
    f'<svg role="img" aria-label="{html.escape(graphique)}" '
    f'viewBox="0 0 {LARGEUR} {BASE + 40}" style="width:100%;height:auto;display:block;font-family:\'Plus Jakarta Sans\','
    f'sans-serif">'
    # Zones nommées (fond)
    f'<rect x="{xp0:.1f}" y="{Y0 - 44}" width="{xp1 - xp0:.1f}" height="{BASE - Y0 + 44}" rx="10" fill="#F1F2F6" '
    f'fill-opacity="0.07"/>'
    f'<rect x="{xs0:.1f}" y="{Y0 - 44}" width="{xn0 - xs0 - 4:.1f}" height="{BASE - Y0 + 44}" rx="10" fill="{SOIR}" '
    f'fill-opacity="0.14"/>'
    f'<text x="{(xs0 + xn0) / 2:.1f}" y="{Y0 - 20}" text-anchor="middle" font-size="19" font-weight="700" '
    f'fill="{SOIR}">Soir 20h-minuit</text>'
    f'<rect x="{xn0:.1f}" y="{Y0 - 44}" width="{xn1 - xn0:.1f}" height="{BASE - Y0 + 44}" rx="10" fill="{ROSE_NUIT}" '
    f'fill-opacity="0.13"/>'
    f'<text x="{(xp0 + xp1) / 2:.1f}" y="{Y0 - 20}" text-anchor="middle" font-size="19" font-weight="700" '
    f'fill="#F1F2F6">7h-10h</text>'
    f'<text x="{xm:.1f}" y="{Y0 - 20}" text-anchor="middle" font-size="19" font-weight="700" fill="{ROSE_NUIT}">'
    f'Nuit minuit-5h</text>'
    # Courbe : aire claire, trait de journée, aire et trait de nuit, un point par heure de nuit
    f'<path d="{lisse(pts)}L{pts[-1][0]:.1f},{BASE}L{pts[0][0]:.1f},{BASE}Z" fill="{GRIS_JOUR}" fill-opacity="0.18"/>'
    f'<path d="{lisse(pts[:s0 + 1])}" fill="none" stroke="#C9CDD8" stroke-width="3" stroke-linecap="round"/>'
    f'<path d="{lisse(pts[s0:n0 + 1])}" fill="none" stroke="{SOIR}" stroke-width="3.5" stroke-linecap="round"/>'
    f'<path d="{lisse(pts[n0:])}L{pts[-1][0]:.1f},{BASE}L{pts[n0][0]:.1f},{BASE}Z" fill="{ROSE_NUIT}" fill-opacity="0.45"/>'
    f'<path d="{lisse(pts[n0:])}" fill="none" stroke="{ROSE_NUIT}" stroke-width="3.5" stroke-linecap="round"/>'
    + "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{ROSE_NUIT}" stroke="{u.CARTE_NUIT}" stroke-width="2"/>'
              for x, y in pts[n0:])
    # Repères : niveau de la pointe prolongé, flèche vers la nuit, pastille du rapport
    + f'<line x1="{xp1:.1f}" y1="{yp:.1f}" x2="{xm:.1f}" y2="{yp:.1f}" stroke="#F1F2F6" stroke-width="1.5" '
    f'stroke-dasharray="5 6" stroke-opacity="0.75"/>'
    f'<text x="{xp1 + 32:.1f}" y="{yp + 24:.1f}" font-size="19" font-weight="600" fill="#F1F2F6">'
    f'<tspan x="{xp1 + 32:.1f}">De 7h à 10h :</tspan><tspan x="{xp1 + 32:.1f}" dy="21">'
    f'{u.fr(round(pointe, -3))} / h</tspan></text>'   # deux lignes courtes : le texte ne croise pas la courbe
    f'<line x1="{xm:.1f}" y1="{yp + 4:.1f}" x2="{xm:.1f}" y2="{yn - 12:.1f}" stroke="{ROSE_NUIT}" stroke-width="2"/>'
    f'<path d="M{xm - 6:.1f},{yn - 19:.1f} L{xm:.1f},{yn - 10:.1f} L{xm + 6:.1f},{yn - 19:.1f}" fill="none" '
    f'stroke="{ROSE_NUIT}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    f'<rect x="{xm - 74:.1f}" y="{ym - 19:.1f}" width="148" height="38" rx="19" fill="{ROSE_NUIT}"/>'
    f'<text x="{xm:.1f}" y="{ym + 6:.1f}" text-anchor="middle" font-size="20" font-weight="800" fill="{u.FOND_NUIT}">'
    f'{fois} fois moins</text>'
    f'<text x="{xn0 - 10:.1f}" y="{yn - 6:.1f}" text-anchor="end" font-size="19" font-weight="700" fill="{ROSE_NUIT}">'
    f'Nuit : {u.fr(round(nuit, -3))} / h</text>'
    # Axe et heures (une sur trois)
    f'<line x1="{X0 - 14}" y1="{BASE}" x2="{X0 + LONGUEUR + 24}" y2="{BASE}" stroke="#5A6386" stroke-width="1"/>'
    f'<g font-size="19" fill="#9AA0B2">'
    + "".join(f'<text x="{px(i):.1f}" y="{BASE + 28}" text-anchor="middle">{h}h</text>'
              for i, h in enumerate(heures) if h % 3 == 2)
    + '</g></svg>')
# Légende du graphique (demandée par Melvyn le 11/11) : trait de journée, trait et points de nuit, pointillés.
# Chaque élément visuel a son libellé écrit : l'information n'est jamais portée par la couleur seule.
def element_legende(dessin: str, libelle: str) -> str:
    """Une entrée de légende : petit dessin SVG (décoratif) suivi de son libellé écrit."""
    return (f'<span style="display:inline-flex;align-items:center;gap:8px;padding:3px 10px;border-radius:999px;'
            f'background:#262E48;font-size:14px;font-weight:600;color:#F1F2F6"><svg aria-hidden="true" width="28" '
            f'height="14" viewBox="0 0 28 14">{dessin}</svg>{libelle}</span>')


legende_courbe = ('<div style="display:flex;flex-wrap:wrap;gap:8px">'
                  + element_legende('<line x1="2" y1="7" x2="26" y2="7" stroke="#C9CDD8" stroke-width="3" '
                                    'stroke-linecap="round"/>', "De 5h à 20h")   # aucune source ne nomme cette plage
                  + element_legende(f'<line x1="2" y1="7" x2="26" y2="7" stroke="{SOIR}" stroke-width="3.5" '
                                    f'stroke-linecap="round"/>', "Soir (20h-minuit)")
                  + element_legende(f'<line x1="2" y1="7" x2="26" y2="7" stroke="{ROSE_NUIT}" stroke-width="3.5" '
                                    f'stroke-linecap="round"/><circle cx="14" cy="7" r="4.5" fill="{ROSE_NUIT}"/>',
                                    "Nuit (minuit-5h)")
                  + element_legende('<line x1="2" y1="7" x2="26" y2="7" stroke="#F1F2F6" stroke-width="1.5" '
                                    'stroke-dasharray="5 4"/>', "Moyenne de 7h à 10h")
                  + '</div>')   # libellés courts (demande de Melvyn, 11/11) : le graphique les précise déjà
# Phrase qui résume le graphique (demande de Melvyn, 11/11). Sans chiffre : « 13 fois moins » et le niveau de nuit
# sont déjà dans le titre et sur la courbe (règle : ne pas répéter la même information sur une page)
resume = ("<strong>Lecture :</strong> l'offre de transport culmine vers 8h et vers 18h, baisse le "
          "soir, puis s'effondre après minuit jusqu'à 5h.")
st.markdown(
    f'<figure style="margin:0;background:{u.CARTE_NUIT};border:1px solid #262E48;border-radius:16px;padding:22px 28px;'
    f'display:flex;flex-direction:column;gap:10px">'
    f'<figcaption style="display:flex;align-items:center;gap:10px;font-size:17px;font-weight:700;color:#F1F2F6">'
    f'{u.badge_mode("navette", nuit=True)}Offre de transport prévue chaque heure (bus, métros, trains, trams), un jour '
    f'de semaine, toute l\'Île-de-France</figcaption>{legende_courbe}'
    f'<div class="defile-mobile defile-fin" style="--largeur-mobile:840px">{svg}</div>'
    f'<p style="margin:0;font-size:15px;line-height:1.5;color:#C9CDD8">{resume}</p>'
    # Source des plages (règle CLAUDE.md : aucune définition sans source)
    f'<p style="margin:0;font-size:14px;line-height:1.5;color:#9AA0B2">Soir et nuit selon l\'INSEE (enquête Emploi) : '
    f'soir de 20h à minuit, nuit de minuit à 5h. Le Code du travail retient une plage plus large pour la nuit '
    f'(21h-6h).</p></figure>', unsafe_allow_html=True)
# Sonification (le « plus » validé le 2026-11-12) : une note par heure, de 5h à 4h comme la courbe ; quelques heures
# repères sont dites avant leur note (début, heure de pointe du matin, minuit)
REPERES_SONORES = {5: "5 heures du matin", 8: "8 heures", 0: "minuit"}
plus_haut = max(valeurs)
u.bouton_sonification(
    "Chaque note est une heure, de 5 heures du matin à 4 heures du matin le lendemain. Plus le son est aigu, plus il y "
    "a de passages prévus.",
    [(REPERES_SONORES.get(h, ""), v / plus_haut) for h, v in zip(heures, valeurs)],
    f"Après minuit, le son tombe : {round(100 / rapport)} fois moins de passages qu'aux heures de pointe.",
    duree_note=0.35, nuit=True)
u.tableau(offre.sort_values("ordre")[["Heure", "Moment", "Passages par heure"]])

u.encadres(retenir, "On compte l'offre de transport prévue, pas qui la prend ni pourquoi : tous les voyageurs de nuit ne "
           "vont pas travailler. Horaires de travail : chiffres France entière.", couleur=ROSE_NUIT, fond="#2A2140",
           nuit=True)

# Bloc de la maquette validée : carte de la nuit par commune, puis une phrase sur le dimanche.
# Changement validé le 2026-11-11 (planche « Lire la carte : nuit ») : la carte d'origine passe de 6 nuances à
# 2 couleurs (aucun passage / au moins un), avec un titre qui donne le message et une phrase « Lecture ».
# Carte et comptage : preparation/preparer_carte_nuit_2couleurs.py (le chiffre du titre est calculé, pas écrit).
compte = u.lire("carte_nuit_compte.csv").iloc[0]
sur_dix = round(10 * compte["communes_aucun_passage"] / compte["communes_total"])
LEGENDE_NUIT = [("Aucun passage de minuit à 5h", u.echantillon("#3A4368", "#8E96B3")),
                ("Au moins un passage", u.echantillon(ROSE_NUIT))]
with st.expander("Pour aller plus loin : la carte de la nuit et le dimanche"):
    u.ecouter_partie(
        f"La carte de la nuit et le dimanche. {sur_dix} communes sur 10 n'ont aucune offre de transport de nuit : "
        f"{u.fr(compte['communes_aucun_passage'])} communes sur {u.fr(compte['communes_total'])} n'ont aucun bus ni "
        f"train entre minuit et 5 heures, surtout en grande couronne. La nuit, l'offre de transport se resserre sur Paris "
        f"et la petite couronne. Le dimanche, l'offre de transport est de {dimanche:.0f} % de celle d'un jour de "
        f"semaine ; {TRAVAIL_DIMANCHE_PCT['Employés']} % des employés travaillent le dimanche, contre "
        f"{TRAVAIL_DIMANCHE_PCT['Cadres']} % des cadres.", nuit=True)
    st.markdown(u.figure_carte(
        "carte_nuit_2couleurs.svg",
        f"Carte nocturne des communes d'Île-de-France : {u.fr(compte['communes_aucun_passage'])} communes sur "
        f"{u.fr(compte['communes_total'])} n'ont aucun passage de bus ni de train entre minuit et 5h, surtout en grande "
        "couronne ; la plupart des communes de Paris et de petite couronne gardent une offre", LEGENDE_NUIT,
        titre=f'<span style="font-family:Poppins,sans-serif;font-size:21px;font-weight:800;line-height:1.5">'
              f'<span style="background:{ROSE_NUIT};color:#141A2E;border-radius:14px;padding:0 12px">{sur_dix} communes '
              f'sur 10</span> n\'ont aucune offre de transport de nuit (aucun bus ni train entre minuit et 5h)</span>',
        note="<strong>Lecture :</strong> la nuit, l'offre de transport se resserre sur Paris et la petite couronne ; "
             "au-delà, la plupart des communes n'ont plus aucun passage.", nuit=True), unsafe_allow_html=True)
    st.markdown(f'<p style="margin-top:14px;font-size:15px;line-height:1.5">Le dimanche, l\'offre de transport est de '
                f'{dimanche:.0f} % de celle d\'un jour de semaine ; {TRAVAIL_DIMANCHE_PCT["Employés"]} % des employés travaillent le '
                f'dimanche, contre {TRAVAIL_DIMANCHE_PCT["Cadres"]} % des cadres.</p>', unsafe_allow_html=True)

u.navigation_bas(FICHIER)
u.sources("IDFM, offre hebdomadaire moyenne hors vacances 2025 (moyenne du mardi au jeudi) ; INSEE, enquête Emploi 2025, "
          "salariés, France entière.")
