/*
 * zoom_cartes.js : zoom et déplacement sur les cartes de l'application.
 *
 * Chaque carte est écrite dans les pages comme <div class="cadre-carte"><img class="carte-zoomable" alt="…"></div>.
 * Ce script ajoute à chaque cadre trois boutons (zoomer, dézoomer, revenir à la carte entière) et permet :
 *   - de glisser la carte avec la souris ou le doigt quand elle est agrandie ;
 *   - de zoomer avec Ctrl + molette (la molette seule continue de faire défiler la page, sans piéger le lecteur)
 *     ou par double-clic, à l'endroit visé ;
 *   - au clavier, une fois la carte atteinte avec Tab : + et - pour zoomer, flèches pour se déplacer, 0 pour revenir.
 *
 * Choix techniques :
 *   - On agrandit la largeur de l'image (et non une transformation CSS) : le navigateur redessine le SVG à la
 *     nouvelle taille, la carte reste nette à tous les niveaux de zoom.
 *   - On ne déplace aucun élément de la page : on ajoute seulement les boutons dans le cadre. Streamlit (React)
 *     peut ainsi redessiner la page sans conflit.
 *   - Le script est installé une seule fois dans la page principale (variable window.__zoomCartes) et surveille
 *     les changements (MutationObserver) : une carte qui apparaît (bloc déplié, autre commune choisie, autre page)
 *     reçoit ses boutons ; une image qui change revient à la carte entière.
 *   - Aucune bibliothèque extérieure : une soixantaine de lignes suffisent, rien à télécharger.
 */
