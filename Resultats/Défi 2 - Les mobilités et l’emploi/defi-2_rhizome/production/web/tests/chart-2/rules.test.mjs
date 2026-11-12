import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import vm from "node:vm";
import { deliveredData, mountedExplorer } from "./explorer-harness.mjs";
import { expectedPetal, indicatorValues } from "./expected-encoding.mjs";

const dataset = await deliveredData();

// The delivered background covers the reference map and excludes features entirely outside it.
const mapBounds = { west: 1.78, south: 48.49, east: 3.02, north: 49.09 };
function coordinates(value) {
  if (typeof value[0] === "number") return [value];
  return value.flatMap(coordinates);
}
function intersectsBounds(feature) {
  const points = coordinates(feature.geometry.coordinates);
  return (
    Math.min(...points.map((p) => p[0])) <= mapBounds.east &&
    Math.max(...points.map((p) => p[0])) >= mapBounds.west &&
    Math.min(...points.map((p) => p[1])) <= mapBounds.north &&
    Math.max(...points.map((p) => p[1])) >= mapBounds.south
  );
}
for (const layer of ["communes", "oldLines", "lines", "stations"]) {
  assert.ok(
    dataset[layer].features.every(intersectsBounds),
    `${layer} contains a feature outside the reference map`,
  );
}
const recentLines = new Set(
  dataset.lines.features.map((feature) => feature.properties.nom),
);
assert.ok(
  !recentLines.has("TRAM 14"),
  "The T14 was renamed in 2025, not opened: it belongs to the older network",
);
assert.equal(
  dataset.lines.features.filter(
    (feature) =>
      feature.properties.nom === "METRO 11" &&
      feature.properties.annee === 2024,
  ).length,
  6,
  "The undated tracks of the 2024 metro 11 extension are drawn",
);
const linePoints = new Set(
  dataset.lines.features.flatMap((feature) =>
    feature.geometry.coordinates.map((point) => point.join()),
  ),
);
for (const name of [
  "Serge Gainsbourg",
  "Romainville - Carnot",
  "Montreuil - Hôpital",
  "La Dhuys",
  "Coteaux Beauclair",
  "Rosny-Bois-Perrier",
]) {
  const station = dataset.stations.features.find(
    (feature) => feature.properties.nom === name,
  );
  assert.ok(
    station && linePoints.has(station.geometry.coordinates.join()),
    `${name} sits on a drawn track`,
  );
}
for (const layer of ["communes", "zones", "oldLines", "lines", "stations"]) {
  for (const feature of dataset[layer].features) {
    for (const [lon, lat] of coordinates(feature.geometry.coordinates))
      assert.ok(
        lon === Math.round(lon * 1e5) / 1e5 &&
          lat === Math.round(lat * 1e5) / 1e5,
        `${layer}: coordinates are rounded to the metre`,
      );
  }
}
for (const layer of ["oldLines", "lines"])
  assert.ok(
    dataset[layer].features.every(
      (feature) => feature.geometry.coordinates.length >= 2,
    ),
    `${layer}: every track keeps both ends`,
  );
assert.ok(
  dataset.communes.features.some(
    (feature) => feature.properties.code === "75056",
  ),
  "Paris remains available",
);

