# Le réseau mène à Paris, pas aux emplois de banlieue

**Équipe :** équipe 18 : Melvyn MOTHO, Pierre THAI, Maroua Zoubir
**Mail(s) de contact :** melvynmotho@gmail.com
**Défi :** Défi 2 : Les mobilités et l'emploi

## La problématique

**Les deux questions du défi 2 :** les transports en commun permettent-ils d'accéder à l'emploi ? Sur quels territoires d'autres solutions de mobilité seraient-elles utiles ?

**Pourquoi nous regardons les employés et les ouvriers :** le télétravail a changé les trajets des cadres, pas les leurs. Ils sont 2 millions en Île-de-France à ne presque jamais pouvoir télétravailler (cuisine, soin, nettoyage, logistique, sécurité, bâtiment…) : pour eux, chaque journée de travail commence par un trajet. Si l'offre de transport ne les mène pas à leur lieu de travail, ou ne circule pas à leurs horaires, ils n'ont pas d'autre solution que la voiture.

**Notre problématique :**

> **L'offre de transport en commun d'Île-de-France mène-t-elle les employés et les ouvriers jusqu'à leur lieu de travail, et à leurs horaires ? Sinon, où et pour qui d'autres solutions seraient-elles les plus utiles ?**

Elle se découpe en cinq questions, une par page de l'application :

| Page | Question | Ce que nous mesurons |
|---|---|---|
| 1 | Qui ne peut pas télétravailler ? | Part du télétravail par métier |
| 2 | Où sont leurs emplois ? | Part des emplois situés dans une commune sans gare (ni métro, ni RER, ni train, ni tram) |
| 3 | Comment vont-ils travailler ? | Part de la voiture selon que le lieu de travail a une gare ou non |
| 4 | Que reste-t-il de l'offre de transport la nuit ? | Passages prévus heure par heure, communes sans aucune offre de nuit |
| 5 | Quelles solutions, et où ? | Trajets courts en voiture (vélo), emplois sans gare (navettes), recrutements jugés difficiles par territoire |

Une sixième page permet à chacun de chercher sa commune.

**Petite et grande couronne :** la petite couronne regroupe les Hauts-de-Seine, la Seine-Saint-Denis et le Val-de-Marne ; la grande couronne, la Seine-et-Marne, les Yvelines, l'Essonne et le Val-d'Oise.

**D'où viennent nos trois catégories :** cadres, employés et ouvriers ne sont pas un classement fait par nous. C'est la nomenclature officielle de l'INSEE, la variable « groupe socioprofessionnel en 6 postes » du recensement (codes 3, 5 et 6 de la PCS 2020), présente pour chaque actif dans le fichier des mobilités professionnelles. Toutes nos hypothèses tirées du recensement ont été testées sur ces groupes (l'analyse des recrutements difficiles utilise, elle, les familles de métiers publiées par France Travail). Ce que recouvre chaque groupe : les **cadres** (ingénieurs, cadres d'entreprise, professeurs…), les **employés** (métiers de bureau, de commerce et de service : vendeurs, caissiers, aides-soignants, agents d'accueil, agents de sécurité…) et les **ouvriers** (usine, chantier, entrepôt, conduite de véhicules…). Un salarié d'usine est donc un ouvrier, pas un employé. Nous en gardons trois sur six : les employés et les ouvriers, qui ne peuvent presque pas télétravailler, et les cadres comme point de comparaison. Les trois autres groupes sont écartés : les agriculteurs, les artisans, commerçants et chefs d'entreprise (souvent installés sur leur lieu de travail), et les professions intermédiaires (un groupe mélangé, entre les deux).

**Ce que nous ne traitons pas** (et pourquoi) : la durée réelle des trajets et les correspondances (aucune donnée ouverte ne les donne par trajet domicile-travail), la fréquentation de nuit (on connaît l'offre prévue, pas qui la prend), les raisons des difficultés de recrutement (l'enquête de France Travail ne les donne pas par territoire).

## Ce que montrent les données

**Ce n'est pas le métier qui éloigne du réseau, c'est le lieu de travail.**

- Hors de Paris, **1 emploi d'ouvrier sur 4** se trouve dans une commune sans gare (ni métro, ni RER, ni train, ni tram), contre **1 emploi de cadre sur 8**.
- Pour aller d'une commune de banlieue à une autre, la voiture passe d'environ un trajet sur deux quand le lieu de travail a une gare à près de trois sur quatre quand il n'en a pas, **pour tous les métiers, cadres compris** (77 % sans gare).
- Ce résultat **ne s'explique pas par le revenu** : à niveau de vie égal de la commune de résidence, l'absence de gare fait toujours monter la voiture de 17 à 28 points.
- La nuit, l'offre de transport est **13 fois moins** importante qu'entre 7h et 10h, sur l'ensemble de l'Île-de-France, et 6 communes sur 10 n'en ont plus aucune ; or les ouvriers travaillent deux fois plus souvent la nuit que les cadres.
- Chaque territoire a sa solution :
  - **le vélo en petite couronne** : 22 % des trajets en voiture d'une commune de banlieue à une autre font moins de 5 km (339 000 sur 1,54 million), et 31 % en petite couronne ;
  - **des navettes en grande couronne** : hors de Paris, 20 % des postes d'employés et d'ouvriers sont dans une commune sans gare (322 000 sur 1,59 million), et 32 % en grande couronne. Les plus grands pôles sont Gonesse, Guyancourt, Bonneuil-sur-Marne et Les Ulis.
- Les employeurs de grande couronne jugent 41 % de leurs recrutements difficiles, contre 29 % à Paris (France Travail, 2026). C'est une coïncidence géographique : l'enquête ne dit pas que le transport en est la cause.

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
| Carte des emplois sans gare | `08` | 154 communes sans gare comptent au moins 500 postes d'employés et d'ouvriers |
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

- **La ponctualité de tout le réseau** : notre analyse couvre les 13 lignes de RER et Transilien publiées par la SNCF ; le métro, le tram et le bus, publiés à part, compléteraient le tableau.
- **Des temps de trajet réels**, porte à porte, pour remplacer la présence d'une gare dans la commune.
- **Une analyse plus fine que la commune**, au niveau du quartier.

## Qui a fait quoi

- **Melvyn MOTHO** : hypothèses et protocoles de test, analyses des données (scripts 00 à 11), maquettes et application.
- **Pierre THAI** : relecture critique des maquettes, à partir de captures annotées. Ses recommandations ont donné le titre de l'Accueil (« Quand le lieu de travail impose la voiture »), la formulation « 13 fois moins » à la place d'un pourcentage mal compris, le titre, le sous-titre et le « À retenir » de la page sur le télétravail, et une description plus exacte de la page « Loin des gares » (« presque deux fois plus souvent »). Il a aussi proposé l'hypothèse sur le revenu (« la voiture comme luxe ? », script 09), qui est devenue le contrôle du résultat principal : à revenu égal, l'absence de gare fait toujours monter la voiture.
- **Maroua Zoubir** : idée et premier travail sur la ponctualité des lignes de RER et de train, repris dans le script 11 et la page « Loin des gares ».

## Licence

Code sous licence [MIT](https://github.com/hackathons-mobilites/hackaviz_2026/blob/main/Docs/License.md). Résultats et données dérivées sous Licence Ouverte 2.0, sauf ceux tirés de sources sous ODbL, qui restent sous ODbL : ponctualité des lignes (`production/resultats/11_h24/`, `application/donnees/ponctualite_lignes.csv`) et couleurs des lignes (`application/donnees/couleurs_lignes.csv`). Textes et visuels sous licence CC-BY 4.0.
