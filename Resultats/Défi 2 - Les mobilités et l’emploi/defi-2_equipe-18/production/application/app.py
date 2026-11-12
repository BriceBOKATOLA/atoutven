"""
app.py : point d'entrée de l'application « Le lieu de travail décide » (Hackaviz IDFM 2026, défi 2, équipe 18).

L'application est un récit en 8 pages, à lire dans l'ordre comme une ligne de métro :
accueil, 6 stations (une par question), conclusion.

st.navigation permet des titres avec accents dans le menu (les noms de fichiers, eux, n'en ont pas).
Le menu standard est caché (position="hidden") : il est redessiné par utils.menu() en ligne de métro.

Lancer :  streamlit run app.py
"""

import streamlit as st

import utils as u

# Configuration commune, avant tout autre appel Streamlit
st.set_page_config(page_title="Le lieu de travail décide", page_icon=":material/train:", layout="wide")

# Chemins absolus (u.DOSSIER / fichier) et non relatifs : Streamlit Cloud lance l'application depuis la racine du
# dépôt. Avec des chemins relatifs, les pages n'étaient pas reconnues (testé le 2026-11-12 en lançant un clone depuis
# la racine) : Streamlit les ouvrait sans passer par ce fichier, donc sans le titre ni la mise en page « wide »
# (marge intérieure de 16 px au lieu de 80 px).
pages = [st.Page(u.DOSSIER / fichier, title=titre, default=(i == 0))
         for i, (fichier, titre, _, _) in enumerate(u.PAGES)]
st.navigation(pages, position="hidden").run()
