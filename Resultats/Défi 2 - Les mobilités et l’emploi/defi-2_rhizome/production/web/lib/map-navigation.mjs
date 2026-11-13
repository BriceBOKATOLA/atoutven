/**
 * Add map-level keyboard controls without taking keys from Highcharts points or
 * legend controls. Wheel zoom, primary-button drag and two-finger gestures stay
 * with Highmaps, which owns the view and its geographic limits.
 * Pass the frame outside chart.renderTo: Highcharts moves its own keyboard
 * target to renderTo when that element has tabindex. Keep those targets apart.
 * @param {HTMLElement} host
 * @param {{plotWidth: number, plotHeight: number, mapView?: {
 *   zoom: number,
 *   zoomBy(amount?: number): void,
 *   pixelsToLonLat(point: {x: number, y: number}): {lon: number, lat: number} | undefined,
 *   setView(center: [number, number], zoom?: number, redraw?: boolean, animation?: boolean): void
 * }}} chart
 */
export function bindMapNavigation(host, chart) {
  const attributes = {
    tabindex: "0",
    role: "group",
    "aria-label":
      "Déplacer et agrandir la carte : flèches pour déplacer, + ou = pour agrandir, - pour réduire, 0 pour revenir à la vue initiale. Tabulation pour parcourir les données et la légende.",
  };
  const previousAttributes = Object.fromEntries(
    Object.keys(attributes).map((name) => [name, host.getAttribute(name)]),
  );
  for (const [name, value] of Object.entries(attributes))
    host.setAttribute(name, value);

  const controller = new AbortController();
  host.addEventListener(
    "keydown",
    (event) => {
      if (
        event.target !== host ||
        event.defaultPrevented ||
        event.altKey ||
        event.ctrlKey ||
        event.metaKey
      )
        return;
      const view = chart.mapView;
      if (!view) return;
      if (event.key === "+" || event.key === "=") view.zoomBy(1);
      else if (event.key === "-") view.zoomBy(-1);
      else if (event.key === "0") view.zoomBy();
      else {
        const directions = {
          ArrowLeft: [-1, 0],
          ArrowRight: [1, 0],
          ArrowUp: [0, -1],
          ArrowDown: [0, 1],
        };
        const direction = directions[event.key];
        if (!direction) return;
        const center = view.pixelsToLonLat({
          x: chart.plotWidth * (0.5 + direction[0] * 0.2),
          y: chart.plotHeight * (0.5 + direction[1] * 0.2),
        });
        if (!center) return;
        view.setView([center.lon, center.lat], view.zoom, true, false);
      }
      event.preventDefault();
    },
    { signal: controller.signal },
  );
  // MapChart's native followTouchMove:false allows one-finger map panning.
  // Intercept only single-touch movement before it reaches that handler. Leave
  // its default browser action intact, and allow native two-finger pinch/pan.
  host.addEventListener(
    "touchmove",
    (event) => {
      if (event.touches.length === 1) event.stopPropagation();
    },
    { capture: true, passive: true, signal: controller.signal },
  );
  return () => {
    controller.abort();
    for (const [name, value] of Object.entries(previousAttributes)) {
      if (value === null) host.removeAttribute(name);
      else host.setAttribute(name, value);
    }
  };
}
