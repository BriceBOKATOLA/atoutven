# EcloWork

**Équipe :** Rhizome (équipe 16).  
**Membres :** Aurélie Auzas, Amar Tamourt, Michel Huang, Elodie Thiébault et Loane Cotellon.

**Défi :** 2, les mobilités et l’emploi.  
**Contact :** Aurélie Auzas

**Site :** [EcloWork — site interactif](https://dataviz-rhizome-liard.vercel.app/).

**En local :** [http://localhost:3000](http://localhost:3000), après démarrage selon les [instructions du site](production/web/README.md#démarrer-le-site).

## Notre question

Quel a été l’impact du développement du réseau de transport sur l’emploi ces dix dernières années ? La présentation propose aussi d'examiner les zones qui gagnent en accessibilité et celles qui restent à l'écart. Les données présentées ne mesurent pas directement l'accessibilité et ne permettent pas d'attribuer une évolution de l'emploi au développement des transports.

## Notre visualisation

Le [site interactif](https://dataviz-rhizome-liard.vercel.app/) présente trois cartes : le réseau ferré, les demandeurs d'emploi par zone d'emploi et les pôles d'emploi par département. La carte du réseau existe aussi en [PNG](pitch/png/01_reseau_transport_extens.png) et en [PDF](pitch/PDF/01_reseau_transport_extens.pdf). Le [support de présentation](pitch/EcloWork.pdf) accompagne le projet.

Le récit s'adresse au public du Hackaviz et aux personnes intéressées par les mobilités et l'emploi en Île-de-France. Selon les données disponibles, les comparaisons portent sur 2015–2025 pour le réseau et l'emploi privé, 2016–2024 pour les demandeurs d'emploi, et 2017–2023 pour l'emploi total.

## Les données utilisées

Les [données utilisées](donnees.md) présentent les sources, les périodes, les limites et les conditions de réutilisation.

## Les outils employés

- **Site web :** JavaScript, TypeScript, React, Next.js et CSS. Highcharts Maps affiche les cartes interactives.
- **Développement et qualité :** Node.js et npm pour le site, `node:test` et `unittest` pour les tests, TypeScript pour la vérification des types, ESLint et Prettier pour le code.
- **Données et planches :** Python, GeoPandas, pandas, NumPy, SciPy et openpyxl pour préparer les données ; Matplotlib et adjustText pour produire les figures.
- **Cartographie :** QGIS pour consulter les projets cartographiques et PyQGIS pour les reconstruire.

## Difficultés et suite du projet

La mise en route a pris du temps. Il a fallu trouver des moments d'échange communs et une approche qui convienne au groupe. La coordination à distance était également difficile, car les membres de l'équipe ne se connaissaient pas. L'équipe a commencé à cinq et terminé le projet à quatre.

La recherche de données cohérentes et lissées pour l'angle choisi a aussi été difficile. Les années, les trimestres et les zones disponibles ne coïncidaient pas toujours entre les sources.

Pour prolonger le projet, des données de déplacements domicile-travail et de temps de trajet pourraient aider à mesurer l'accès aux pôles d'emploi. Des indicateurs plus complets permettraient aussi d'affiner les comparaisons entre territoires. Ces pistes ne suffiraient pas, à elles seules, à établir une relation causale.

## Installation et utilisation

Les [instructions d'installation et d'exécution](production/web/README.md) décrivent le lancement du site, la préparation des données et la génération de la carte statique.

## Licences

Le code et la documentation du projet utilisent la [licence MIT](LICENSE), reprise du dépôt Hackaviz 2026. Les [conditions des données et des dépendances](donnees.md#conditions-de-réutilisation) sont distinctes de cette licence.
