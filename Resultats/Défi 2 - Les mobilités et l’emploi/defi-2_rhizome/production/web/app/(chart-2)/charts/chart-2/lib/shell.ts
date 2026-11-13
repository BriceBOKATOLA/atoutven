// Trusted, local markup from variante-poles. Never insert user content here.
export const shell = `
<a class="skip" href="#explorer">Accéder au portrait de la zone</a>
<header>
<div class="headline"><h1>Plus d’emplois, pas forcément moins de demandeurs d’emploi</h1><p class="claim">Évolution du nombre de demandeurs d’emploi des catégories A, B et C par commune, entre les moyennes du 4e trimestre 2016 et 2024.</p></div>
<a class="to-portrait" href="#explorer">Voir le portrait d’une zone d’emploi<svg viewBox="0 0 10 12" aria-hidden="true"><path d="M5 0v10.5M1 6.5l4 4 4-4"/></svg></a>
</header>
<main>
<div class="primary">
<section class="map-section" aria-label="Carte des demandeurs d’emploi">
<div id="map-wrap" class="map-wrap"><div id="map" aria-label="Carte interactive de l’Île-de-France"></div><div class="compass" aria-hidden="true"><span>N</span><svg viewBox="0 0 80 80"><path d="M40 0 46 32 80 40 46 46 40 80 33 46 0 40 33 33Z"/></svg></div>
<div id="map-scale" class="map-scale" aria-label="Échelle approximative à la latitude de Paris" hidden><span></span><i></i></div>
<div id="load-status" class="load-status" role="status">Chargement de la carte et des indicateurs…</div></div>
<div id="map-tooltip" class="map-tooltip" role="tooltip" hidden></div>
<p id="commune-detail" role="status"></p>
</section>
<section id="explorer" class="portrait" aria-labelledby="portrait-title">
<h2 id="portrait-title">Portrait des zones d’emploi</h2>
<p class="portrait-note">Chaque fleur représente cinq indicateurs pour une zone d’emploi. Chaque indicateur garde la même place et la même couleur.</p>
<div class="flower-legend"><div id="legend-flower" class="legend-flower" aria-hidden="true"></div><ol id="flower-colors" class="flower-colors" role="list" aria-label="Indicateurs, dans l’ordre des pétales"></ol></div>
<p class="portrait-note">Pour un même indicateur, la longueur du pétale est proportionnelle à sa valeur. Le plus long correspond au maximum des zones. Les pétales d’indicateurs différents ne se comparent pas entre eux. Une valeur nulle ne dessine pas de pétale. Un contour gris en pointillés signale une donnée absente.</p>
<fieldset id="zone-options" class="zone-options"><legend>Choisissez une zone, ici ou sur la carte</legend></fieldset>
<div id="zone-summary" aria-live="polite"><div class="zone-head"><h3 id="zone-name">Données en cours de chargement</h3><div id="flower-preview" aria-hidden="true"></div></div>
<dl id="details"></dl></div>
<p class="portrait-note">Les demandeurs d’emploi sont comptés à leur lieu de résidence. Les salariés et les emplois sont comptés à leur lieu de travail. Ces indicateurs ne disent pas qui occupe les emplois d’une zone.</p>
</section>
</div>
<aside aria-labelledby="panel-title">
<h2 id="panel-title">Demandeurs d’emploi, 2016–2024</h2>
<div class="key-figures"><div><strong>+4,4 %</strong><p>en Île-de-France<br><span title="972 835 à 1 015 850">972,8&nbsp;k à 1,02&nbsp;M</span></p></div><div><strong>+8,6 %</strong><p>autour du Tram T4<br>(reste : +6,7 %)</p></div></div>
<section class="takeaway"><h3>À retenir</h3><p>Autour du Tram T4, l’emploi salarié a progressé plus vite que dans le reste de la région (+9,6 points de pourcentage), mais le nombre de demandeurs d’emploi a aussi augmenté. Ces chiffres ne disent pas qui occupe les emplois créés ni quel est l’effet de la ligne.</p></section>
<section class="caution"><h3>Précaution</h3><p>2015 : rupture de série. 2025 : inscriptions<br class="wide-only"> automatiques (loi pour le plein emploi).<br>On compare les moyennes du 4e trimestre 2016 et 2024.</p></section>
</aside>
</main>
<footer class="chart-sources" aria-labelledby="sources-title">
<h2 id="sources-title">Sources et notes</h2>
<p><a href="/data/LICENCES.txt">Conditions de réutilisation des données</a></p>
<div class="sources-grid">
<div class="source-group">
<p><strong><a href="https://www.data.gouv.fr/datasets/inscrits-a-france-travail-donnees-communales-trimestrielles-brutes">Dares / France Travail.</a></strong> « Inscrits à France Travail – données communales » : catégories A, B, C, données brutes arrondies au multiple de 5, moyennes du 4e trimestre 2016 et 2024. Les agrégats régionaux sont des sommes de valeurs communales arrondies. Données sous <a href="https://github.com/etalab/licence-ouverte/blob/master/LO.md">Licence Ouverte 2.0</a>.</p>
<p><strong><a href="https://open.urssaf.fr/explore/dataset/etablissements-et-effectifs-salaries-au-niveau-commune-x-ape-last/">Urssaf.</a></strong> Salariés du secteur privé au 31 décembre 2016 et 2024, agrégés par zone dans le classeur de l’équipe. Les sommes ignorent les cellules sectorielles non renseignées ; celles-ci ne sont pas des zéros confirmés. Données sous <a href="https://opendatacommons.org/licenses/odbl/1-0/">ODbL 1.0</a> selon la <a href="https://www.data.gouv.fr/datasets/nombre-detablissements-employeurs-et-effectifs-salaries-du-secteur-prive-par-commune-x-ape-au-31-12-depuis-2006">fiche des effectifs</a>.</p>
<p><strong>Insee.</strong> <a href="https://www.insee.fr/fr/statistiques/1893230">Taux de chômage par zone d’emploi</a> : moyenne annuelle 2024, zonage 2020. <a href="https://www.insee.fr/fr/statistiques/4171446">Recensement 2016, emploi et population active</a> : calcul des emplois dans la zone pour 100 actifs occupés résidents de 15 à 64 ans. Source : Insee. Réutilisation sous <a href="https://www.insee.fr/fr/information/2008466">Licence Ouverte 2.0, sauf mention contraire</a>.</p>
<p><strong>Île-de-France Mobilités.</strong> <a href="https://data.iledefrance-mobilites.fr/explore/dataset/traces-du-reseau-ferre-idf/">Tracés du réseau ferré</a> et <a href="https://data.iledefrance-mobilites.fr/explore/dataset/emplacement-des-gares-idf/">gares par ligne</a>. Données sous <a href="https://github.com/etalab/licence-ouverte/blob/master/LO.md">Licence Ouverte 2.0</a>.</p>
<p><strong>Fonds de carte.</strong> La documentation de l’équipe cite la Région Île-de-France pour les <a href="https://data.iledefrance.fr/explore/dataset/base-des-zones-demploi-contours/">contours des zones d’emploi</a> et leur <a href="https://data.iledefrance.fr/explore/dataset/base-des-zones-demploi/">composition communale</a>. L’origine des contours communaux et les transformations initiales restent à confirmer. La provenance et la licence des copies locales restent à confirmer.</p>
</div>
<div class="source-group">
<p><strong>Notes de lecture.</strong> Paris regroupe ses 20 arrondissements.</p>
<p id="coverage"></p>
</div>
</div>
</footer>
`;
