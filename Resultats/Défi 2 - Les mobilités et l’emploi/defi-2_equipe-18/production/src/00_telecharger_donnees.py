"""
00_telecharger_donnees.py : télécharge toutes les données brutes du projet
depuis leurs sources officielles (INSEE, Île-de-France Mobilités, État).

Pourquoi un script : les données brutes (plus de 600 Mo) ne sont pas
publiées dans le dépôt. Ce script permet à n'importe qui de les récupérer
exactement comme nous, puis de relancer les scripts 01 à 08.
L'inventaire détaillé (licences, millésimes, dates) est dans data/README.md.

Seuls les fichiers réellement lus par les scripts sont téléchargés.

Lancer depuis le dossier production/ :
    python src/00_telecharger_donnees.py                  # tout
    python src/00_telecharger_donnees.py --seulement calendrier geo_communes_idf
    python src/00_telecharger_donnees.py --forcer         # retélécharge même si le fichier existe

Bibliothèque standard uniquement (urllib) : aucune installation nécessaire.
"""

import argparse
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
BRUT = RACINE / "data" / "brut"

INSEE_2023 = "https://www.insee.fr/fr/statistiques/fichier/9004795"   # recensement 2023, publié le 25/06/2026
INSEE_2022 = "https://www.insee.fr/fr/statistiques/fichier/8589904"   # recensement 2022, pour comparaison (script 01)
FILOSOFI = "https://www.insee.fr/fr/statistiques/fichier/8984752"     # revenus par commune 2023, publiés le 06/08/2026
IDFM = "https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets"
EDUCATION = "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets"
GEO = "https://geo.api.gouv.fr/communes"

# Trimestres de validations : les 4 plus récents publiés par IDFM (juillet 2025 à juin 2026)
TRIMESTRES = {"3eme-trimestre": "2025T3", "4eme-trimestre": "2025T4",
              "1er-trimestre": "2026T1", "2eme-trimestre": "2026T2"}


def url(base: str, **parametres) -> str:
    """Construit une adresse avec ses paramètres encodés (espaces, guillemets, point-virgule)."""
    return base + ("?" + urllib.parse.urlencode(parametres) if parametres else "")


# Une ligne par fichier : (dossier, nom du fichier, adresse, ce qu'il contient)
SOURCES = [
    ("insee_mobpro_2023", "RP2023_mobpro.parquet", f"{INSEE_2023}/RP2023_mobpro.parquet",
     "Déplacements domicile-travail, une ligne par individu (recensement 2023)"),
    ("insee_mobpro_2023", "varmod_mobpro_2023.csv", f"{INSEE_2023}/varmod_mobpro_2023.csv",
     "Dictionnaire des variables et de leurs modalités"),
    ("insee_mobpro_2023", "contenu_RP2023_mobpro.pdf", f"{INSEE_2023}/contenu_RP2023_mobpro.pdf",
     "Documentation INSEE du fichier"),
    ("insee_mobpro_2022", "RP2022_mobpro.parquet", f"{INSEE_2022}/RP2022_mobpro.parquet",
     "Recensement 2022, pour comparer les millésimes (script 01)"),
    ("insee_mobpro_2022", "varmod_mobpro_2022.csv", f"{INSEE_2022}/varmod_mobpro_2022.csv",
     "Dictionnaire 2022"),
    ("insee_filosofi_2023", "FILOSOFI_CC_csv.zip", f"{FILOSOFI}/FILOSOFI_CC_csv.zip",
     "Revenus et pauvreté par commune en 2023 (niveau de vie médian, script 09) ; archive décompressée sur place"),
    ("idfm_offre_hebdo_2025", "offre_hebdomadaire_moyenne_hors_vacances.csv",
     url(f"{IDFM}/offre_hebdomadaire_moyenne_hors_vacances/exports/csv", delimiter=";"),
     "Passages prévus par arrêt, ligne, heure et jour, semaine type 2025 hors vacances (environ 300 Mo)"),
    ("idfm_referentiel_arrets", "zones-de-correspondance.csv",
     url(f"{IDFM}/zones-de-correspondance/exports/csv", delimiter=";"),
     "Référentiel des gares et stations, avec leur code commune"),
] + [
    ("idfm_validations_ferre", f"validations_ferre_jour_{nom}.csv",
     url(f"{IDFM}/validations-reseau-ferre-nombre-validations-par-jour-{identifiant}/exports/csv", delimiter=";"),
     f"Validations par jour et par gare, réseau ferré, {nom}")
    for identifiant, nom in TRIMESTRES.items()
] + [
    ("calendrier", "jours_feries_metropole.json", "https://calendrier.api.gouv.fr/jours-feries/metropole.json",
     "Jours fériés en métropole"),
    ("calendrier", "vacances_scolaires_zone_c.csv",
     url(f"{EDUCATION}/fr-en-calendrier-scolaire/exports/csv", delimiter=";", refine="zones:Zone C",
         where='annee_scolaire in ("2024-2025","2025-2026")'),
     "Vacances scolaires de la zone C (Île-de-France), années 2024-2025 et 2025-2026"),
    ("geo_communes_idf", "communes_idf_centres.json",
     url(GEO, codeRegion="11", fields="code,nom,centre,codeDepartement,population", format="json"),
     "Centre et population des 1 266 communes d'Île-de-France"),
    ("geo_communes_idf", "communes_idf_contours.geojson",
     url(GEO, codeRegion="11", format="geojson", geometry="contour", fields="code,nom"),
     "Contours des communes d'Île-de-France (cartes)"),
    # France Travail, enquête Besoins en main-d'œuvre 2026 (Licence Ouverte, fichier officiel de la page open data) :
    # projets de recrutement et projets jugés difficiles, par bassin d'emploi et par métier (script 10)
    ("francetravail_bmo", "Base-open-data-BMO-2026.xlsx",
     "https://www.francetravail.org/files/live/sites/peorg/files/documents/Statistiques-et-analyses/Open-data/BMO/"
     "Base-open-data-BMO-2026.xlsx",
     "Besoins en main-d'œuvre 2026 : recrutements prévus et jugés difficiles, par bassin d'emploi et métier"),
    # IDFM, référentiel des lignes (licence ODbL) : couleurs officielles des lignes ferrées (pictogrammes, page 6)
    ("idfm_referentiel_lignes", "referentiel_lignes_ferrees.csv",
     url(f"{IDFM}/referentiel-des-lignes/exports/csv", delimiter=";",
         select="transportmode,transportsubmode,networkname,shortname_line,colourweb_hexa,textcolourweb_hexa,status",
         where='transportmode in ("rail","metro","tram")'),
     "Couleurs officielles des lignes de métro, RER, train et tram (licence ODbL)"),
    # SNCF, régularité mensuelle Transilien (licence ODbL) : ponctualité par mois et par ligne, RER et Transilien
    # (script 11). API du portail open data de la SNCF.
    ("sncf_ponctualite", "ponctualite_mensuelle_transilien.csv",
     url("https://ressources.data.sncf.com/api/explore/v2.1/catalog/datasets/ponctualite-mensuelle-transilien/exports/csv",
         delimiter=";"),
     "Ponctualité mensuelle des RER et Transilien depuis 2013 (licence ODbL)"),
]


