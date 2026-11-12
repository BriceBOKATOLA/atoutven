# Spécifications du site

Le site présente les évolutions du réseau ferré et de l'emploi en Île-de-France. Il s'adresse au public du Hackaviz et aux personnes intéressées par les mobilités et l'emploi. Ces rapprochements sont descriptifs : ils ne mesurent ni les déplacements ni l'effet des transports sur l'emploi.

## Parcours et routes

La page d'accueil `/` rassemble trois cartes dans un récit, suivi d'une section de méthode. La navigation utilise les ancres `#reseau`, `#emploi`, `#territoires` et `#methode` et indique le chapitre courant. Un lien permet d'accéder directement au récit.

Les règles de calcul et les sources figurent dans le [catalogue des données](donnees.md).

## Cartes

Chaque carte affiche un état de chargement et permet de réessayer en cas d'échec. Les légendes et les sources accompagnent les visualisations.

### Réseau ferré

La carte montre les lignes et gares ouvertes entre 2015 et 2025, par période, sur le réseau existant. Elle affiche les nombres de lignes et de gares ainsi que la longueur des tronçons retenus. Les gares sont comptées par ligne. Six tronçons du prolongement du métro 11 sont présents dans la source sans date de mise en service : le filtre les exclut de la carte et du total ; ses gares figurent sur la carte. Le T14, renommé en 2025, reste classé dans le réseau existant. La présence d'une gare ne mesure pas un trajet domicile-travail.

### Demandeurs d'emploi et zones d'emploi

La carte présente la variation communale des demandeurs d'emploi entre les moyennes du 4e trimestre 2016 et du 4e trimestre 2024. La sélection d'une zone sur la carte ou parmi les quinze fleurs affiche son portrait. Paris est sélectionné au chargement. Le survol, le focus clavier ou le clic sur une fleur de la carte affiche une infobulle avec la fleur agrandie et ses cinq indicateurs. Le clic, Entrée ou Espace sélectionne la zone et synchronise son portrait sans faire défiler la page. Échap ferme l’infobulle. La sélection d'une commune affiche ses valeurs et le portrait de sa zone ; le portrait affiche cinq indicateurs. Au clavier, la carte permet de parcourir les communes visibles et de les sélectionner avec Entrée ou Espace. La longueur des pétales compare les zones pour un même indicateur ; les valeurs manquantes restent distinctes de zéro. La carte ne propose aucune commande d'export ou de téléchargement des données.

### Pôles d'emploi et départements

La carte présente la densité d'emploi salarié privé fin 2025 et les communes comptant au moins 10 000 emplois salariés privés. Un clic sur une commune, un pôle ou une fleur sélectionne son département. La carte principale démarre sans sélection, sauf si le paramètre d'URL `departement` contient un code valide. Un second clic sur la fleur sélectionnée ou le bouton de fermeture efface la sélection. Le paramètre conserve la sélection au rechargement. Le moteur prévoit un fragment pour les URL `file://`, mais le site utilise des chemins `/data/` et doit être servi par un serveur statique. Le panneau présente les chiffres régionaux et les six premiers pôles hors Paris. Les fleurs départementales utilisent les données du classeur : emploi salarié et intérimaire au deuxième trimestre 2025, créations au troisième trimestre 2025 et défaillances cumulées sur les douze mois jusqu’en août 2026. Le fond communal et les pôles restent datés de 2025. La surface des pétales compare les départements pour un même indicateur. Une valeur manquante est signalée ; un indicateur sans valeur est omis. Une ligne qui traverse une commune n'indique pas nécessairement qu'une gare s'y trouve. Les [données du site](donnees.md) détaillent les indicateurs et leurs périodes.

Les pétales d'indicateurs différents ne sont pas directement comparables. Les [données du site](donnees.md) décrivent les sources, leur provenance et leurs limites.

### Présentation des valeurs

Le formatage intervient uniquement à l'affichage. Les données sources, les instantanés JSON, les calculs de variation et les valeurs utilisées pour dessiner les cartes et les fleurs restent inchangés.

Dans le panneau des pôles d'emploi, les comparaisons régionales sont affichées en millions avec deux décimales. Les six grands pôles sont présentés en milliers avec une décimale. Chaque valeur arrondie porte son unité : « M » pour les millions et « k » pour les milliers, par exemple « 4,54 M à 5,19 M ». Les valeurs sont présentées directement, sans volet « Valeurs détaillées » ni note d’abréviation. Les indicateurs départementaux utilisent une notation compacte avec au plus deux décimales ; leurs effectifs complets restent disponibles dans les attributs `title` et `aria-label`.

Les pourcentages de variation sont calculés sur les valeurs non arrondies. Une variation nulle est affichée sans signe positif. Les ratios « pour 100 » et les écarts en points de pourcentage conservent leurs unités distinctes. La légende de densité affiche quatre classes : « < 100 », « 100 à moins de 500 », « 500 à moins de 2 000 » et « ≥ 2 000 », en emplois salariés privés par km².

