# Spécifications du site

Le site présente les évolutions du réseau ferré et de l'emploi en Île-de-France. Il s'adresse au public du Hackaviz et aux personnes intéressées par les mobilités et l'emploi. Ces rapprochements sont descriptifs : ils ne mesurent ni les déplacements ni l'effet des transports sur l'emploi.

## Parcours et routes

La page d'accueil `/` rassemble trois cartes dans un récit, suivi d'une section de méthode. La navigation utilise les ancres `#reseau`, `#emploi`, `#territoires` et `#methode` et indique le chapitre courant. Un lien permet d'accéder directement au récit.

Les trois cartes sont intégrées au récit. Leurs règles de calcul et de lecture figurent dans les notices des graphiques concernées.

## Cartes

Chaque carte propose des commandes de déplacement, de zoom et de recadrage. Elle affiche un état de chargement et permet de réessayer en cas d'échec. Les légendes et les sources accompagnent les visualisations.

### Réseau ferré

La carte montre les lignes et gares ouvertes entre 2015 et 2025, par période, sur le réseau existant. Elle affiche les nombres de lignes et de gares ainsi que la longueur des tronçons retenus. Les gares sont comptées par ligne. Six tronçons du prolongement du métro 11 sont présents dans la source sans date de mise en service : le filtre les exclut de la carte et du total ; ses gares figurent sur la carte. Le T14, renommé en 2025, reste classé dans le réseau existant. La présence d'une gare ne mesure pas un trajet domicile-travail.

### Demandeurs d'emploi et zones d'emploi

La carte présente la variation communale des demandeurs d'emploi entre les moyennes du 4e trimestre 2016 et du 4e trimestre 2024. La sélection d'une zone sur la carte ou parmi les quinze fleurs affiche son portrait. Paris est sélectionné au chargement. La sélection d'une commune affiche ses valeurs et le portrait de sa zone ; le portrait affiche cinq indicateurs. Au clavier, la carte permet de parcourir les communes visibles et de les sélectionner avec Entrée ou Espace. La longueur des pétales compare les zones pour un même indicateur ; les valeurs manquantes restent distinctes de zéro. Le cadrage limite les objets géographiques chargés, mais les séries des quinze zones restent disponibles. La [documentation du graphique 2](../public/charts/graphique-2/README.md) détaille les indicateurs et leur calcul.

### Pôles d'emploi et départements

La carte présente la densité d'emploi salarié privé fin 2025 et les communes comptant au moins 10 000 emplois salariés privés. Un clic sur une commune, un pôle ou une fleur sélectionne son département. La carte principale démarre sans sélection, sauf si le paramètre d'URL `departement` contient un code valide. Un second clic sur la fleur sélectionnée ou le bouton de fermeture efface la sélection. Le paramètre conserve la sélection au rechargement. En `file://`, le fragment `#departement=93` remplit ce rôle, par exemple. Un sélecteur accessible permet aussi de consulter les valeurs communales au clavier. Le panneau présente les chiffres régionaux et les six premiers pôles hors Paris. Les fleurs départementales utilisent les données du classeur : emploi salarié et intérimaire au deuxième trimestre 2025, créations au troisième trimestre 2025 et défaillances cumulées sur les douze mois jusqu’en août 2026. Le fond communal et les pôles restent datés de 2025. La surface des pétales compare les départements pour un même indicateur. Une valeur manquante est signalée ; un indicateur sans valeur est omis. Une ligne qui traverse une commune n'indique pas nécessairement qu'une gare s'y trouve. La [documentation du graphique 3](../public/charts/graphique-3/README.md) détaille les indicateurs et leurs périodes.

Les pétales d'indicateurs différents ne sont pas directement comparables. Les [données du site](donnees.md) décrivent les sources, leur provenance et leurs limites.

## Fonctionnement et accessibilité