test("native legend displays five evolution classes and enables accessible filtering", async (t) => {
  const app = await mountedExplorer(t, dataset);
  assert.equal(app.options.legend.enabled, true);
  assert.equal(app.options.legend.accessibility.enabled, true);
  assert.match(
    app.options.accessibility.description,
    /Classes d’évolution : Moins de −5 %/,
  );
  assert.match(
    app.options.accessibility.description,
    /15 % ou plus. Donnée indisponible/,
  );
  assert.deepEqual(
    app.options.colorAxis.dataClasses.map(({ name, color }) => [name, color]),
    [
      ["Moins de −5 %", "#2C7FB8"],
      ["−5 % à moins de 0 %", "#A6CEE3"],
      ["0 % à moins de 5 %", "#FBE6CC"],
      ["5 % à moins de 15 %", "#F5AE6B"],
      ["15 % ou plus", "#D9531E"],
    ],
  );
  const missing = app.options.series.find(
    (series) => series.name === "Donnée indisponible",
  );
  assert.equal(missing.color, "#F1EFEA");
  assert.equal(missing.showInLegend, true);
  assert.deepEqual(missing.data, []);
  assert.equal(app.options.plotOptions.series.colorAxis, false);
  assert.equal(app.options.plotOptions.series.showInLegend, false);
  assert.equal(
    app.options.series.find((series) => series.id === "communes").colorAxis,
    0,
  );
});

test("native network and territory keys reproduce the mapped lines and station symbol", async (t) => {
  const app = await mountedExplorer(t, dataset);
  const keys = app.options.series.filter(
    (series) => series.showInLegend && series.type === "mapline",
  );
  assert.deepEqual(
    keys.map(({ name, color, lineWidth, dashStyle }) => [
      name,
      color,
      lineWidth,
      dashStyle,
    ]),
    [
      ["Ligne ouverte entre 2015 et 2025", "#0e1b2c", 2.2, undefined],
      ["Réseau antérieur à 2015", "#a3aab5", 0.7, undefined],
      ["Encadré du Tram T4", "#1e3442", 1.5, "Dash"],
      ["Contour de zone d’emploi", "#66727f", 1, undefined],
    ],
  );
  assert.ok(
    keys.every(
      (key) => key.data.length === 0 && key.legendSymbol === "lineMarker",
    ),
  );
  assert.deepEqual(keys[0].marker, {
    enabled: true,
    symbol: "circle",
    radius: 2.6,
    fillColor: "#fff",
    lineColor: "#0e1b2c",
    lineWidth: 1,
  });
  assert.equal(app.options.legend.navigation.enabled, false);
});

test("native legend reserves only its current height and clears it on disposal", async (t) => {
  const app = await mountedExplorer(t, dataset);
  const style = app.control("map-wrap").style;
  const writes = [];
  style.setProperty = (name, value) => writes.push([name, value]);
  app.map.legend = { legendHeight: 180.4 };
  app.redraw();
  app.redraw();
  assert.deepEqual(writes, [["--map-legend-height", "181px"]]);
  app.map.legend.legendHeight = 80;
  app.redraw();
  assert.deepEqual(writes[1], ["--map-legend-height", "80px"]);
  app.dispose();
  assert.deepEqual(writes[2], ["--map-legend-height", "0px"]);
});

