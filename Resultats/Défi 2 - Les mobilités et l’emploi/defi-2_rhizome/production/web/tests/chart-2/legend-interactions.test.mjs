import { test } from "node:test";
import assert from "node:assert/strict";
import "highcharts/es-modules/Core/Series/Series.js";
import ColorAxis from "highcharts/es-modules/Core/Axis/Color/ColorAxis.js";
import ColorAxisBase from "highcharts/es-modules/Core/Axis/Color/ColorAxisBase.js";
import LegendComponent from "highcharts/es-modules/Accessibility/Components/LegendComponent.js";
import { deliveredData, mountedExplorer } from "./explorer-harness.mjs";

function layer(points = []) {
  return {
    points,
    visible: true,
    setVisible(visible, redraw) {
      assert.equal(redraw, false);
      this.visible = visible;
    },
  };
}

test("missing-data legend toggles only null communes and preserves selected details", async (t) => {
  const points = [null, -5, 0, 5, 15].map((value) => ({
    value,
    visible: true,
    selected: true,
    graphic: {
      attr(attributes) {
        Object.assign(this, attributes);
      },
    },
    setVisible(visible) {
      this.visible = visible;
    },
  }));
  const layers = new Map([["communes", layer(points)]]);
  const app = await mountedExplorer(t, await deliveredData(), {
    map: { get: (id) => layers.get(id), redraw() {} },
  });
  const item = {
    ...layer(),
    options: { id: "legend-missing" },
    name: "Donnée indisponible",
  };
  const details = app.control("details").textContent;
  assert.ok(details.length > 0);
  const click = () =>
    app.options.legend.events.itemClick.call(
      { chart: app.map },
      { legendItem: item },
    );
  assert.equal(click(), false);
  assert.deepEqual(
    points.map((point) => point.visible),
    [false, true, true, true, true],
  );
  assert.ok(points.every((point) => point.selected));
  assert.equal(points[0].hiddenInDataClass, true);
  assert.equal(points[0].graphic.visibility, "hidden");
  app.redraw();
  assert.equal(points[0].graphic.visibility, "hidden");
  assert.equal(app.control("details").textContent, details);
  click();
  assert.ok(points.every((point) => point.visible));
  assert.equal(points[0].hiddenInDataClass, false);
  assert.equal(points[0].graphic.visibility, "inherit");
});

test("network keys toggle all related layers without affecting other representations", async (t) => {
  const ids = [
    "recent-lines-halo",
    "recent-lines",
    "recent-stations",
    "recent-line-labels",
    "old-lines",
    "tram-t4-box",
    "tram-t4-label",
    "communes",
  ];
  const layers = new Map(ids.map((id) => [id, layer()]));
  const app = await mountedExplorer(t, await deliveredData(), {
    map: { get: (id) => layers.get(id), redraw() {} },
  });
  for (const id of ids)
    assert.ok(
      app.options.series.some((series) => series.id === id),
      id,
    );
  for (const [id, affected] of [
    ["legend-recent", ids.slice(0, 4)],
    ["legend-old", ["old-lines"]],
    ["legend-t4", ["tram-t4-box", "tram-t4-label"]],
  ]) {
    const item = { ...layer(), options: { id } };
    const click = () =>
      app.options.legend.events.itemClick.call(
        { chart: app.map },
        { legendItem: item },
      );
    click();
    for (const [layerId, series] of layers)
      assert.equal(series.visible, !affected.includes(layerId), layerId);
    click();
    assert.ok([...layers.values()].every((series) => series.visible));
  }
});

test("zone outline visibility survives redraw and selection while flowers remain visible", async (t) => {
  const dataset = await deliveredData();
  const app = await mountedExplorer(t, dataset, {
    map: { redraw() {} },
  });
  const item = { ...layer(), options: { id: "legend-zones" } };
  const click = () =>
    app.options.legend.events.itemClick.call(
      { chart: app.map },
      { legendItem: item },
    );
  click();
  assert.equal(app.map.zoneLayer.attributes.visibility, "hidden");
  app.select(dataset.zones.features[0].properties.code);
  assert.equal(app.map.zoneLayer.attributes.visibility, "hidden");
  app.redraw();
  assert.equal(app.map.zoneLayer.attributes.visibility, "hidden");
  assert.notEqual(app.map.flowerLayer.attributes.visibility, "hidden");
  click();
  assert.equal(app.map.zoneLayer.attributes.visibility, "visible");
});

