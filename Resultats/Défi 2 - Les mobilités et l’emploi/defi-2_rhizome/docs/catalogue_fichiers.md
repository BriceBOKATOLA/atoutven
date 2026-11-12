# Préparation des données du site

Les trois cartes utilisent des instantanés JSON générés à partir des fichiers de `production/datasets/`. Les scripts de `production/scripts/` produisent les instantanés, sans télécharger les sources. Les [conditions de réutilisation](../donnees.md) et les [commandes d'exécution](../production/web/README.md#préparer-les-données-et-la-carte-statique) sont documentées séparément.

## Entrées des trois cartes

| Carte et instantané | Principales entrées locales | Script d'export |
|---|---|---|
| Réseau : [rail-network.json](../production/web/public/data/rail-network.json) | Tracés et gares IDFM, contours communaux du GeoPackage `clean/shared/hackathon_emploi.gpkg`, départements et noms officiels. | `export-network.py` |
| Demandeurs d'emploi : [jobseekers-employment-zones.json](../production/web/public/data/jobseekers-employment-zones.json) | `src/defm_2016_2024.txt`, classeur `src/jobseekers/Recap_mobilites_emploi_IDF.xlsx`, géométries des zones et communes, tracés et gares IDFM. | `export-jobseekers.py` |
| Pôles d'emploi : [employment-centers-departments.json](../production/web/public/data/employment-centers-departments.json) | `clean/06_employment_centers_2015_2025/06_poles_emploi.gpkg`, CSV Urssaf des auto-entrepreneurs, classeur `src/employment-centers/indicateurs-departementaux-2025-2026.xlsx` et constantes régionales de la planche 06. | `export-employment-centers.py` |

Les chemins `src/` et `clean/` du tableau sont relatifs à `production/datasets/`. Les fichiers sont déjà préparés. Certaines étapes initiales et certains calculs régionaux ne peuvent pas être reproduits intégralement avec les seuls scripts fournis.

## Méthodes et limites

- **Réseau.** Les ouvertures couvrent 2015 à 2025. Les gares desservies par plusieurs lignes sont comptées par ligne et certains tronçons peuvent se superposer. Six tronçons du prolongement du métro 11 n'ont pas de date dans la source : ils sont exclus de la carte et du total, mais les gares figurent. Le T14 est classé dans le réseau existant.
- **Demandeurs d'emploi.** Les données Dares sont des moyennes brutes du 4e trimestre, arrondies au multiple de cinq. L'extrait communal retient les communes ayant au moins 300 demandeurs en 2016 et leurs valeurs de 2024. Les valeurs absentes ne sont pas des zéros. Les séries historiques par groupe excluent deux codes communaux absents du CSV local.
- **Zones d'emploi.** Les indicateurs affichés proviennent du classeur des zones. Le taux de chômage utilisé est une moyenne annuelle 2024. Le ratio d'emplois 2016 divise les emplois au lieu de travail par les actifs occupés résidents de 15 à 64 ans, puis multiplie le résultat par 100. Les cellules Urssaf manquantes sont exclues des sommes et ne sont pas des zéros confirmés.
- **Pôles d'emploi.** Un pôle compte au moins 10 000 emplois salariés privés. Les données Urssaf de 2015 et 2025 ne couvrent pas le même champ que l'emploi total Insee de 2017 et 2023.
- **Indicateurs départementaux.** L'emploi total et l'intérim portent sur le 2e trimestre 2025. Les créations couvrent le 3e trimestre 2025 et sont calculées à partir de trois premières publications mensuelles provisoires. Les défaillances couvrent les douze mois jusqu'en août 2026. Les valeurs correspondent aux figures 3, 7 et 22 du [tableau de bord Insee](https://www.insee.fr/fr/statistiques/2109644) et aux [fiches Bpifrance](../donnees.md#sources-principales).

Les fichiers `territoires.json` contiennent aussi des séries de déclarations préalables à l'embauche et d'offres d'emploi. Ces séries ne sont pas reprises dans l'instantané du site. Les contours et les données d'emploi ne mesurent ni les trajets individuels ni l'effet causal d'une ligne sur l'emploi.
