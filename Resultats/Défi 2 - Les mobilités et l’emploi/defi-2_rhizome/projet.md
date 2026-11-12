# Cadrer Eclowork

## Défi principal

Défi 2 : les mobilités et l’emploi. Explorez le lien entre mobilité et accès à l’emploi, ainsi que la manière dont les réseaux de transport répondent aux besoins du monde du travail. Consultez la [présentation des défis](../../../Docs/Présentation_des_défis.md).

## Question

Comment l'évolution du réseau de transport francilien se situe-t-elle par rapport à celle de l'emploi entre 2015 et 2025 ? La présentation pose aussi la question des zones qui gagnent en accessibilité ou restent à l'écart. Les données disponibles ne permettent pas de mesurer directement cette accessibilité ni d'établir un effet causal.

## Public et usage

La visualisation s'adresse au public du Hackaviz et aux personnes qui s'intéressent aux mobilités et à l'emploi en Île-de-France. Elle permet de situer les extensions du réseau, les pôles d'emploi et les évolutions observées sur le territoire.

## Idée de visualisation

Le [site interactif](https://dataviz-rhizome-liard.vercel.app/) propose un parcours en trois graphiques : le réseau ferré, les demandeurs d'emploi par zone d'emploi et les pôles d'emploi par département. Seul le graphique 1, consacré au réseau ferré, est également fourni en PNG et en PDF, avec ses données et son script de génération. La [documentation des visualisations](production/docs/visualisation.md) présente les livrables et les travaux antérieurs.

## Périmètre

Le territoire étudié est l'Île-de-France. La présentation propose les dates 2015, 2019 et 2025. Les planches disponibles comparent principalement 2015 et 2025 pour le réseau et l'emploi privé, 2016 et 2024 pour les demandeurs d'emploi, et 2017 et 2023 pour l'emploi total. Une comparaison communale complète pour 2019 n'est pas documentée dans les données préparées.

## Décisions et questions ouvertes

| Sujet | Décision ou question | Date |
|---|---|---|
| Accessibilité | Les ouvertures de lignes et la présence d'une gare ne mesurent pas les temps de trajet ou l'accès effectif à l'emploi. | Non précisée |
| Relation causale | Les cartes décrivent des évolutions ; elles ne démontrent pas l'effet d'une ouverture sur l'emploi. | Non précisée |
| Comparaison 2019 | Vérifier les données communales et le traitement nécessaires avant de présenter cette date comme un résultat. | Non précisée |

## Site interactif

Le [site web](production/web/README.md) intègre les trois cartes au récit. Ses [spécifications](production/web/docs/specifications.md) décrivent les vues et leurs limites.