test("commune map classes include every boundary and escape tooltip content", async (t) => {
  const fixture = structuredClone(dataset);
  const cases = [
    [null, "#F1EFEA"],
    [-5.001, "#2C7FB8"],
    [-5, "#A6CEE3"],
    [-0.001, "#A6CEE3"],
    [0, "#FBE6CC"],
    [4.999, "#FBE6CC"],
    [5, "#F5AE6B"],
    [14.999, "#F5AE6B"],
    [15, "#D9531E"],
    [150, "#D9531E"],
  ];
  fixture.communes.features = fixture.communes.features.slice(0, cases.length);
  fixture.communes.features.forEach((feature, index) => {
    feature.properties.evolution = cases[index][0];
  });
  fixture.communes.features[0].properties.nom = '<img src=x onerror="x">';
  const app = await mountedExplorer(t, fixture);
  const communes = app.options.series.find(
    (series) => series.id === "communes",
  );
  const context = vm.createContext({
    module: { exports: {} },
    exports: {},
    console,
  });
  vm.runInContext(
    await readFile(
      new URL("../../node_modules/highcharts/highmaps.js", import.meta.url),
      "utf8",
    ),
    context,
  );
  const ColorAxis = context.module.exports.ColorAxis;
  const axis = { dataClasses: app.options.colorAxis.dataClasses };
  assert.deepEqual(
    communes.data.map((point) => point.value),
    cases.map(([value]) => value),
  );
  assert.ok(communes.data.every((point) => !("color" in point)));
  assert.deepEqual(
    communes.data.map((point) =>
      point.value === null
        ? communes.nullColor
        : ColorAxis.prototype.toColor.call(axis, point.value, {}),
    ),
    cases.map(([, color]) => color),
  );
  assert.equal(communes.nullColor, "#F1EFEA");
  const tooltip = app.options.tooltip.formatter.call({
    options: communes.data[0],
  });
  assert.ok(tooltip.startsWith("&lt;img src=x onerror=&quot;x&quot;&gt;"));
  assert.ok(!tooltip.includes("<img"));
  for (const [name, full] of [
    ["TRAM 13", "Tram T13"],
    ["METRO 14", "Métro 14"],
    ["CABLE 1", "Câble C1"],
    ["RER E", "RER E"],
  ]) {
    assert.equal(
      app.options.tooltip.formatter.call({
        options: {},
        properties: { nom: name, annee: 2024 },
      }),
      `${full}<br>Mise en service (donnée IDFM) : 2024`,
    );
  }
});

test("five displayed indicators preserve formulas and real-data gaps", async (t) => {
  const app = await mountedExplorer(t, dataset);
  assert.equal(dataset.zones.features.length, 15);
  const decimal = new Intl.NumberFormat("fr-FR", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  });
  const signed = new Intl.NumberFormat("fr-FR", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
    signDisplay: "exceptZero",
  });
  for (const { properties: zone } of dataset.zones.features) {
    const values = indicatorValues(zone);
    assert.equal(
      values[0] === null,
      values[3] === null,
      `${zone.nom}: both private-employment indicators share their gaps`,
    );
    app.select(zone.code);
    const amounts = app
      .control("details")
      .children.map((row) => row.children[1].textContent);
    assert.deepEqual(
      amounts,
      values.map((value, index) =>
        value === null
          ? "Donnée indisponible"
          : `${(index < 2 ? signed : decimal).format(value)}${index < 3 ? "\u00a0%" : index === 3 ? "\u00a0pour 100 salariés" : "\u00a0pour 100 actifs occupés résidents"}`,
      ),
    );
    for (const value of values)
      assert.ok(value === null || Number.isFinite(value));
  }
  for (let index = 0; index < 5; index++) {
    const values = dataset.zones.features
      .map(({ properties }) => indicatorValues(properties)[index])
      .filter((value) => value !== null);
    assert.ok(
      values.length >= 13 && Math.max(...values) > 0,
      `Indicator ${index + 1}: enough zones to compare`,
    );
  }
  const outlines = app.graphics.filter(
    (item) =>
      item.parent === app.map.zoneLayer && item.attributes.stroke !== "#fffefa",
  );
  assert.equal(
    outlines.length,
    dataset.zones.features.length,
    "Every zone has a rendered outline",
  );
  assert.ok(outlines.every((outline) => outline.geometry.length > 0));
});

