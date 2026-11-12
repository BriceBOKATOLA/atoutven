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
<div class="map-tools" role="group" aria-label="Déplacer et zoomer la carte">
<button type="button" data-pan="left" disabled aria-label="Déplacer la carte vers l’ouest"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M10 3L5 8l5 5"/></svg></button>
<button type="button" data-pan="up" disabled aria-label="Déplacer la carte vers le nord"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 10l5-5 5 5"/></svg></button>
<button type="button" data-pan="down" disabled aria-label="Déplacer la carte vers le sud"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 6l5 5 5-5"/></svg></button>
<button type="button" data-pan="right" disabled aria-label="Déplacer la carte vers l’est"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M6 3l5 5-5 5"/></svg></button>
<button type="button" id="zoom-out" class="tool-gap" disabled aria-label="Réduire la carte"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10"/></svg></button>
<button type="button" id="zoom-in" disabled aria-label="Agrandir la carte"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M8 3v10"/></svg></button>
<button type="button" id="reset-view" class="tool-gap tool-text" disabled>Recadrer</button>
</div>
<p class="map-help">Déplacez la carte avec les boutons fléchés ou en la faisant glisser. Zoomez avec +, − ou deux doigts. Le bouton « Recadrer » rétablit la vue initiale. Sur écran tactile, utilisez deux doigts pour déplacer la carte. Pour zoomer avec la molette, maintenez Ctrl ou ⌘. Cliquez sur une commune, un pôle ou une fleur pour sélectionner son département.</p>
<div class="commune-reader">
<label for="commune-select">Consulter une commune</label>
<p id="commune-help" class="section-note">Choisissez une commune pour consulter ses emplois fin 2015 et fin 2025 et sa densité d’emploi. Son département sera sélectionné sur la carte.</p>
<select id="commune-select" aria-describedby="commune-help" disabled><option value="">Choisir une commune</option></select>
<div id="commune-detail" class="commune-detail" role="status" aria-atomic="true" hidden></div>
</div>
<div id="map-tooltip" class="map-tooltip" role="tooltip" hidden></div>
</section>
<section class="legend" aria-labelledby="legend-title">
<h2 id="legend-title" class="visually-hidden">Légende de la carte</h2>
<div class="legend-group">
<h3>Densité d’emploi</h3>
<p class="legend-note">Emplois salariés privés par km², fin 2025</p>
<ol class="ramp">
<li><i style="--swatch:#F1EFEA"></i>&lt; 100</li>
<li><i style="--swatch:#DCE3EC"></i>100 à 500</li>
<li><i style="--swatch:#B3C3D9"></i>500 à 2 000</li>
<li><i style="--swatch:#7F9BC2"></i>≥ 2 000</li>
</ol>
</div>
<div class="legend-group legend-poles">
<h3>Pôles d’emploi</h3>
<p class="legend-note">Communes d’au moins 10 000 emplois ; taille selon l’effectif fin 2025</p>
<div class="sizes" id="size-legend"></div>
<ul class="keys">
<li><svg viewBox="0 0 22 16" aria-hidden="true"><circle class="key-pole" cx="11" cy="8" r="6"/></svg>Plus d’emplois qu’en 2015</li>
<li><svg viewBox="0 0 22 16" aria-hidden="true"><circle class="key-pole key-declining" cx="11" cy="8" r="6"/></svg>Moins d’emplois qu’en 2015</li>
<li><svg viewBox="0 0 22 16" aria-hidden="true"><circle class="key-pole key-new" cx="11" cy="8" r="5.5"/></svg>Nouveau pôle depuis 2015</li>
</ul>
</div>
<div class="legend-group">
<h3>Réseau ferré</h3>
<p class="legend-note">Train, RER, métro, tramway et câble</p>
<ul class="keys">
<li><svg viewBox="0 0 22 16" aria-hidden="true"><path class="key-rail-new" d="M1 8h20"/></svg>Ligne ouverte depuis 2015</li>
<li><svg viewBox="0 0 22 16" aria-hidden="true"><path class="key-rail-earlier" d="M1 8h20"/></svg>Ligne déjà en service</li>
<li><svg viewBox="0 0 22 16" aria-hidden="true"><path class="key-boundary" d="M1 8h20"/></svg>Limite de département</li>
</ul>
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
<p class="panel-note">Emplois salariés privés, de fin 2015 à fin 2025</p>
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
<div class="sources-grid">
<div class="source-group">
<p><strong><a href="https://open.urssaf.fr/explore/dataset/etablissements-et-effectifs-salaries-au-niveau-commune-x-ape-last/">Urssaf.</a></strong> Effectifs salariés du secteur privé par commune au 31 décembre 2015 et 2025, et <a href="https://open.urssaf.fr/explore/dataset/auto-entrepreneurs-par-departement/">auto-entrepreneurs par département</a>.</p>
<p><strong><a href="https://catalogue-donnees.insee.fr/fr/catalogue/recherche/DS_RP_EMPLOI_LT_PRINC">Insee.</a></strong> Recensement de la population, emploi au lieu de travail 2017 et 2023.</p>
<p><strong><a href="https://www.data.gouv.fr/datasets/inscrits-a-france-travail-donnees-communales-trimestrielles-brutes">France Travail et Dares.</a></strong> Demandeurs d’emploi de catégories A, B et C.</p>
<p><strong><a href="https://data.iledefrance-mobilites.fr/explore/dataset/traces-du-reseau-ferre-idf/">Île-de-France Mobilités.</a></strong> Tracés du réseau ferré.</p>
<p><strong><a href="https://github.com/gregoiredavid/france-geojson">IGN et Insee.</a></strong> Contours administratifs.</p>
</div>
<div class="source-group">
<p><strong>Notes de lecture.</strong> Indicateurs départementaux : tableau de l’équipe, source d’origine à préciser.</p>
<p id="coverage"></p>
<p>Eclowork, équipe Rhizome. Hackaviz Mobilités 2026, défi 2 : les mobilités et l’emploi.</p>
</div>
</div>
</footer>
<p id="announce" class="visually-hidden" aria-live="polite"></p>
<noscript><p class="noscript">Cette carte a besoin de JavaScript pour s’afficher. Les chiffres et la méthode sont décrits dans le README du projet.</p></noscript>`;
