"""
utils.py : tout ce qui est commun aux pages de l'application « Le lieu de travail décide ».
(Nom provisoire, choisi le 11/11 pour remplacer « Sur place, loin du réseau » : « sur place » était du jargon.)

- la charte (couleurs, polices) et le style CSS appliqué à chaque page ;
- les composants réutilisés : en-tête de page, panneau-chiffre, encadrés « À retenir » et « Limite »,
  bouton d'écoute, menu en forme de ligne de métro, boutons de navigation, sources ;
- la lecture des fichiers de résultats (dossier donnees/), mise en cache.

Choix d'accessibilité (RGAA), valables sur toutes les pages :
- textes de 14 px minimum, contrastes calculés (voir les commentaires des couleurs) ;
- jamais d'information portée par la couleur seule : chaque couleur est accompagnée d'un mot ou d'une forme ;
- sous chaque graphique, une phrase qui dit ce qu'il montre et un tableau des chiffres ;
- un bouton « Écouter » qui lit le titre, la description et le « À retenir » (synthèse vocale du navigateur,
  sans service extérieur ni propriétaire).
"""

import html
import json
from pathlib import Path

import pandas as pd
import streamlit as st

DOSSIER = Path(__file__).parent
DONNEES = DOSSIER / "donnees"

# ---------------------------------------------------------------------------
# Charte : couleurs (contrastes vérifiés par calcul, voir charte.md du projet)
# ---------------------------------------------------------------------------

ENCRE = "#1B1F2A"            # texte principal (15:1 sur le fond)
ENCRE_SECONDAIRE = "#4E5466"  # descriptions (7:1)
GRIS_TEXTE = "#5E6475"       # légendes et sources (5,5:1)
FOND = "#F6F7F4"
FOND_NUIT = "#141A2E"
CARTE_NUIT = "#1B2238"

# Une couleur fixe par métier, jamais par rang : elle ne change pas quand un filtre change.
# « donnee » sert aux barres et aux points ; « texte » est une version plus foncée, lisible en texte.
METIERS = {
    "Cadres": {"donnee": "#3A8FB7", "texte": "#1F6A8C", "pale": "#E5EFF5"},
    "Employés": {"donnee": "#E4572E", "texte": "#C0401A", "pale": "#FCEDE8"},
    "Ouvriers": {"donnee": "#B23A86", "texte": "#B23A86", "pale": "#F7E8F1"},
}

# Pages du récit : (fichier, titre court du menu, numéro de station, question complète)
PAGES = [
    ("pages/accueil.py", "Accueil", "", ""),
    ("pages/p1_metiers.py", "Ceux qui ne télétravaillent pas", "1", "Qui ne peut pas télétravailler ?"),
    ("pages/p2_gares.py", "Loin des gares", "2", "Où sont leurs emplois ?"),
    ("pages/p3_voiture.py", "Comment ils vont travailler", "3", "Comment vont-ils travailler ?"),
    ("pages/p4_nuit.py", "Les trajets de nuit", "4", "Que reste-t-il du réseau la nuit ?"),
    ("pages/p5_solutions.py", "Les solutions", "5", "Quelles solutions, et où en priorité ?"),
    ("pages/p6_commune.py", "Chercher ma commune", "6", "Chercher ma commune"),
    ("pages/conclusion.py", "Conclusion", "", ""),
]

# Pictogrammes : traits blancs sur carré arrondi encre = un mode ou un lieu ;
# les ronds de couleur sont réservés aux métiers. Toujours accompagnés de leur texte.
_SVG = '<svg width="{t}" height="{t}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" ' \
       'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{d}</svg>'
