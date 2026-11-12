# Mobilités et emploi en Île-de-France

Ce dossier rassemble les travaux de l’équipe Rhizome pour le défi 2. Il contient des cartes, leurs données et les scripts associés. Il complète le [projet Eclowork](../../README.md).

## Objectif

Explorer comment l'évolution du réseau de transport francilien se situe par rapport à celle de l'emploi et du nombre de demandeurs d'emploi. Les cartes comparent notamment les communes ayant reçu une gare ou station et les autres territoires. Elles visent à alimenter la réflexion sur l'accès à l'emploi ; elles ne mesurent ni les trajets individuels ni l'effet causal d'une ouverture de ligne.

Le territoire étudié est l'Île-de-France. Selon l'indicateur, les comparaisons portent sur 2015–2025, 2016–2024 ou 2017–2023.

## Résultats disponibles

| Production | Contenu | Fichiers |
|---|---|---|
| 01 — Réseau et extensions | Lignes et gares ouvertes de 2015 à 2025. | [PNG](../pitch/png/01_reseau_transport_extens.png) · [PDF](../pitch/PDF/01_reseau_transport_extens.pdf) · [données](../datasets/clean/01_network/) |
| 02 — Progression de l'emploi | Variation de l'emploi salarié privé par commune, avec le réseau récent. La planche indique environ 651 000 emplois supplémentaires en Île-de-France entre 2015 et 2025. | [PNG](../pitch/png/02_emploi_progress.png) · [PDF](../pitch/PDF/02_emploi_progress.pdf) · [données](../datasets/clean/02_employment_growth/) |
| 04 — Demandeurs d'emploi | Évolution des inscrits en catégories A, B et C entre les moyennes du 4e trimestre 2016 et du 4e trimestre 2024, avec un focus sur le tram T4. | [PNG](../pitch/png/04_demandeurs_emplois.png) · [PDF existant](../pitch/PDF/03_demandeurs_emplois.pdf) · [données](../datasets/clean/04_jobseekers/) |
| 05 — Ensemble du réseau | Comparaison des réseaux et de leurs longueurs en 2015 et 2025. | [PNG](../pitch/png/05_tous_reseaux_2015_2025.png) · [PDF](../pitch/PDF/05_tous_reseaux_2015_2025.pdf) · [données](../datasets/clean/05_all_networks_2015_2025/) |
| 06 — Pôles d'emploi | Communes d'au moins 10 000 emplois salariés privés, et indicateurs complémentaires sur l'emploi et les auto-entrepreneurs. | [PNG](../pitch/png/06_poles_emploi_2015_2025.png) · [PDF](../pitch/PDF/06_poles_emploi_2015_2025.pdf) · [données](../datasets/clean/06_employment_centers_2015_2025/) |

Pour la planche 04, le PNG est présent ; un PDF des demandeurs d'emploi est disponible sous le nom `03_demandeurs_emplois.pdf`, et non sous le nom indiqué dans le tableau. Les fichiers existants ne sont pas nécessairement identiques aux sorties des scripts actuels.

## Sources et fichiers utilisés

La [liste des sources](../../donnees.md) précise les jeux, leurs licences et leur récupération. Le [catalogue des fichiers](catalogue_fichiers.md) décrit les données locales et les traitements connus.

## Méthode et limites

- Les cartes rapprochent des données communales et des ouvertures de lignes. Une commune desservie n'est pas une mesure de la distance réelle, du temps de trajet ou de l'accès effectif à un emploi. Des facteurs comme les autres projets urbains peuvent aussi influer sur l'emploi.
- L'emploi Urssaf couvre les salariés du secteur privé ; il exclut la fonction publique. L'intérim est compté au lieu de l'agence. L'emploi total Insee et les auto-entrepreneurs ont des champs et des périodes différents : leurs valeurs ne sont pas directement interchangeables ni additionnables.
- Les scripts retiennent 2016–2024 pour les demandeurs d'emploi en raison d'une rupture en 2015 et de l'effet des inscriptions automatiques en 2025. Les données communales manquantes ou sous le seuil indiqué sur la carte ne doivent pas être interprétées comme zéro.
- Le script de la planche 01 utilise le même instantané que la carte web. Six tronçons du prolongement du métro 11 sont présents dans la source sans date de mise en service : le filtre les exclut de la carte et du total, mais les gares figurent. Le T14 y est classé dans le réseau existant. Les exports déjà déposés n'ont pas été régénérés et peuvent utiliser l'ancien périmètre. La longueur des lignes peut compter des tronçons superposés : le producteur précise que les lignes commerciales peuvent partager des géométries.
- Les constats des planches sont descriptifs. En particulier, les nombres d'emplois et de demandeurs ne suffisent pas à établir qui bénéficie des emplois créés. Les chiffres affichés et les traitements n'ont pas été recalculés indépendamment.

Les [instructions d’exécution](execution.md) décrivent les dépendances, les commandes et les limites de reproduction.

## Site interactif

Le [site web](../web/README.md) intègre trois cartes au récit. Les [spécifications du site](../web/docs/specifications.md) décrivent leurs indicateurs et leurs limites.
