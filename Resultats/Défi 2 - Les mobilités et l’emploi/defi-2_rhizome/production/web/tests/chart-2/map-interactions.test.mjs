import { test } from "node:test";
import assert from "node:assert/strict";
import { deliveredData, mountedExplorer } from "./explorer-harness.mjs";

test("region selection respects polygon interiors, holes and separate islands", async (t) => {
  const dataset = await deliveredData();
  const ring = (x, y, size) => [
    [x, y],
    [x + size, y],
    [x + size, y + size],
    [x, y + size],
    [x, y],
  ];
  const properties = dataset.zones.features[0].properties;
  dataset.zones.features = [
    {
      properties: { ...properties, code: "main", nom: "Main" },
      geometry: {
        type: "Polygon",
        coordinates: [ring(0, 0, 10), ring(3, 3, 2)],
      },
    },
    {
      properties: { ...properties, code: "islands", nom: "Islands" },
      geometry: {
        type: "MultiPolygon",
        coordinates: [[ring(20, 0, 2)], [ring(30, 0, 2)]],
      },
    },
  ];
  const app = await mountedExplorer(t, dataset);
  function click(lon, lat) {
    app.map.mapView.pixelsToLonLat = () => ({ lon, lat });
    app.options.chart.events.click.call(app.map, { chartX: 212, chartY: 108 });
    return app.control("zone-name").textContent;
  }
  assert.equal(click(21, 1), "Islands");
  assert.equal(click(1, 1), "Main");
  assert.equal(click(31, 1), "Islands");
  assert.equal(
    click(4, 4),
    "Islands",
    "A hole preserves the previous selection",
  );
  assert.equal(
    click(15, 1),
    "Islands",
    "Outside all polygons preserves the previous selection",
  );
});

test("map and commune clicks select the geographic zone while preserving commune details", async (t) => {
  const dataset = await deliveredData();
  const app = await mountedExplorer(t, dataset);
  let coordinates;
  app.map.mapView.pixelsToLonLat = (point) => {
    coordinates = point;
    return { lon: 2.35, lat: 48.85 };
  };
  app.select(
    dataset.zones.features.find((feature) => feature.properties.nom !== "Paris")
      .properties.code,
  );
  assert.equal(app.options.mapNavigation.enableMouseWheelZoom, true);
  app.options.chart.events.click.call(app.map, { chartX: 212, chartY: 108 });
  assert.deepEqual(
    coordinates,
    { x: 200, y: 100 },
    "Use plot coordinates after zoom or pan",
  );
  assert.equal(app.control("zone-name").textContent, "Paris");
  const commune = app.options.series.find((series) => series.id === "communes");
  const parisCommune = commune.data.find((point) => point.name === "Paris");
  commune.point.events.click.call(
    { options: parisCommune },
    { chartX: 212, chartY: 108 },
  );
  assert.match(app.control("commune-detail").textContent, /^Paris \(75056\)/);
  assert.equal(app.control("zone-name").textContent, "Paris");
  assert.equal(app.control("explorer").scrolls, 2);
  app.map.mapView.pixelsToLonLat = () => ({ lon: 0, lat: 0 });
  app.options.chart.events.click.call(app.map, { chartX: 212, chartY: 108 });
  assert.equal(app.control("zone-name").textContent, "Paris");
  assert.equal(
    app.control("explorer").scrolls,
    2,
    "Outside the available zones preserves the current portrait",
  );
});

test("delivered zone centers resolve to their own zone without guessing from commune names", async (t) => {
  const dataset = await deliveredData();
  const app = await mountedExplorer(t, dataset);
  for (const { properties: zone } of dataset.zones.features) {
    app.map.mapView.pixelsToLonLat = () => ({
      lon: zone.center[0],
      lat: zone.center[1],
    });
    app.options.chart.events.click.call(app.map, { chartX: 212, chartY: 108 });
    assert.equal(app.control("zone-name").textContent, zone.nom);
  }
});

test("French map labels stay local to the explorer instead of changing the shared engine", async (t) => {
  const app = await mountedExplorer(t, await deliveredData());
  const summary = app.options.lang.accessibility.series?.summary;
  assert.equal(
    summary?.map,
    "{series.name}, carte de {series.points.length} communes.",
  );
  assert.equal(
    summary?.mapCombination,
    "{series.name}, série {seriesNumber} sur {chart.series.length}. Carte de {series.points.length} communes.",
  );
  assert.equal(app.options.lang.zoomIn, "Agrandir");
  assert.equal(app.options.lang.zoomOut, "Réduire");
  assert.equal(
    app.options.lang.accessibility.zoom.mapZoomIn,
    "Agrandir la carte",
  );
  assert.equal(
    app.options.lang.accessibility.screenReaderSection.endOfChartMarker,
    "Fin de la carte interactive.",
  );
});
