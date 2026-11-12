# Utilisation des sources locales

Cette analyse couvre les trois exports web et la préparation de `territoires.json`. Elle distingue les fichiers lus de leurs champs réellement utilisés. La vérification du 12 novembre 2026 ci-dessous confronte aussi les références publiques et les 32 valeurs départementales affichées. Elle ne valide pas toutes les valeurs communales chez leurs producteurs ni les étapes de préparation absentes.

## Graphique 1 : réseau ferré

`export-network.py` utilise `map_utils.load()` pour lire les fichiers suivants :

- `datasets/clean/shared/hackathon_emploi.gpkg` : contours des communes et de Paris.
- `datasets/src/dep_idf.geojson` : contours départementaux.
- `datasets/src/reseau_ferre_idf.geojson` et `gares_idf.geojson` : tracés, gares et dates.
- `datasets/src/noms_officiels.json` : noms des communes.
- `datasets/src/rivieres_idf.geojson` : fichier chargé par `map_utils`, mais non inclus dans l'instantané du réseau.

L'export filtre les ouvertures de 2015 à 2025 et traite le renommage du T14. Son résultat est `web/public/data/rail-network.json`.

## Graphique 2 : demandeurs d'emploi et zones

`export-jobseekers.py` combine :

- `datasets/src/jobseekers/territoires.json` : codes, noms et géométries des zones. L'export n'utilise pas les séries d'indicateurs contenues dans ce fichier.
- `datasets/src/jobseekers/Recap_mobilites_emploi_IDF.xlsx` : indicateurs des zones, dans l'onglet « Zones d’emploi ».
- `datasets/src/jobseekers/communes.geojson` et `traces.geojson` : géométries et propriétés sélectionnées pour la carte.
- `datasets/src/defm_2016_2024.txt` : effectifs communaux en 2016 et 2024, joints par code communal.
- `datasets/src/gares_idf.geojson` et `reseau_ferre_idf.geojson` : gares et tracés pour le réseau.

`defm_2016_2024.txt` est reconstructible depuis le CSV communal Dares local avec `scripts/build_defm.py`. Le script retient les communes comptant au moins 300 demandeurs en 2016. Les séries par groupe sont reconstructibles avec `scripts/build_defm_series.py` et les groupes déjà préparés. Le CSV ne contient pas deux communes des groupes T11 et T12 : le script reproduit leur exclusion historique et signale les séries incomplètes. Les résultats ont été comparés aux fichiers conservés ; la préparation initiale du CSV et des groupes reste inconnue.

L'export écrit `web/public/data/jobseekers-employment-zones.json`. Le graphique utilise une sélection d'années et d'indicateurs du classeur, principalement 2016 et 2024. La disponibilité d'une série dans un fichier ne signifie donc pas qu'elle est affichée.

`build_territories.py` peut régénérer `territoires.json` à partir de `datasets/src/jobseekers/communes.geojson`, de `datasets/src/jobseekers/territories_sources/map-data/zones_emploi.geojson` et de deux classeurs dans `datasets/src/mobility-employment/idf-raw-sources/` : DPAE départementales et offres Dares. Il calcule notamment des séries DPAE et d'offres, conservées dans `territoires.json` mais non reprises par l'export web actuel. Les GeoJSON d'entrée sont eux-mêmes des données préparées ; leurs traitements initiaux ne sont pas tous disponibles.

`rebuild_workbook_indicators.py` reconstitue les six indicateurs des zones utilisés par l'export à partir des sources locales citées par le classeur et les compare à son onglet « Zones d’emploi ». Les 1 080 cellules comparées correspondent, dont 457 valeurs absentes. Certaines cellules Urssaf sont vides ; leur omission des sommes ne prouve pas qu'elles valent zéro. Le rapport indique ces limites et les communes manquantes.

## Graphique 3 : pôles d'emploi

`export-employment-centers.py` lit le classeur et la configuration dans `datasets/src/employment-centers/`, ainsi que `06_poles_emploi.gpkg` et le CSV des auto-entrepreneurs dans `datasets/clean/06_employment_centers_2015_2025/`. Il lit aussi les constantes régionales du script `06_employment_centers.py`. Il écrit `web/public/data/employment-centers-departments.json`.

Les indicateurs départementaux combinent l'emploi et les créations de 2025 avec les défaillances cumulées sur les douze mois jusqu'en août 2026. Leurs périodes sont différentes. Les 24 valeurs d’emploi salarié total, d’intérim et de défaillances correspondent exactement au tableau de bord Insee ; les huit totaux de créations correspondent aux fiches mensuelles Bpifrance. Les références et périodes sont détaillées ci-dessous. L’historique d’extraction du classeur reste inconnu.

