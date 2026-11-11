# Le réseau mène à Paris, pas aux emplois de banlieue

**Équipe :** équipe 18 : Melvyn MOTHO, Pierre THAI, Maroua Zoubir
**Mail(s) de contact :** melvynmotho@gmail.com
**Défi :** Défi 2 : Les mobilités et l'emploi

## Notre question

Les transports en commun d'Île-de-France permettent-ils d'atteindre les lieux où travaillent les employés et les ouvriers, qui ne peuvent presque pas télétravailler ? Et où des solutions complémentaires (vélo, navettes, covoiturage) seraient-elles les plus utiles ?

## Ce que montrent les données

**Ce n'est pas le métier qui éloigne du réseau, c'est le lieu de travail.**

- Hors de Paris, **1 emploi d'ouvrier sur 4** se trouve dans une commune sans gare (ni métro, ni RER, ni train, ni tram), contre **1 emploi de cadre sur 8**.
- Pour aller d'une commune de banlieue à une autre, la voiture passe d'environ un trajet sur deux quand le lieu de travail a une gare à près de trois sur quatre quand il n'en a pas, **pour tous les métiers, cadres compris** (77 % sans gare).
- Ce résultat **ne s'explique pas par le revenu** : à niveau de vie égal de la commune de résidence, l'absence de gare fait toujours monter la voiture de 17 à 28 points.
- La nuit, il passe **13 fois moins** de bus et de trains qu'à l'heure de pointe, partout en Île-de-France ; or les ouvriers travaillent deux fois plus souvent la nuit que les cadres.
- Deux cibles pour réduire la voiture : **339 000 trajets en voiture de moins de 5 km** entre communes de banlieue (vélo), et **322 000 emplois d'employés et d'ouvriers dans des communes sans gare** (navettes, covoiturage), dont Gonesse, Guyancourt, Bonneuil-sur-Marne et Les Ulis.

## Notre visualisation

Une application web en forme de récit : une page par question, à parcourir comme les stations d'une ligne de métro.

