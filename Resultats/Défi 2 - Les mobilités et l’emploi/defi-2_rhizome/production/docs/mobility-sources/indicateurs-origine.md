# Projet C — « Dix ans de réseau, dix ans d'emploi » : évolution du réseau IDF 2015-2025 et accès à l'emploi (défi 3 impact territorial, pont défi 2)

Ce document décrit les indicateurs et choix du projet d'origine. Les [spécifications actuelles du site](../../web/docs/specifications.md) font référence pour les graphiques livrés.

*Vérifications du 7 novembre 2026. Légende : ✔ jeu testé via l'API · ◐ identifié, non testé · ✘ n'existe pas en open data.*

## 1. Cadrage
**Question.** Comment le réseau de transport francilien a-t-il évolué entre 2015 et 2025 (tous modes), et quel impact sur l'accès à l'emploi des territoires desservis ?
**Rendu.** Carte interactive avec curseur temporel 2015 → 2025 (→ 2030 avec les projets) : tronçons et stations apparaissant à leur date de mise en service, stations dimensionnées par les validations annuelles, fond de carte par commune ou zone d'emploi colorié selon les actifs, les demandeurs d'emploi ou les emplois ; comparaison avant/après autour des nouvelles gares.
**Couches souhaitées et disponibilité.** réseau et modes ✔ (ferré, tram, câble ; bus partiel) · validations par gare 2015-2025 ✔ · actifs par commune ◐ (recensements 2015 → 2021, pas au-delà) · demandeurs d'emploi par commune ◐ (série trimestrielle 1996 → 2025) · emplois au lieu de travail par commune ◐ (2015 → 2021) · zones d'emploi 2020 ✔.
**Mises en service 2015-2025 lisibles dans les tracés IDFM** : T6 (2016), T11 Express (2017), T3b (2018), T1 et T4 prolongés (2019), M14 Mairie de Saint-Ouen (2020), T9 (2021), M4 Bagneux et M12 Mairie d'Aubervilliers (2022), T13 (2022), T10 et T12 (2023), RER E Nanterre (2024), M14 Orly / Saint-Denis Pleyel (2024), T14 (2025), Câble C1 (déc. 2025) ; à venir M18 (2026), 15 Sud (2026), 16/17.

---

## 2. Les sources, par type de données

