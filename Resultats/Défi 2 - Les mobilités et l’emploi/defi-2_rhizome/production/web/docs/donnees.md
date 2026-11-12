# Données du site

Le site utilise trois instantanés JSON locaux. Ils permettent de consulter les cartes sans appel à une source de données externe. Les indicateurs ont des périodes et des champs différents. La présence d'une ligne ou d'une gare ne mesure pas un trajet ni l'accès effectif à l'emploi.

| Instantané                                        | Utilisation                                                                    | Sources et limites                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ------------------------------------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `public/data/rail-network.json`                   | Carte du réseau ferré et chiffres associés.                                    | Export depuis les fichiers préparés de production, avec les tracés et les gares Île-de-France Mobilités. Six tronçons du prolongement du métro 11 sont présents dans la source sans date de mise en service ; le filtre les exclut de la carte et du total, mais les gares figurent. Le T14, renommé en 2025, reste classé dans le réseau ancien.                                                                                                                                                                                                                                                |
| `public/data/jobseekers-employment-zones.json`    | Évolution des demandeurs d'emploi par commune et portraits des zones d'emploi. | Les [spécifications du site](specifications.md#demandeurs-demploi-et-zones-demploi) décrivent la période et les valeurs manquantes. L’[analyse des sources](../../docs/analyse_sources.md#graphique-2--demandeurs-demploi-et-zones) détaille les entrées et les champs utilisés.                                                                                                                                                                                                                                                                                                                 |
| `public/data/employment-centers-departments.json` | Pôles d'emploi, réseau et indicateurs départementaux.                          | Le classeur départemental reprend l’emploi salarié total et intérimaire au T2 2025 (données corrigées des variations saisonnières) et les défaillances de septembre 2025 à août 2026 : 24 valeurs identiques au [tableau de bord Insee](https://www.insee.fr/fr/statistiques/2109644), figures 3, 7 et 22. Les huit totaux de créations au T3 2025 correspondent aux premières publications mensuelles Bpifrance Création, toutes provisoires, fondées sur les données brutes Insee. Voir les [preuves et dates de mise à jour](../../docs/analyse_sources.md#vérification-du-12-novembre-2026). |

## Reproduction

Les trois scripts de `production/scripts/` utilisent les fichiers de `production/datasets/` et écrivent directement les instantanés de `web/public/data/`. Depuis `production/web`, créez un environnement virtuel dans `production/`, installez les dépendances, puis lancez les exports :

```sh
python3 -m venv ../.venv
../.venv/bin/python -m pip install -r ../requirements.txt
../.venv/bin/python ../scripts/export-network.py
../.venv/bin/python ../scripts/export-jobseekers.py
../.venv/bin/python ../scripts/export-employment-centers.py
```

Chaque commande remplace son instantané. L'option `--output` permet de choisir un autre fichier. Les scripts acceptent aussi des chemins d'entrée configurables : consultez leur option `--help`.

Le script du réseau utilise notamment `production/scripts/map_utils.py` et les données préparées communes. Les étapes initiales de préparation de certaines entrées restent indisponibles ; voir les [instructions de production](../../docs/execution.md).

## Provenance et conditions d'utilisation

La [liste des données utilisées](../../../donnees.md#données-du-site-web) décrit l'origine des fichiers copiés. Les [conditions et provenances à compléter](../../../donnees.md#conditions-et-provenance-à-compléter) recensent les droits de diffusion à vérifier, les sources inconnues et les conditions de Highcharts.
