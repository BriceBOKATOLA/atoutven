# Eclowork

**Équipe :** Rhizome (équipe 16).  
**Membres :** Aurélie Auzas, Amar Tamourt, Michel Huang, Elodie Thiébault et Loane Cotellon.

**Défi :** 2, les mobilités et l’emploi.  
**Contact :** à compléter avec au moins une adresse que l'équipe accepte de publier.

## Par où commencer

1. Consultez le [cadrage du projet](projet.md).
2. Retrouvez les sources et leurs conditions d'utilisation dans [donnees.md](donnees.md).
3. Explorez les cartes et leur documentation dans [production/](production/README.md).

Ce dossier est placé dans le répertoire du défi 2. Il contient ce README et `production/`, comme demandé dans les [instructions de dépôt](../../README.md).

## Notre question

Comment l'évolution des transports franciliens se situe-t-elle par rapport à celle de l'emploi entre 2015 et 2025 ? La présentation propose aussi d'examiner les zones qui gagnent en accessibilité et celles qui restent à l'écart. Les données présentées ne mesurent pas directement l'accessibilité et ne permettent pas d'attribuer une évolution de l'emploi au développement des transports.

## Notre visualisation

Les [planches](production/docs/visualisation.md) présentent l’évolution du réseau ferré et des indicateurs d’emploi en Île-de-France. Les planches sont fournies avec leurs données et scripts. Certains exports sont absents du dépôt ; leur état est précisé dans la documentation des planches. Elles décrivent des évolutions sans établir de relation causale.

## Les données utilisées

Les [sources et leurs conditions d’utilisation](donnees.md) sont répertoriées avec leurs fichiers locaux. Le [catalogue des fichiers](production/docs/catalogue_fichiers.md) décrit leurs champs et leurs limites.

## Les outils employés

Les cartes utilisent Python, GeoPandas, pandas, NumPy, Matplotlib, SciPy et adjustText. Des projets cartographiques sont également fournis pour QGIS. Le script de création des projets utilise PyQGIS.

## Difficultés et suite du projet

L'emploi Urssaf concerne les salariés du secteur privé. Les autres indicateurs couvrent des populations et des périodes différentes. La présence d'une gare dans une commune ne mesure pas l'accès réel à l'emploi. Certaines étapes de préparation des données ne sont pas disponibles, et la comparaison communale pour 2019 reste à documenter. Les [limites des sources](production/docs/visualisation.md#méthode-et-limites) et les [étapes manquantes pour la reproduction](production/docs/execution.md#ce-qui-manque-pour-une-reproduction-complète) précisent ces points.

## Installation et utilisation

Les [instructions d'exécution](production/docs/execution.md) décrivent l'installation des dépendances et la génération des cartes. Les [fichiers de production](production/README.md) donnent accès aux exports, aux données et aux scripts.

## Licences

Le code et la documentation du projet utilisent la [licence MIT](LICENSE), reprise du dépôt Hackaviz 2026. Les licences des données et des éléments réutilisés restent à vérifier et à documenter avant publication.

## Site interactif

Le [site web](production/web/README.md) présente le récit et trois cartes interactives. Ses [spécifications](production/web/docs/specifications.md) et son [catalogue de données](production/web/docs/donnees.md) précisent les indicateurs, leurs sources et les limites de reproduction.
