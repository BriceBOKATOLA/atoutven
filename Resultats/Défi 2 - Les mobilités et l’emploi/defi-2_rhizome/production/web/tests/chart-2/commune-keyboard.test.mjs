import { test } from "node:test";
import assert from "node:assert/strict";
import SeriesKeyboardNavigation from "highcharts/es-modules/Accessibility/Components/SeriesComponent/SeriesKeyboardNavigation.js";
import { shell } from "../../app/(chart-2)/charts/chart-2/lib/shell.ts";
import { deliveredData, mountedExplorer } from "./explorer-harness.mjs";

test("all loaded communes expose accessible point descriptions without a separate selector", async (t) => {
  const dataset = await deliveredData();
  const app = await mountedExplorer(t, dataset);
  assert.doesNotMatch(
    shell,
    /commune-select|commune-control|Choisir une commune/,
  );
  assert.equal(
    app.options.accessibility.series.pointDescriptionEnabledThreshold,
    false,
  );
  assert.equal(
    app.options.accessibility.keyboardNavigation.seriesNavigation
      .pointNavigationEnabledThreshold,
    false,
  );
  assert.equal(
    app.options.accessibility.keyboardNavigation.seriesNavigation
      .skipNullPoints,
    false,
  );
  const communes = app.options.series.find(
    (series) => series.id === "communes",
  );
  assert.equal(communes.accessibility.enabled, true);
  assert.equal(communes.data.length, 795);
  const describe = communes.accessibility.point.descriptionFormatter;
  assert.equal(
    describe({
      options: communes.data.find((point) => point.code === "75056"),
    }),
    "Paris (75056) ; 2016 : 201 985 ; 2024 : 196 995 ; évolution : -2,5 %",
  );
  for (const point of communes.data)
    assert.ok(
      describe({ options: point }).startsWith(`${point.name} (${point.code})`),
    );
});

test("the installed Highcharts Enter and Space handlers activate commune data and zone", async (t) => {
  const dataset = await deliveredData();
  const selected = {
    options: { code: "75056" },
    select(value) {
      this.selected = value;
    },
  };
  const app = await mountedExplorer(t, dataset, {
    map: { get: () => ({ points: [selected] }) },
  });
  const communes = app.options.series.find(
    (series) => series.id === "communes",
  );
  const point = {
    options: communes.data.find((point) => point.code === "75056"),
    plotX: 200,
    plotY: 100,
    series: {},
    firePointEvent(type, event) {
      communes.point.events[type].call(this, event);
    },
  };
  const chart = { ...app.map, highlightedPoint: point };
  const handler = new SeriesKeyboardNavigation(chart, {
    enter: 13,
    space: 32,
  }).getKeyboardNavigationHandler();
  const paris = dataset.zones.features.find(
    (f) => f.properties.nom === "Paris",
  ).properties;
  const cergy = dataset.zones.features.find(
    (f) => f.properties.nom === "Cergy-Vexin",
  ).properties;
  for (const keyCode of [13, 32]) {
    app.select(cergy.code);
    assert.equal(handler.run({ keyCode }), handler.response.success);
    assert.equal(app.control("zone-name").textContent, "Paris");
    assert.equal(
      app.control("commune-detail").textContent,
      "Paris (75056) ; 2016 : 201 985 ; 2024 : 196 995 ; évolution : -2,5 %",
    );
    assert.equal(selected.selected, true);
    assert.equal(
      app.control("explorer").scrolls,
      0,
      "Keyboard activation keeps the focused commune in view",
    );
    app.select(paris.code);
    assert.match(app.control("commune-detail").textContent, /^Paris/);
    app.select(cergy.code);
    assert.equal(app.control("commune-detail").textContent, "");
    assert.equal(selected.selected, false);
  }
});

test("accessible commune descriptions and activation preserve absent observations", async (t) => {
  const dataset = await deliveredData();
  dataset.communes.features[0].properties = {
    code: "missing",
    nom: "Sans données",
    defm2016: null,
    defm2024: 0,
    evolution: null,
  };
  const app = await mountedExplorer(t, dataset);
  const communes = app.options.series.find(
    (series) => series.id === "communes",
  );
  const point = {
    options: communes.data.find((point) => point.code === "missing"),
  };
  const expected =
    "Sans données (missing) ; 2016 : indisponible ; 2024 : 0 ; évolution indisponible";
  assert.equal(
    communes.accessibility.point.descriptionFormatter(point),
    expected,
  );
  communes.point.events.click.call(point, { chartX: 212, chartY: 108, point });
  assert.equal(app.control("commune-detail").textContent, expected);
});
