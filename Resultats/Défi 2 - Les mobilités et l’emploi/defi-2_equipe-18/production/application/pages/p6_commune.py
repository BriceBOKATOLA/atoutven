"""
p6_commune.py : station 6, « Chercher ma commune ».

Le lecteur choisit sa commune ; la page montre, pour les employés et ouvriers qui y habitent :
  - trois tuiles : combien ils sont, la part qui reste dans la commune, la part qui va à Paris ;
  - la carte des communes où ils travaillent (même dessin que la carte d'Évry de la maquette validée :
    5 classes de couleur, commune de résidence encadrée) et la liste de leurs principales communes de travail ;
  - « Une gare dans la commune ? » : les lignes ferrées de la commune, et la part de leurs emplois situés dans
    une commune sans gare (case « [à calculer] » de la maquette, désormais calculée).

Changements validés le 2026-11-11 (planche « Lire la carte : ma commune ») : la carte s'ouvre cadrée sur les lieux de
travail des habitants (un interrupteur montre toute la région), 3 classes au lieu de 5, les 3 premières communes de
travail écrites sur la carte avec leur part, un titre qui donne le message, une phrase « Lecture », et les lignes de
la commune en pictogrammes (couleurs officielles IDFM) au lieu du texte.

Maquette : maquettes_validees/Commune.dc.html. Données : preparation/preparer_communes.py.
"""

import html
import json

import pandas as pd
import streamlit as st

import utils as u
from svg_leger import relatif

FICHIER = "pages/p6_commune.py"
CODE_DEFAUT = "91228"           # Évry-Courcouronnes : la commune de la maquette validée
CODE_PARIS = "75056"
SEUIL_FRAGILE = 200             # en dessous de 200 personnes, l'INSEE déconseille de commenter les écarts
NOMS_DEPARTEMENTS = {"75": "Paris", "77": "Seine-et-Marne", "78": "Yvelines", "91": "Essonne", "92": "Hauts-de-Seine",
                     "93": "Seine-Saint-Denis", "94": "Val-de-Marne", "95": "Val-d'Oise"}
# 3 classes (planche validée) : l'œil distingue 3 nuances sans aller-retour vers la légende ; couleurs reprises de la
# carte d'Évry de la maquette (la plus foncée et celle du milieu), plus une nuance claire
CLASSES = [(5, "5 % et plus", "#8e2a10"), (1, "1 à 5 %", "#c48674"), (0.25, "0,25 à 1 %", "#f3cfc3")]
SANS_COULEUR = "#EEF0EC"
SEUIL_ZOOM_PCT = 1              # la vue cadrée englobe les communes de travail qui pèsent au moins 1 %
NB_ETIQUETTES = 3               # communes écrites sur la carte avec leur part
MAX_LIGNES_AFFICHEES = 8        # au-delà (Paris, La Défense…), on résume : « et N autres lignes »

u.appliquer_style()
u.menu(FICHIER)

residence = u.lire("communes_residence.csv").astype({"code": str, "departement": str}).set_index("code")
destinations = u.lire("communes_destinations.csv").astype({"code_residence": str, "code_travail": str})


@st.cache_data
def contours() -> dict:
    """Contours des communes déjà projetés et simplifiés (une seule lecture pour toutes les recherches)."""
    return json.loads((u.DONNEES / "contours_communes.json").read_text(encoding="utf-8"))


@st.cache_data
def chemins_legers() -> dict:
    """Contours écrits en écarts relatifs (svg_leger.relatif), calculés une seule fois pour toutes les recherches.

    Même dessin, carte environ 40 % plus légère : elle est renvoyée au navigateur à chaque changement de commune, ce
    qui créait de la latence en ligne (2026-11-12). Les tracés absolus de contours() restent utilisés pour le cadrage
    (boite), qui lit les coordonnées absolues.
    """
    return {code: relatif(chemin) for code, chemin in contours()["chemins"].items()}


def couleur_classe(part: float) -> str:
    """Couleur de la classe d'une part (%), ou gris très clair sous 0,25 %."""
    return next((c for seuil, _, c in CLASSES if part >= seuil), SANS_COULEUR)


def boite(chemin: str) -> tuple:
    """Rectangle englobant d'un tracé SVG (x min, y min, x max, y max) : sert au cadrage et aux étiquettes."""
    import re
    nombres = [float(v) for v in re.findall(r"-?\d+\.?\d*", chemin)]
    return min(nombres[0::2]), min(nombres[1::2]), max(nombres[0::2]), max(nombres[1::2])