ICONES = {
    "train": '<rect x="5" y="3" width="14" height="13" rx="3"/><path d="M5 10h14"/><path d="M9 20l-2 2"/><path d="M15 20l2 2"/>',
    "train_barre": '<rect x="5" y="3" width="14" height="13" rx="3"/><path d="M5 10h14"/><path d="M9 20l-2 2"/>'
                   '<path d="M15 20l2 2"/><path d="M2 2l20 20"/>',
    "voiture": '<path d="M5 17h14v-5l-2-5H7l-2 5z"/><path d="M5 12h14"/><circle cx="8" cy="17" r="2"/><circle cx="16" cy="17" r="2"/>',
    "velo": '<circle cx="6" cy="16" r="3.5"/><circle cx="18" cy="16" r="3.5"/><path d="M6 16l4-7h6l2 7"/>'
            '<path d="M10 9L8.5 6H7"/><path d="M14 6h2.5"/>',
    "navette": '<rect x="4" y="4" width="16" height="13" rx="2"/><path d="M4 11h16"/><circle cx="8" cy="20" r="1.5"/>'
               '<circle cx="16" cy="20" r="1.5"/>',
    "lune": '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>',
    "maison": '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/>',
    "emploi": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"/>',
    "personnes": '<circle cx="9" cy="7" r="4"/><path d="M2 21v-2a5 5 0 0 1 5-5h4a5 5 0 0 1 5 5v2"/>'
                 '<path d="M16 3.5a4 4 0 0 1 0 7"/><path d="M22 21v-2a5 5 0 0 0-4-4.8"/>',
    "repere": '<path d="M12 21s-7-6.2-7-12a7 7 0 0 1 14 0c0 5.8-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/>',
    "drapeau": '<path d="M4 21V4"/><path d="M4 4h12l-2 4 2 4H4"/>',
    "ampoule": '<path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.3 1 2.3h6c0-1 '
               '.4-1.8 1-2.3A7 7 0 0 0 12 2z"/>',
    "info": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
    "loupe": '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>',
}


def icone(nom: str, taille: int = 18, couleur: str = "#FFFFFF") -> str:
    """Renvoie le SVG d'un pictogramme (décoratif : aria-hidden, le sens est porté par le texte voisin)."""
    return _SVG.format(t=taille, c=couleur, d=ICONES[nom])


def badge_mode(nom: str, taille: int = 32, nuit: bool = False) -> str:
    """Pictogramme de mode ou de lieu : carré arrondi encre (inversé sur fond nuit)."""
    fond, trait = ("#F1F2F6", FOND_NUIT) if nuit else (ENCRE, "#FFFFFF")
    return (f'<span aria-hidden="true" style="width:{taille}px;height:{taille}px;border-radius:{taille // 3.5:.0f}px;'
            f'background:{fond};display:inline-flex;align-items:center;justify-content:center;flex-shrink:0">'
            f'{icone(nom, int(taille * 0.56), trait)}</span>')


# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------

def appliquer_style(nuit: bool = False) -> None:
    """Injecte les polices et le style commun. nuit=True : fond bleu nuit pour la page des trajets de nuit.

    On cible les éléments de texte, jamais un sélecteur large du type [class*="st-"] : sinon la police
    des icônes de Streamlit est écrasée et leur nom s'affiche en toutes lettres.
    """
    fond = FOND_NUIT if nuit else FOND
    encre = "#F1F2F6" if nuit else ENCRE
    secondaire = "#C9CDD8" if nuit else ENCRE_SECONDAIRE
    carte = CARTE_NUIT if nuit else "#FFFFFF"
    bord = "#2E3756" if nuit else "#E7EAE4"
    st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Barlow+Semi+Condensed:wght@600&display=swap');
.stApp {{ background: {fond}; }}
.stApp p, .stApp li, .stApp label, .stApp td, .stApp th, [data-testid="stMarkdownContainer"] {{
  font-family: 'Plus Jakarta Sans', sans-serif; color: {encre}; font-size: 16px; }}
[data-testid="stIconMaterial"] {{ font-family: 'Material Symbols Rounded' !important; }}
.block-container {{ max-width: 1100px; padding-top: 2.2rem; }}
h1.titre {{ font-family: 'Poppins', sans-serif; font-weight: 800; font-size: 38px; line-height: 1.15;
  color: {encre}; margin: 4px 0 8px; padding: 0; }}
h2.sous-titre {{ font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; font-size: 18px; color: {encre};
  margin: 0 0 10px; padding: 0; }}