test("installed Highcharts class filtering uses exact raw boundaries and leaves null separate", async (t) => {
  const values = [-5.001, -5, -0.001, 0, 4.999, 5, 14.999, 15, 15.001, null];
  const points = values.map((value) => ({
    value,
    visible: true,
    graphic: {
      attr(attributes) {
        Object.assign(this, attributes);
      },
    },
    setVisible(visible) {
      this.visible = visible;
    },
  }));
  const app = await mountedExplorer(t, await deliveredData(), {
    map: { get: (id) => (id === "communes" ? { points } : undefined) },
  });
  const series = { points };
  for (const point of points) point.series = series;
  const axis = {
    dataClasses: app.options.colorAxis.dataClasses,
    series: [series],
    chart: {
      options: { legend: {} },
      numberFormatter: String,
      legend: { colorizeItem() {} },
    },
  };
  for (const point of points) {
    if (point.value !== null)
      ColorAxisBase.toColor.call(axis, point.value, point);
  }
  assert.deepEqual(
    points.map((point) => point.dataClass),
    [0, 1, 1, 2, 2, 3, 3, 4, 4, undefined],
  );
  const entries = ColorAxis.prototype.getDataClassLegendSymbols.call(axis);
  const expected = [[0], [1, 2], [3, 4], [5, 6], [7, 8]];
  for (const [index, item] of entries.entries()) {
    const click = () =>
      app.options.legend.events.itemClick.call(
        { chart: app.map },
        { legendItem: item },
      );
    click();
    assert.deepEqual(
      points.flatMap((point, i) => (point.visible ? [] : [i])),
      expected[index],
    );
    for (const point of points)
      assert.equal(
        point.graphic.visibility,
        point.visible ? "inherit" : "hidden",
      );
    app.redraw();
    assert.deepEqual(
      points.flatMap((point, i) =>
        point.graphic.visibility === "hidden" ? [i] : [],
      ),
      expected[index],
    );
    click();
    assert.ok(points.every((point) => point.visible));
  }
});

test("installed legend keyboard handler toggles composite controls with Enter and Space", async (t) => {
  const series = layer();
  const app = await mountedExplorer(t, await deliveredData(), {
    map: { get: (id) => (id === "old-lines" ? series : undefined) },
  });
  const attributes = {};
  const item = {
    ...layer(),
    name: "Réseau antérieur à 2015",
    options: { id: "legend-old" },
    a11yProxyElement: {
      innerElement: {
        setAttribute(name, value) {
          attributes[name] = value;
        },
      },
      click() {
        app.options.legend.events.itemClick.call(
          { chart: app.map },
          { legendItem: item },
        );
      },
    },
  };
  const component = new LegendComponent();
  component.chart = { ...app.map, legend: { allItems: [item] } };
  component.keyCodes = { enter: 13, space: 32 };
  component.highlightedLegendItemIx = 0;
  const handler = component.getKeyboardNavigation();
  for (const keyCode of [13, 32]) {
    assert.equal(handler.run({ keyCode }), handler.response.success);
    assert.equal(series.visible, false);
    assert.equal(attributes["aria-label"], "Afficher Réseau antérieur à 2015");
    assert.equal(handler.run({ keyCode }), handler.response.success);
    assert.equal(series.visible, true);
    assert.equal(attributes["aria-label"], "Masquer Réseau antérieur à 2015");
  }
});

