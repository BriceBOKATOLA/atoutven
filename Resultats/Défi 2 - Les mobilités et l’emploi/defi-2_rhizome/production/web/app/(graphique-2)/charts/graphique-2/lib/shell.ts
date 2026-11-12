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
<div class="map-wrap"><div id="map" aria-label="Carte interactive de l’Île-de-France"></div><div class="compass" aria-hidden="true"><span>N</span><svg viewBox="0 0 80 80"><path d="M40 0 46 32 80 40 46 46 40 80 33 46 0 40 33 33Z"/></svg></div>
<div id="map-scale" class="map-scale" aria-label="Échelle approximative à la latitude de Paris" hidden><span></span><i></i></div>
<div id="load-status" class="load-status" role="status">Chargement de la carte et des indicateurs…</div></div>
<div class="map-tools" role="group" aria-label="Déplacer et zoomer la carte">
<button type="button" data-pan="left" aria-label="Déplacer la carte vers l’ouest" disabled>←</button>
<button type="button" data-pan="up" aria-label="Déplacer la carte vers le nord" disabled>↑</button>
<button type="button" data-pan="down" aria-label="Déplacer la carte vers le sud" disabled>↓</button>
<button type="button" data-pan="right" aria-label="Déplacer la carte vers l’est" disabled>→</button>
<button id="zoom-out" type="button" aria-label="Réduire la carte" disabled>−</button>
<button id="zoom-in" type="button" aria-label="Agrandir la carte" disabled>+</button>
<button id="reset-view" type="button" disabled>Recadrer</button>
</div>
<p class="map-help">Au clavier, accédez à la carte avec Tab, parcourez les communes avec les touches fléchées et consultez leurs données avec Entrée ou Espace. Déplacez la carte avec les boutons fléchés ou en la faisant glisser. Zoomez avec +, − ou deux doigts. Le bouton « Recadrer » rétablit la vue initiale. Sur écran tactile, utilisez deux doigts pour déplacer la carte. Vous pouvez aussi zoomer avec la molette. Cliquez dans une zone d’emploi pour consulter son portrait. Les données restent limitées au cadrage chargé.</p>
<section id="map-legend" class="map-legend" aria-labelledby="legend-title">
  <h2 id="legend-title" class="visually-hidden">Légende de la carte</h2>
  <div class="legend-group">
    <h3>Demandeurs d’emploi</h3>
    <p class="legend-note">Évolution par commune, entre les moyennes du 4e trimestre 2016 et 2024</p>
    <ol class="legend-ramp" aria-label="Classes d’évolution">
      <li><i style="--swatch:#2C7FB8"></i>Moins de −5 %</li>
      <li><i style="--swatch:#A6CEE3"></i>−5 % à moins de 0 %</li>
      <li><i style="--swatch:#FBE6CC"></i>0 % à moins de 5 %</li>
      <li><i style="--swatch:#F5AE6B"></i>5 % à moins de 15 %</li>
      <li><i style="--swatch:#D9531E"></i>15 % ou plus</li>
    </ol>
    <ul class="legend-keys"><li><i class="legend-swatch" style="--swatch:#F1EFEA"></i>Donnée indisponible</li></ul>
  </div>
  <div class="legend-group">
    <h3>Réseau et territoires</h3>
    <p class="legend-note">Lignes ferrées et zones d’emploi</p>
    <ul class="legend-keys">
      <li><i class="line"></i>Ligne ouverte entre 2015 et 2025</li>
      <li><i class="old-line"></i>Réseau antérieur à 2015</li>
      <li><i class="t4-line"></i>Encadré du Tram T4</li>
      <li><i class="zone-line"></i>Contour de zone d’emploi</li>
    </ul>
    <p class="legend-note">Cliquez sur une zone ou sa fleur pour voir son portrait.</p>
  </div>
</section>
<p id="commune-detail" role="status">Sélectionnez une commune sur la carte pour consulter ses données.</p>
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
<div class="key-figures"><div><strong>+4,4 %</strong><p>en Île-de-France<br>972 835 à 1 015 850</p></div><div><strong>+8,6 %</strong><p>autour du Tram T4<br>(reste : +6,7 %)</p></div></div>
<section class="takeaway"><h3>À retenir</h3><p>Autour du Tram T4, l’emploi salarié a progressé plus vite que dans le reste de la région (+9,6 points), mais le nombre de demandeurs d’emploi a aussi augmenté. Ces chiffres ne disent pas qui occupe les emplois créés ni quel est l’effet de la ligne.</p></section>
<section class="caution"><h3>Précaution</h3><p>2015 : rupture de série. 2025 : inscriptions<br class="wide-only"> automatiques (loi pour le plein emploi).<br>On compare les moyennes du 4e trimestre 2016 et 2024.</p></section>
</aside>
</main>
<footer class="chart-sources" aria-labelledby="sources-title">
<h2 id="sources-title">Sources et notes</h2>
<div class="sources-grid">
<div class="source-group">
<p><strong>DARES / France Travail.</strong> « Inscrits à France Travail – données communales » : catégories A, B, C, données brutes arrondies au multiple de 5, moyennes du 4e trimestre 2016 et 2024. Les agrégats régionaux sont des sommes de valeurs communales arrondies.</p>
<p><strong>Urssaf et INSEE.</strong> Indicateurs des zones d’emploi issus du classeur de l’équipe : salariés du secteur privé, 2016–2024 (Urssaf) ; chômage localisé, 2024, et emplois rapportés aux actifs occupés résidents, 2016 (INSEE).</p>
<p><strong>Île-de-France Mobilités.</strong> Tracés du réseau ferré et emplacement des gares.</p>
</div>
<div class="source-group">
<p><strong>Notes de lecture.</strong> Paris regroupe ses 20 arrondissements.</p>
<p id="coverage"></p>
</div>
</div>
</footer>
`;