## Sources conservées pour la provenance

Les fichiers de `datasets/src/mobility-employment/idf-raw-sources/` comprennent les extraits Insee et Flores, les effectifs Urssaf et les jeux Dares utilisés par les scripts de reconstruction des territoires, des séries Dares et des indicateurs de zones. Les archives de validations ferroviaires, trois extraits non utilisés et le classeur récapitulatif de `mobility-employment/` ont été retirés après vérification des traitements présents. Certaines préparations historiques restent impossibles à vérifier avec les fichiers conservés.

Les sources et les copies ont été comparées par SHA-256 avant le retrait prévu du dossier d'origine. Les scripts initiaux d'extraction ou de transformation manquent encore pour plusieurs données préparées. Voir [l'exécution et ses limites](execution.md) et [la liste des données](../../donnees.md).

## Vérification du 12 novembre 2026

### Références publiques et données locales

- **Réseau** : les fiches IDFM des [tracés](https://data.iledefrance-mobilites.fr/explore/dataset/traces-du-reseau-ferre-idf/) et des [gares par ligne](https://data.iledefrance-mobilites.fr/explore/dataset/emplacement-des-gares-idf/) sont accessibles et décrivent les objets utilisés. Une gare desservie par plusieurs lignes possède plusieurs objets ; les tronçons peuvent aussi se superposer. Le contrôle ne compare pas chaque géométrie locale au jeu actuel.
- **Demandeurs d’emploi** : la [fiche Dares / France Travail](https://www.data.gouv.fr/datasets/inscrits-a-france-travail-donnees-communales-trimestrielles-brutes) confirme les catégories A, B et C, les moyennes du quatrième trimestre, les arrondis au multiple de cinq et la Licence Ouverte 2.0. Les sommes locales de valeurs arrondies ne sont pas nécessairement égales aux séries agrégées du producteur.
- **Urssaf** : les [effectifs communaux](https://open.urssaf.fr/explore/dataset/etablissements-et-effectifs-salaries-au-niveau-commune-x-ape-last/) sont des données brutes au 31 décembre, sur le secteur privé. Les fiches data.gouv des [effectifs](https://www.data.gouv.fr/datasets/nombre-detablissements-employeurs-et-effectifs-salaries-du-secteur-prive-par-commune-x-ape-au-31-12-depuis-2006) et des [auto-entrepreneurs](https://www.data.gouv.fr/datasets/auto-entrepreneurs-par-departement) confirment l’ODbL. La reconstruction des zones ignore 48 975 cellules sectorielles vides en 2016 et 46 706 en 2024 ; elles ne sont pas des zéros confirmés.
- **Chômage des zones** : la [page Insee 1893230](https://www.insee.fr/fr/statistiques/1893230) fournit le fichier annuel `chomage-zone-2003-2025.xlsx`, homonyme de la copie locale. Le graphique utilise sa moyenne annuelle 2024, sur les zones d’emploi 2020. La page présente aussi des séries trimestrielles, qui ne sont pas celles affichées ici.
- **Ratio d’emplois** : la [base Insee du recensement 2016](https://www.insee.fr/fr/statistiques/4171446) documente les variables utilisées : somme des emplois `C16_EMPLT` divisée par la somme des actifs occupés résidents de 15 à 64 ans `P16_ACTOCC1564`, multipliée par 100. Les données sont en géographie communale 2019 et regroupées selon les zones locales. Ce ratio calculé ne doit pas être confondu avec un indicateur dont le dénominateur couvrirait tous les âges.
- **Contrôle des zones** : reconstruction en mémoire des six indicateurs depuis les fichiers locaux, puis comparaison du classeur au JSON web : 1 080 cellules sans écart à chaque étape, dont 457 absentes. Ce résultat établit la cohérence locale, pas l’exhaustivité des extractions initiales.

### Concordance des indicateurs départementaux

Le [tableau de bord Insee Île-de-France](https://www.insee.fr/fr/statistiques/2109644), consulté le 12 novembre 2026, contient les 24 valeurs locales d’emploi et de défaillances : figures 3 et 7, colonne T2 2025, et figure 22, cumul de septembre 2025 à août 2026. L’emploi salarié est total (public et privé), en fin de trimestre et corrigé des variations saisonnières ; estimations Urssaf, Dares et Insee mises à jour le 18 septembre 2026. Les défaillances sont issues de Fiben, Banque de France, en date de jugement, données arrêtées au 20 octobre et mises à jour le 28 octobre 2026.

Les huit totaux de créations correspondent à la somme des fiches Bpifrance Création de [juillet](https://bpifrance-creation.fr/sites/default/files/oce/OCE_FSM_%C3%8Ele-de-France_202507.pdf), [août](https://bpifrance-creation.fr/sites/default/files/oce/OCE_FSM_%C3%8Ele-de-France_202508.pdf) et [septembre 2025](https://bpifrance-creation.fr/sites/default/files/oce/OCE_FSM_%C3%8Ele-de-France_202509.pdf), page 8. Les trois premières publications sont provisoires, selon leur méthode page 10. Exemple Paris : 10 584 + 7 866 + 9 572 = 28 022. Ces données brutes Insee ne doivent pas être remplacées par les créations trimestrielles désaisonnalisées du tableau de bord.

| Département | Salariés T2 2025, milliers | Intérim T2 2025, milliers | Créations T3 2025 | Défaillances sept. 2025–août 2026 |
|---|---:|---:|---:|---:|
| Paris | 1 980,2 | 38,7 | 28 022 | 5 220 |
| Seine-et-Marne | 517,2 | 16,1 | 6 121 | 2 130 |
| Yvelines | 531,0 | 6,3 | 6 878 | 1 190 |
| Essonne | 498,8 | 9,8 | 5 827 | 1 350 |
| Hauts-de-Seine | 1 169,2 | 16,9 | 8 960 | 1 680 |
| Seine-Saint-Denis | 677,4 | 9,2 | 9 542 | 2 560 |
| Val-de-Marne | 554,9 | 7,0 | 7 675 | 1 370 |
| Val-d’Oise | 419,5 | 10,5 | 6 193 | 1 040 |

Résultat : 32 valeurs sur 32 identiques. Cette concordance identifie les publications correspondantes ; elle ne reconstitue pas l’historique d’extraction du classeur.

### Limites conservées

- Le dépôt [France GeoJSON](https://github.com/gregoiredavid/france-geojson) confirme une édition 2018 d’Admin Express COG et des codes Insee. La documentation locale le cite pour les graphiques 1 et 3, mais les GeoPackages ne contiennent pas de métadonnées d’origine permettant de retracer leurs transformations. Le site présente donc cette origine comme une attribution documentaire.
- Pour le graphique 2, les fiches Région Île-de-France des [contours](https://data.iledefrance.fr/explore/dataset/base-des-zones-demploi-contours/) et de la [composition communale](https://data.iledefrance.fr/explore/dataset/base-des-zones-demploi/) existent. Les copies locales contiennent respectivement 15 zones et 1 266 communes. Cela ne prouve pas l’identité des géométries ; l’origine des contours communaux et les traitements initiaux restent à établir.
- Le catalogue Insee `DS_RP_EMPLOI_LT_PRINC` est accessible mais son contenu n’a pas été extractible avec l’outil web. Les requêtes Melodi historiques et les valeurs communales 2017/2023 n’ont pas été revalidées en ligne.
- Les droits sur les classeurs complets, les fichiers combinés et certaines copies géographiques restent à examiner. Les attributions publiques ne résolvent pas ces questions ; voir les [conditions et provenances à compléter](../../donnees.md#conditions-et-provenance-à-compléter).

### Vérification de l’intégration web

Les blocs « Sources et notes » des trois graphiques ont été mis à jour sans modifier les valeurs des instantanés. Contrôles du 12 novembre 2026 :

- 52 tests Node réussis. Certains tests utilisent un environnement simulé ; ils ne remplacent pas le contrôle navigateur.
- ESLint, Prettier et TypeScript (`tsc --noEmit --incremental false`) : réussis.
- Navigateur sur `http://localhost:3000` : répertoire du serveur confirmé, nouvelles formulations présentes, trois cartes chargées, 21 liens de sources rendus, aucune ancre interne invalide et aucune erreur console. À 390 px de large, les trois blocs de sources restent visibles sur une colonne, sans débordement horizontal.
- Export de production non validé : `npm run build` échoue sur le nettoyage de `.next` (`EPERM`). La tentative sur une copie temporaire est bloquée par l’accès réseau à `registry.npmjs.org`. Le serveur de développement existant a permis le contrôle réel de l’affichage ; aucun déploiement n’a été effectué.