@st.cache_data
def carte_svg(code: str, entiere: bool) -> str:
    """Carte SVG des communes de travail des habitants de `code`, encodée pour une balise <img> (texte alternatif).

    entiere=False : vue cadrée sur les communes de travail d'au moins 1 % (avec une marge), pour voir tout de suite où
    vont les habitants ; entiere=True : toute l'Île-de-France. Les 3 premières communes de travail sont écrites sur la
    carte avec leur part (texte foncé cerné de blanc, lisible sur toutes les nuances).
    """
    import base64
    geo = contours()
    d = destinations[destinations["code_residence"] == code].sort_values("part_pct", ascending=False)
    parts = d.set_index("code_travail")["part_pct"]
    legers = chemins_legers()
    # Trait blanc commun à toutes les communes, écrit une seule fois sur le groupe (même rendu, carte plus légère)
    chemins = ('<g stroke="#FFFFFF" stroke-width="0.5">'
               + "".join(f'<path d="{legers[c]}" fill="{couleur_classe(parts.get(c, 0))}"/>' for c in geo["chemins"])
               + "</g>")
    # Commune de résidence encadrée en dernier, pour passer au-dessus des voisines
    cadre = f'<path d="{legers[code]}" fill="none" stroke="#1B1F2A" stroke-width="2.4"/>' if code in legers else ""
    zone = [c for c in d.loc[d["part_pct"] >= SEUIL_ZOOM_PCT, "code_travail"] if c in geo["chemins"]] or [code]
    if entiere:
        x0, y0, largeur, hauteur = 0, 0, geo["largeur"], geo["hauteur"]
    else:
        b = [boite(geo["chemins"][c]) for c in zone]
        x0, y0 = min(v[0] for v in b) - 12, min(v[1] for v in b) - 12
        largeur, hauteur = max(v[2] for v in b) + 12 - x0, max(v[3] for v in b) + 12 - y0
        largeur += largeur * 0.3   # place à droite pour les étiquettes des communes du bord
    taille = largeur / 520         # texte d'environ 15 px à l'affichage, quelle que soit la vue
    etiquettes, fin_etiquettes = "", 0
    # Étiquettes seulement sur la vue cadrée : à l'échelle de la région, les communes voisines se chevauchent
    for t in d.head(0 if entiere else NB_ETIQUETTES).itertuples():
        if t.code_travail not in geo["chemins"]:
            continue   # destination hors Île-de-France : pas de tracé
        b = boite(geo["chemins"][t.code_travail])
        x, y = b[2] + 4 * taille, (b[1] + b[3]) / 2
        if t.code_travail == CODE_PARIS:   # Paris : étiquette dedans (à droite, elle flotterait près du bois de Vincennes)
            x, y = b[0] + (b[2] - b[0]) * 0.25, (b[1] + b[3]) / 2 - 4 * taille
        texte = f"{t.nom_travail} {pct(t.part_pct)}"
        fin_etiquettes = max(fin_etiquettes, x + len(texte) * 15 * taille * 0.62)
        etiquettes += (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Plus Jakarta Sans, sans-serif" '
                       f'font-size="{15 * taille:.2f}" font-weight="800" fill="#1B1F2A" stroke="#FFFFFF" '
                       f'stroke-width="{3 * taille:.2f}" paint-order="stroke">{html.escape(texte)}</text>')
    # Élargit la vue jusqu'au bout de l'étiquette la plus longue (largeur d'un caractère gras : environ 0,62 x la taille)
    largeur = max(largeur, fin_etiquettes - x0 + 6 * taille) if not entiere else largeur
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.1f} {y0:.1f} {largeur:.1f} {hauteur:.1f}">'
           f'{chemins}{cadre}{etiquettes}</svg>')
    return base64.b64encode(svg.encode("utf-8")).decode("ascii")


def arrondi(n: float) -> str:
    """Effectif arrondi (centaine au-delà de 1 000, dizaine en dessous) : le recensement est une estimation."""
    return u.fr(round(n, -2) if n >= 1000 else round(n, -1))


def pct(x: float) -> str:
    """Pourcentage sans décimale, sauf sous 10 % où la décimale aide à comparer (4,4 % et 3,0 %)."""
    return f"{u.fr(x, 1 if x < 10 else 0)} %"


# Prépositions devant un nom de commune (relecture du 12/11 : « d'habitants de Évry-Courcouronnes » était fautif).
# 131 communes commencent par une voyelle, 55 par « Le » ou « Les ». Le « H » est laissé de côté : l'élision dépend
# du mot (h muet ou aspiré), on garde « de » pour ne pas se tromper.
VOYELLES = tuple("AEIOUYÂÀÉÈÊÎÏÔÛ")


