import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  mapSeries,
  mountHighmaps,
  mapLegendOptions,
  mountMapLegends,
} from "./highmaps-adapter.mjs";
import { densityColor, densityKey, poleKey } from "./geometry.mjs";
const data = JSON.parse(
  readFileSync(
    new URL(
      "../../../../../public/data/employment-centers-departments.json",
      import.meta.url,
    ),
  ),
);
test("Highmaps keeps all density polygons, rail segments, departments and ranked employment poles", () => {
  const series = mapSeries(data);
  assert.equal(series.find((item) => item.id === "density").data.length, 1276);
  assert.equal(series.find((item) => item.id === "departments").data.length, 8);
  const poles = series.find((item) => item.id === "poles").data;
  assert.equal(poles.length, 87);
  assert.equal(poles[0].id, "75056");
  assert.equal(
    poles.find((item) => item.id === "75056").marker.fillColor,
    "rgba(230,159,0,.14)",
  );
  assert.equal(series.find((item) => item.id === "rail-recent").lineWidth, 2.6);
  assert.equal(series.find((item) => item.id === "rail-casing").lineWidth, 5.5);
  assert.equal(series.find((item) => item.id === "rail-earlier").lineWidth, 1);
  assert.ok(series.every((item) => item.enableMouseTracking === false));
});

test("the overlay map exposes one credit link and removes it on disposal", () => {
  const previousDocument = globalThis.document;
  const created = [];
  globalThis.document = {
    createElement(tagName) {
      const node = {
        tagName,
        setAttribute() {},
        append() {},
        remove() {
          this.removed = true;
        },
      };
      created.push(node);
      return node;
    },
  };
  const overlay = {};
  const frame = {
    insertBefore(node, target) {
      assert.equal(target, overlay);
    },
    append(node) {
      this.credit = node;
    },
    classList: { add() {}, remove() {} },
  };
  let destroyed = false;
  const H = {
    mapChart(container, options) {
      assert.equal(
        options.credits.enabled,
        false,
        "the chart must not duplicate the overlay credit",
      );
      return {
        options: {
          credits: {
            href: "https://www.highcharts.com?credits",
            text: "Highcharts.com",
          },
        },
        destroy() {
          destroyed = true;
        },
      };
    },
  };
  try {
    const map = mountHighmaps(H, frame, overlay, data);
    assert.equal(frame.credit.tagName, "a");
    assert.equal(frame.credit.href, "https://www.highcharts.com?credits");
    assert.equal(frame.credit.textContent, "Highcharts.com");
    assert.equal(frame.credit.className, "reference-highmaps-credit");
    map.destroy();
    assert.ok(destroyed);
    assert.ok(
      created
        .filter((node) => node !== created[1])
        .every((node) => node.removed),
      "both map container and link must be removed",
    );
  } finally {
    globalThis.document = previousDocument;
  }
});

test("native density legend preserves exact class boundaries and distinguishes missing data", () => {
  const options = mapLegendOptions("density");
  assert.equal(options.legend.enabled, true);
  assert.deepEqual(
    options.series.map(({ name, color }) => [name, color]),
    [
      ["< 100", "#F1EFEA"],
      ["100 à moins de 500", "#DCE3EC"],
      ["500 à moins de 2 000", "#B3C3D9"],
      ["≥ 2 000", "#7F9BC2"],
      ["Donnée non disponible", "#ffffff"],
    ],
  );
  assert.ok(options.series.every((series) => series.showInLegend));
  const event = {
    prevented: false,
    preventDefault() {
      this.prevented = true;
    },
  };
  options.legend.events.itemClick(event);
  assert.equal(
    event.prevented,
    true,
    "a reference key cannot toggle unrelated overlays",
  );
});

