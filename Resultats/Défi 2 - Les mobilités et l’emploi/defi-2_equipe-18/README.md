# Trajemploi

**L'emploi au-delà du rail**

**Équipe :** équipe 18 : Melvyn MOTHO, Pierre THAI, Maroua Zoubir
**Mail(s) de contact :** melvynmotho@gmail.com
**Défi :** Défi 2 : Les mobilités et l'emploi

Une application web en forme de récit, qui montre que l'accès à l'emploi en transports en commun dépend moins du métier que du lieu de travail : hors de Paris, les emplois sans gare sont surtout ceux des employés et des ouvriers, et sans gare, la voiture s'impose pour tous.

**Application en ligne :** [hackaviz2026-trajemploi-idfm.streamlit.app](https://hackaviz2026-trajemploi-idfm.streamlit.app/) · **Code :** [`production/application/`](production/application/)

## Présentation du projet

Ce projet a été développé dans le cadre du Hackaviz Mobilités 2026 spécial dataviz, organisé par Île-de-France Mobilités du 2 au 26 novembre 2026. Pour en savoir plus, voici le [Guide des participants et participantes](https://github.com/hackathons-mobilites/hackaviz_2026/blob/main/README.md).

### Le problème et la proposition de valeur (notre question)

**Les deux questions du défi 2 :** les transports en commun permettent-ils d'accéder à l'emploi ? Sur quels territoires d'autres solutions de mobilité seraient-elles utiles ?

**Pourquoi nous regardons les employés et les ouvriers :** le télétravail a changé les trajets des cadres, pas les leurs. Ils sont 2 millions en Île-de-France à ne presque jamais pouvoir télétravailler (cuisine, soin, nettoyage, logistique, sécurité, bâtiment…) : pour eux, chaque journée de travail commence par un trajet. Si l'offre de transport ne les mène pas à leur lieu de travail, ou ne circule pas à leurs horaires, ils n'ont pas d'autre solution que la voiture.

**Notre problématique :**

> **L'offre de transport en commun d'Île-de-France mène-t-elle les employés et les ouvriers jusqu'à leur lieu de travail, et à leurs horaires ? Sinon, où et pour qui d'autres solutions seraient-elles les plus utiles ?**

**Les usagers cibles :**

- **Île-de-France Mobilités** : savoir où agir et avec quelle solution (le vélo là où les trajets en voiture sont courts, des navettes vers les emplois sans gare, l'offre de nuit) et pour qui.
- **Les communes et intercommunalités** : la page « Chercher ma commune » montre où travaillent leurs habitants, cadres, employés ou ouvriers, et si ces lieux de travail ont une gare.
- **Les habitants** : comprendre le sujet en quelques minutes, puis regarder leur propre commune et leur propre catégorie.
- **Toute personne, quelle que soit sa façon de lire** : chaque page se lit aussi à l'oreille (voir l'accessibilité ci-dessous).

**Petite et grande couronne :** la petite couronne regroupe les Hauts-de-Seine, la Seine-Saint-Denis et le Val-de-Marne ; la grande couronne, la Seine-et-Marne, les Yvelines, l'Essonne et le Val-d'Oise.

**D'où viennent nos trois catégories :** cadres, employés et ouvriers ne sont pas un classement fait par nous. C'est la nomenclature officielle de l'INSEE, la variable « groupe socioprofessionnel en 6 postes » du recensement (codes 3, 5 et 6 de la PCS 2020), présente pour chaque actif dans le fichier des mobilités professionnelles. Toutes nos hypothèses tirées du recensement ont été testées sur ces groupes (l'analyse des recrutements difficiles utilise, elle, les familles de métiers publiées par France Travail). Ce que recouvre chaque groupe : les **cadres** (ingénieurs, cadres d'entreprise, professeurs…), les **employés** (métiers de bureau, de commerce et de service : vendeurs, caissiers, aides-soignants, agents d'accueil, agents de sécurité…) et les **ouvriers** (usine, chantier, entrepôt, conduite de véhicules…). Un salarié d'usine est donc un ouvrier, pas un employé. Nous en gardons trois sur six : les employés et les ouvriers, qui ne peuvent presque pas télétravailler, et les cadres comme point de comparaison. Les trois autres groupes sont écartés : les agriculteurs, les artisans, commerçants et chefs d'entreprise (souvent installés sur leur lieu de travail), et les professions intermédiaires (un groupe mélangé, entre les deux).

**Ce que nous ne traitons pas** (et pourquoi) : la durée réelle des trajets et les correspondances (aucune donnée ouverte ne les donne par trajet domicile-travail), la fréquentation de nuit (on connaît l'offre prévue, pas qui la prend), les raisons des difficultés de recrutement (l'enquête de France Travail ne les donne pas par territoire).

### La solution (notre visualisation)

Une application web en forme de récit : une page par question, à parcourir comme les stations d'une ligne de métro. Chaque page donne un titre qui répond à la question, un graphique principal et une phrase « À retenir » ; le détail se déplie dans des blocs « Pour aller plus loin ».

| Page | Question | Ce que nous mesurons |
|---|---|---|
| 1 | Qui ne peut pas télétravailler ? | Part du télétravail par métier |
| 2 | Où sont leurs emplois ? | Part des emplois situés dans une commune sans gare (ni métro, ni RER, ni train, ni tram) |
| 3 | Comment vont-ils travailler ? | Part de la voiture selon que le lieu de travail a une gare ou non |
| 4 | Que reste-t-il de l'offre de transport la nuit ? | Passages prévus heure par heure, communes sans aucune offre de nuit |
| 5 | Quelles solutions, et où ? | Trajets courts en voiture (vélo), emplois sans gare (navettes), recrutements jugés difficiles par territoire |
| 6 | Chercher ma commune | Où travaillent les habitants de chaque commune, avec un interrupteur par catégorie (cadres, employés, ouvriers : une ou plusieurs) |

Une conclusion reprend le message et propose trois actions à Île-de-France Mobilités.

**Accessibilité numérique, intégrée à chaque page** (jamais une page à part) :

- un bouton « Écouter » lit un **commentaire complet** de la page, dans l'ordre où un voyant la lit : où l'on est, la réponse, ce que montre le graphique avec ses chiffres, le chiffre clé, « À retenir », la limite, ce qu'il y a à déplier et la page suivante. Chaque bloc « Pour aller plus loin » a son propre bouton ;
- un bouton « **Écouter le graphique en sons** » sur chaque page à graphique (stations 1 à 6) : chaque valeur devient une note, plus aiguë quand la valeur est plus haute ; on entend par exemple l'écart entre les métiers, le saut de la voiture quand il n'y a pas de gare, ou la chute de l'offre après minuit ;
- pour les lecteurs d'écran, une **description d'ensemble** de chaque graphique (la comparaison, pas un texte par barre) et de **vrais tableaux** de données (titre, en-têtes) ; sur la page « Chercher ma commune », le résultat est annoncé dès qu'on change de commune ou de catégorie ;
- aucune information portée par la couleur seule, textes de 14 px minimum, navigation au clavier, page déclarée en français, affichage adapté au téléphone et au zoom ;
- synthèse vocale et sons produits par le navigateur (Web Speech API, Web Audio API) : aucun service extérieur ;
- contrôle automatique axe-core (règles WCAG 2.1 A et AA) : 0 violation sur les 8 pages, blocs dépliés. Reste à faire : un test par une personne non voyante, avec son lecteur d'écran.

#### Ce que montrent les données

**Ce n'est pas le métier qui éloigne du réseau, c'est le lieu de travail.**

- Hors de Paris, **1 emploi d'ouvrier sur 4** se trouve dans une commune sans gare (ni métro, ni RER, ni train, ni tram), contre **1 emploi de cadre sur 8**.
- Pour aller d'une commune de banlieue à une autre, la voiture passe d'environ un trajet sur deux quand le lieu de travail a une gare à près de trois sur quatre quand il n'en a pas, **pour tous les métiers, cadres compris** (77 % sans gare).
- Ce résultat **ne s'explique pas par le revenu** : à niveau de vie égal de la commune de résidence, l'absence de gare fait toujours monter la voiture de 17 à 28 points.
- La nuit, l'offre de transport est **13 fois moins** importante qu'entre 7h et 10h, sur l'ensemble de l'Île-de-France, et 6 communes sur 10 n'en ont plus aucune ; or les ouvriers travaillent deux fois plus souvent la nuit que les cadres.
- Chaque territoire a sa solution :
  - **le vélo en petite couronne** : 22 % des trajets en voiture d'une commune de banlieue à une autre font moins de 5 km (339 000 sur 1,54 million), et 31 % en petite couronne ;
  - **des navettes en grande couronne** : hors de Paris, 20 % des postes d'employés et d'ouvriers sont dans une commune sans gare (322 000 sur 1,59 million), et 32 % en grande couronne. Les communes qui en comptent le plus sont Gonesse, Guyancourt, Bonneuil-sur-Marne et Les Ulis.
- Les employeurs de grande couronne jugent difficiles 41 % de leurs projets de recrutement, contre 29 % à Paris (France Travail, 2026). C'est une coïncidence géographique : l'enquête ne dit pas que le transport en est la cause.
- **Une gare dans la commune ne suffit pas** (constat exploratoire, script `12_gare_ne_suffit_pas.py`) : dans 151 des 290 communes d'emploi qui ont une gare, au moins 2 actifs sur 3 viennent encore en voiture (seuil choisi par l'équipe ; communes d'au moins 200 trajets). Le constat vaut pour les cadres comme pour les employés et les ouvriers ; la donnée ne dit pas pourquoi (distance, horaires, directions).

#### Les données utilisées

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
| IDFM | Référentiel des lignes (couleurs officielles des lignes) | [data.iledefrance-mobilites.fr](https://data.iledefrance-mobilites.fr/explore/dataset/referentiel-des-lignes/) |
| SNCF | Régularité mensuelle Transilien (ponctualité des lignes de RER et de train) | [ressources.data.sncf.com](https://ressources.data.sncf.com/explore/dataset/ponctualite-mensuelle-transilien/) |
| France Travail | Enquête Besoins en main-d'œuvre 2026 | [data.gouv.fr](https://www.data.gouv.fr/datasets/enquete-besoins-en-main-doeuvre-bmo) |
| État | Communes d'Île-de-France (centres, contours) | [geo.api.gouv.fr](https://geo.api.gouv.fr/decoupage-administratif/communes) |
| État | Jours fériés, calendrier scolaire | [calendrier.api.gouv.fr](https://calendrier.api.gouv.fr/jours-feries/), [data.education.gouv.fr](https://data.education.gouv.fr/explore/dataset/fr-en-calendrier-scolaire/) |

### Les problèmes surmontés et les enjeux en matière de données

#### Notre démarche

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
| Carte des emplois sans gare | `08` | 154 communes sans gare comptent au moins 500 postes d'employés et d'ouvriers |
| Revenu et choix de la voiture | `09` | L'effet de la gare tient à tout niveau de revenu |
| Recrutements jugés difficiles par territoire | `10` | 41 % des projets en grande couronne, 29 % à Paris |
| Ponctualité des lignes de RER et de train | `11` | Les 4 lignes qui desservent le plus de postes d'employés et d'ouvriers sont à 87,7 % à l'heure, les 9 autres à 91,1 % |
| Une gare dans la commune suffit-elle ? (exploratoire) | `12` | Dans 151 des 290 communes avec gare, au moins 2 actifs sur 3 viennent encore en voiture |

#### Les limites

- **L'accès au réseau est mesuré par la présence d'une gare dans la commune**, pas par un temps de trajet : c'est plus grossier, mais léger à calculer et facile à mettre à jour. Une gare peut se trouver juste à côté, dans la commune voisine.
- Tout est calculé à l'échelle de la **commune**, pas du quartier.
- Le moyen de transport est celui **déclaré** au recensement (le principal), pas les trajets réellement effectués.
- L'offre IDFM compte des passages **prévus** : elle ne dit ni qui voyage, ni pourquoi.
- Les distances des trajets courts sont mesurées **à vol d'oiseau** entre les centres des communes.
- Les parts de télétravail et les horaires de travail sont des chiffres **France entière**.

#### Nos recommandations à Île-de-France Mobilités sur les données

- **Compléter le code commune des arrêts dans l'offre hebdomadaire** : il manque pour 90 % des arrêts de train et de RER. Il a fallu le reprendre du référentiel des arrêts ; sans cette correction, on aurait compté 147 communes avec gare au lieu de 407.
- **Publier des temps de parcours en transports en commun entre communes**, aux heures de pointe et la nuit, en données ouvertes et simples à télécharger : ils remplaceraient notre mesure la plus grossière, la présence d'une gare dans la commune.
- **Réunir la ponctualité de tous les modes dans un même jeu de données ouvert** : celui que nous avons utilisé ne couvre que 13 lignes de RER et de Transilien, sans le métro, le tram ni le bus.

### Et la suite ?

- **La ponctualité de tout le réseau** : notre analyse couvre les 13 lignes de RER et Transilien publiées par la SNCF ; le métro, le tram et le bus compléteraient le tableau.
- **Des temps de trajet réels**, porte à porte, pour remplacer la présence d'une gare dans la commune.
- **La distance réelle entre les emplois et la gare** (base Sirene géolocalisée de l'INSEE et arrêts IDFM, données ouvertes) : elle dirait pourquoi une gare dans la commune ne suffit pas toujours.
- **Une analyse plus fine que la commune**, au niveau du quartier.
- **Un test de l'application par des personnes non voyantes**, avec leur lecteur d'écran.

## Installation et utilisation (les outils employés)

**Outils :** Python 3.13, pandas, pyarrow et openpyxl (traitements) ; Streamlit (application). Les graphiques et les cartes sont dessinés en SVG par notre code, sans bibliothèque de graphiques. Tous open source.

```bash
# Lancer l'application (les fichiers de données préparés sont fournis dans production/application/donnees/)
cd production/application
pip install -r requirements.txt
streamlit run app.py

# Refaire les analyses depuis les données brutes
cd production
pip install -r requirements.txt
python src/00_telecharger_donnees.py          # télécharge les données (environ 600 Mo)
python src/01_explorer_mobpro.py              # puis les scripts 02 à 12, dans l'ordre

# Refaire les fichiers de l'application (chaque script dit en tête ce qu'il prépare)
cd production/application
python preparation/preparer_offre_horaire.py  # et les autres scripts du dossier preparation/
```

Un test vérifie que chaque page contient les éléments des maquettes validées : `python tests/verifier_conformite.py` (depuis `production/application/`).

## La licence

Code sous licence [MIT](https://github.com/hackathons-mobilites/hackaviz_2026/blob/main/Docs/License.md). Résultats et données dérivées sous Licence Ouverte 2.0, sauf ceux tirés de sources sous ODbL, qui restent sous ODbL : ponctualité des lignes (`production/resultats/11_h24/`, `application/donnees/ponctualite_lignes.csv`) et couleurs des lignes (`application/donnees/couleurs_lignes.csv`). Textes et visuels sous licence CC-BY 4.0.