def de_commune(nom: str) -> str:
    """« de » accordé au nom : d'Évry-Courcouronnes, du Chesnay-Rocquencourt, des Ulis, de La Garenne-Colombes."""
    if nom.startswith("Le "):
        return "du " + nom[3:]
    if nom.startswith("Les "):
        return "des " + nom[4:]
    return ("d'" if nom.startswith(VOYELLES) else "de ") + nom


def a_commune(nom: str) -> str:
    """« à » accordé au nom : au Chesnay-Rocquencourt, aux Ulis, à Évry-Courcouronnes."""
    if nom.startswith("Le "):
        return "au " + nom[3:]
    if nom.startswith("Les "):
        return "aux " + nom[4:]
    return "à " + nom


def libelle(code: str) -> str:
    """Libellé d'une commune dans la liste de recherche : nom, département et numéro."""
    r = residence.loc[code]
    return f"{r['nom']} ({NOMS_DEPARTEMENTS.get(r['departement'], r['departement'])} · {r['departement']})"


# --- En-tête : à gauche le titre (maquette), à droite la recherche à la place du panneau-chiffre ---
gauche, droite = st.columns([1.25, 1], vertical_alignment="top")
with gauche:
    u.entete(FICHIER, 'Et chez <span style="color:#1F6A8C">vous</span> ?',
             f"Cherchez votre commune parmi les {u.fr(len(contours()['chemins']))} d'Île-de-France : où travaillent ses "
             "employés et ouvriers, et si leurs lieux de travail ont une gare.")
with droite:
    # st.selectbox plutôt qu'un champ de texte libre : on peut taper le début du nom pour filtrer la liste,
    # il se manie au clavier, et il ne propose que des communes qui existent dans les données.
    # Habillage de la maquette : libellé gras gris, champ blanc à bord bleu de 2 px et coins arrondis
    st.markdown('<style>[data-testid="stSelectbox"] label p{font-size:14px;font-weight:600;color:#4E5466}'
                '[data-testid="stSelectbox"] [role="group"]{background:#FFFFFF;border:2px solid #3A8FB7;border-radius:14px;'
                'min-height:48px}[data-testid="stSelectbox"] input{font-size:16px;font-weight:600;color:#1B1F2A}</style>', unsafe_allow_html=True)
    codes = sorted(residence.index, key=lambda c: residence.loc[c, "nom"])
    code = st.selectbox("Rechercher une commune", codes, index=codes.index(CODE_DEFAUT), format_func=libelle,
                        key="commune", placeholder="Tapez le nom d'une commune")

r = residence.loc[code]
nom = html.escape(r["nom"])
dest = destinations[destinations["code_residence"] == code].sort_values("part_pct", ascending=False)
if r["employes_ouvriers"] < SEUIL_FRAGILE:
    st.warning(f"Moins de {SEUIL_FRAGILE} employés et ouvriers habitent cette commune : les parts ci-dessous reposent "
               "sur peu de réponses au recensement et sont à lire avec prudence (l'INSEE conseille la prudence sous 200 "
               "personnes).")


# --- Trois tuiles (maquette) : barre de couleur à gauche, rond avec repère, valeur, contexte ---
def tuile(libelle_tuile: str, valeur: str, contexte: str, couleur: str) -> str:
    """Une tuile chiffrée de la maquette."""
    return (f'<div style="position:relative;background:#FFFFFF;border:1px solid #E7EAE4;border-radius:16px;'
            f'padding:14px 18px 14px 24px"><span aria-hidden="true" style="position:absolute;left:0;top:12px;bottom:12px;'
            f'width:5px;border-radius:0 3px 3px 0;background:{couleur}"></span>'
            f'<div style="display:flex;align-items:center;gap:10px;font-size:14px;font-weight:600;color:#4E5466">'
            f'<span aria-hidden="true" style="width:28px;height:28px;border-radius:50%;background:{couleur};display:inline-flex;'
            f'align-items:center;justify-content:center;flex-shrink:0">{u.icone("repere", 14)}</span>{libelle_tuile}</div>'
            f'<div style="font-family:Poppins,sans-serif;font-weight:800;font-size:26px;line-height:1.25;margin-top:4px">'
            f'{valeur}</div><div style="font-size:14px;color:#5E6475">{contexte}</div></div>')