*[Lien vers l'application en ligne : à venir]* · Code : [`production/application/`](production/application/)

**Accessibilité, intégrée à chaque page :** bouton « Écouter » (synthèse vocale du navigateur, sans service extérieur), tableau des chiffres sous chaque graphique, aucune information portée par la couleur seule, navigation au clavier vérifiée, page déclarée en français, affichage adapté au téléphone et au zoom. Reste à faire : un test avec un lecteur d'écran.

## Notre démarche

1. **Chaque idée devient une hypothèse**, avec un critère de réponse écrit **avant** d'ouvrir les données, pour ne pas adapter le critère au résultat.
2. **Les hypothèses réfutées sont gardées et montrées.** Par exemple : le réseau n'est pas plus faible la nuit là où travaillent les ouvriers (il l'est partout) ; la baisse de fréquentation du vendredi ne suit pas la part de cadres.
3. **Les résultats sont contrôlés** contre les objections prévisibles (le revenu, la destination du trajet).
4. **Les erreurs sont corrigées et visibles dans l'historique.** Dans l'offre IDFM, 90 % des arrêts de train et de RER n'ont pas de code commune : la première version de l'analyse ne trouvait que 147 communes avec gare. Le référentiel des arrêts permet d'en rattacher 407 ; les analyses concernées ont été relancées, sans changer leurs conclusions.
5. **Chaque chiffre affiché vient d'un script**, jamais d'une saisie à la main (sauf les parts de télétravail et les horaires de travail, tirés d'une publication INSEE citée).

| Analyse | Script | Résultat |
|---|---|---|
| Moyen de transport selon le métier | `02` | Les cadres prennent le plus les transports en commun, sauf à Paris |
| Lieux de travail selon le métier | `03` | En grande couronne, 51 % des ouvriers travaillent dans une autre commune de banlieue (cadres : 35 %) |
| Fréquentation des gares le lundi et le vendredi | `04` | Le vendredi baisse partout ; le lundi, la baisse suit les quartiers de cadres |
| Offre de transport la nuit et le dimanche | `05` | 7,6 % des passages de la pointe la nuit, 47 % le dimanche, partout |
| Trajets courts en voiture, pôles d'emploi sans desserte de nuit | `06` | 22 % des trajets en voiture entre banlieues font moins de 5 km |
| Emplois dans une commune sans gare | `07` | 23 % des emplois d'ouvriers hors Paris, 13 % de ceux des cadres |
| Carte des emplois sans gare | `08` | 154 communes sans gare comptent au moins 500 emplois d'employés et d'ouvriers |
| Revenu et choix de la voiture | `09` | L'effet de la gare tient à tout niveau de revenu |

## Les données utilisées

Toutes les données sont publiques et ouvertes, récupérées depuis leurs **fichiers de téléchargement ou interfaces officiels** (aucune récupération automatique de pages web). Inventaire complet, licences vérifiées et explication du millésime : [`production/data/README.md`](production/data/README.md).

**Pourquoi le « recensement 2023 » :** il combine les enquêtes annuelles de 2021 à 2025 (celle de 2021 a été reportée à cause du Covid) et a été publié par l'INSEE le 25 juin 2026. C'est le plus récent disponible : il décrit la situation après le Covid, pas l'année 2023 seule.

| Source | Jeu de données | Lien |
|---|---|---|
| INSEE | Recensement 2023, mobilités professionnelles (fichier détail) | [insee.fr](https://www.insee.fr/fr/statistiques/9004795) |
| INSEE | Revenus et pauvreté au niveau local en 2023 (Filosofi) | [insee.fr](https://www.insee.fr/fr/statistiques/8984752) |
| INSEE | Organisation du temps de travail, enquête Emploi 2025 (publication) | [insee.fr](https://www.insee.fr/fr/statistiques/8733073) |
| IDFM | Offre hebdomadaire moyenne hors vacances (2025) | [data.iledefrance-mobilites.fr](https://data.iledefrance-mobilites.fr/explore/dataset/offre_hebdomadaire_moyenne_hors_vacances/) |
| IDFM | Validations sur le réseau ferré, par jour (juillet 2025 à juin 2026) | [data.iledefrance-mobilites.fr](https://data.iledefrance-mobilites.fr/explore/dataset/validations-reseau-ferre-nombre-validations-par-jour-2eme-trimestre/) |
| IDFM | Zones de correspondance (référentiel des arrêts) | [data.iledefrance-mobilites.fr](https://data.iledefrance-mobilites.fr/explore/dataset/zones-de-correspondance/) |
| État | Communes d'Île-de-France (centres, contours) | [geo.api.gouv.fr](https://geo.api.gouv.fr/decoupage-administratif/communes) |
| État | Jours fériés, calendrier scolaire | [calendrier.api.gouv.fr](https://calendrier.api.gouv.fr/jours-feries/), [data.education.gouv.fr](https://data.education.gouv.fr/explore/dataset/fr-en-calendrier-scolaire/) |

## Les limites

- **L'accès au réseau est mesuré par la présence d'une gare dans la commune**, pas par un temps de trajet : c'est plus grossier, mais léger à calculer et facile à mettre à jour. Une gare peut se trouver juste à côté, dans la commune voisine.
- Tout est calculé à l'échelle de la **commune**, pas du quartier.
- Le moyen de transport est celui **déclaré** au recensement (le principal), pas les trajets réellement effectués.
- L'offre IDFM compte des passages **prévus** : elle ne dit ni qui voyage, ni pourquoi.
- Les parts de télétravail et les horaires de travail sont des chiffres **France entière**.

## Les outils employés

Python 3.13, pandas, pyarrow (traitements) ; Streamlit et Altair (application). Tous open source.

## Reproduire les résultats

```bash
cd production
pip install -r requirements.txt
python src/00_telecharger_donnees.py          # télécharge les données (environ 600 Mo)
python src/01_explorer_mobpro.py              # puis les scripts 02 à 09, dans l'ordre

cd application
pip install -r requirements.txt
python preparation/preparer_offre_horaire.py  # prépare les passages par heure
streamlit run app.py                          # lance l'application
```

## Et la suite ?

- **La ponctualité des lignes** : avoir une gare ne suffit pas, encore faut-il que le train soit à l'heure. Une analyse de la ponctualité des lignes RER et Transilien est en cours (branche de travail de l'équipe).
- **Des temps de trajet réels**, porte à porte, pour remplacer la présence d'une gare dans la commune.
- **Une analyse plus fine que la commune**, au niveau du quartier.

## Licence

Code sous licence [MIT](https://github.com/hackathons-mobilites/hackaviz_2026/blob/main/Docs/License.md). Résultats et données dérivées sous Licence Ouverte 2.0. Textes et visuels sous licence CC-BY 4.0.