L'application Next.js produit un export statique et utilise trois instantanés locaux dans `public/data/`. Les cartes utilisent Highcharts installé par npm. Aucun backend n'est nécessaire. JavaScript est nécessaire pour afficher et manipuler les cartes ; le récit et les liens de navigation restent accessibles sans JavaScript.

Les commandes des cartes sont accessibles au clavier et portent des libellés. Les graphiques 2 et 3 proposent également des valeurs textuelles. Les styles utilisent notamment `@scope` et les requêtes de conteneur CSS : un navigateur compatible est nécessaire. Sur les graphiques 2 et 3, les boutons et le glissement déplacent la carte, les boutons de zoom changent son échelle et « Recadrer » rétablit le cadrage initial. Le clavier permet aussi de déplacer et de zoomer la carte. Sur le graphique 3, il permet de parcourir les pôles. Sur écran étroit, la carte du graphique 3 précède son panneau.

## Dépendances et environnement

Le site utilise les dépendances npm déclarées dans `package.json`. Le fichier `package-lock.json` fixe les versions installées par `npm ci` :

| Dépendance | Plage déclarée | Version verrouillée | Rôle |
| --- | --- | --- | --- |
| Next.js | `16.4.5` | 16.4.5 | Application et export statique |
| React et React DOM | `^19.3.1` | 19.3.1 | Rendu de l'interface |
| Highcharts | `^13.1.1` | 13.1.1 | Cartes Highmaps et accessibilité |
| TypeScript | `6.0.3` | 6.0.3 | Vérification des types, en développement |

Pour le développement, les tests et l'export, le projet exige Node.js 22.18 ou plus récent dans la branche 22, ou Node.js 24 ou plus récent, et npm. Le contrat `engines.node` de `package.json` est `^22.18.0 || >=24.0.0`. Les tests du graphique 2 utilisent l'exécution native de fichiers TypeScript.

`npm run typecheck` génère les types de routes puis vérifie les types. `npm run build` produit le site dans `out/` avec `output: "export"` et `trailingSlash: true`. Le site doit être servi par un serveur de fichiers statiques. Les URL des instantanés commencent à la racine `/data/` ; un hébergement sous un sous-chemin nécessite une adaptation des chemins. Les commandes détaillées figurent dans le [README du site](../README.md).

### Lint et formatage

Les commandes `lint`, `lint:fix`, `format:check` et `format` ainsi que leurs configurations sont préparées. Les dépendances ESLint, `eslint-config-next`, `eslint-config-prettier` et Prettier doivent encore être installées : l'accès au registre npm était bloqué. Les versions et la commande d'installation sont indiquées dans le [README du site](../README.md#vérification-et-export-statique). Les vérifications n'ont pas encore été exécutées. Les fichiers générés et les instantanés de données sont exclus du formatage.

### Scripts de données

Les scripts de données utilisent Python et les dépendances non figées de `production/requirements.txt` : adjustText, GeoPandas, Matplotlib, NumPy, pandas, SciPy et openpyxl. La génération des planches a été vérifiée avec Python 3.15.2 ; aucune version minimale de Python ou série de versions figées n'est définie pour ces scripts. L'export des demandeurs d'emploi nécessite openpyxl. PyQGIS requiert une installation QGIS distincte. Les versions, les commandes et les limites de reproduction sont décrites dans les [instructions d'exécution](../../docs/execution.md).

### Navigateur et hébergement

Le navigateur doit prendre en charge JavaScript, SVG, `@scope` et les requêtes de conteneur CSS. Aucun serveur applicatif ou appel à une source de données externe n'est nécessaire après déploiement ; les cartes chargent les instantanés locaux. Les liens vers les sources restent externes. Les conditions de Highcharts sont distinctes de la licence du code du projet.

## Points à vérifier avant publication

Les [conditions et provenances à compléter](../../../donnees.md#conditions-et-provenance-à-compléter) recensent les droits de diffusion à vérifier, notamment ceux du classeur départemental et de Highcharts. Certaines étapes de préparation des données initiales manquent ; les [instructions de production](../../docs/execution.md) précisent les limites de reproduction.