test("native legends retain pole states and the rail and territory explanations", () => {
  const poles = mapLegendOptions("poles").series;
  assert.deepEqual(
    poles.map(({ name }) => name),
    [
      "Plus d’emplois qu’en 2015",
      "Moins d’emplois qu’en 2015",
      "Nouveau pôle depuis 2015",
    ],
  );
  assert.equal(poles[1].marker.fillColor, "#fffefa");
  assert.equal(poles[1].marker.lineWidth, 2.2);
  assert.equal(poles[2].marker.lineColor, "#d55e00");
  assert.equal(poles[2].marker.lineWidth, 3);
  const network = mapLegendOptions("network").series;
  assert.deepEqual(
    network.map(({ name }) => name),
    [
      "Ligne ouverte depuis 2015",
      "Ligne déjà en service",
      "Limite de département",
      "Départements",
    ],
  );
  assert.equal(network[0].lineWidth, 2.6);
  assert.equal(network[1].color, "#8b929b");
  assert.equal(network[2].color, "#d9739f");
});

function legendHost() {
  return {
    attributes: {},
    ownerDocument: {
      createElement: () => ({
        setAttribute() {},
        append(child) {
          this.child = child;
        },
      }),
    },
    setAttribute(name, value) {
      this.attributes[name] = value;
    },
    replaceChildren(child) {
      this.child = child;
    },
  };
}

test("native legends expose all definitions and destroy every chart on unmount", () => {
  const destroyed = [];
  const hosts = Object.fromEntries(
    ["density", "poles", "network"].map((group) => [group, legendHost()]),
  );
  const H = {
    chart(host) {
      return {
        destroy() {
          destroyed.push(host);
        },
      };
    },
  };
  const legends = mountMapLegends(H, hosts);
  assert.equal(hosts.density.attributes.role, "group");
  assert.match(hosts.density.attributes["aria-label"], /Donnée non disponible/);
  assert.match(
    hosts.poles.attributes["aria-label"],
    /Nouveau pôle depuis 2015/,
  );
  legends.destroy();
  assert.deepEqual(
    destroyed,
    Object.values(hosts).map((host) => host.child.child),
  );
});

test("native legend mounting releases earlier charts when a later chart fails", () => {
  let destroyed = 0;
  const host = legendHost();
  const H = {
    chart() {
      if (destroyed === 0 && this.mounted) throw new Error("fixture error");
      this.mounted = true;
      return {
        destroy() {
          destroyed++;
        },
      };
    },
  };
  assert.throws(
    () => mountMapLegends(H, { density: host, poles: host }),
    /fixture error/,
  );
  assert.equal(destroyed, 1);
});

test("density colors preserve half-open boundaries and the missing-data swatch", () => {
  for (const [value, expected] of [
    [0, "#F1EFEA"],
    [99.9, "#F1EFEA"],
    [100, "#DCE3EC"],
    [499.9, "#DCE3EC"],
    [500, "#B3C3D9"],
    [1999.9, "#B3C3D9"],
    [2000, "#7F9BC2"],
    [100000, "#7F9BC2"],
    [null, "#ffffff"],
    [undefined, "#ffffff"],
    [NaN, "#ffffff"],
  ])
    assert.equal(densityColor(value), expected, `density ${value}`);
});

test("legend keys toggle their own layer and synchronize native visibility", () => {
  const changes = [];
  const options = mapLegendOptions("network", (key, visible) =>
    changes.push([key, visible]),
  );
  assert.equal(options.series.at(-1).name, "Départements");
  const item = {
    options: options.series[0],
    visible: true,
    setVisible(visible) {
      this.visible = visible;
    },
  };
  options.legend.events.itemClick({ preventDefault() {}, legendItem: item });
  assert.deepEqual(changes, [["rail-recent", false]]);
  assert.equal(item.visible, false);
});