if code == CODE_PARIS:
    # Pour Paris, « vont à Paris » répéterait « restent dans la commune » : on montre la part qui sort de Paris
    troisieme = tuile("Vont en dehors de Paris", pct(100 - r["part_meme_commune_pct"]),
                      f"{int(r['communes_au_moins_0_25_pct'])} communes pèsent au moins 0,25 %", "#3A8FB7")
else:
    troisieme = tuile("Vont à Paris", pct(r["part_paris_pct"]),
                      f"{int(r['communes_au_moins_0_25_pct'])} communes pèsent au moins 0,25 %", "#3A8FB7")
st.markdown('<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:6px 0 18px">'
            + tuile("Employés et ouvriers", arrondi(r["employes_ouvriers"]), f"qui habitent {nom}", "#E4572E")
            + tuile("Restent dans la commune", pct(r["part_meme_commune_pct"]), f"travaillent {a_commune(nom)} même", "#B23A86")
            + troisieme + '</div>', unsafe_allow_html=True)

# --- Carte et colonne de droite (principales communes, gare) ---
# Texte alternatif écrit à partir des données : les trois premières communes de travail
noms_top = list(dest["nom_travail"].head(3))
if len(noms_top) >= 2:
    enumeration = "surtout " + ", ".join(noms_top[:-1]) + " et " + noms_top[-1]
else:
    enumeration = f"surtout {noms_top[0]}" if noms_top else "aucune commune ne dépasse 0,25 %"
alt = f"Carte des communes où travaillent les employés et ouvriers {de_commune(r['nom'])} : {enumeration}."
legende = "".join(u.pastille_legende(lib, f"width:12px;height:12px;border-radius:3px;background:{c}")
                  for _, lib, c in CLASSES)
legende += u.pastille_legende("Moins de 0,25 %", f"width:12px;height:12px;border-radius:3px;background:{SANS_COULEUR};"
                                                 "box-shadow:inset 0 0 0 1px #C9CDD3")
# Titre-message de la carte : la part qui reste dans la commune (pastille), puis les 2 premières autres destinations
autres = list(dest.loc[dest["code_travail"] != code, "nom_travail"].head(2))
suite = f", les autres vont surtout vers {' et '.join(html.escape(a) for a in autres)}" if autres else ""
titre_carte = (f'<div style="font-family:Poppins,sans-serif;font-size:20px;font-weight:800;line-height:1.5">'
               f'<span style="background:#C0401A;color:#FFFFFF;border-radius:14px;padding:0 12px">'
               f'{pct(r["part_meme_commune_pct"])}</span> restent {a_commune(nom)}{suite}</div>')
# Interrupteur plutôt que bouton dans la carte : un vrai widget, atteignable au clavier et lu par les lecteurs d'écran
entiere = st.toggle("Voir toute l'Île-de-France sur la carte", key="vue_entiere")
lecture = (f"plus la commune est foncée, plus elle attire d'habitants {de_commune(nom)}. La carte est cadrée sur leurs lieux de "
           "travail ; l'interrupteur au-dessus montre toute la région.")
figure = (f'<figure style="margin:0;background:#FFFFFF;border:1px solid #E7EAE4;border-radius:16px;padding:18px 20px;'
          f'display:flex;flex-direction:column;gap:12px">{titre_carte}<figcaption style="font-size:15px;font-weight:600;'
          f'color:#4E5466">Où travaillent les employés et ouvriers qui habitent {nom} (commune encadrée)</figcaption>'
          f'<div class="cadre-carte"><img class="carte-zoomable" src="data:image/svg+xml;base64,{carte_svg(code, entiere)}" '
          f'alt="{html.escape(alt)}" style="width:100%;height:auto;display:block"></div>'
          f'<div style="display:flex;flex-wrap:wrap;gap:6px;font-size:14px;font-weight:600">{legende}</div>'
          f'<p style="margin:0;font-size:14px;line-height:1.5;color:#4E5466"><strong style="color:#1B1F2A">Lecture :</strong> '
          f'{lecture}</p></figure>')

top = dest.head(6)
echelle = max(30, top["part_pct"].max() if len(top) else 30)   # échelle de la maquette (30 %), élargie si besoin
lignes_top = "".join(
    f'<div style="display:grid;grid-template-columns:1fr 90px 52px;gap:10px;align-items:center;font-size:14px;'
    f'padding:3px 0"><span>{html.escape(t.nom_travail)}</span><div aria-hidden="true" style="height:10px;'
    f'background:#EEF0EC;border-radius:5px;overflow:hidden"><div style="height:10px;border-radius:5px;background:#E4572E;'
    f'width:{t.part_pct / echelle * 100:.1f}%"></div></div><span style="text-align:right;font-weight:700">'
    f'{pct(t.part_pct)}</span></div>' for t in top.itertuples())
