# Exécuter les scripts des planches

Les commandes ci-dessous partent du dossier `defi-2_rhizome`. Les scripts utilisent les données préparées dans `production/datasets/`. La planche 01 lit aussi `production/web/public/data/rail-network.json`, l'instantané du graphique web. Ils ne téléchargent pas les sources et ne reconstruisent pas les données préparées.

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

La planche 01 utilise les mêmes données et chiffres que la carte web : 15 lignes, 125 gares et 118 km dans l'instantané actuel. Pour mettre à jour cet instantané après une modification des données sources, exécutez d'abord `.venv/bin/python production/scripts/export-network.py`. Le script 01 accepte `--network-data` pour lire un autre instantané et `--output-dir` pour enregistrer ses deux fichiers dans un autre dossier.

Les dossiers de destination sont créés automatiquement. Les fichiers portant ces noms sont remplacés. Les six scripts exportent désormais les PNG à **300 dpi**, soit **5 400 × 3 450 pixels** pour leurs figures de 18 × 11,5 pouces. La commande groupée utilise ces mêmes scripts. Les PDF restent produits par Matplotlib. Cette correction ne modifie pas les livrables déjà présents : leurs métadonnées et leur correspondance avec le code courant restent à vérifier séparément.

`map_theme.py` et `map_utils.py` sont des modules communs, appelés par les scripts de planches. Ils ne sont pas des commandes de production autonomes.

## Vérifier les exports sans remplacer les livrables

Les tests utilisent l'interpréteur de l'environnement installé :

```sh
.venv/bin/python -m unittest discover -s production/tests -v
```

`test_plate_resolution.py` exécute les instructions d'export des six scripts sur une figure Matplotlib réelle. Il vérifie les dimensions, les métadonnées de résolution du PNG (tolérance de 0,01 dpi liée à l'encodage en pixels par mètre) et la signature PDF. Il ne charge pas les données cartographiques. `test_generate_pitch.py` vérifie l'orchestration et l'arrêt sur erreur avec des scripts de substitution.

Pour vérifier aussi le chargement et le rendu des six scripts réels, exécutez depuis `defi-2_rhizome` cette copie temporaire. Elle utilise les données locales et supprime ses exports à la fin. Les fichiers de `production/pitch/` ne sont pas remplacés.

```sh
.venv/bin/python - <<'PY'
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
from PIL import Image

source = Path("production").resolve()
with tempfile.TemporaryDirectory(prefix="rhizome-plates-") as temp:
    root = Path(temp)
    for folder in ("scripts", "datasets"):
        shutil.copytree(source / folder, root / folder,
                        ignore=shutil.ignore_patterns("__pycache__"))
    snapshot = root / "web/public/data/rail-network.json"
    snapshot.parent.mkdir(parents=True)
    shutil.copy2(source / "web/public/data/rail-network.json", snapshot)
    env = dict(os.environ, MPLCONFIGDIR=str(root / "mpl-cache"))
    subprocess.run([sys.executable, str(root / "scripts/generate_pitch.py")],
                   check=True, env=env)
    images = sorted((root / "pitch/png").glob("*.png"))
    assert len(images) == 6
    for path in images:
        with Image.open(path) as image:
            assert image.size == (5400, 3450), (path, image.size)
            assert all(abs(dpi - 300) < 0.01 for dpi in image.info["dpi"])
            print(path.name, image.size, image.info["dpi"])
        pdf = root / "pitch/PDF" / (path.stem + ".pdf")
        assert pdf.read_bytes().startswith(b"%PDF-")
PY
```

Ce bloc utilise la syntaxe de redirection d'un shell POSIX. Sur Windows, enregistrez son contenu Python dans un fichier et exécutez ce fichier avec l'interpréteur de l'environnement virtuel, depuis `defi-2_rhizome`.

Pillow (`PIL`) est une dépendance de Matplotlib. Un succès de ce contrôle prouve la génération depuis les fichiers préparés locaux ; il ne valide ni leur provenance initiale, ni l'identité visuelle avec les livrables historiques.

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

La génération des planches commence avec des fichiers déjà préparés. Le [catalogue](catalogue_fichiers.md) et la [liste des sources](../../donnees.md) recensent les producteurs et les fichiers ; ils ne remplacent pas les requêtes et scripts absents.

