"""
accueil.py : page d'accueil. Pose la question du défi 2 et le message central, en quatre chiffres.

Fond nuit, comme sur la maquette : on entre dans le récit comme on prend un train tôt le matin.
"""

import streamlit as st

import utils as u

FICHIER = "pages/accueil.py"

u.appliquer_style(nuit=True)
u.menu(FICHIER, nuit=True)

actifs = u.lire("parts_modales_par_gs.csv").set_index("GS")["effectif_pondere"]
h21 = u.lire("h21_emplois_sans_gare.csv").set_index("groupe")
dest = u.lire("destinations_par_gs_et_couronne.csv")
gc_ouvriers = dest[(dest["couronne"] == "Grande couronne") & (dest["GS"] == "Ouvriers")]["Grande couronne (autre commune)"].iloc[0]

# Formulations reprises des remarques de l'équipe (11/11) : titre = le résultat central ; « par nécessité » retiré,
# car la donnée montre l'usage de la voiture, pas la contrainte.
message = ("En Île-de-France, de nombreux employés et ouvriers travaillent dans des communes éloignées du réseau "
           "ferroviaire. Pour rejoindre leur lieu de travail, notamment de banlieue à banlieue, la voiture s'impose "
           "souvent. L'enjeu n'est pas tant le métier exercé que l'accessibilité du lieu d'emploi.")
st.markdown('<div class="surtitre" style="color:#F28B6B">Mobilités et emploi en Île-de-France</div>',
            unsafe_allow_html=True)
u.bouton_ecouter("Quand le lieu de travail impose la voiture. " + message, nuit=True)
st.markdown(f'<h1 class="titre" style="font-size:46px;color:#F1F2F6">Quand le lieu de travail <span style="color:#F28B6B">'
            f'impose la voiture</span></h1><p class="description" style="max-width:760px">{message}</p>',
            unsafe_allow_html=True)

# « 13 fois moins » plutôt que « 7,6 % » : même chiffre (7,6 % = environ 1 sur 13), mais compris sans explication
fois_moins_nuit = round(100 / u.part_nuit_pct())
chiffres = [
    (f"{(actifs['Employé'] + actifs['Ouvrier']) / 1e6:.0f} millions",
     "d'actifs ne peuvent presque pas télétravailler (employés et ouvriers)", "#E4572E"),
    (u.fr(round(h21.loc['Employés et ouvriers', 'emplois_sans_gare'], -3)),
     "ouvriers et employés travaillent dans une commune sans gare", "#B23A86"),
    (f"{gc_ouvriers:.0f} %", "des ouvriers de grande couronne travaillent dans une autre commune de banlieue", "#B23A86"),
    (f"{fois_moins_nuit} fois moins", "de bus et de trains la nuit qu'à l'heure de pointe du matin", "#F1F2F6"),
]
st.markdown('<div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;max-width:760px;margin:22px 0">'
            + "".join(f'<div style="position:relative;background:#1B2238;border:1px solid #262E48;border-radius:16px;'
                      f'padding:12px 16px 12px 22px"><span aria-hidden="true" style="position:absolute;left:0;top:12px;'
                      f'bottom:12px;width:5px;border-radius:0 3px 3px 0;background:{c}"></span>'
                      f'<div style="font-family:Poppins,sans-serif;font-weight:800;font-size:28px;color:#F1F2F6">{v}</div>'
                      f'<div style="font-size:14px;color:#C9CDD8">{t}</div></div>' for v, t, c in chiffres)
            + '</div>', unsafe_allow_html=True)

st.page_link("pages/p1_metiers.py", label="Commencer le voyage →", icon=":material/train:")
st.page_link("pages/p6_commune.py", label="Aller directement à ma commune", icon=":material/search:")
u.sources("INSEE, recensement 2023 ; IDFM, offre hebdomadaire 2025 ; geo.api.gouv.fr."
)