Les références sur le formatage des nombres sont les guides de [data.europa.eu sur le format des nombres](https://data.europa.eu/apps/data-visualisation-guide/number-formatting) et de la [Government Analysis Function sur la précision et les arrondis](https://analysisfunction.civilservice.gov.uk/policy-store/data-visualisation-tables/).

## Fonctionnement et accessibilité

L'application Next.js produit un export statique et utilise trois instantanés locaux dans `public/data/`. Les cartes utilisent Highcharts installé par npm. Aucun backend n'est nécessaire. JavaScript est nécessaire pour afficher et manipuler les cartes ; le récit et les liens de navigation restent accessibles sans JavaScript.

Les graphiques 2 et 3 proposent également des valeurs textuelles. Les styles utilisent notamment `@scope` et les requêtes de conteneur CSS : un navigateur compatible est nécessaire. Sur les graphiques 2 et 3, le glissement déplace la carte. Sur le graphique 3, le clavier permet de déplacer la carte et de parcourir les pôles. Sur écran étroit, la carte du graphique 3 précède son panneau.

## Dépendances et environnement

Le site utilise les dépendances npm déclarées dans `package.json`. Le fichier `package-lock.json` fixe les versions installées par `npm ci` :

| Dépendance         | Plage déclarée | Version verrouillée | Rôle                                     |
| ------------------ | -------------- | ------------------- | ---------------------------------------- |
| Next.js            | `16.4.5`       | 16.4.5              | Application et export statique           |
| React et React DOM | `^19.3.1`      | 19.3.1              | Rendu de l'interface                     |
| Highcharts         | `^13.1.1`      | 13.1.1              | Cartes Highmaps et accessibilité         |
| TypeScript         | `6.0.3`        | 6.0.3               | Vérification des types, en développement |

Pour le développement, les tests et l'export, le projet exige Node.js 22.18 ou plus récent dans la branche 22, ou Node.js 24 ou plus récent, et npm. Le contrat `engines.node` de `package.json` est `^22.18.0 || >=24.0.0`. Les tests du graphique 2 utilisent l'exécution native de fichiers TypeScript.

`npm run typecheck` génère les types de routes puis vérifie les types. `npm run build` produit le site dans `out/` avec `output: "export"` et `trailingSlash: true`. Le site doit être servi par un serveur de fichiers statiques. Les URL des instantanés commencent à la racine `/data/` ; un hébergement sous un sous-chemin nécessite une adaptation des chemins. Les commandes détaillées figurent dans le [README du site](../README.md).

### Lint et formatage

ESLint et Prettier sont déclarés dans `package.json` et verrouillés dans `package-lock.json`. Le [README du site](../README.md#vérification-et-export-statique) décrit les commandes de vérification et de correction.

### Scripts de données

Les scripts de données utilisent Python et les dépendances non figées de `production/requirements.txt` : adjustText, GeoPandas, Matplotlib, NumPy, pandas, SciPy et openpyxl. Aucune version minimale de Python ou série de versions figées n'est définie pour ces scripts. L'export des demandeurs d'emploi nécessite openpyxl. PyQGIS requiert une installation QGIS distincte. Les versions, les commandes et les limites de reproduction sont décrites dans les [instructions d'exécution](../../docs/execution.md).

## Sources et chaîne de production

| Carte               | Script d’export                                                              | Sources et préparation                                                                                                                                                                                                                                                                                                                                                                                     |
| ------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Réseau ferré        | [`export-network.py`](../../scripts/export-network.py)                       | [Tracés](https://data.iledefrance-mobilites.fr/explore/dataset/traces-du-reseau-ferre-idf/) et [gares IDFM](https://data.iledefrance-mobilites.fr/explore/dataset/emplacement-des-gares-idf/).                                                                                                                                                                                                             |
| Demandeurs d’emploi | [`export-jobseekers.py`](../../scripts/export-jobseekers.py)                 | [Données communales Dares](https://www.data.gouv.fr/datasets/inscrits-a-france-travail-donnees-communales-trimestrielles-brutes) et classeur local des zones. Les scripts de reconstruction reproduisent l'extrait communal et les six indicateurs de zones à partir des sources locales.                                                                                                                  |
| Pôles d’emploi      | [`export-employment-centers.py`](../../scripts/export-employment-centers.py) | GeoPackage et classeur local. Le classeur utilise notamment des données de [Bpifrance Création](https://bpifrance-creation.fr/observatoire/etudes-thematiques/statistiques-creation/suivi-regulier-creations-dentreprise). Les valeurs d’emploi salarié total, d’intérim et de défaillances correspondent aux figures 3, 7 et 22 du [tableau de bord Insee](https://www.insee.fr/fr/statistiques/2109644). |

Les entrées locales et les champs lus par les scripts sont détaillés dans l’[analyse des sources](../../docs/analyse_sources.md). Les [instructions d'exécution](../../docs/execution.md) décrivent la reconstruction des groupes de lignes, des données Dares, des indicateurs de zones et des territoires. Ces reconstructions commencent avec des copies locales déjà préparées.

## Documentation associée

- Le [catalogue des données du site](donnees.md) décrit les instantanés, les indicateurs et leurs limites.
- La [notice des sources et licences](../../../donnees.md) présente la provenance et les conditions de diffusion des données et des composants tiers.
- Les [instructions de production](../../docs/execution.md) décrivent les commandes et le périmètre de reproduction à partir des fichiers locaux.