| Étape initiale | Éléments disponibles | Limite de reproduction depuis le producteur |
|---|---|---|
| Télécharger les tracés et gares IDFM | Liens des deux jeux, date de collecte déclarée et GeoJSON locaux. | Commandes d'export, filtres, pagination et version de la réponse non conservés. Un téléchargement actuel ne prouverait pas l'identité avec la copie locale. |
| Préparer les communes et noms | Géométries dans `clean/shared/hackathon_emploi.gpkg`, `src/dep_idf.geojson`, dictionnaire `src/noms_officiels.json` ; sources administratives citées. | Extraction exacte des contours, millésime du dictionnaire, jointures et traitement des changements de codes non fournis. Source et millésime de `src/rivieres_idf.geojson` non établis. |
| Extraire et agréger l'emploi Urssaf | Jeu producteur identifié, valeurs communales 2015/2025 dans le GeoPackage, séries 2015–2025 dans `clean/shared/series_emploi_urssaf.json`. | Requêtes, filtres d'activité, agrégation, gestion des valeurs manquantes et construction du GeoPackage non conservés. Les séries annuelles communales nécessaires pour reconstruire chaque groupe ne sont pas fournies. |
| Croiser gares et communes | Géométries locales et résultat `clean/shared/groupes_lignes.json` avec codes communaux, lignes et années. | `build_line_groups.py` reproduit les groupes conservés à partir des fichiers locaux. Le script initial et ses règles ne sont pas conservés ; la correspondance du résultat ne prouve pas que sa méthode était identique. |
| Extraire les demandeurs Dares / France Travail | Jeu producteur identifié, CSV communal local, `src/defm_2016_2024.txt` et `clean/shared/series_defm_dares.json`. | Le téléchargement et la préparation initiale du CSV ne sont pas fournis. L'extrait communal est reproductible depuis ce CSV ; voir ci-dessous. |
| Extraire l'emploi Insee et les auto-entrepreneurs Urssaf | Jeu Melodi `DS_RP_EMPLOI_LT_PRINC`, fichier texte communal 2017/2023, CSV départemental Urssaf 2015/2025 et constantes dans la planche 06. | Requêtes exactes, sélection des dimensions, filtres et rattachement des constantes aux réponses sources non conservés. |
| Préparer les CSV et GeoPackages de chaque planche | Fichiers locaux et logique de filtrage/calcul visible dans les scripts des planches. | Ces scripts exportent des images et PDF, pas les tables ni les couches QGIS. `build_qgis_projects.py` lit les GeoPackages existants et écrit seulement les projets `.qgz`. |

Les conversions EPSG:2154, le nettoyage des noms et l'extraction des années sont reproductibles avec `map_utils.py`. L'export du réseau prépare l'instantané partagé par le site et la planche 01. Les scripts des autres planches appliquent leurs filtres et calculs avant l'export. Reconstituer les étapes initiales exigerait de fixer les requêtes, versions, règles de jointure et valeurs manquantes, puis de comparer les sorties aux copies conservées. Aucune reconstruction depuis les producteurs n'est revendiquée ici.

Certains chiffres régionaux et textes des planches sont écrits en dur, notamment dans `06_employment_centers.py` : modifier les données ne les met pas tous à jour. Les exports existants ne sont pas garantis identiques à ceux que produirait une nouvelle exécution.

Le 12 novembre 2026, les six scripts de cartes ont été exécutés avec succès par `generate_pitch.py` dans une copie temporaire de `scripts/` et `datasets/`, avec l'interpréteur `production/.venv/bin/python` déjà disponible (Python 3.15.2, Matplotlib 3.11.2, GeoPandas 1.2.0). Les six PNG mesurent 5 400 × 3 450 pixels et déclarent 299,9994 dpi, valeur d'encodage correspondant au réglage 300 dpi ; les six PDF ont une signature valide. Les empreintes SHA-256 des fichiers existants dans `production/pitch/` sont restées identiques. Les imports explicites de `BASE` et `CLEAN` dans les planches 02, 03, 04 et 06 corrigent les erreurs de chargement rencontrées pendant ce contrôle.

