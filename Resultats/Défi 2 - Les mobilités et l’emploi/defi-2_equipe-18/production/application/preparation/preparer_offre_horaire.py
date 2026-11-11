"""
preparer_offre_horaire.py : passages prévus heure par heure sur tout le réseau d'Île-de-France,
pour la page « Les trajets de nuit » de l'application.

Même méthode que le script 05 du projet (src/05_tester_h4b_h10_offre.py) :
- jour de semaine = moyenne du mardi, du mercredi et du jeudi (on écarte le lundi et le vendredi,
  touchés par le télétravail, et les nuits du vendredi et du samedi, où le métro ferme plus tard) ;
- tranches horaires d'IDFM : la journée va de 4h à 3h59, donc minuit-1h = tranche 24, 1h-2h = 25, etc.

Entrée  : data/brut/idfm_offre_hebdo_2025/offre_hebdomadaire_moyenne_hors_vacances.csv (environ 300 Mo)
Sortie  : application/donnees/offre_par_heure.csv (24 lignes, quelques Ko)

Lancer depuis le dossier application/ : python preparation/preparer_offre_horaire.py
"""

import sys
from pathlib import Path

import pandas as pd

# Données brutes du projet : production/data/brut (deux niveaux au-dessus de ce fichier)
BRUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "data" / "brut"
SORTIE = Path(__file__).resolve().parents[1] / "donnees" / "offre_par_heure.csv"

JOURS_SEMAINE = ["nb_courses_mardi", "nb_courses_mercredi", "nb_courses_jeudi"]
JOUR_DIMANCHE = "nb_courses_dimanche"


def main() -> None:
    """Additionne les passages de tous les arrêts, par tranche horaire, et enregistre le petit fichier résultat."""
    offre = pd.read_csv(BRUT / "idfm_offre_hebdo_2025" / "offre_hebdomadaire_moyenne_hors_vacances.csv",
                        sep=";", encoding="utf-8-sig", usecols=["tranche_horaire"] + JOURS_SEMAINE + [JOUR_DIMANCHE])
    par_tranche = offre.groupby("tranche_horaire").sum()
    resultat = pd.DataFrame({
        "tranche_horaire": par_tranche.index,
        "heure": par_tranche.index % 24,                         # tranche 25 = 1h du matin
        "passages_semaine": par_tranche[JOURS_SEMAINE].mean(axis=1).round(0),
        "passages_dimanche": par_tranche[JOUR_DIMANCHE].round(0),
    })
    SORTIE.parent.mkdir(exist_ok=True)
    resultat.to_csv(SORTIE, index=False, encoding="utf-8-sig")

    nuit = resultat[resultat["tranche_horaire"].isin([24, 25, 26, 27, 4])]["passages_semaine"].mean()
    pointe = resultat[resultat["tranche_horaire"].isin([7, 8, 9])]["passages_semaine"].mean()
    print(f"{len(resultat)} tranches ; nuit {nuit:,.0f} passages/h ; pointe {pointe:,.0f} passages/h ; "
          f"rapport {100 * nuit / pointe:.1f} %".replace(",", " "))
    print(f"dimanche / semaine : {100 * resultat['passages_dimanche'].sum() / resultat['passages_semaine'].sum():.1f} %")


if __name__ == "__main__":
    main()
