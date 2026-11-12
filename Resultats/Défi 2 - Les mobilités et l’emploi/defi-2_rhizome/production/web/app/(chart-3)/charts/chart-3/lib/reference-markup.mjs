export const referenceMarkup = `
<a class="skip" href="#map">Aller à la carte</a>
<header class="page-header">
<h1>14 nouveaux pôles d’emploi, surtout en grande couronne</h1>
<p class="lead">Entre fin 2015 et fin 2025, l’Île-de-France est passée de 75 à 87 communes d’au moins 10 000 emplois salariés privés. Les lignes ferrées ouvertes depuis, en trait noir sur la carte, traversent 30 des 73 pôles plus anciens, mais un seul des 14 nouveaux.</p>
</header>
<main>
<div class="primary">
<section class="map-section" aria-labelledby="map-title">
<h2 id="map-title" class="visually-hidden">Carte des pôles d’emploi fin 2025</h2>
<div class="map-wrap" id="carte">
<svg id="map" tabindex="0" role="group" aria-roledescription="carte interactive" aria-labelledby="map-title" aria-describedby="map-keys" viewBox="0 0 1000 800"></svg>
<p id="map-keys" class="visually-hidden">Flèches : déplacer la carte. Plus et moins : zoomer. Zéro : recadrer. Tabulation : atteindre les pôles, puis flèches pour passer de l’un à l’autre, du plus grand au plus petit. Entrée : sélectionner le département du pôle.</p>
<div id="selection" class="selection" hidden>
<p id="selection-text"></p>
<button id="clear-selection" type="button" aria-label="Effacer la sélection du département"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 3l10 10M13 3L3 13"/></svg></button>
</div>
<svg class="compass" viewBox="-11 -22 22 34" aria-hidden="true"><text y="-13">N</text><path d="M0-10 2-2 10 0 2 2 0 10-2 2-10 0-2-2Z"/></svg>
<div class="scale" aria-hidden="true"><span id="scale-label"></span><i id="scale-line"></i></div>
<p id="map-hint" class="map-hint" hidden aria-hidden="true"></p>
<div id="load-status" class="load-status" role="status">Chargement de la carte…</div>
</div>
<div id="map-tooltip" class="map-tooltip" role="tooltip" hidden></div>
</section>
<section class="legend" aria-labelledby="legend-title">
<h2 id="legend-title" class="visually-hidden">Légende de la carte</h2>
<div class="legend-group">
<h3>Densité d’emploi</h3>
<p class="legend-note">Emplois salariés privés par km², fin 2025</p>
<div id="density-legend" class="native-map-legend"></div>
</div>
<div class="legend-group legend-poles">
<h3>Pôles d’emploi</h3>
<p class="legend-note">Communes d’au moins 10&nbsp;k emplois ; taille selon l’effectif fin 2025.</p>
<p class="size-legend-title">Taille des cercles · emplois</p>
<div class="sizes" id="size-legend" role="img" aria-label="Taille des cercles : 10 000, 50 000 et 150 000 emplois salariés privés fin 2025."></div>
<div id="pole-legend" class="native-map-legend"></div>
</div>
<div class="legend-group">
<h3>Réseau ferré</h3>
<p class="legend-note">Train, RER, métro, tramway et câble</p>
<div id="network-legend" class="native-map-legend"></div>
</div>
</section>
<section class="flower-legend" aria-labelledby="flower-legend-title">
<h2 id="flower-legend-title">Lire les fleurs départementales</h2>
<p class="section-note">Quatre indicateurs, toujours aux mêmes positions, dans le sens des aiguilles d’une montre.</p>
<div class="flower-legend-key">
<div id="flower-legend-diagram" class="flower-legend-diagram" aria-hidden="true"></div>
<ol id="flower-legend-items" class="flower-legend-items" role="list" aria-label="Indicateurs dans l’ordre des pétales"></ol>
</div>
<p class="section-note">La surface de chaque pétale est proportionnelle à la valeur de son indicateur. Pour un même indicateur, le plus grand pétale correspond au maximum des huit départements. Les pétales d’indicateurs différents ne se comparent pas entre eux.</p>
<p class="section-note">Une valeur de zéro ne dessine pas de pétale. Un contour en pointillés signale une donnée absente, et non une valeur nulle.</p>
</section>
<section class="departments" aria-labelledby="departments-title">
<h2 id="departments-title">Les huit départements</h2>
<p id="departments-intro" class="section-note"></p>
<div id="departments" class="rings"></div>
<p id="departments-missing" class="section-note" hidden></p>
</section>
</div>
<aside class="panel" aria-labelledby="panel-title">
<h2 id="panel-title">L’emploi francilien en chiffres</h2>
<div class="key-figures">
<p><strong id="pole-count">—</strong><span>pôles d’emploi fin 2025</span></p>
<p><strong id="employment-count">—</strong><span>emplois salariés privés fin 2025</span></p>
</div>
<p id="pole-comparison" class="panel-note"></p>
<dl id="comparison-figures" class="figures"></dl>
<section aria-labelledby="top-title">
<h3 id="top-title">Les six plus grands pôles hors Paris</h3>
<p class="panel-note">Emplois salariés privés, de fin 2015 à fin 2025.</p>
<dl id="top-poles" class="figures compact"></dl>
</section>
<section aria-labelledby="takeaways-title">
<h3 id="takeaways-title">À retenir</h3>
<ul id="takeaways" class="takeaways">
<li>Les plus grands pôles restent à l’ouest (La Défense) et au nord (Saint-Denis, Roissy).</li>
</ul>
</section>
</aside>
</main>
<footer class="chart-sources" aria-labelledby="sources-title">
<h2 id="sources-title">Sources et notes</h2>
<p><a href="/data/LICENCES.txt">Conditions de réutilisation des données</a></p>
<div class="sources-grid">
<div class="source-group">
<p><strong><a href="https://open.urssaf.fr/explore/dataset/etablissements-et-effectifs-salaries-au-niveau-commune-x-ape-last/">Urssaf.</a></strong> Effectifs salariés du secteur privé par commune au 31 décembre 2015 et 2025, et <a href="https://open.urssaf.fr/explore/dataset/auto-entrepreneurs-par-departement/">auto-entrepreneurs par département</a> au 4e trimestre 2015 et 2025 (administrativement et économiquement actifs). Données sous <a href="https://opendatacommons.org/licenses/odbl/1-0/">ODbL 1.0</a> selon la <a href="https://www.data.gouv.fr/datasets/nombre-detablissements-employeurs-et-effectifs-salaries-du-secteur-prive-par-commune-x-ape-au-31-12-depuis-2006">fiche des effectifs</a> et la <a href="https://www.data.gouv.fr/datasets/auto-entrepreneurs-par-departement">fiche des auto-entrepreneurs</a>.</p>
<p><strong><a href="https://catalogue-donnees.insee.fr/fr/catalogue/recherche/DS_RP_EMPLOI_LT_PRINC">Insee.</a></strong> Recensement de la population, emploi au lieu de travail 2017 et 2023. Source : Insee. Réutilisation sous <a href="https://www.insee.fr/fr/information/2008466">Licence Ouverte 2.0, sauf mention contraire</a>.</p>
<p><strong><a href="https://www.data.gouv.fr/datasets/inscrits-a-france-travail-donnees-communales-trimestrielles-brutes">France Travail et Dares.</a></strong> Demandeurs d’emploi de catégories A, B et C, moyennes du 4e trimestre 2016 et 2024, données brutes arrondies au multiple de cinq. Données sous <a href="https://github.com/etalab/licence-ouverte/blob/master/LO.md">Licence Ouverte 2.0</a>.</p>
<p><strong><a href="https://data.iledefrance-mobilites.fr/explore/dataset/traces-du-reseau-ferre-idf/">Île-de-France Mobilités.</a></strong> Tracés du réseau ferré. Données sous <a href="https://github.com/etalab/licence-ouverte/blob/master/LO.md">Licence Ouverte 2.0</a>.</p>
<p><strong>Fonds de carte.</strong> La documentation de l’équipe cite <a href="https://github.com/gregoiredavid/france-geojson">France GeoJSON</a> : tracés IGN Admin Express COG et codes Insee, édition 2018. L’extraction et les transformations initiales des copies locales ne sont pas documentées. La provenance et la licence des copies locales restent à confirmer.</p>
</div>
<div class="source-group">
<p><strong>Créations d’entreprises.</strong> Tableau de l’équipe, à partir de l’Observatoire de la création d’entreprise, Bpifrance Création :</p>
<ul>
<li><a href="https://bpifrance-creation.fr/sites/default/files/oce/OCE_FSM_%C3%8Ele-de-France_202507.pdf">La création d’entreprise en Île-de-France — chiffres de juillet 2025</a> (publication : août 2025).</li>
<li><a href="https://bpifrance-creation.fr/sites/default/files/oce/OCE_FSM_%C3%8Ele-de-France_202508.pdf">La création d’entreprise en Île-de-France — chiffres d’août 2025</a> (publication : septembre 2025).</li>
<li><a href="https://bpifrance-creation.fr/sites/default/files/oce/OCE_FSM_%C3%8Ele-de-France_202509.pdf">La création d’entreprise en Île-de-France — chiffres de septembre 2025</a> (publication : octobre 2025).</li>
</ul>
<p>Reproduction collective autorisée avec mention des sources selon la page 10 de chaque publication. Source : Insee (Sirene) ; traitements : Observatoire de la création d’entreprise. Données brutes et non corrigées des variations saisonnières. Les trois chiffres mensuels sont ceux de leur première publication, provisoire ; les révisions ultérieures peuvent modifier les totaux.</p>
<p><strong><a href="https://www.insee.fr/fr/statistiques/2109644">Insee — tableau de bord de la conjoncture.</a></strong> Emploi salarié total (public et privé) et intérim au 2e trimestre 2025 : estimations Urssaf, Dares et Insee, en fin de trimestre, corrigées des variations saisonnières ; mise à jour du 18 septembre 2026. Défaillances : Banque de France, Fiben, cumul de septembre 2025 à août 2026 en date de jugement ; mise à jour du 28 octobre 2026. Les valeurs correspondent aux figures 3, 7 et 22. Source : Insee. Réutilisation sous <a href="https://www.insee.fr/fr/information/2008466">Licence Ouverte 2.0, sauf mention contraire</a>.</p>
<p><strong>Notes de lecture.</strong> Les variations sur trois mois reconstituées dans le fichier à partir de variations annuelles arrondies peuvent différer d’environ 0,1 point d’un calcul sur les chiffres exacts. Elles ne sont pas affichées ici. Les défaillances couvrent les douze mois jusqu’en août 2026 ; les autres indicateurs datent de 2025.</p>
<p id="coverage"></p>
</div>
</div>
</footer>
<p id="announce" class="visually-hidden" aria-live="polite"></p>
<noscript><p class="noscript">Cette carte a besoin de JavaScript pour s’afficher. Les chiffres et la méthode sont décrits dans le README du projet.</p></noscript>`;