test("visibility keys preserve exact density bounds and exclusive pole appearances", () => {
  for (const [value, key] of [
    [0, "density-0"],
    [99.9, "density-0"],
    [100, "density-1"],
    [499.9, "density-1"],
    [500, "density-2"],
    [1999.9, "density-2"],
    [2000, "density-3"],
    [null, "density-missing"],
    [undefined, "density-missing"],
    [NaN, "density-missing"],
  ])
    assert.equal(densityKey(value), key);
  assert.equal(poleKey({ isNew: true, change: 0.2 }), "poles-new");
  assert.equal(poleKey({ isNew: false, change: -0.2 }), "poles-declining");
  assert.equal(poleKey({ isNew: false, change: 0 }), "poles-growing");
  const series = mapSeries(data);
  assert.equal(
    series
      .find((s) => s.id === "poles")
      .data.filter((p) => p.custom.legendKey === "poles-new").length,
    14,
  );
  assert.equal(
    series
      .find((s) => s.id === "poles")
      .data.filter((p) => p.custom.legendKey === "poles-growing").length,
    56,
  );
});

test("map visibility keeps density bounds, recent casing, pole groups and selection independent", () => {
  const previous = globalThis.document;
  globalThis.document = {
    createElement: () => ({ setAttribute() {}, append() {}, remove() {} }),
  };
  const series = new Map(
    mapSeries({
      ...data,
      communes: [...data.communes, { ...data.communes[0], densite_2025: null }],
    }).map((options) => [
      options.id,
      {
        ...options,
        visible: true,
        setVisible(visible) {
          this.visible = visible;
        },
        points: options.data.map((options) => ({
          options,
          custom: options.custom,
          id: options.id,
          update(update) {
            Object.assign(this.options, update);
          },
        })),
      },
    ]),
  );
  const chart = {
    options: { credits: {} },
    get: (id) => series.get(id),
    redraw() {},
    destroy() {},
  };
  const frame = {
    insertBefore() {},
    append() {},
    classList: { add() {}, remove() {} },
  };
  try {
    const engine = mountHighmaps({ mapChart: () => chart }, frame, {}, data);
    engine.visibility("density-0", false);
    assert.equal(
      series
        .get("density")
        .points.filter((p) => p.options.color === "rgba(0,0,0,0)").length,
      848,
    );
    assert.equal(
      series
        .get("density")
        .points.find((p) => p.custom.legendKey === "density-1").options.color,
      "#DCE3EC",
    );
    engine.visibility("density-0", true);
    assert.equal(
      series
        .get("density")
        .points.find((p) => p.custom.legendKey === "density-0").options.color,
      "#F1EFEA",
    );
    engine.visibility("density-missing", false);
    const missing = series
      .get("density")
      .points.find((p) => p.custom.legendKey === "density-missing");
    assert.equal(missing.options.color, "rgba(0,0,0,0)");
    assert.equal(missing.options.borderWidth, 0);
    engine.visibility("density-missing", true);
    assert.equal(missing.options.color, "#ffffff");
    engine.visibility("rail-recent", false);
    assert.equal(series.get("rail-casing").visible, false);
    assert.equal(series.get("rail-earlier").visible, true);
    engine.visibility("poles-growing", false);
    assert.equal(
      series
        .get("poles")
        .points.filter((p) => p.options.marker.enabled === false).length,
      56,
    );
    assert.equal(
      series.get("poles").points.find((p) => p.custom.legendKey === "poles-new")
        .options.marker.enabled,
      undefined,
    );
    for (const key of ["poles-growing", "poles-declining", "poles-new"]) {
      const points = series
        .get("poles")
        .points.filter((point) => point.custom.legendKey === key);
      const appearances = points.map((point) => ({ ...point.options.marker }));
      engine.visibility(key, false);
      engine.visibility(key, true);
      for (const [index, point] of points.entries())
        assert.deepEqual(point.options.marker, {
          ...appearances[index],
          enabled: true,
        });
    }
    engine.visibility("departments", false);
    engine.select("75");
    assert.equal(series.get("departments").visible, false);
    assert.equal(
      series.get("selection").points.find((p) => p.id === "selection-75")
        .options.borderWidth,
      2.5,
    );
    engine.select("");
    assert.ok(
      series.get("selection").points.every((p) => p.options.borderWidth === 0),
    );
    engine.destroy();
  } finally {
    globalThis.document = previous;
  }
});
