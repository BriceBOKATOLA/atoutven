# Projet C — fichiers sources (Hackaviz 2026)

## Contenu
- [idf-raw-sources](../../datasets/src/mobility-employment/idf-raw-sources/) : extraits bruts filtrés Île-de-France, tels que téléchargés ou directement exportés des portails (INSEE, DARES, Urssaf, geo.api.gouv.fr, Région IDF). `flores/` : Flores 2017-2021 agrégé par commune × NA17 (Paris agrégé 75056).
- [GeoJSON préparés](../../datasets/src/jobseekers/) : données préparées pour la carte (`traces.geojson` tracés IDFM avec `annee_mes` ; `communes.geojson` 1 266 communes avec tous les indicateurs ; `zones_emploi.geojson` 15 zones).
- `Projet_C_evolution_reseau_emploi_donnees.md` (fiche), `Projet_C_sources_et_recap_2015_2020_2025.xlsx` (sources + récap), `Projet_C_dumbbell_departements_zones_emploi.html` (maquette).

## Fichiers volumineux non inclus (à retélécharger)
| Fichier | Taille | Source |
|---|---|---|
| RP 2016 `base-cc-emploi-pop-act-2016-csv.zip` (France) | 32 Mo | https://www.insee.fr/fr/statistiques/4171446 — extrait IDF : `actifs_emplois_2016_com.csv` |
| RP 2016 `base-ic-activite-residents-2016.zip` (IRIS France, xls 89 Mo) | 39 Mo | https://www.insee.fr/fr/statistiques/4228426 — l'extrait IDF des modes n'est plus conservé localement. |
| RP 2021 `base-ic-activite-residents-2021_csv.zip` (IRIS France) | 38 Mo | https://www.insee.fr/fr/statistiques/8268843 — extrait IDF : `actifs_2021_com.csv` |
| Flores `TD_FLORES2017…2021_NA17_TREF_NBSAL_CSV.zip` (France) | 5 × 1,7 Mo | https://www.insee.fr/fr/statistiques/4991205 — extraits IDF dans `flores/` |
| Tracés du réseau ferré (export GeoJSON complet) | 6 Mo | https://data.iledefrance-mobilites.fr/explore/dataset/traces-du-reseau-ferre-idf/ — version préparée : `production/datasets/src/jobseekers/traces.geojson` |

## Licences

Les licences et les droits de redistribution restent à vérifier pour chaque fichier.

## Préparation des territoires

Voir les [instructions d'exécution](../execution.md#reconstituer-les-données-des-territoires) et l'[analyse des sources](../analyse_sources.md).
