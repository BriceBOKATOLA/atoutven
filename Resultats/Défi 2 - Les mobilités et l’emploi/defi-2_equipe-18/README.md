# Le réseau mène à Paris, pas aux emplois de banlieue

**Équipe :** équipe 18 : Melvyn MOTHO, Pierre THAI, Maroua Zoubir
**Mail(s) de contact :** melvynmotho@gmail.com
**Défi :** Défi 2 : Les mobilités et l'emploi

## Notre question

Les transports en commun d'Île-de-France permettent-ils d'atteindre les lieux où travaillent ceux dont le métier se fait sur place (employés et ouvriers, qui ne peuvent presque pas télétravailler) ? Et où des solutions complémentaires (vélo, navettes, covoiturage) seraient-elles les plus utiles ?

## Notre visualisation

*[Lien vers l'application en ligne : à venir]*

## Les données utilisées

Toutes les données sont publiques et ouvertes. Inventaire complet, licences et explication du millésime du recensement : [`production/data/README.md`](production/data/README.md).

| Source | Jeu de données | Lien |
|---|---|---|
| INSEE | Recensement 2023, mobilités professionnelles (fichier détail) | [insee.fr](https://www.insee.fr/fr/statistiques/9004795) |
| IDFM | Offre hebdomadaire moyenne hors vacances (2025) | [data.iledefrance-mobilites.fr](https://data.iledefrance-mobilites.fr/explore/dataset/offre_hebdomadaire_moyenne_hors_vacances/) |
| IDFM | Validations sur le réseau ferré, par jour (juillet 2025 à juin 2026) | [data.iledefrance-mobilites.fr](https://data.iledefrance-mobilites.fr/explore/dataset/validations-reseau-ferre-nombre-validations-par-jour-2eme-trimestre/) |
| IDFM | Zones de correspondance (référentiel des arrêts) | [data.iledefrance-mobilites.fr](https://data.iledefrance-mobilites.fr/explore/dataset/zones-de-correspondance/) |
| État | Communes d'Île-de-France (centres, contours) | [geo.api.gouv.fr](https://geo.api.gouv.fr/decoupage-administratif/communes) |
| État | Jours fériés, calendrier scolaire | [calendrier.api.gouv.fr](https://calendrier.api.gouv.fr/jours-feries/), [data.education.gouv.fr](https://data.education.gouv.fr/explore/dataset/fr-en-calendrier-scolaire/) |

## Les outils employés

Python 3.13, pandas, pyarrow ; *[application : à venir]*.

## Reproduire les résultats

```bash
cd production
pip install -r requirements.txt
python src/00_telecharger_donnees.py      # télécharge les données (environ 600 Mo)
python src/01_explorer_mobpro.py          # puis les scripts 02 à 08, dans l'ordre
```

## Licence

Code sous licence [MIT](https://github.com/hackathons-mobilites/hackaviz_2026/blob/main/Docs/License.md). Résultats et données dérivées sous Licence Ouverte 2.0. Textes et visuels sous licence CC-BY 4.0.