(function () {
  if (window.__zoomCartes) return;
  window.__zoomCartes = true;

  const ZOOM_MAX = 8;          // au-delà, les communes de grande couronne sont plus grandes que l'écran
  const PAS = 1.6;             // facteur d'un clic sur + ou -
  const DEPLACEMENT = 60;      // pixels par appui sur une flèche

  const DESSINS = {
    plus: '<path d="M12 5v14"/><path d="M5 12h14"/>',
    moins: '<path d="M5 12h14"/>',
    entiere: '<path d="M4 9V4h5"/><path d="M20 9V4h-5"/><path d="M4 15v5h5"/><path d="M20 15v5h-5"/>'
  };

  /** Crée un bouton rond avec son pictogramme ; le nom lu par les lecteurs d'écran est dans aria-label. */
  function bouton(nom, libelle, action) {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'zoom-bouton';
    b.setAttribute('aria-label', libelle);
    b.title = libelle;
    b.innerHTML = '<svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
      + 'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">' + DESSINS[nom] + '</svg>';
    b.addEventListener('click', function (e) { e.stopPropagation(); action(); });
    return b;
  }

  /** Applique l'état (niveau k, décalage x, y) à l'image du cadre, en gardant la carte dans le cadre. */
  function appliquer(cadre) {
    const z = cadre.__zoom, img = cadre.querySelector('img.carte-zoomable');
    if (!img) return;
    if (z.k <= 1) {
      z.k = 1; z.x = 0; z.y = 0;
      img.style.position = ''; img.style.width = ''; img.style.maxWidth = ''; img.style.left = ''; img.style.top = '';
      cadre.style.height = ''; cadre.classList.remove('zoom-actif');
    } else {
      const L = cadre.clientWidth, H = z.hauteur;
      cadre.style.height = H + 'px';
      // La carte agrandie ne doit jamais laisser de vide dans le cadre
      z.x = Math.min(0, Math.max(L - L * z.k, z.x));
      z.y = Math.min(0, Math.max(H - H * z.k, z.y));
      img.style.position = 'absolute'; img.style.maxWidth = 'none';
      img.style.width = (L * z.k) + 'px'; img.style.left = z.x + 'px'; img.style.top = z.y + 'px';
      cadre.classList.add('zoom-actif');
    }
    z.entiere.disabled = z.k === 1;
  }

  /** Zoome du facteur f autour du point (cx, cy) du cadre : ce point reste sous le curseur. */
  function zoomer(cadre, f, cx, cy) {
    const z = cadre.__zoom;
    if (z.k === 1) z.hauteur = cadre.clientHeight;   // hauteur de la carte entière, gardée pendant le zoom
    if (cx === undefined) { cx = cadre.clientWidth / 2; cy = z.hauteur / 2; }
    const k = Math.min(ZOOM_MAX, Math.max(1, z.k * f));
    z.x = cx - (cx - z.x) * (k / z.k);
    z.y = cy - (cy - z.y) * (k / z.k);
    z.k = k;
    appliquer(cadre);
  }

  /** Installe les boutons et les gestes sur un cadre de carte (une seule fois par cadre). */
  function installer(cadre) {
    if (cadre.__zoom) return;
    const z = cadre.__zoom = { k: 1, x: 0, y: 0, hauteur: 0, src: '' };
    cadre.tabIndex = 0;
    cadre.setAttribute('role', 'group');
    cadre.setAttribute('aria-label', 'Carte agrandissable : touches plus et moins pour zoomer, flèches pour se déplacer, '
      + 'zéro pour revenir à la carte entière');
    const barre = document.createElement('div');
    barre.className = 'zoom-boutons';
    barre.appendChild(bouton('plus', 'Zoomer sur la carte', function () { zoomer(cadre, PAS); }));
    barre.appendChild(bouton('moins', 'Dézoomer', function () { zoomer(cadre, 1 / PAS); }));
    z.entiere = bouton('entiere', 'Revenir à la carte entière', function () { z.k = 1; appliquer(cadre); });
    barre.appendChild(z.entiere);
    cadre.appendChild(barre);
    appliquer(cadre);

    // Ctrl + molette : zoom à l'endroit du curseur
    cadre.addEventListener('wheel', function (e) {
      if (!e.ctrlKey && !e.metaKey) return;
      e.preventDefault();
      const r = cadre.getBoundingClientRect();
      zoomer(cadre, e.deltaY < 0 ? 1.25 : 0.8, e.clientX - r.left, e.clientY - r.top);
    }, { passive: false });
    cadre.addEventListener('dblclick', function (e) {
      const r = cadre.getBoundingClientRect();
      zoomer(cadre, 2, e.clientX - r.left, e.clientY - r.top);
    });
    // Glisser pour se déplacer (souris, stylet ou doigt), seulement quand la carte est agrandie
    let depart = null;
    cadre.addEventListener('pointerdown', function (e) {
      if (z.k === 1 || e.target.closest('.zoom-bouton')) return;
      depart = { px: e.clientX, py: e.clientY, x: z.x, y: z.y };
      cadre.setPointerCapture(e.pointerId);
      e.preventDefault();
    });
    cadre.addEventListener('pointermove', function (e) {
      if (!depart) return;
      z.x = depart.x + e.clientX - depart.px; z.y = depart.y + e.clientY - depart.py;
      appliquer(cadre);
    });
    cadre.addEventListener('pointerup', function () { depart = null; });
    cadre.addEventListener('pointercancel', function () { depart = null; });
    // Clavier
    cadre.addEventListener('keydown', function (e) {
      if (e.target !== cadre) return;           // les boutons gardent leur comportement (Entrée, Espace)
      const fleches = { ArrowLeft: [1, 0], ArrowRight: [-1, 0], ArrowUp: [0, 1], ArrowDown: [0, -1] };
      if (e.key === '+' || e.key === '=') zoomer(cadre, PAS);
      else if (e.key === '-') zoomer(cadre, 1 / PAS);
      else if (e.key === '0') { z.k = 1; appliquer(cadre); }
      else if (fleches[e.key] && z.k > 1) {
        z.x += fleches[e.key][0] * DEPLACEMENT; z.y += fleches[e.key][1] * DEPLACEMENT; appliquer(cadre);
      } else return;
      e.preventDefault();
    });
  }

  /** Parcourt la page : installe les nouveaux cadres et remet à la carte entière ceux dont l'image a changé. */
  function parcourir() {
    document.querySelectorAll('.cadre-carte').forEach(function (cadre) {
      installer(cadre);
      const img = cadre.querySelector('img.carte-zoomable');
      const src = img ? img.src.length + ':' + img.src.slice(-40) : '';
      if (src !== cadre.__zoom.src) { cadre.__zoom.src = src; cadre.__zoom.k = 1; appliquer(cadre); }
    });
  }

  parcourir();
  new MutationObserver(parcourir).observe(document.body, { childList: true, subtree: true, attributes: true,
                                                           attributeFilter: ['src'] });
  // Fenêtre redimensionnée : on revient à la carte entière (les décalages en pixels ne seraient plus justes)
  window.addEventListener('resize', function () {
    document.querySelectorAll('.cadre-carte').forEach(function (c) { if (c.__zoom) { c.__zoom.k = 1; appliquer(c); } });
  });
})();
