# Les données du projet

Toutes les données utilisées sont **publiques et ouvertes**. Elles ne sont pas copiées dans ce dépôt (plus de 600 Mo) : le script `src/00_telecharger_donnees.py` les récupère depuis leurs sources officielles.

```bash
# depuis le dossier production/
python src/00_telecharger_donnees.py
```

Les fichiers sont rangés dans `data/brut/`, un dossier par source. Seuls les fichiers réellement lus par les scripts sont téléchargés.

## Inventaire

| Dossier | Source | Ce qu'on en tire | Version utilisée | Licence |
|---|---|---|---|---|
| `insee_mobpro_2023/` | [INSEE, recensement 2023, mobilités professionnelles (fichier détail)](https://www.insee.fr/fr/statistiques/9004795) | Commune de résidence et de travail, moyen de transport et catégorie socioprofessionnelle de chaque actif | Millésime 2023, publié le 25/06/2026 (voir ci-dessous) | [Licence Ouverte 2.0](https://www.insee.fr/fr/information/2381863) |
| `insee_mobpro_2022/` | [INSEE, recensement 2022, mobilités professionnelles](https://www.insee.fr/fr/statistiques/8589904) | Comparaison des millésimes (script 01) | Millésime 2022 | Licence Ouverte 2.0 |
| `insee_filosofi_2023/` | [INSEE, revenus et pauvreté au niveau local en 2023 (Filosofi)](https://www.insee.fr/fr/statistiques/8984752) | Niveau de vie médian de chaque commune (script 09 : le revenu explique-t-il le choix de la voiture ?) | Millésime 2023, publié le 06/08/2026 (nouvelle méthode, non comparable aux millésimes avant 2021) | [Licence Ouverte 2.0](https://www.insee.fr/fr/information/2381863) |
| `idfm_offre_hebdo_2025/` | [IDFM, offre hebdomadaire moyenne hors vacances](https://data.iledefrance-mobilites.fr/explore/dataset/offre_hebdomadaire_moyenne_hors_vacances/) | Nombre de passages prévus par arrêt, ligne, heure et jour ; communes avec gare | Semaine type 2025 hors vacances | Licence Ouverte 2.0 |
| `idfm_validations_ferre/` | IDFM, validations sur le réseau ferré, nombre de validations par jour ([exemple : 2e trimestre](https://data.iledefrance-mobilites.fr/explore/dataset/validations-reseau-ferre-nombre-validations-par-jour-2eme-trimestre/)) | Fréquentation par gare et par jour (script 04) | 4 trimestres : juillet 2025 à juin 2026 | Licence Ouverte 2.0 |
| `idfm_referentiel_arrets/` | [IDFM, zones de correspondance](https://data.iledefrance-mobilites.fr/explore/dataset/zones-de-correspondance/) | Code commune de chaque gare | Version du 25/10/2026 (mise à jour quotidienne par IDFM) | Licence Ouverte 2.0 |
| `calendrier/` | [Jours fériés](https://calendrier.api.gouv.fr/jours-feries/) et [calendrier scolaire](https://data.education.gouv.fr/explore/dataset/fr-en-calendrier-scolaire/) (Éducation nationale) | Écarter les jours fériés et les vacances de la zone C | Années scolaires 2024-2025 et 2025-2026 | Licence Ouverte 2.0 |
| `geo_communes_idf/` | [geo.api.gouv.fr, découpage administratif](https://geo.api.gouv.fr/decoupage-administratif/communes) | Centres et contours des 1 266 communes (distances, cartes) | Téléchargés le 25/10/2026 | Licence Ouverte 2.0 |
| `francetravail_bmo/` | [France Travail, enquête Besoins en main-d'œuvre](https://www.data.gouv.fr/datasets/enquete-besoins-en-main-doeuvre-bmo) | Projets de recrutement et projets jugés difficiles, par bassin d'emploi et métier (script 10) | Enquête 2026, publiée le 21/04/2026 | Licence Ouverte 2.0 |
| `sncf_ponctualite/` | [SNCF, régularité mensuelle Transilien](https://ressources.data.sncf.com/explore/dataset/ponctualite-mensuelle-transilien/) | Ponctualité des 13 lignes de RER et Transilien (script 11). Métro, tram, bus et ligne V non publiés dans ce jeu | Janvier 2013 à octobre 2026 (moyenne des 12 derniers mois utilisée) | **ODbL** : le résultat dérivé `application/donnees/ponctualite_lignes.csv` est lui aussi sous ODbL |
| `idfm_referentiel_lignes/` | [IDFM, référentiel des lignes](https://data.iledefrance-mobilites.fr/explore/dataset/referentiel-des-lignes/) | Couleurs officielles des lignes ferrées, pour les pictogrammes de la page « Chercher ma commune » | Version du 11/11/2026 | **ODbL** ; le fichier dérivé `application/donnees/couleurs_lignes.csv` est lui aussi sous ODbL |

Les licences des jeux IDFM et du calendrier scolaire ont été vérifiées le 11/11/2026 dans les métadonnées de leurs portails.

Données téléchargées les 24 et 25 octobre 2026 (revenus Filosofi : le 11 novembre 2026 ; enquête Besoins en main-d'œuvre et référentiel des lignes : le 11 novembre 2026). Les résultats du dossier `resultats/` correspondent à ces versions.

## Pourquoi le « recensement 2023 » est la donnée la plus récente

Le recensement ne se fait plus en une seule fois : l'INSEE interroge une partie des communes chaque année, puis combine **cinq enquêtes annuelles successives**. Le résultat porte le nom de l'année du milieu ([INSEE, présentation du recensement](https://www.insee.fr/fr/information/2383265)).

- Le millésime **2023** combine les enquêtes de **2021 à 2025**. L'enquête 2021 a été reportée à cause du Covid ([INSEE](https://www.insee.fr/fr/information/4985873)) : les réponses viennent donc surtout des enquêtes **2022 à 2025**, l'INSEE ayant compensé l'année manquante par des méthodes statistiques.
- Il a été **publié le 25 juin 2026**. C'est le millésime le plus récent disponible pendant le hackathon.
- Ces données décrivent donc la situation **après le Covid**, avec le télétravail installé, et non l'année 2023 seule.

## Précautions d'usage

- **Recensement :** chaque ligne représente plusieurs personnes. On pondère toujours par la variable `IPONDI`, et on manipule avec prudence les effectifs inférieurs à 200 ([conseils de l'INSEE](https://www.insee.fr/fr/information/2383243)).
- **Moyen de transport :** dans le recensement, la modalité « voiture » inclut les camions et fourgonnettes.
- **Offre IDFM :** ce sont des passages **prévus**, pas réellement effectués. Ils ne disent ni combien de personnes voyagent, ni pourquoi.
- **Codes commune des gares :** dans le fichier d'offre, 90 % des arrêts de train et de RER n'ont pas de code commune. Les scripts 05 et 07 le complètent avec le référentiel des zones de correspondance.