principales = (f'<section aria-label="Principales communes de travail" style="background:#FFFFFF;border:1px solid #E7EAE4;'
               f'border-radius:16px;padding:16px 18px;display:flex;flex-direction:column;gap:6px">'
               f'<div style="font-size:14px;font-weight:700">Leurs principales communes de travail</div>{lignes_top}</section>')

lignes = [x for x in str(r["lignes"]).split(", ") if x and x != "nan"]
# Lignes en pictogrammes (planche validée) ; au-delà de 8 (Paris…), on écrit combien d'autres lignes s'arrêtent
if not r["gare"]:
    # Marqueur visuel (remarque de Melvyn, 11/11) : le « Non » seul passait inaperçu à côté des pictogrammes de ligne.
    # Pictogramme « train barré » de la charte (carré encre = un mode), comme aux pages 2 et 3, avec son texte.
    reponse_gare = (f'<div style="display:flex;align-items:center;gap:8px;margin-top:4px">{u.badge_mode("train_barre", 34)}'
                    f'<span style="font-weight:700;font-size:16px">Non, aucune gare</span></div>')
else:
    reste = len(lignes) - MAX_LIGNES_AFFICHEES
    reponse_gare = ('<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:4px">'
                    + "".join(u.picto_ligne(x) for x in lignes[:MAX_LIGNES_AFFICHEES])
                    + (f'<span style="align-self:center;font-weight:700;font-size:15px">et {reste} autres lignes</span>'
                       if reste > 0 else "") + '</div>')
gare = (f'<section aria-label="Desserte par le train" style="background:#FFFFFF;border:1px solid #E7EAE4;border-radius:16px;'
        f'padding:16px 18px;display:flex;flex-direction:column;gap:12px"><div style="font-size:14px;font-weight:700">'
        f'Une gare dans la commune ?</div><div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px">'
        f'<div style="background:#F2F3F0;border-radius:12px;padding:10px 12px"><div style="font-size:14px;color:#4E5466">'
        f'{nom}</div>{reponse_gare}</div>'
        f'<div style="background:#F2F3F0;border-radius:12px;padding:10px 12px"><div style="font-size:14px;color:#4E5466">'
        # Même marqueur que la case voisine (remarque de Melvyn, 11/11) : pictogramme « train barré » + valeur, et une
        # petite barre pour situer la part d'un coup d'œil (piste grise = 100 %)
        f'Ses communes de travail sans gare</div><div style="display:flex;align-items:center;gap:8px;margin-top:4px">'
        f'{u.badge_mode("train_barre", 34)}<span style="font-weight:700;font-size:16px">'
        f'{pct(r["part_emplois_sans_gare_pct"])} des emplois</span></div>'
        f'<div aria-hidden="true" style="height:8px;border-radius:4px;background:#E3E6E0;margin-top:8px">'
        f'<div style="height:8px;border-radius:4px;background:{u.ENCRE};'
        f'width:{min(100, r["part_emplois_sans_gare_pct"]):.0f}%"></div></div></div></div>'
        f'<div style="font-size:14px;color:#5E6475">Commune avec gare : au moins un arrêt de métro, RER, train ou tram '
        f'(offre IDFM 2025). Part des emplois des habitants situés dans une commune sans gare.</div></section>')

st.markdown(f'<div class="pile-mobile" style="display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,1fr);'
            f'gap:18px">{figure}'
            f'<div style="display:flex;flex-direction:column;gap:14px">{principales}{gare}</div></div>',
            unsafe_allow_html=True)

# Alternative accessible à la carte : toutes les communes colorées, avec leur part et la présence d'une gare
u.tableau(pd.DataFrame({
    "Commune de travail": dest["nom_travail"],
    "Part des employés et ouvriers (%)": [u.fr(p, 1) for p in dest["part_pct"]],
    "Gare dans la commune": ["Oui" if g else "Non" for g in dest["travail_avec_gare"]]}),
    "Voir les données de la carte")

u.navigation_bas(FICHIER)
u.sources("INSEE, recensement 2023, fichier détail des mobilités professionnelles ; IDFM, offre hebdomadaire 2025 et "
          "référentiel des arrêts ; IDFM, référentiel des lignes (couleurs des lignes, licence ODbL) ; contours des communes, geo.api.gouv.fr. Communes sans couleur : moins de 0,25 % des "
          "trajets.")
