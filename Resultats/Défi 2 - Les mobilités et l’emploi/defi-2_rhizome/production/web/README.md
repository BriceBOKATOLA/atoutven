# EcloWork : installation et utilisation

EcloWork est un site statique Next.js. Il utilise trois fichiers JSON locaux pour afficher les cartes. Consultez le [README du projet](../../README.md) pour les livrables et la [notice des données](../../donnees.md) pour les sources et leurs conditions.

## Démarrer le site

Installez Node.js 22.18 ou une version ultérieure de la branche 22, ou Node.js 24 ou une version ultérieure. Depuis `defi-2_rhizome` :

```sh
cd production/web
npm ci
npm run dev
```

Ouvrez [http://localhost:3000](http://localhost:3000). Le récit et les liens restent lisibles sans JavaScript ; les cartes nécessitent JavaScript.

## Vérifier et exporter le site

Depuis `production/web` :

```sh
npm run lint
npm run format:check
npm run typecheck
node --test "tests/*.test.mjs" "tests/chart-2/*.test.mjs" "tests/chart-3/*.test.mjs" "scripts/*.test.mjs" "app/(chart-3)/charts/chart-3/lib/*.test.mjs"
npm run build
```

L'export statique est créé dans `out/`. Pour le consulter, lancez un serveur depuis `production/web` :

```sh
python3 -m http.server 3000 --directory out
```

Ouvrez ensuite [http://localhost:3000](http://localhost:3000). L'export doit être servi à la racine d'un site : les fichiers de données utilisent le chemin `/data/`.

## Préparer les données et la carte statique

Les scripts Python utilisent les fichiers préparés de `production/datasets/`. Depuis `defi-2_rhizome`, installez les dépendances :

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r production/requirements.txt
```

Sur Windows, utilisez `.venv\Scripts\python.exe`. Les dépendances Python ne sont pas figées.

Pour régénérer les données du site, exécutez les trois scripts suivants. **Ils remplacent les fichiers JSON existants** dans `production/web/public/data/` :

```sh
.venv/bin/python production/scripts/export-network.py
.venv/bin/python production/scripts/export-jobseekers.py
.venv/bin/python production/scripts/export-employment-centers.py
```

Chaque script accepte `--output` pour écrire ailleurs. La préparation initiale de certaines entrées n'est pas disponible ; le [catalogue des données](../../docs/catalogue_fichiers.md) décrit les entrées utilisées et les limites.

Pour générer la carte statique du réseau :

```sh
.venv/bin/python production/scripts/01_transport_extensions.py
```

Le script lit `rail-network.json` et remplace les fichiers de `pitch/png/` et `pitch/PDF/`. Pour conserver les livrables existants, ajoutez par exemple `--output-dir /tmp/eclowork-reseau`. Le rendu utilise Arial, Liberation Sans ou DejaVu Sans selon les polices disponibles ; le titre privilégie Arial Narrow.

Les tests Python s'exécutent depuis la racine du projet :

```sh
.venv/bin/python -m unittest discover -s production/tests -v
```

Les scripts `build_line_groups.py`, `build_territories.py`, `rebuild_workbook_indicators.py`, `build_defm.py` et `build_defm_series.py` reconstruisent une partie des données préparées. Utilisez leur option `--help` pour les entrées et les destinations disponibles. Le script `generate_pitch.py` régénère les cinq planches, y compris les travaux antérieurs, et remplace les fichiers de même nom dans `pitch/`.

Les projets QGIS sont dans `production/datasets/clean/`. Leur reconstruction par `build_qgis_projects.py` nécessite PyQGIS et remplace les projets existants.

## Fichiers du site

- `app/(story)/` contient le récit. `components/NetworkMap.tsx` affiche la carte du réseau.
- `app/(chart-2)/` et `app/(chart-3)/` contiennent les cartes des demandeurs et des pôles d'emploi.
- `public/data/` contient les trois instantanés et leur notice de licence.

Les cartes permettent de masquer des couches, de zoomer et de se déplacer à la souris ou au clavier. Sur écran tactile, deux doigts déplacent ou agrandissent la carte. Les logos du pied de page proviennent des dépôts [Île-de-France Mobilités](https://github.com/IleDeFranceMobilites/hackathon_ia_mobilites_2024/blob/4d96130f4f085dbb07e2f0655d3d58d2418f6580/resultats/repositories/equipe_07_tranquiliscore/tranquili-score-main/Documents/t-app-js/ressources/IdFMobilit%C3%A9s.svg.png) et [Datactivist](https://github.com/datactivist/slides_datactivist/blob/master/inst/rmarkdown/templates/xaringan/resources/img/logo.png).