test("flower key hides only map flowers and preserves hidden state across render and selection", async (t) => {
  const dataset = await deliveredData();
  const app = await mountedExplorer(t, dataset);
  const key = app.options.series.find(
    (series) => series.id === "legend-flowers",
  );
  assert.ok(key, "a native legend entry controls the map flowers");
  assert.equal(key.showInLegend, true);
  assert.equal(key.type, "mappoint");
  const attributes = {};
  const item = {
    ...layer(),
    name: key.name,
    options: { id: key.id },
    a11yProxyElement: {
      innerElement: {
        setAttribute(name, value) {
          attributes[name] = value;
        },
      },
    },
  };
  const click = () =>
    app.options.legend.events.itemClick.call(
      { chart: app.map },
      { legendItem: item },
    );
  const details = app.control("details").textContent;
  const preview = app.control("flower-preview").firstElementChild;
  const legend = app.control("legend-flower").firstElementChild;
  const marker = app.markers()[0];
  marker.element.onmouseenter();
  assert.equal(app.control("map-tooltip").hidden, false);
  click();
  assert.equal(item.visible, false);
  assert.equal(app.map.flowerLayer.attributes.visibility, "hidden");
  assert.equal(app.map.flowerLayer.element.getAttribute("aria-hidden"), "true");
  assert.ok(
    app
      .markers()
      .every(({ element }) => element.getAttribute("tabindex") === "-1"),
  );
  assert.equal(app.control("map-tooltip").hidden, true);
  marker.element.onfocus();
  marker.element.onmouseenter();
  marker.element.onclick({ preventDefault() {}, stopPropagation() {} });
  marker.element.onkeydown({
    key: "Enter",
    preventDefault() {},
    stopPropagation() {},
  });
  assert.equal(app.control("map-tooltip").hidden, true);
  assert.equal(app.control("details").textContent, details);
  assert.equal(app.control("flower-preview").firstElementChild, preview);
  assert.equal(app.control("legend-flower").firstElementChild, legend);
  assert.equal(attributes["aria-label"], `Afficher ${key.name}`);
  assert.equal(attributes["aria-pressed"], "false");
  app.setZoom(2);
  app.redraw();
  app.select(dataset.zones.features[0].properties.code);
  assert.equal(app.map.flowerLayer.attributes.visibility, "hidden");
  assert.notEqual(app.map.zoneLayer.attributes.visibility, "hidden");
  assert.ok(
    app
      .markers()
      .every(({ element }) => element.getAttribute("tabindex") === "-1"),
  );
  click();
  assert.equal(app.map.flowerLayer.attributes.visibility, "visible");
  assert.equal(
    app.map.flowerLayer.element.getAttribute("aria-hidden"),
    "false",
  );
  assert.ok(
    app
      .markers()
      .every(({ element }) => element.getAttribute("tabindex") === "0"),
  );
  assert.equal(attributes["aria-pressed"], "true");
  app.markers()[0].element.onfocus();
  assert.equal(app.control("map-tooltip").hidden, false);
});

test("native legend keyboard handler hides and restores flowers with Enter and Space", async (t) => {
  const app = await mountedExplorer(t, await deliveredData());
  const attributes = {};
  const item = {
    ...layer(),
    name: "Zones d’emploi",
    options: { id: "legend-flowers" },
    a11yProxyElement: {
      innerElement: {
        setAttribute(name, value) {
          attributes[name] = value;
        },
      },
      click() {
        app.options.legend.events.itemClick.call(
          { chart: app.map },
          { legendItem: item },
        );
      },
    },
  };
  const component = new LegendComponent();
  component.chart = { ...app.map, legend: { allItems: [item] } };
  component.keyCodes = { enter: 13, space: 32 };
  component.highlightedLegendItemIx = 0;
  const handler = component.getKeyboardNavigation();
  for (const keyCode of [13, 32]) {
    assert.equal(handler.run({ keyCode }), handler.response.success);
    assert.equal(app.map.flowerLayer.attributes.visibility, "hidden");
    assert.equal(attributes["aria-pressed"], "false");
    assert.equal(attributes["aria-label"], "Afficher Zones d’emploi");
    assert.equal(handler.run({ keyCode }), handler.response.success);
    assert.equal(app.map.flowerLayer.attributes.visibility, "visible");
    assert.equal(attributes["aria-pressed"], "true");
    assert.equal(attributes["aria-label"], "Masquer Zones d’emploi");
  }
});

test("native flower legend symbol uses the map's five petals and indicator colors", async (t) => {
  const app = await mountedExplorer(t, await deliveredData());
  const key = app.options.series.find(({ id }) => id === "legend-flowers");
  assert.match(key.marker.symbol, /^url\(data:image\/svg\+xml,/);
  const svg = decodeURIComponent(
    key.marker.symbol.slice("url(data:image/svg+xml,".length, -1),
  );
  assert.match(svg, /viewBox="-46 -46 92 92"/);
  assert.equal((svg.match(/<path /g) ?? []).length, 5);
  for (const color of ["#B3CF78", "#E06A55", "#E0A52A", "#F2BFC8", "#9A5A90"])
    assert.ok(svg.includes(`fill="${color}"`), color);
  assert.equal((svg.match(/rotate\(/g) ?? []).length, 5);
  assert.ok(!svg.includes("<script"));
});
