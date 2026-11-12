"""
verifier_conformite.py : vérifie que chaque page de l'application contient les éléments de sa maquette validée
(plus les changements validés depuis, notés dans le journal des choix de l'équipe).

Pourquoi ce test : un test « la page s'exécute sans erreur » ne voit pas qu'une carte ou un bouton a disparu.
Le 11/11, la carte de l'Accueil et d'autres éléments validés ont ainsi disparu sans être signalés.
Ce test est lancé avant chaque commit qui touche l'application ; il complète la comparaison des captures.

Chaque élément attendu = un morceau de texte ou de code HTML qui doit apparaître dans la page rendue.
Les textes attendus sont COPIÉS DES MAQUETTES (maquettes_validees/) : on ne modifie jamais le test pour
qu'il colle à l'application, c'est l'application qui doit coller à la maquette.
Quand un élément change avec l'accord de l'équipe, on met à jour cette liste dans le même commit.

Lancer depuis le dossier application/ :
    python tests/verifier_conformite.py
Code de sortie 1 s'il manque au moins un élément.
"""

import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

APPLICATION = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APPLICATION))

# (description lisible, fragment à trouver dans la page rendue). Source : maquettes validées + changements validés.
ATTENDU = {
    "pages/accueil.py": [
        ("bande de couleur à gauche de la page", 'class="bande-page"'),
        ("titre validé", "Quand le lieu de travail"),
        ("carte à points (image d'origine de la maquette)", "Carte à points de l'Île-de-France"),
        ("légende de la carte (texte de la maquette)", "Chaque point = 200 employés ou ouvriers"),
        ("sources sous la carte (avec liens depuis le 12/11)", "contours des communes, <a "),
        ("quatre chiffres", "13 fois moins"),
        ("bouton principal plein « Commencer le voyage »", 'class="bouton-principal"'),
        ("lien « Aller directement à ma commune »", "Aller directement à ma commune"),
        ("phrase en bas du menu", "Chaque chapitre est une station"),
    ],
    "pages/p1_metiers.py": [
        ("bande de couleur à gauche de la page", 'class="bande-page"'),
        ("titre validé", "surtout pour les cadres"),
        ("trois silhouettes-jauges (description d'ensemble, 12/11)", "0 % des ouvriers"),
        ("panneau-chiffre", "Sans télétravail possible"),
        ("encadré « À retenir »", "À retenir"),
        ("encadré « Limite »", "Limite"),
    ],
    "pages/p2_gares.py": [
        ("bande de couleur à gauche de la page", 'class="bande-page"'),
        ("titre", "loin des gares"),
        ("panneau-chiffre", "Emplois sans gare"),
        ("barres par métier", "Part des emplois hors Paris situés dans une commune sans gare"),
        ("barres dessinées comme la maquette (rond du métier, fond gris clair)", "grid-template-columns:170px 1fr 80px"),
        ("graphique de flux de banlieue à banlieue (validé le 2026-11-11, remplace la carte)", "Où travaillent les actifs de banlieue"),
        # Tableaux par département retirés le 2026-11-11 (jugés trop techniques par Melvyn)
        ("ponctualité des lignes (travail de Maroua, validé le 2026-11-11)", "encore faut-il que le train soit"),
        ("étiquette allégée « Top 4 postes » (option A validée le 2026-11-12)", "Top 4 postes"),
    ],
    "pages/p3_voiture.py": [
        ("bande de couleur à gauche de la page", 'class="bande-page"'),
        ("titre nuancé (relecture du 2026-11-12 : 71 à 77 %, pas « tout le monde »)", "trajets sur 4"),
        ("panneau-chiffre", "Personnes concernées"),
        ("barres-pilules avec légende gare / sans gare (12/11)", "Le lieu de travail a une gare"),
        ("barres-pilules, axe 0 / 50 / 100 % (12/11)", "100 % en voiture"),
        ("bande « sans gare » gardée sur les barres-pilules (12/11)", "quel que soit le métier"),
        ("voiture selon la destination (à déplier)", "la voiture selon la destination"),
    ],
    "pages/p4_nuit.py": [
        ("bande de couleur à gauche de la page", 'class="bande-page"'),
        ("titre validé", "13 fois moins"),
        ("panneau-chiffre", "Travaillent la nuit"),
        ("offre de transport heure par heure (libellé validé le 2026-11-11)", "Offre de transport prévue chaque heure"),
        ("niveau moyen de 7h à 10h écrit sur le graphique (libellé corrigé le 2026-11-11)", "De 7h à 10h :"),
        ("courbe de la variante A validée le 2026-11-11 : zone de nuit nommée (« minuit » depuis le 2026-11-12)", "Nuit minuit-5h"),
        ("courbe de la variante A validée le 2026-11-11 : pastille du rapport", "fois moins</text>"),
        ("carte de la nuit par commune (image d'origine)", "Carte nocturne des communes"),
        ("carte de la nuit en 2 couleurs avec titre-message (changement validé le 2026-11-11)",
         "aucun bus ni train entre minuit et 5h"),
    ],
    "pages/p5_solutions.py": [
        ("bande de couleur à gauche de la page", 'class="bande-page"'),
        ("titre validé le 2026-11-11 (proposition p5, version 2)", "des navettes pour"),
        ("repères numérotés des cartes et classement (validés le 2026-11-11)", "rang de la commune dans le classement"),
        ("interrupteur vue cadrée / toute l'Île-de-France (validé le 2026-11-11)", "Voir toute l"),
        ("carte du potentiel vélo (image d'origine)", "part des trajets en voiture de moins de 5 km"),
        ("carte des emplois sans gare (texte de la maquette)", "communes sans gare comptent au moins 500"),
    ],
    "pages/p6_commune.py": [
        ("bande de couleur à gauche de la page", 'class="bande-page"'),
        ("titre", "Et chez"),
        ("champ de recherche d'une commune", "Rechercher une commune"),
        ("chiffres de la commune", "Restent dans la commune"),
        ("carte des lieux de travail de la commune", "Où travaillent les employés et ouvriers qui habitent"),
        ("principales communes de travail", "Leurs principales communes de travail"),
        ("lignes de la commune en pictogrammes (changement validé le 2026-11-11)", 'class="picto-ligne"'),
        ("phrase « Lecture » sous la carte (changement validé le 2026-11-11)", "Lecture :"),
        ("interrupteur carte entière (changement validé le 2026-11-11)", "Voir toute l"),   # libellé de widget : accents codés dans le rendu, on cherche le début
    ],
    "pages/conclusion.py": [
        # Conclusion validée le 2026-11-12 (canevas « schéma compact et chiffré ») : elle conclut au lieu de résumer
        ("bande de couleur à gauche de la page", 'class="bande-page"'),
        ("titre-message", "qui décide"),
        ("schéma en aiguillage", "Lieu de"),
        ("nuance du script 12 sur la branche « avec gare »", "communes avec gare"),
        ("actions pour IDFM", "Ce que ça change pour"),
        ("perspective sous chaque action", "Et ensuite :"),
        ("bouton vers la page commune", "Et votre commune ?"),
        ("bouton retour à l'accueil (maquette validée)", "Revenir à l"),
        ("méthode en une ligne", "15 hypothèses"),
    ],
}