def telecharger(adresse: str, destination: Path) -> int:
    """Télécharge une adresse dans un fichier temporaire, puis le renomme : jamais de fichier à moitié écrit.

    Renvoie la taille du fichier en octets.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporaire = destination.with_suffix(destination.suffix + ".partiel")
    # Un nom de client explicite : certains serveurs refusent les requêtes sans en-tête User-Agent
    requete = urllib.request.Request(adresse, headers={"User-Agent": "hackaviz-2026-equipe-18"})
    with urllib.request.urlopen(requete, timeout=600) as reponse, open(temporaire, "wb") as sortie:
        while bloc := reponse.read(1 << 20):   # par blocs de 1 Mo : la mémoire reste faible même pour 300 Mo
            sortie.write(bloc)
    temporaire.replace(destination)
    return destination.stat().st_size


def main() -> None:
    """Télécharge les fichiers manquants (ou tous avec --forcer) et affiche un bilan."""
    parseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parseur.add_argument("--seulement", nargs="*", help="ne traiter que ces dossiers (ex. calendrier)")
    parseur.add_argument("--forcer", action="store_true", help="retélécharger même les fichiers déjà présents")
    parseur.add_argument("--dossier", type=Path, default=BRUT, help="dossier de destination (défaut : data/brut)")
    args = parseur.parse_args()

    echecs = 0
    for dossier, fichier, adresse, description in SOURCES:
        if args.seulement and dossier not in args.seulement:
            continue
        destination = args.dossier / dossier / fichier
        if destination.exists() and not args.forcer:
            print(f"déjà présent  {dossier}/{fichier}")
            continue
        debut = time.time()
        try:
            taille = telecharger(adresse, destination)
            if fichier.endswith(".zip"):   # archive INSEE : on décompresse à côté, les scripts lisent le CSV
                with zipfile.ZipFile(destination) as archive:
                    archive.extractall(destination.parent)
            print(f"téléchargé    {dossier}/{fichier}  ({taille / 1e6:.1f} Mo, {time.time() - debut:.0f} s)  {description}")
        except OSError as erreur:   # réseau coupé, adresse changée, serveur indisponible
            echecs += 1
            print(f"ÉCHEC         {dossier}/{fichier} : {erreur}\n              adresse : {adresse}")
    if echecs:
        sys.exit(f"{echecs} fichier(s) non téléchargé(s) : voir data/README.md pour les pages des sources")


if __name__ == "__main__":
    main()
