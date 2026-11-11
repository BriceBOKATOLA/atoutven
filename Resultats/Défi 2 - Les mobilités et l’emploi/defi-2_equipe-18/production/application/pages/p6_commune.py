"""
p6_commune.py : station 6, « Chercher ma commune ».

En préparation : la recherche par commune demande un fichier de données par commune (lieux de travail
de ses habitants, présence d'une gare), à produire par un script de préparation.
"""

import streamlit as st

import utils as u

FICHIER = "pages/p6_commune.py"

u.appliquer_style()
u.menu(FICHIER)
u.entete(FICHIER, 'Et chez <span style="color:#1F6A8C">vous</span> ?',
         "Cherchez votre commune : où travaillent ses employés et ouvriers, et si leurs lieux de travail ont une gare.")
st.info("Page en préparation : recherche par commune.")
u.navigation_bas(FICHIER)