.surtitre {{ display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 15px; color: {secondaire}; }}
.description {{ font-size: 17px !important; line-height: 1.55; color: {secondaire} !important; margin: 0; }}
.carte {{ background: {carte}; border: 1px solid {bord}; border-radius: 16px; padding: 20px 24px; margin-bottom: 14px; }}
.panneau {{ background: {carte}; border: 1px solid {bord}; border-radius: 16px; overflow: hidden; }}
.chiffre {{ font-family: 'Barlow Semi Condensed', sans-serif; font-weight: 600; line-height: 1.05; }}
.encadre {{ border-radius: 14px; padding: 14px 18px; font-size: 15px; line-height: 1.5; height: 100%; }}
.source {{ font-size: 14px !important; color: {"#9AA0B2" if nuit else GRIS_TEXTE} !important; margin-top: 18px; }}
a:focus-visible, button:focus-visible, summary:focus-visible {{ outline: 3px solid #1F6A8C; outline-offset: 3px; }}
[data-testid="stSidebar"] {{ background: {"#0E1324" if nuit else "#ECEEE9"}; }}
[data-testid="stSidebar"] [data-testid="stPageLink"] a {{ min-height: 40px; border-radius: 999px; }}
[data-testid="stSidebar"] [data-testid="stPageLink"] p {{ font-size: 15px; color: {encre}; white-space: normal;
  overflow: visible; text-overflow: clip; line-height: 1.3; }}
[data-testid="stPageLink"] [data-testid="stIconMaterial"] {{ color: {encre}; }}
/* Liens de la page principale : en forme de bouton (cible de 44 px, lisible comme une action) */
[data-testid="stMain"] [data-testid="stPageLink"] a {{ border: 2px solid {encre}; border-radius: 999px;
  padding: 6px 18px; min-height: 44px; display: inline-flex; width: auto; }}
[data-testid="stMain"] [data-testid="stPageLink"] p {{ font-weight: 700; white-space: normal; }}
[data-testid="stExpander"] summary p {{ font-weight: 700; font-size: 16px; }}
/* Blocs à déplier : bordure et flèche visibles aussi sur fond nuit (on doit voir que c'est cliquable) */
[data-testid="stExpander"] details {{ border: 1px solid {"#5A6386" if nuit else bord} !important; border-radius: 12px; background: {carte}; }}
[data-testid="stExpander"] summary [data-testid="stIconMaterial"] {{ color: {encre}; }}
/* Espacement régulier entre les blocs, comme sur les maquettes (22 px) */
[data-testid="stMain"] [data-testid="stVerticalBlock"] {{ gap: 22px; }}
.description {{ margin-bottom: 4px !important; }}
.carte {{ margin-bottom: 0; }}
/* Conteneurs-cartes : st.container(border=True, key="carte_...") prend l'allure d'une carte blanche */
[class*="st-key-carte"] {{ background: {carte}; border: 1px solid {bord} !important; border-radius: 16px !important;
  padding: 20px 24px !important; }}
[class*="st-key-carte"] [data-testid="stVerticalBlock"] {{ gap: 10px; }}
[data-testid="stSidebar"] nav a:hover span:last-child {{ text-decoration: underline; }}
/* --- Accessibilité au clavier (constats du test au clavier du 2026-11-11) --- */
/* Contour bien visible sur tout élément qui reçoit le focus, y compris les liens-boutons de Streamlit */
a:focus-visible, button:focus-visible, summary:focus-visible, [data-testid="stPageLink"] a:focus-visible {{
  outline: 3px solid {"#8FC3DE" if nuit else "#1F6A8C"} !important; outline-offset: 3px !important; }}
/* Barre d'outils des graphiques (boutons anglais « Show data », « Download as PNG »…) : retirée.
   Le tableau des chiffres en français la remplace ; display:none la sort aussi de l'ordre de tabulation. */
[data-testid="stElementToolbar"] {{ display: none !important; }}
/* Liens d'ancre « Link to heading » ajoutés par Streamlit sur les titres : arrêts inutiles au clavier */
[data-testid="stHeaderActionElements"] {{ display: none !important; }}
/* Téléphone : les grilles de 2, 3 ou 5 colonnes passent en une seule colonne, et le trait du plan de ligne
   (dessin horizontal) est masqué. À 720 px (écran de 1440 px zoomé à 200 %), la mise en page reste lisible
   telle quelle (vérifié sur capture). Le sélecteur cherche « repeat(n » sans les deux-points, car le navigateur
   réécrit les styles avec des espaces. */
@media (max-width: 600px) {{
  [style*="repeat(2"], [style*="repeat(3"], [style*="repeat(5"] {{ grid-template-columns: 1fr !important; }}
  .trait-ligne {{ display: none !important; }}
  h1.titre {{ font-size: 30px; }}
}}
</style>""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Composants
# ---------------------------------------------------------------------------

def menu(fichier_courant: str, nuit: bool = False) -> None:
    """Menu latéral en forme de ligne de métro : une station par chapitre, la station courante signalée.

    st.page_link donne de vrais liens, utilisables au clavier et annoncés par les lecteurs d'écran.
    """
    with st.sidebar:
        st.markdown(f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:18px">'
                    f'{badge_mode("train", 42, nuit)}<div><div style="font-family:Poppins,sans-serif;font-weight:800;'
                    f'font-size:16px;color:{"#F1F2F6" if nuit else ENCRE}">Le lieu de travail décide</div>'
                    f'<div style="font-size:14px;color:{"#9AA0B2" if nuit else GRIS_TEXTE}">Hackaviz IDFM 2026 · Défi 2</div>'
                    f'</div></div>', unsafe_allow_html=True)
        st.markdown(_ligne_de_metro(fichier_courant, nuit), unsafe_allow_html=True)


def _ligne_de_metro(fichier_courant: str, nuit: bool) -> str:
    """Dessine la ligne du menu : un trait vertical continu qui relie les stations, comme sur un plan de ligne.

    Chaque station est un vrai lien <a> (atteignable avec Tab, annoncé par les lecteurs d'écran) ;
    la station courante porte aria-current="page" et une pastille pleine. Le trait et les pastilles sont
    décoratifs (aria-hidden) : le nom de la station suffit à comprendre.
    Adresse de chaque page : nom du fichier sans extension (règle de st.Page), « / » pour l'accueil.
    """
    encre = "#F1F2F6" if nuit else ENCRE
    fond_menu = "#0E1324" if nuit else "#ECEEE9"
    fond_courant = "#1E2640" if nuit else "#FFFFFF"
    stations = []
    for i, (fichier, titre, numero, _) in enumerate(PAGES):
        courant = fichier == fichier_courant
        adresse = "/" if i == 0 else "/" + Path(fichier).stem
        pastille = (f"width:30px;height:30px;background:#C0401A;border:3px solid {encre};color:#FFFFFF;font-size:14px"
                    if courant else
                    f"width:26px;height:26px;background:{fond_menu};border:3px solid {encre};color:{encre};font-size:12px")
        stations.append(
            f'<a href="{adresse}" target="_self" {"aria-current=\"page\"" if courant else ""} style="display:flex;'
            f'align-items:center;gap:12px;text-decoration:none;color:{encre};min-height:36px;position:relative;'
            f'{f"background:{fond_courant};border-radius:999px;margin-left:-6px;padding:3px 14px 3px 6px;" if courant else ""}">'
            f'<span aria-hidden="true" style="{pastille};border-radius:50%;box-sizing:border-box;flex-shrink:0;'
            f'display:flex;align-items:center;justify-content:center;font-weight:700">{numero}</span>'
            f'<span style="font-size:15px;line-height:1.3;font-weight:{700 if courant else 500}">{titre}</span></a>')
    return (f'<nav aria-label="Chapitres du récit" style="position:relative;display:flex;flex-direction:column;'
            f'gap:14px;padding-left:4px"><div aria-hidden="true" style="position:absolute;left:15px;top:14px;'
            f'bottom:14px;width:4px;background:{encre};border-radius:2px"></div>' + "".join(stations) + '</nav>')


def bouton_ecouter(texte: str, nuit: bool = False) -> None:
    """Bouton « Écouter cette page » : lit le texte avec la synthèse vocale du navigateur (Web Speech API).

    Aucun service extérieur : la voix est celle de l'ordinateur du visiteur. Un second clic arrête la lecture.
    """
    couleur, fond = ("#F1F2F6", "#1E2640") if nuit else (ENCRE, "#FFFFFF")
    # st.iframe exécute notre propre HTML (jamais un contenu venu de l'extérieur) : le script de lecture y fonctionne
    st.iframe(f"""
<style>button:focus-visible {{ outline: 3px solid {"#8FC3DE" if nuit else "#1F6A8C"}; outline-offset: 3px; }}
body {{ margin: 0; padding: 4px; }}</style>
<button id="b" type="button" aria-pressed="false" style="display:inline-flex;align-items:center;gap:6px;
 min-height:44px;padding:8px 16px;border:2px solid {couleur};border-radius:999px;background:{fond};color:{couleur};
 font:700 15px 'Plus Jakarta Sans',sans-serif;cursor:pointer">
 <svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
 stroke-linecap="round" stroke-linejoin="round"><path d="M11 5L6 9H2v6h4l5 4z"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/>
 <path d="M19 5a10 10 0 0 1 0 14"/></svg><span id="t">Écouter cette page</span></button>
<script>
// Langue de la page : Streamlit déclare « en » ; un lecteur d'écran lirait alors le français avec une voix anglaise.
// Ce cadre est sur le même domaine que l'application : il peut corriger la page qui l'accueille.
try {{
  const d = window.parent.document;
  d.documentElement.lang = 'fr';
  const traduire = () => d.querySelectorAll('a').forEach(a => {{
    if (a.textContent.trim() === 'Skip to main content') a.textContent = 'Aller au contenu';
  }});
  traduire(); setTimeout(traduire, 1500);   // le lien d'évitement peut être dessiné après ce script
}} catch (e) {{}}
const texte = {json.dumps(texte)};
const b = document.getElementById('b'), t = document.getElementById('t');
b.onclick = () => {{
  const s = window.speechSynthesis;
  if (s.speaking) {{ s.cancel(); t.textContent = 'Écouter cette page'; b.setAttribute('aria-pressed','false'); return; }}
  const u = new SpeechSynthesisUtterance(texte); u.lang = 'fr-FR'; u.rate = 0.95;
  u.onend = () => {{ t.textContent = 'Écouter cette page'; b.setAttribute('aria-pressed','false'); }};
  s.speak(u); t.textContent = 'Arrêter la lecture'; b.setAttribute('aria-pressed','true');
}};
</script>""", height=52, alt="Bouton pour écouter la page à voix haute")


def entete(fichier: str, titre_html: str, description: str, a_lire_en_plus: str = "",
           panneau_html: str = "", nuit: bool = False) -> None:
    """En-tête de page : station et question, bouton d'écoute, titre (la réponse), description, panneau-chiffre.

    Le texte lu à voix haute = question + titre + description + a_lire_en_plus (le « À retenir »).
    """
    _, titre_court, numero, question = next(p for p in PAGES if p[0] == fichier)
    surtitre = f"{numero} / 6 · {question}" if numero else titre_court
    gauche, droite = st.columns([1.9, 1]) if panneau_html else (st.container(), None)
    with gauche:
        st.markdown(f'<div class="surtitre">{surtitre}</div>', unsafe_allow_html=True)
        titre_texte = html.unescape(_sans_balises(titre_html))
        bouton_ecouter(". ".join(x for x in (question, titre_texte, description, a_lire_en_plus) if x), nuit)
        st.markdown(f'<h1 class="titre">{titre_html}</h1><p class="description">{description}</p>',
                    unsafe_allow_html=True)
    if droite is not None:
        with droite:
            st.markdown(panneau_html, unsafe_allow_html=True)


def _sans_balises(texte: str) -> str:
    """Retire les balises HTML d'un titre, pour la lecture à voix haute."""
    import re
    return re.sub(r"<[^>]+>", "", texte)


def panneau(libelle: str, valeur: str, detail: str, couleur_bande: str, couleur_valeur: str,
            icone_nom: str = "", nuit: bool = False) -> str:
    """Panneau-chiffre en haut à droite : un seul chiffre, jamais répété dans le graphique de la page."""
    pic = badge_mode(icone_nom, 24, nuit) if icone_nom else ""
    secondaire = "#C9CDD8" if nuit else GRIS_TEXTE
    return (f'<div class="panneau"><div style="height:6px;background:{couleur_bande}"></div>'
            f'<div style="padding:12px 20px 14px"><div style="display:flex;align-items:center;gap:8px;font-size:14px;'
            f'font-weight:600;color:{secondaire}">{pic}{libelle}</div>'
            f'<div class="chiffre" style="font-size:52px;color:{couleur_valeur}">{valeur}</div>'
            f'<div style="font-size:14px;line-height:1.4;color:{secondaire}">{detail}</div></div></div>')


def encadres(retenir: str, limite: str, couleur: str = "#C0401A", fond: str = "#FCEDE8", nuit: bool = False) -> None:
    """Encadrés « À retenir » (le message) et « Limite » (ce que la donnée ne dit pas), côte à côte."""
    g, d = st.columns([1.25, 1])
    fond_limite, titre_limite = ("#1E2640", "#F1F2F6") if nuit else ("#EDEFEA", "#3F4555")
    with g:
        st.markdown(f'<div class="encadre" style="background:{fond}"><div style="display:flex;align-items:center;gap:8px;'
                    f'font-weight:700;color:{couleur};margin-bottom:4px">{icone("ampoule", 18, couleur)}À retenir</div>'
                    f'{retenir}</div>', unsafe_allow_html=True)
    with d:
        st.markdown(f'<div class="encadre" style="background:{fond_limite}"><div style="display:flex;align-items:center;'
                    f'gap:8px;font-weight:700;color:{titre_limite};margin-bottom:4px">{icone("info", 18, titre_limite)}'
                    f'Limite</div>{limite}</div>', unsafe_allow_html=True)


def navigation_bas(fichier: str) -> None:
    """Boutons « précédente » et « station suivante » en bas de page (vrais liens, utilisables au clavier)."""
    i = next(k for k, p in enumerate(PAGES) if p[0] == fichier)
    st.write("")
    g, _, d = st.columns([1, 0.4, 1])
    if i > 0:
        with g:
            st.page_link(PAGES[i - 1][0], label=f"← {PAGES[i - 1][1]}")
    if i < len(PAGES) - 1:
        with d:
            st.page_link(PAGES[i + 1][0], label=f"Station suivante : {PAGES[i + 1][1]} →")


def sources(texte: str) -> None:
    """Ligne des sources en bas de page."""
    st.markdown(f'<p class="source">Sources : {texte}</p>', unsafe_allow_html=True)


def tableau(df: pd.DataFrame, titre: str = "Voir les données du graphique") -> None:
    """Alternative accessible à un graphique : le tableau des chiffres, dans un bloc à déplier."""
    with st.expander(titre):
        st.dataframe(df, hide_index=True, width="stretch")


@st.cache_data
def lire(nom: str) -> pd.DataFrame:
    """Lit un fichier de résultats du dossier donnees/ (une seule lecture, partagée par toutes les pages)."""
    return pd.read_csv(DONNEES / nom, encoding="utf-8-sig")


def part_nuit_pct() -> float:
    """Passages prévus de minuit à 5h, en % de ceux de 7h à 10h (jour de semaine) : un seul calcul pour toutes les pages."""
    offre = lire("offre_par_heure.csv")
    nuit = offre[offre["tranche_horaire"].isin([24, 25, 26, 27, 4])]["passages_semaine"].mean()
    pointe = offre[offre["tranche_horaire"].isin([7, 8, 9])]["passages_semaine"].mean()
    return 100 * nuit / pointe


def fr(nombre: float, decimales: int = 0) -> str:
    """Nombre au format français : espace pour les milliers, virgule décimale (12 345,6)."""
    texte = f"{nombre:,.{decimales}f}".replace(",", " ").replace(".", ",")
    return texte.replace(" ", " ")   # espace fine insécable : le nombre ne se coupe pas en fin de ligne
