# Exécuter les scripts des planches

Les commandes ci-dessous partent du dossier `defi-2_rhizome`. Les scripts lisent les fichiers présents dans `production/datasets/`. Ils ne téléchargent pas les sources et ne reconstruisent pas les données préparées.

## Installer les dépendances des cartes

Python, GeoPandas, pandas, NumPy, Matplotlib, SciPy et adjustText sont nécessaires. GeoPandas utilise aussi ses dépendances géographiques, notamment Shapely et un moteur de lecture des fichiers géographiques. Les versions d'origine ne sont pas connues : la commande suivante installe les versions disponibles pour votre système, sans garantir un rendu identique.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r production/requirements.txt
```

Sur Windows, remplacez `.venv/bin/python` par `.venv\Scripts\python.exe` dans les commandes. L'installation nécessite un accès aux paquets Python. Les polices Barlow et Barlow Condensed améliorent la fidélité ; si elles sont absentes, Matplotlib utilise une police de remplacement.

## Générer les planches

Pour générer les six planches et enregistrer les PNG et PDF directement dans `production/pitch/`, lancez :

```sh
.venv/bin/python production/scripts/generate_pitch.py
```

La commande fonctionne quel que soit le dossier courant si le chemin vers le script est adapté. Elle remplace les fichiers de même nom dans `pitch/png/` et `pitch/PDF/`. Elle s'arrête à la première erreur ; les planches déjà générées restent enregistrées. Le PDF des demandeurs porte le numéro 04 et celui de la comparaison de l'emploi porte le numéro 03.

Pour générer une seule planche dans `production/pitch/`, lancez le script correspondant :

```sh
.venv/bin/python production/scripts/01_transport_extensions.py
.venv/bin/python production/scripts/02_employment_growth.py
.venv/bin/python production/scripts/03_employment_comparison.py
.venv/bin/python production/scripts/04_jobseekers.py
.venv/bin/python production/scripts/05_transport_networks.py
.venv/bin/python production/scripts/06_employment_centers.py
```

| Script | Sujet | Fichiers produits dans `production/pitch/png/` et `production/pitch/PDF/` |
|---|---|---|
| `01_transport_extensions.py` | Extensions du réseau | `01_reseau_transport_extens.png`, `01_reseau_transport_extens.pdf` |
| `02_employment_growth.py` | Évolution de l'emploi | `02_emploi_progress.png`, `02_emploi_progress.pdf` |
| `03_employment_comparison.py` | Comparaison des groupes de communes | `03_avant_apres.png`, `03_avant_apres.pdf` |
| `04_jobseekers.py` | Demandeurs d'emploi | `04_demandeurs_emplois.png`, `04_demandeurs_emplois.pdf` |
| `05_transport_networks.py` | Réseaux en 2015 et 2025 | `05_tous_reseaux_2015_2025.png`, `05_tous_reseaux_2015_2025.pdf` |
| `06_employment_centers.py` | Pôles d'emploi | `06_poles_emploi_2015_2025.png`, `06_poles_emploi_2015_2025.pdf` |

Les dossiers de destination sont créés automatiquement. Les fichiers portant ces noms sont remplacés. Les PNG produits par ces scripts sont configurés à 200 dpi ; les instructions du dépôt demandent au moins 300 dpi pour une image statique. Les PDF sont également produits. Les exports de la planche 03 sont présents ; leur correspondance exacte avec le script reste à vérifier.

`map_theme.py` et `map_utils.py` sont des modules communs, appelés par les scripts de planches. Ils ne sont pas des commandes de production autonomes.

## Projets QGIS

Les cinq fichiers `.qgz` et leurs GeoPackages correspondants sont dans `production/datasets/clean/`. Ouvrez directement un `.qgz` dans QGIS pour consulter le projet existant.

`production/scripts/build_qgis_projects.py` reconstruit ces cinq projets et **remplace les fichiers `.qgz` existants**. Il faut le lancer avec un interpréteur Python configuré pour les modules de l'installation QGIS et Qt, par exemple :

```sh
/path/to/qgis-python production/scripts/build_qgis_projects.py
```

Remplacez `/path/to/qgis-python` par l'interpréteur de votre installation QGIS. Sa configuration dépend du système et de la distribution QGIS ; l'environnement virtuel des cartes ne fournit pas PyQGIS. Cette commande n'a pas été testée ici. Le GeoPackage de la planche 03 n'est pas présent : ce script ne crée pas de projet QGIS pour elle.

## Récapitulatif

Le dossier `scripts_recap` n’est plus présent dans le projet. Les commandes de génération et le test du récapitulatif ne sont donc pas disponibles.

## Ce qui manque pour une reproduction complète

Les entrées référencées directement par les scripts de cartes sont présentes. Les cinq projets QGIS existants référencent des GeoPackages présents à côté de leurs `.qgz`. Cela ne vérifie pas le rendu ni toutes les opérations effectuées à l'exécution.

Les scripts d'extraction par API, le croisement initial des gares et communes, la construction des séries, du GeoPackage communal et de certains CSV et GeoPackages par planche ne sont pas fournis. Les résultats préparés correspondants sont présents, mais ces étapes ne peuvent pas être reproduites entièrement à partir des sources. Certains chiffres régionaux et textes des planches sont écrits en dur, notamment dans `06_employment_centers.py` : modifier les données ne les met pas tous à jour. Les exports existants ne sont pas garantis identiques à ceux que produirait une nouvelle exécution.

La compilation Python et les références directes aux fichiers ont été vérifiées. Le test du récapitulatif a réussi avant la disparition de `scripts_recap`, mais il ne peut plus être exécuté. Les six scripts de cartes et le script QGIS n'ont pas été exécutés : les bibliothèques géographiques et QGIS ne sont pas disponibles ici, et l'accès à PyPI a été bloqué. Leur fonctionnement et leur rendu restent donc à confirmer dans un environnement équipé.