test("missing years, zero bases and zero denominators remain unavailable without fallback", async (t) => {
  const fixture = structuredClone(dataset);
  const inputs = [
    {
      "Salariés privés": { 2016: 100, 2024: 200 },
      "Demandeurs ABC": { 2016: 100, 2024: 50 },
      "Taux de chômage localisé": { 2024: 0 },
      "Emplois au lieu de travail": { 2016: 1 },
      "Actifs occupés résidents": { 2016: 4 },
    },
    {
      "Salariés privés": { 2016: 100, 2024: 150 },
      "Demandeurs ABC": { 2016: 0, 2024: 50 },
    },
    {
      "Salariés privés": { 2016: 100, 2024: 50 },
      "Demandeurs ABC": { 2024: 1 },
    },
    {
      "Salariés privés": { 2016: 100, 2024: 100 },
      "Demandeurs ABC": { 2016: 100, 2024: null },
    },
    {
      "Salariés privés": { 2016: 100, 2023: 200, 2024: null },
      "Taux de chômage localisé": { 2016: 8, 2023: 9, 2024: null },
    },
    {
      "Salariés privés": { 2016: 0, 2024: 0 },
      "Demandeurs ABC": { 2016: 100, 2024: 5 },
      "Emplois au lieu de travail": { 2016: 1 },
      "Actifs occupés résidents": { 2016: 0 },
    },
  ];
  fixture.zones.features = fixture.zones.features.slice(0, inputs.length);
  fixture.zones.features.forEach((feature, index) => {
    feature.properties.indicators = inputs[index];
  });
  const app = await mountedExplorer(t, fixture);
  const expected = [
    ["+100,0 %", "-50,0 %", "0,0 %", "25,0", "25,0"],
    ["+50,0 %", "Indisponible", "Indisponible", "33,3", "Indisponible"],
    ["-50,0 %", "Indisponible", "Indisponible", "2,0", "Indisponible"],
    ["0,0 %", "Indisponible", "Indisponible", "Indisponible", "Indisponible"],
    [
      "Indisponible",
      "Indisponible",
      "Indisponible",
      "Indisponible",
      "Indisponible",
    ],
    ["Indisponible", "-95,0 %", "Indisponible", "Indisponible", "Indisponible"],
  ];
  for (let index = 0; index < inputs.length; index++) {
    const zone = fixture.zones.features[index].properties;
    app.select(zone.code);
    const amounts = app
      .control("details")
      .children.map((row) =>
        row.children[1].textContent.replaceAll("\u00a0", " "),
      );
    assert.deepEqual(
      amounts,
      expected[index].map((value, indicatorIndex) =>
        value === "Indisponible"
          ? "Donnée indisponible"
          : value +
            (indicatorIndex === 3
              ? " pour 100 salariés"
              : indicatorIndex === 4
                ? " pour 100 actifs occupés résidents"
                : ""),
      ),
    );
    const marker = app
      .markers()
      .find((marker) =>
        app
          .children(marker)
          .some(
            (item) => item.kind === "text" && item.geometry[0] === zone.nom,
          ),
      );
    const paths = app.children(marker).filter((item) => item.kind === "path");
    const length = [42, 21, 21, 0, 12, 12][index];
    assert.deepEqual(
      paths[0].geometry,
      expectedPetal(length * 0.75),
      "Proportional lengths, zero and missing stubs",
    );
    assert.deepEqual(
      paths[2].geometry,
      expectedPetal((index === 0 ? 0 : 12) * 0.75),
      "Zero maximum draws no petal; missing remains a stub",
    );
  }
});

test("line tags stay anchored to their recent line and near its terminus", async (t) => {
  const app = await mountedExplorer(t, dataset);
  const tags = app.options.series.find(
    (series) => series.name === "Noms des lignes",
  ).data;
  const names = [
    ...new Set(dataset.lines.features.map((feature) => feature.properties.nom)),
  ].filter((name) => name !== "TRAM 4");
  assert.equal(
    tags.length,
    names.length,
    "One tag per recent line; T4 has its framed label",
  );
  assert.equal(new Set(tags.map((tag) => tag.name)).size, tags.length);
  for (const tag of tags) {
    assert.ok(
      dataset.lines.features.some((feature) =>
        feature.geometry.coordinates.some(
          ([lon, lat]) => lon === tag.lon && lat === tag.lat,
        ),
      ),
      `${tag.name} is anchored on its line`,
    );
    assert.ok(
      Number.isFinite(tag.dataLabels.x) &&
        Number.isFinite(tag.dataLabels.y) &&
        Math.hypot(tag.dataLabels.x, tag.dataLabels.y) < 40,
      `${tag.name} stays next to its terminus`,
    );
  }
  for (const tag of ["T13", "M14", "C1", "RER E"])
    assert.ok(
      tags.some((item) => item.name === tag),
      tag,
    );
});

