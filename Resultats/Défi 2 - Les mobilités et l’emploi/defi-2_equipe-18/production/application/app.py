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

pages = [st.Page(fichier, title=titre, default=(i == 0)) for i, (fichier, titre, _, _) in enumerate(u.PAGES)]
st.navigation(pages, position="hidden").run()