| Type | Source | Lien | Producteur · licence (vérifiée) | Granularité / période | Usage | État |
|---|---|---|---|---|---|---|
| **Réseau** | Tracés du réseau ferré IDF (`date_mes`) | https://data.iledefrance-mobilites.fr/explore/dataset/traces-du-reseau-ferre-idf/ | IDFM · Licence Ouverte 2.0 | tronçon × mode × date de mise en service (1837 → 2026) ; 1 676 tronçons | animation année par année du métro, RER, train, tram, câble | ✔ |
| | Tracés schématiques du réseau ferré et des gares | https://data.iledefrance-mobilites.fr/explore/dataset/traces-du-reseau-de-transport-ferre-dile-de-france-schematique/ · `schema_gares-gf` | IDFM · à vérifier | plan schématique | rendu « plan de métro » animé | ◐ |
| | Lignes et arrêts en projet | https://data.iledefrance-mobilites.fr/explore/dataset/projets_lignes_idf/ · …/projets_arrets_idf/ | IDFM · Licence Ouverte | 50 projets (statut AVP / DUP / travaux, `mes_estime` 2026-2038), 301 arrêts | prolonger la carte jusqu'en 2030-2035 (GPE 15/16/17/18, T1, T10, bus en site propre) | ✔ |
| | Référentiel des lignes et des arrêts (état 2025) | https://data.iledefrance-mobilites.fr/explore/dataset/referentiel-des-lignes/ · …/arrets/ | IDFM · ODbL / Licence Ouverte | lignes et arrêts actifs | photo 2025 du réseau, dont bus | ✔ |
| | Archives GTFS | https://transport.data.gouv.fr/datasets/reseau-urbain-et-interurbain-dile-de-france-mobilites | IDFM · Licence Mobilité | seulement ~25 dernières versions (≈ 10 jours), pas d'archive 2021 | évolution de l'offre bus impossible sans archivage propre/tram/métro récente | ◐ |
| | Tracés des lignes de bus (2025) | https://data.iledefrance-mobilites.fr/explore/dataset/traces-des-lignes-regulieres-de-bus-en-ile-de-france/ | IDFM · ODbL | 1 939 lignes | couche bus « état 2025 » | ✔ |
| **Fréquentation** | Historique des validations réseau ferré 2015-2025 | https://data.iledefrance-mobilites.fr/explore/dataset/histo-validations-reseau-ferre/ | IDFM · ODbL | Les archives annuelles ne sont plus conservées localement. | taille des stations année par année ; montée en charge des nouvelles gares | Source externe |
| | Historique des validations réseau de surface 2015-2025 | https://data.iledefrance-mobilites.fr/explore/dataset/histo-validations-reseau-surface/ | IDFM · ODbL | un zip par an, par ligne | apparition / disparition / essor des lignes de bus et tram | ✔ |
| | Trafic annuel entrant par station RATP 2011-2015 | https://www.data.gouv.fr/datasets/trafic-annuel-entrant-par-station-annee-2015-sur-le-reseau-ferre-ratp | IDFM · Licence Ouverte | station × an | prolonger la série avant 2015 | ◐ |
| **Actifs et emploi** | Recensement de la population — séries historiques et bases « Emploi – population active » par commune (millésimes 2015, 2016 … 2021) | https://www.insee.fr/fr/statistiques?debut=0&theme=81 (bases « Emploi - population active ») | INSEE · Licence Ouverte 2.0 | commune × année : actifs, actifs occupés, chômeurs au sens du RP, emplois au lieu de travail × secteur × PCS | évolution 2015 → 2021 des actifs et des emplois autour des nouvelles gares | ◐ |
| | MOBPRO 2015 / 2016 … 2021 (mobilités professionnelles) | https://www.insee.fr/fr/statistiques/8205896 (2021) ; millésimes antérieurs sur insee.fr | INSEE · Licence Ouverte 2.0 | commune de résidence × commune de travail × mode × PCS, chaque année de 2015 à 2021 | évolution de la part des TC et des flux vers les pôles desservis | ◐ (2021 ✔) |
| | Demandeurs d'emploi en fin de mois (DEFM) par commune, catégories A-E | https://statistiques.francetravail.org (rubrique « Demandeurs d'emploi – données communales ») ; https://www.data.gouv.fr/organizations/france-travail/ | France Travail · Licence Ouverte 2.0 | commune × trimestre, 1996 → 2025 | évolution des demandeurs d'emploi avant/après mise en service | ◐ |
| | Base Tous Salariés / Flores (emplois salariés par commune d'établissement) | https://www.insee.fr/fr/statistiques/4991205 (Flores 2017 → 2021, fichiers TD_FLORESyyyy_NA17_TREF_NBSAL ; 2022 non publié) | INSEE · Licence Ouverte 2.0 | commune × secteur × année | emplois salariés créés autour des gares | ◐ |
| | SIRENE (créations d'établissements géolocalisées, 2015-2025) | https://www.data.gouv.fr/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/ + géocodage | INSEE · Licence Ouverte 2.0 | établissement × date de création × adresse | dynamique d'implantation autour des nouvelles stations | ◐ |
| | Zones et bassins d'emploi 2020 | https://data.iledefrance.fr/explore/dataset/base-des-zones-demploi-contours/ (contours) · https://data.iledefrance.fr/explore/dataset/base-des-zones-demploi/ (composition communale) · référentiel INSEE https://www.insee.fr/fr/information/4652957 | INSEE / Région · Licence Ouverte | polygones | agrégation territoriale | ✔ |
| | Filosofi carroyé 200 m (2015, 2017, 2019) | https://www.data.gouv.fr/datasets/revenus-pauvrete-et-niveau-de-vie-donnees-carroyees | INSEE · Licence Ouverte 2.0 | carreaux × millésime | population et revenus à 800 m des gares, avant/après | ◐ |
| | Isochrones GPE 2023 / 2030 | vue Airtable Hackaviz | SGP / IDFM | isochrones par gare | emplois accessibles en 45 min avant/après | ◐ |
| **Territoires** | Communes, EPCI, QPV 2015 / 2024 | https://www.data.gouv.fr/datasets/carte-quartiers-prioritaires-de-la-politique-de-la-ville-anct-26avril2024 | ANCT · Licence Ouverte | polygones | ciblage des quartiers desservis | ◐ |

---

## 3. Ce qui manque, et comment faire avec

| Manque | Conséquence | Contournement | Risque résiduel |
|---|---|---|---|
| **Historique du réseau de bus 2015-2025** (aucune date de création / suppression de ligne ou d'arrêt en open data) | la carte tous modes ne peut montrer le bus qu'en photo 2025 | GTFS (aucune archive ouverte ; ~10 jours de versions sur transport.data.gouv) ; historique des validations par ligne (apparition / disparition) ; historique OSM (ODbL) | bus incomplet avant 2021 |
| **Actifs et emplois par commune après 2021** (recensement : dernier millésime 2021 ; 2022 publié en 2025) | la série « emploi » s'arrête avant la fin de la période réseau | DEFM France Travail jusqu'en 2025 ; SIRENE créations jusqu'en 2025 ; Flores 2022 | décalage de 3-4 ans entre réseau et emploi |
| **Causalité** : une gare n'« explique » pas la baisse du chômage | risque de sur-interprétation | comparer les communes desservies à des communes témoins comparables (différence de différences), afficher les tendances régionales en référence, parler de « co-évolution » | lecture prudente à assumer dans le pitch |
| **Emplois accessibles en temps TC pour chaque année** | mesurer l'accès à l'emploi exige un routage par année | GTFS actuel seulement (pas d'archive ouverte) ; isochrones GPE 2023/2030 ; pour 2015, approximation par distance aux gares | pas d'isochrones 2015 exacts |
| **Validations bus par arrêt** (par ligne seulement) | essor des quartiers desservis par bus non mesurable à l'arrêt | utiliser les gares (données par station) et les lignes | — |
| **Titres et tarification** : zonage Navigo supprimé en 2015, télétravail post-2020 | ruptures de série dans les validations | normaliser par la tendance régionale ; flagger 2020-2021 | — |
| Introuvable : données employeurs, recrutements par gare, Orange Flux Vision | — | — | ✘ |

---

## 4. Licences des livrables
Tracés ferré, projets, recensement, DEFM, SIRENE, zones d'emploi = Licence Ouverte 2.0 → tables dérivées en Licence Ouverte ou CC-BY possibles. Dès que les **validations** (ODbL) ou les **tracés bus / référentiel des lignes** (ODbL) sont intégrés dans une table, celle-ci doit être publiée en **ODbL**. Code : MIT. Visuels et carte : CC-BY 4.0. GTFS archivés : Licence Mobilité (à citer à part).

## 5. Remarque de positionnement
Le sujet relève d'abord du **défi 3 (impact territorial)** ; le pont vers le défi 2 passe par les couches actifs / demandeurs d'emploi / emplois accessibles, et vers les projets A et B par le fond de carte commun (réseau et gares 2025).

## 6. Idées de dataviz (cartes et autres formes)

**Cartes**
1. Carte à curseur temporel 2015 → 2025 → 2035 : tronçons allumés à leur `date_mes`, gares en cercles proportionnels aux validations annuelles, fond communal DEFM / actifs, projets GPE en pointillé.
2. Petits multiples « une ouverture, un territoire » : 14 vignettes (T6, T11, T3b, T4, M14 Saint-Ouen, T9, M4, M12, T13, T10, T12, RER E, M14 Orly/Pleyel, T14), rayon 1,5 km, avant/après validations, DEFM, créations SIRENE.
3. Carte bivariée gain de desserte × évolution du chômage par commune (4 quadrants).
4. Isochrones 2015 vs 2025 depuis des communes à fort chômage (Grigny, Sevran, Garges, Argenteuil) : emplois à 45 min.
5. Cartogramme par zone d'emploi : taille = emplois, couleur = km ouverts ou part TC (MOBPRO 2015 → 2021).
6. Population à moins de 800 m d'une gare 2015 vs 2025 (carreaux Filosofi).

**Hors cartes**
7. Frise « plan de métro qui pousse » (schéma IDFM) avec courbe du chômage IDF et jalons (2015 zone unique, 2020 Covid, 2024 JO).
8. Courbes d'adoption des nouvelles gares alignées sur « année 0 ».
9. Slope chart 2015 → 2021 : part TC domicile-travail, communes desservies vs autres.
10. Dumbbell chart DEFM par commune 2015 vs 2025, communes nouvellement desservies colorées.
11. Courbes desservies vs témoins (différence de différences).
12. Sankey / cordes des flux domicile-travail entre zones d'emploi 2015 vs 2021, liens créés par le réseau surlignés.
13. Bar chart race des gares par validations 2015-2025.
14. Streamgraph des validations par mode 2015-2025.
15. Compteurs animés (km ouverts, gares nouvelles, habitants et emplois à < 800 m, DEFM des communes desservies).
16. Scrollytelling « une gare, une histoire » (Saint-Denis Pleyel, Nanterre La Folie, Villejuif Gustave Roussy).
17. Sonification : une note par mise en service, hauteur = chômage.

Recommandation : 1 en écran principal ; 2 + 11 pour la rigueur ; 8 ou 13 pour l'émotion. Limite : emploi INSEE jusqu'en 2021, DEFM jusqu'en 2025.

## 7. Outils pour l'animation année par année des lignes
Principe : exporter `traces-du-reseau-ferre-idf` en GeoJSON, filtrer `date_mes ≤ année` ; couleur par `mode` ; gares en cercles proportionnels aux validations annuelles.
- **Sans code** : Kepler.gl (filtre temporel sur `date_mes`, export HTML/vidéo) · QGIS Temporal Controller → images par année → GIF/MP4 · Flourish projection map · Datawrapper (petits multiples statiques).
- **Avec code (rendu final)** : MapLibre GL JS (`setFilter(['<=','date_mes',annee])` + slider, `interpolate` pour les cercles) — recommandé · deck.gl `TripsLayer`/`PathLayer` (lignes qui se dessinent) · Leaflet TimeDimension / Folium `TimestampedGeoJson` · D3 / Observable Plot pour le plan schématique et les courbes · Plotly `animation_frame` ou GeoPandas + matplotlib FuncAnimation pour prototyper.
- **Scrollytelling** : Svelte/Vue + MapLibre ou Scrollama + D3.
- **Pipeline** : GeoPandas → GeoJSON « tronçons + année » + CSV « gare × année × validations » → MapLibre (carte) + D3 (graphiques) ; Kepler.gl pour tester tout de suite.

### 7.1 Stack TypeScript 100 % open source
- Carte : **MapLibre GL JS** (BSD-3) — `setFilter(['<=', ['get','annee_mes'], annee])`, cercles `interpolate` sur `val_<annee>` ; fond OpenFreeMap / Protomaps (PMTiles) ; **deck.gl** (MIT) pour `TripsLayer` ; Leaflet en alternative légère.
- Graphiques : **D3** / **Observable Plot** (ISC) ou **ECharts** (Apache-2.0).
- Données client : **Arquero** (BSD-3) ou **DuckDB-WASM** (MIT) ; formats Parquet / FlatGeobuf / PMTiles ; **Turf.js** (MIT) pour buffers 800 m.
- App : **Vite + Svelte/SvelteKit** (ou React) ; **Scrollama** (MIT) pour le scrollytelling ; **Tone.js** (MIT) pour la sonification ; déploiement GitHub Pages.
- Préparation : script Node (`@turf/turf`, `csv-parse`) ou Python → `troncons.geojson` (`annee_mes`), `gares.geojson` (validations par année), `communes_defm.geojson`.
- Licences : code MIT ; données dérivées ODbL (validations, tracés bus) avec `LICENSE` séparé dans `data/`.

## 8. Chiffres vérifiés (session du 08/11/2026)

### 8.1 Validations annuelles du réseau ferré IDF (IDFM `histo-validations-reseau-ferre`, ODbL)
Somme de `NB_VALD` par année (« Moins de 5 » compté 3). Indice 2019 = 100.

| Année | Validations | Indice 2019 |
|---|---|---|
| 2015 | 1,49 Md | 88 |
| 2016 | 1,59 Md | 94 |
| 2017 | 1,67 Md | 99 |
| 2018 | 1,68 Md | 99 |
| 2019 | 1,70 Md | 100 (déc. 2019 : 57 M, grèves) |
| 2020 | 0,93 Md | 55 (Covid) |
| 2021 | 1,25 Md | 74 |
| 2022 | 1,63 Md | 96 |
| 2023 | 1,73 Md | 102 |
| 2024 | 1,91 Md | 112 (JO) |
| 2025 | 2,16 Md | 127 — à vérifier : hausse trop forte, probable changement de périmètre/format (xlsx trimestriels) |

Formats hétérogènes : txt `;`/tab latin-1 (≤ 2022), UTF-16 (2023 S2), S1+T3+T4 (2024), xlsx par trimestre (2025). Fichier : `carte-evolution/data_src/validations_ferre_annuelles.csv`.
Aucune donnée ouverte n'isole un « effet IA » ; le facteur documenté est le télétravail (Enquête Emploi INSEE / DARES, non chargé ici).

### 8.2 Navetteurs vers Paris (INSEE MOBPRO 2021, Licence Ouverte)
- 1 029 000 actifs occupés résidant en IDF hors Paris travaillent à Paris (sur 1 777 000 emplois occupés à Paris ; 748 000 Parisiens travaillent à Paris, 311 000 Parisiens travaillent en banlieue).
- Par département de résidence : 92 : 241 k · 93 : 209 k · 94 : 194 k · 95 : 102 k · 78 : 100 k · 77 : 96 k · 91 : 88 k.
- Mode : TC 74 %, voiture 18 %, vélo 3,7 %, deux-roues motorisé 3,1 %, marche 1,1 %.
- PCS : cadres 341 k, prof. intermédiaires 264 k, employés 264 k, ouvriers 113 k, artisans-commerçants 47 k.

### 8.3 Offres d'emploi et « acceptations » (DARES, Licence Ouverte)
- `dares_offres_collectees_satisfaites_france_travail_brutes_trim` : offres **collectées** par France Travail, IDF, par département, 1996 → 2026-T3, arrondies à la centaine. IDF : 182 k (2015), 211 k (2017), 108 k (2020), 204 k (2022), 170 k (2024), 132 k (2025 T1-T3). 2024 par dépt : Paris 57,7 k, 92 25,9 k, 93 17,7 k, 78 16,8 k, 77 14,6 k, 91 13 k, 95 12,3 k, 94 12,1 k.
- Offres **satisfaites** (= pourvues) : série arrêtée en **2013-T2** et seulement France entière → pas de chiffre d'« acceptation » par région après 2013.
- Proxy disponible : `dares_defm_flux_france_region_brut_trim`, sorties des listes ABC IDF (tous motifs) : 365 k (2015), 395 k (2019), 344 k (2020), 405 k (2022), 405 k (2024), 538 k (2025, rupture : réforme inscription France Travail 2025). Pas de ventilation par motif (reprise d'emploi) dans l'open data.
- Pas de DPAE (déclarations d'embauche Urssaf) par région en open data.

### 8.4 Open data Urssaf (open.urssaf.fr, Opendatasoft, licence ODbL pour tous les jeux)
Vérifié par l'API le 08/11/2026. Filtre IDF : `region="Île-de-France"` ou `code_region="11"`.

| Jeu (dataset_id) | Contenu | Période | Granularité |
|---|---|---|---|
| `dpae-par-departement-x-grand-secteur` | Déclarations préalables à l'embauche (CDI / CDD > 1 mois / CDD < 1 mois), brut et CVS | 2000 → T3 2026 | département × 5 secteurs, trimestriel |
| `dpae-mensuelles-par-region` | DPAE > 1 mois (CDI, CDD) | 2000 → 2026 | région, mensuel |
| `effectifs-salaries-et-masse-salariale-du-secteur-prive-par-zone-demploi` | Effectifs salariés privés, masse salariale | 1998 → T2 2026 | zone d'emploi, trimestriel |
| `effectifs-salaries-et-masse-salariale-du-secteur-prive-par-departement-x-grand-s` | idem | 1998 → T2 2026 | département × 7 secteurs, trimestriel |
| `etablissements-et-effectifs-salaries-au-niveau-commune-x-ape-last` | Établissements employeurs et effectifs au 31/12, colonnes `effectifs_salaries_2006 … 2025` | 2006 → 2025 | commune × APE (130 k lignes IDF) |
| `nombre-etab-effectifs-salaries-et-masse-salariale-secteur-prive-zones-emploi` | Établissements, effectifs moyens, masse salariale | 1998 → 2024 | zone d'emploi, annuel |

Chiffres IDF : DPAE 7,15 M (2015) → 8,02 M (2019) → 5,19 M (2020) → 8,17 M (2022) → 8,51 M (2025) ; CDI 1,06 M → 1,40 M (2019) → 1,56 M (2022) → 1,37 M (2025). Effectifs salariés privés (T4) 4,56 M (2015) → 4,91 M (2019) → 4,84 M (2020) → 5,22 M (2024) → 5,22 M (2025). Par ZE 2015 → 2025 : Évry +22 %, Marne-la-Vallée +20 %, Roissy +20 %, Paris +15 %, Saclay +12 %, Versailles-SQY +3 %, Seine-Yvelinoise +3 %, Provins +1 %. Secteurs : construction +24 %, hôtellerie-restauration +24 %, services non marchands +19 %, industrie +2 %.
Limites : secteur privé seulement, compté au lieu de l'établissement ; ODbL → tables dérivées en partage à l'identique.

### 8.5 INSEE « Emploi, chômage, revenus du travail », édition 2025 (Insee Références, sommaire 8376908, Licence Ouverte)
Fiches nationales/régionales avec un xlsx par fiche (`/fr/statistiques/fichier/<id>/ECRT2025-Fxx.xlsx`). Pas de maille communale → chiffres de cadrage, pas de couche carte.
- F12 Chômage dans les régions (8376844) : taux BIT 2024 IDF 7,0 % (15-24 ans 16,8 %) ; Paris 5,7 %, Hauts-de-Seine 6,0 %, Seine-Saint-Denis 10,3 % (jeunes 22,2 %) ; évolution 2015 → 2024 : IDF −1,9 pt, Paris −2,5, 92 −1,9, 93 −2,8 ; dispersion des ZE IDF 1,2 pt.
- F7 Emploi dans les régions (8376834) : IDF 6 884 k emplois fin 2023 (6 345 k salariés ; 63 % tertiaire marchand, 25 % non marchand, 7 % industrie, 5 % construction) ; emploi salarié 2024 : IDF +0,2 %, 93 +0,8 %, 75 et 92 −0,1 %.
- F14 Transitions (8376848, national) : en un trimestre 2024, chômeurs → emploi 27 % (durée limitée 16,7 %, CDI 10,4 %), restent au chômage 50 %, → inactivité 23 % ; en un an (2023-2024) 40 % des chômeurs sont en emploi.
- F6 Embauches et fins de contrat (8376832, national, DARES MMO 2014-2024) : même univers que les DPAE Urssaf, pas de déclinaison régionale.
Carte : indicateurs Urssaf ajoutés (`txsal_YYYY` salariés privés pour 100 actifs résidents ; `dsal_YYYY` évolution cumulée depuis 2015, communes ≥ 200 salariés en 2015 ; `sal_YYYY`, `etab_2025` dans le popup). Source `data_src/urssaf_effectifs_communes_idf.csv` (ODbL).

### 8.6 Pollution et report voiture → TC (vérifié le 08/11/2026)
**Airparif** (hub ArcGIS data-airparif-asso.opendata.arcgis.com, ODbL) : CSV horaires NO2 par station et par année (« 2018_NO2 » … « 2025_NO2 »). Moyennes annuelles calculées (`carte-evolution/data_src/airparif_no2_moyennes_annuelles_stations.csv`) :
- stations trafic (A1, BP Est, Opéra, Haussmann, Champs-Élysées) : 66 (2018) → 60 (2019) → 46 (2020) → 48 (2021) → 47 (2022) → 38 (2023) → 33 µg/m³ (2024) ;
- fond urbain (12 stations) : 29,5 → 27,4 → 21,1 → 23,8 → 23,2 → 20,3 → 18,8 µg/m³.
Baisse générale (parc automobile, ZFE, trafic, télétravail) : non attribuable aux lignes de TC. Pas d'inventaire d'émissions communal en série longue trouvé (départements 2022, cartes de concentration 2017+ en shapefile).

**Report modal** (INSEE RP 2016 `base-ic-activite-residents-2016` agrégée par commune, RP 2021 déjà chargé ; part des actifs occupés 15 ans+ ; Licence Ouverte) :
- IDF : TC 43,6 → 43,8 %, voiture 41,2 → 39,6 % ;
- communes < 1 km d'une ligne ouverte 2017-2021 (41) : TC 58,7 → 57,7 %, voiture 21,1 → 19,1 % ;
- desservies avant 2017 sans nouveauté (604) : TC 38,6 → 39,6 %, voiture 48,0 → 46,5 % ;
- > 1 km de tout ferré/tram (621) : TC 14,3 → 14,3 %, voiture 76,0 → 76,8 %.
Aucun effet visible des ouvertures 2017-2021 sur la part modale 2021 (collecte 2019-2023, Covid, communes déjà très TC). Hausses locales : Montmagny +5,3 pts, Dugny +5,0, Villeneuve-le-Roi +4,5, Bois-Colombes +3,7, Le Bourget +3,6, Villejuif +3,4. Fichier : `data_src/report_modal_2016_2021_communes.csv`.
Carte : indicateurs `d_tc`, `d_voit` (pts 2016 → 2021) ; popup avec `tc_16`/`tc_21`, `voit_16`/`voit_21`.

### 8.7 Emploi salarié public : INSEE Flores (vérifié le 08/11/2026)
- Page : https://www.insee.fr/fr/statistiques/4991205 — fichiers `TD_FLORESyyyy_NA17_TREF_NBSAL_CSV.zip` (postes salariés fin d'année par commune × NA17 × tranche d'effectif), millésimes 2017 → 2021, Licence Ouverte. Tous employeurs (public, régimes spéciaux inclus), hors particuliers employeurs.
- IDF : 6,00 M postes (2017) → 6,18 M (2021) ; secteur OQ (admin. publique, enseignement, santé, action sociale) 1,61 M → 1,60 M. Écart avec l'Urssaf privé (4,7–5,0 M) ≈ périmètre public.
- Pas de distinction public/privé par statut ; fonction publique stricte (SIASP) seulement par région/département (DGAFP). Maille communale non validée par experts (regrouper les petits effectifs).
- Fichiers préparés : `carte-evolution/data_src/flores/flores_2017_na17_com_idf.csv`, `flores_2021_na17_com_idf.csv` (Paris agrégé 75056).
- Série Flores IDF complète (postes salariés tous employeurs, fin d'année) : 6,00 M (2017) · 5,92 M (2018) · 6,10 M (2019) · 6,02 M (2020) · 6,18 M (2021) ; secteur OQ stable ≈ 1,60 M ; hôtellerie-restauration 319 k → 340 k (2019) → 308 k (2020) → 338 k (2021) ; construction 286 k → 346 k ; information-communication 411 k → 464 k. Fichiers `data_src/flores/flores_2017…2021_na17_com_idf.csv`.
- Carte : indicateurs `flo_tx` (postes pour 100 actifs résidents, 2017 → 2021 synchronisés au curseur), `flo_oq` (part secteur OQ), `d_flo` (évolution 2017 → 2021) ; popup avec postes de l'année, 2017 → 2021 et part OQ. Communes < 200 postes grisées.
- Indicateur `pub_share` (champs `pub_2017…2021`) = (Flores − Urssaf) / Flores : part de l'emploi salarié hors secteur privé Urssaf (public, régimes spéciaux), par commune ≥ 200 postes. Rend visible l'écart entre les deux sources (Créteil 53 %, Orsay 59 %, Le Kremlin-Bicêtre 49 %, Paris 20 %, Saint-Denis 11 %).

## 9. Chiffres clés vérifiés (accroches dataviz)
- Réseau : 14 mises en service ferré/tram 2015-2025, ≈ 100 km nouveaux dont ~70 km de tram (125 → 194 km) ; 50 projets / 301 arrêts à venir 2026-2038.
- Validations ferré : 1,70 Md (2019) → 0,93 Md (2020, −45 %) → 102 % (2023) → 112 % (2024) ; déc. 2019 57 M (grèves).
- Salariés privés (Urssaf) : 4,54 M (2015) → 5,19 M (2025), +14 % ; ZE Évry +22 %, Marne-la-Vallée +20 %, Roissy +20 % ; Provins +1 %, Étampes +2 %. Communes : Brétigny +77 %, Aulnay +48 %, Issy +46 % ; Noisiel −38 %, Wissous −35 %.
- Flores : 6,00 M (2017) → 6,18 M (2021) ; ≈ 1,2 M d'emplois hors privé Urssaf ; part hors privé Créteil 53 %, Orsay 59 %, Paris 20 %.
- DPAE : 8,0 M (2019) → 5,2 M (2020) → 8,5 M (2023-2025) ; CDI 1,56 M (2022) → 1,37 M (2025). Secteurs 2015 → 2025 : construction +24 %, HCR +24 %, industrie +2 %.
- Chômage localisé : ZE Paris 9,2 → 7,4 % ; Roissy 11,7 → 9,6 % ; Saclay ≈ 6 %. Départements 2024 : Paris 5,7 %, 93 10,3 % (jeunes 22 %) ; IDF −1,9 pt depuis 2015. Inscrits ABC 973 k (2016) → 1 083 k (2025). Transitions : 27 % des chômeurs en emploi en un trimestre (national).
- Navetteurs : 1,03 M de Franciliens hors Paris travaillent à Paris (58 % des emplois parisiens), 74 % en TC ; 92 241 k, 93 209 k, 94 194 k.
- Modes 2016 → 2021 : TC 43,6 → 43,8 %, voiture 41,2 → 39,6 % ; > 1 km du ferré : TC 14 %, voiture 77 % (+0,8) ; près des lignes 2017-2021 : TC 58 %, stable. Montmagny +5,3 pts, Dugny +5, Villeneuve-le-Roi +4,5.
- NO2 Airparif : trafic 66 → 33 µg/m³ (2018 → 2024), fond 29,5 → 18,8, A1 Saint-Denis 80 → 44.
- Messages jury : (1) 100 km de lignes, 1,03 M de navetteurs, part TC inchangée ; (2) chômage en recul partout, le plus à Roissy / 93 où réseau et emploi privé ont le plus progressé (co-évolution, témoins) ; (3) frise Covid : −45 % validations, −35 % embauches, retour 2023 sauf voiture petite couronne et NO2 ÷ 2.

### 8.8 Couverture SNCF (vérifié le 08/11/2026)
- Tracés IDFM : exploitant SNCF = Train 1 022 km, RER 510 km, tram-train 33 km (~1 565 km sur ~2 070 km hors TER) ; RATP ≈ 440 km ; TER 1 450 km hors IDF à filtrer.
- Validations IDFM ferré : RATP (code 100) 58,5 %, SNCF (800/810) 41,5 % en S1 2019 ; 303 stations RATP, 444 gares SNCF.
- SNCF open data (ressources.data.sncf.com, ODbL) : `frequentation-gares` (voyageurs annuels par gare 2015, 2016, 2018-2024 ; 401 gares IDF ; IDF 1,98 Md → 2,04 Md (2019) → 0,98 Md (2020) → 2,19 Md (2024) ; Gare du Nord 257 M en 2024 ; Magenta 43 → 39 M, Haussmann-St-Lazare 48 → 38 M) ; `gares-de-voyageurs` (référentiel géolocalisé, code UIC / INSEE). Ponctualité Transilien non trouvée sur le portail SNCF (voir QS IDFM). Fichier : `data_src/sncf_frequentation_gares_idf.csv`.

### 9.1 Tableau par département (RP 2016 → 2021, DARES 2025) — graphique de cadrage
| Dépt | Population | Actifs occupés 2016 → 2021 | Chômeurs 2016 → 2021 | Taux | Inscrits FT ABC 2025 / actifs occupés |
|---|---|---|---|---|---|
| 75 | 2,10 M | 1 044 k → 1 035 k | 143 k → 125 k | 12 → 11 % | 20 % |
| 92 | 1,65 M | 737 k → 769 k | 92 k → 86 k | 11 → 10 % | 17 % |
| 93 | 1,70 M | 618 k → 655 k | 142 k → 128 k | 19 → 16 % | 28 % |
| 94 | 1,43 M | 599 k → 624 k | 90 k → 83 k | 13 → 12 % | 19 % |
| 77 | 1,47 M | 615 k → 635 k | 81 k → 76 k | 12 → 11 % | 19 % |
| 78 | 1,49 M | 625 k → 639 k | 73 k → 69 k | 10 → 10 % | 17 % |
| 91 | 1,34 M | 559 k → 575 k | 71 k → 66 k | 11 → 10 % | 18 % |
| 95 | 1,28 M | 515 k → 533 k | 80 k → 73 k | 13 → 12 % | 21 % |
| IDF | 12,5 M | 5,31 M → 5,46 M | 772 k → 705 k | 12,7 → 11,4 % | — |
Avis : cadrage seulement (8 unités, stocks) ; préférer zones d'emploi / communes desservies vs non, ratios et flux, forme dumbbell ou slope. Ménages RP (« Couples-familles-ménages ») non chargés ; utile surtout pour « ménages sans voiture ».

### 9.2 Maquette dumbbell départements / zones d'emploi
Fichier : `Projet_C_dumbbell_departements_zones_emploi.html` (HTML autonome ; corps JSX `dumbbell_body.html`, données `dumbbell_data.json`). Panneau départements : actifs occupés, chômeurs, taux (RP 2016 → 2021), inscrits ABC 2016 → 2025, salariés privés 2015 → 2025. Panneau zones d'emploi : taux localisé 2015 → 2025 (repère 2019), inscrits ABC, salariés privés. Lecture : chômage en recul partout (93 −2,2 pts, Roissy −2,1, Paris −1,8), inscrits FT en hausse partout (+11 % IDF), salariés privés en hausse partout. Suite envisagée : panneau communes desservies vs non desservies.

### 8.9 Vitesse / temps de parcours (vérifié le 09/11/2026)
- Pas de temps de parcours ni de vitesse historisés en open data ; `projets_lignes_idf` sans champ gain de temps ; transport.data.gouv ne conserve que ~25 versions (~10 jours) du GTFS IDFM → pas d'avant/après 2021-2025 calculable (archiver soi-même le GTFS désormais ; citer les gains annoncés par IDFM en texte).
- Vitesse commerciale théorique calculée sur le GTFS IDFM (nov. 2026, mardi type, distance tracé / temps horaire, DuckDB) : train/RER 53 km/h, métro 30, tram 22, bus 18 (bus parisiens 10, Noctilien 22). Métro : M13 49, M14 42, M1 37, M10 35 … M4/M2/M3 22-23. RER/Transilien : K 80, P 73, A 72, R 70, J 57, N 53, L 50, H 49, D 47, B 47, E 45, C 38. Tram : T14 52, T11 44, T2 25, T6-T10 19-20, T4 17, T5/T8 16, T3a/T3b 16/15,5. Bus : 1 920 lignes, 7,4 km/h (54) → 71 km/h (9103).
- Fichiers : `carte-evolution/data_src/vitesse_commerciale_lignes_gtfs_2026-11.csv`, `vitesse_commerciale_bus_gtfs_2026-11.csv` (GTFS sous Licence Mobilités : publier les agrégats, pas le brut).
- Idée carte : colorer les tronçons par vitesse commerciale ; « minutes gagnées » par ouverture uniquement via chiffres IDFM cités.

### 9.3 Classeur récapitulatif
`Projet_C_sources_et_recap_2015_2020_2025.xlsx` : onglets Sources (22 jeux, liens vérifiés, licences), Récap IDF 2015 / 2020 / 2025 (29 indicateurs avec millésime utilisé), Départements, Zones d'emploi, Notes (ruptures de série, périmètres, licences par livrable).