Les deux tests Python ont réussi. Les polices Barlow et Barlow Condensed sont absentes de cet environnement : le rendu utilise une substitution. Le résultat n'a pas fait l'objet d'une comparaison visuelle avec les exports historiques. Le script QGIS n'a pas été exécuté ; son fonctionnement reste à confirmer avec PyQGIS. Le test du récapitulatif ne peut plus être exécuté depuis la disparition de `scripts_recap`. Ce contrôle des cartes ne vérifie pas l'installation des dépendances dans un nouvel environnement ni les téléchargements depuis les producteurs.

## Reconstituer les groupes de lignes

Depuis `defi-2_rhizome`, générez le résultat dans un fichier temporaire et vérifiez-le sans remplacer le fichier conservé :

```sh
.venv/bin/python production/scripts/build_line_groups.py --output /tmp/rhizome-groupes.json
.venv/bin/python -m unittest discover -s production/tests -p 'test_build_line_groups.py' -v
```

Le script croise les gares ouvertes de 2015 à 2025 avec les contours communaux locaux en EPSG:2154 et exclut Paris. Il retient les points strictement à l'intérieur des contours : les points sur une limite sont exclus. Les communes associées à plusieurs points sont dédoublonnées par ligne et année. Les superpositions peuvent attribuer un point à plusieurs communes historiques. Le résultat reproduit les 15 groupes conservés, y compris leurs noms. Les entrées peuvent être remplacées par les options `--stations`, `--communes` et `--official-names` ; `--output` est obligatoire et remplace le fichier indiqué.

## Reconstituer l'extrait communal des demandeurs d'emploi

Le script `build_defm.py` lit `datasets/src/mobility-employment/idf-raw-sources/defm_communes_idf.csv`. Il retient les données brutes ABC, tous sexes et tous âges, au quatrième trimestre de 2016 et 2024. Il conserve les communes avec au moins 300 demandeurs en 2016, même si leur valeur de 2024 est inférieure au seuil. Il refuse les doublons et les valeurs 2024 manquantes pour les communes retenues. Les données sources sont déjà préparées ; leur téléchargement initial n'est pas reconstitué.

Depuis `defi-2_rhizome`, pour générer et comparer le résultat sans remplacer le fichier du projet :

```sh
python3 production/scripts/build_defm.py --output /tmp/rhizome-defm.txt
cmp /tmp/rhizome-defm.txt production/datasets/src/defm_2016_2024.txt
python3 -m unittest discover -s production/tests -p 'test_build_defm.py' -v
```

L'option `--output` est obligatoire et remplace le fichier indiqué s'il existe. L'option `--source` permet de choisir une autre copie du CSV. Avec la copie locale actuelle, le résultat est identique au fichier de 362 communes conservé. Cette correspondance n'établit pas la méthode initiale ni la provenance du CSV.

Pour reconstruire les séries annuelles par groupe à partir du même CSV et de `clean/shared/groupes_lignes.json` :

```sh
python3 production/scripts/build_defm_series.py --output /tmp/rhizome-series-defm.json
python3 -m unittest discover -s production/tests -p 'test_build_defm_series.py' -v
```

Le test compare les données produites au JSON conservé. Les agrégats ne suivent pas le seuil de 300. Pour reproduire les séries historiques, le script exclut deux codes absents de toutes les années du CSV : 93059 dans le groupe T11 et 91182 dans le groupe T12. Ces séries sont donc incomplètes ; le script signale ces exclusions et refuse les autres observations manquantes détectées. La note descriptive est recopiée du fichier conservé. Les groupes restent des données préparées dont la construction initiale manque.

## Site web

Le [README du site](../web/README.md) décrit son installation et son export statique. Les commandes suivantes partent du dossier `defi-2_rhizome` et remplacent les trois instantanés dans `production/web/public/data/` :

```sh
.venv/bin/python production/scripts/export-network.py
.venv/bin/python production/scripts/export-jobseekers.py
.venv/bin/python production/scripts/export-employment-centers.py
```

Le fichier `production/requirements.txt` comprend `openpyxl`, nécessaire à l'export des demandeurs d'emploi. Les trois scripts ont été testés avec leurs entrées par défaut et ont produit des fichiers identiques aux instantanés existants. Lors du test, `openpyxl` venait d'un cache accessible par `PYTHONPATH` et n'était pas installé dans l'environnement virtuel utilisé ; l'accès à PyPI était bloqué. Son installation dans cet environnement reste à vérifier. Le [catalogue des données web](../web/docs/donnees.md) décrit les sources et les étapes initiales qui restent indisponibles.