test("map scale displays a readable distance and hides when projection is unavailable", async (t) => {
  const app = await mountedExplorer(t, dataset);
  const kmPerDegree = 111.32 * Math.cos((48.85 * Math.PI) / 180);
  app.map.mapView.lonLatToPixels = ({ lon }) => ({
    x: lon * kmPerDegree * 10,
    y: 0,
  });
  app.redraw();
  assert.equal(app.control("map-scale").hidden, false);
  assert.equal(
    app.control("map-scale").querySelector("span").textContent,
    "10 km",
  );
  assert.ok(
    Math.abs(
      parseFloat(app.control("map-scale").querySelector("i").style.width) - 100,
    ) < 1e-8,
  );
  app.map.mapView.lonLatToPixels = () => undefined;
  app.redraw();
  assert.equal(app.control("map-scale").hidden, true);
  app.map.mapView.lonLatToPixels = () => ({ x: 0, y: 0 });
  app.redraw();
  assert.equal(app.control("map-scale").hidden, true);
});

test("delivered metrics retain nonnegative finite observations and zone centers", () => {
  for (const metric of dataset.metrics) {
    for (const { properties: zone } of dataset.zones.features) {
      assert.ok(zone.indicators[metric.name], `${zone.nom}: ${metric.name}`);
      assert.ok(Array.isArray(zone.center) && zone.center.length === 2);
      for (const value of Object.values(zone.indicators[metric.name])) {
        assert.ok(
          value === null ||
            (typeof value === "number" && Number.isFinite(value) && value >= 0),
        );
      }
    }
  }
});

test("the delivered Highmaps engine converts the transport layers consumed by the chart", async (t) => {
  // The VM isolates the real npm engine; map and DOM rendering use the test harness.
  const context = vm.createContext({
    module: { exports: {} },
    exports: {},
    console,
  });
  vm.runInContext(
    await readFile(
      new URL("../../node_modules/highcharts/highmaps.js", import.meta.url),
      "utf8",
    ),
    context,
  );
  const highmaps = context.module.exports;
  const app = await mountedExplorer(t, dataset, {
    geojson: (data, type) => highmaps.geojson(data, type),
  });
  for (const [name, field, layer] of [
    ["Réseau ferré antérieur à 2015", "mapData", "oldLines"],
    ["Lignes ouvertes entre 2015 et 2025", "data", "lines"],
    ["Tracé des lignes ouvertes entre 2015 et 2025", "mapData", "lines"],
    ["Gares ouvertes entre 2015 et 2025", "data", "stations"],
  ]) {
    const converted = app.options.series.find((series) => series.name === name)[
      field
    ];
    assert.equal(converted.length, dataset[layer].features.length, name);
    assert.ok(
      converted.every((point) => point.geometry.coordinates.length > 0),
    );
  }
});

test("unavailable communes keep their fill scale and gain a distinct border", async (t) => {
  const app = await mountedExplorer(t, dataset);
  const series = app.options.series.find(({ id }) => id === "communes");
  const missing = series.data.filter(({ value }) => value === null);
  const available = series.data.filter(({ value }) => value !== null);
  assert.ok(missing.length > 0);
  assert.ok(
    missing.every(
      ({ borderColor, borderWidth }) =>
        borderColor === "#7f8894" && borderWidth === 0.8,
    ),
  );
  assert.ok(
    available.every(
      (point) =>
        point.borderColor === undefined && point.borderWidth === undefined,
    ),
  );
  assert.equal(series.nullColor, "#F1EFEA");
  assert.deepEqual(series.states.hover, {
    borderColor: "#273f31",
    borderWidth: 1,
    brightness: 0.08,
  });
});