def contenu_rendu(fichier: str) -> str:
    """Rend une page (sans navigateur) et renvoie tout son texte et son HTML, menu compris."""
    at = AppTest.from_file(str(APPLICATION / "app.py"), default_timeout=90)
    at.run()
    if not fichier.endswith("accueil.py"):
        at.switch_page(fichier).run()
    if at.exception:
        return "ERREUR D'EXÉCUTION : " + str(at.exception[0].value)
    morceaux = [m.value for m in at.markdown] + [str(c.value) for c in at.caption]
    morceaux += [e.label for e in at.expander]
    morceaux += [str(getattr(el, "proto", "")) for el in at.main] + [str(getattr(el, "proto", "")) for el in at.sidebar]
    return "\n".join(morceaux)


def main() -> None:
    """Vérifie chaque page et affiche, pour chacune, les éléments trouvés et manquants."""
    manquants_total = 0
    for fichier, attendus in ATTENDU.items():
        texte = contenu_rendu(fichier)
        manquants = [description for description, fragment in attendus if fragment not in texte]
        manquants_total += len(manquants)
        etat = "conforme" if not manquants else f"{len(manquants)} élément(s) manquant(s)"
        print(f"{fichier:24} {etat}")
        for description in manquants:
            print(f"    - manque : {description}")
    print(f"\nTotal : {manquants_total} élément(s) manquant(s)")
    sys.exit(1 if manquants_total else 0)


if __name__ == "__main__":
    main()
