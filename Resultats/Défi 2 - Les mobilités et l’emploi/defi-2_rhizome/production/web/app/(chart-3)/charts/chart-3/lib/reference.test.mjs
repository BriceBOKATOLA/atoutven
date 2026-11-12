import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { initializeReference } from "./reference-engine.mjs";
import { palette } from "./flowers.mjs";
import { referenceMarkup } from "./reference-markup.mjs";
// Minimal DOM fixture; real engine/data, no browser layout.
class Node {
  constructor() {
    this.attributes = {};
    this.children = [];
    this.listeners = {};
    this.dataset = {};
    this.offsetWidth = 240;
    this.offsetHeight = 56;
    this.clientWidth = 1000;
    this.clientHeight = 720;
    this.style = { setProperty() {} };
    this.classList = {
      toggle: (name, active) => {
        const names = new Set(
          (this.attributes.class || "").split(" ").filter(Boolean),
        );
        if (active) names.add(name);
        else names.delete(name);
        this.attributes.class = [...names].join(" ");
      },
      add: (name) => this.classList.toggle(name, true),
      remove: (name) => this.classList.toggle(name, false),
      contains: (name) =>
        (this.attributes.class || "").split(" ").includes(name),
    };
  }
  setAttribute(name, value) {
    this.attributes[name] = String(value);
    if (name.startsWith("data-"))
      this.dataset[
        name.slice(5).replace(/-([a-z])/g, (_, char) => char.toUpperCase())
      ] = String(value);
  }
  removeAttribute(name) {
    delete this.attributes[name];
  }
  append(...nodes) {
    for (const node of nodes) {
      node.parent = this;
      this.children.push(node);
    }
  }
  replaceChildren(...nodes) {
    this.children = [];
    this.append(...nodes);
  }
  addEventListener(name, handler, options = {}) {
    this.listeners[name] = handler;
    options.signal?.addEventListener(
      "abort",
      () => {
        if (this.listeners[name] === handler) delete this.listeners[name];
      },
      { once: true },
    );
  }
  closest(selector) {
    const matches = selector.startsWith(".")
      ? this.classList.contains(selector.slice(1))
      : selector === "[data-department]"
        ? !!this.dataset.department
        : selector === "[data-line]"
          ? !!this.dataset.line
          : false;
    return matches ? this : this.parent?.closest(selector);
  }
  matches(selector) {
    return selector === ":focus-visible";
  }
  focus() {
    this.focused = true;
  }
  setPointerCapture() {}
  getBoundingClientRect() {
    return { left: 100, top: 50, bottom: 200, width: 1000, height: 720 };
  }
  querySelector(selector) {
    if (selector === "button") return this.button;
    for (const child of this.children) {
      if (
        selector.startsWith(".") &&
        child.classList.contains(selector.slice(1))
      )
        return child;
      const nested = child.querySelector?.(selector);
      if (nested) return nested;
    }
    return null;
  }
}

const sourceData = JSON.parse(
  readFileSync(
    new URL(
      "../../../../../public/data/employment-centers-departments.json",
      import.meta.url,
    ),
  ),
);
test("rounds regional and pole pairs while preserving raw changes", () => {
  const { nodes, cleanup } = mount();
  const decimals = (digits) =>
    new Intl.NumberFormat("fr-FR", {
      minimumFractionDigits: digits,
      maximumFractionDigits: digits,
    });
  try {
    const comparison = nodes.get("comparison-figures").children;
    assert.equal(comparison.length, sourceData.comparison.rows.length);
    sourceData.comparison.rows.forEach((row, index) => {
      assert.equal(comparison[index].children[0].textContent, row.label);
      assert.equal(
        comparison[index].children[1].textContent,
        `+${decimals(1).format((row.end / row.start - 1) * 100)} %`,
      );
      assert.equal(
        comparison[index].children[2].textContent,
        `${decimals(2).format(row.start / 1e6)}\u00a0M à ${decimals(2).format(row.end / 1e6)}\u00a0M`,
      );
      assert.equal(
        comparison[index].children[3].textContent,
        `${row.source}, ${row.years}`,
      );
    });
    assert.equal(
      comparison[0].children[2].textContent,
      "4,54\u00a0M à 5,19\u00a0M",
    );
    // Rounding the displayed pair first would give 12.7%, instead of 13.0%.
    assert.equal(comparison[2].children[1].textContent, "+13,0 %");
    const poles = nodes.get("top-poles").children;
    assert.equal(poles.length, 6);
    sourceData.comparison.topPoles.forEach((pole, index) => {
      assert.equal(poles[index].children[0].textContent, pole.nom);
      assert.equal(
        poles[index].children[1].textContent,
        `${decimals(1).format(pole.start / 1e3)}\u00a0k à ${decimals(1).format(pole.end / 1e3)}\u00a0k`,
      );
    });
    assert.equal(
      poles[0].children[1].textContent,
      "115,0\u00a0k à 131,0\u00a0k",
    );
    assert.equal(nodes.get("employment-count").textContent, "5,2\u00a0M");
    assert.equal(nodes.get("pole-count").textContent, "87");
  } finally {
    cleanup();
  }
});
test("keeps periods without detailed-value disclosures or abbreviation notes", () => {
  assert.doesNotMatch(
    referenceMarkup,
    /<details\b|Valeurs détaillées|figure-details|comparison-details|top-poles-details/,
  );
  assert.doesNotMatch(
    referenceMarkup,
    /Valeurs arrondies|Effectifs arrondis|k = millier|M = million/,
  );
  assert.match(
    referenceMarkup,
    /Emplois salariés privés, de fin 2015 à fin 2025\./,
  );
});
test("omits the sign for exact zero while keeping nonzero signs", () => {
  const fixture = structuredClone(sourceData);
  fixture.comparison.rows[0].end = fixture.comparison.rows[0].start;
  fixture.comparison.rows[1].end = fixture.comparison.rows[1].start * 0.9;
  const { nodes, cleanup } = mount("", undefined, fixture);
  try {
    const rows = nodes.get("comparison-figures").children;
    assert.equal(rows[0].children[1].textContent, "0,0 %");
    assert.equal(rows[1].children[1].textContent, "−10,0 %");
    assert.equal(rows[2].children[1].textContent, "+13,0 %");
  } finally {
    cleanup();
  }
});
test("abbreviates all 32 departmental values and preserves exact accessible values", () => {
  const { nodes, cleanup } = mount();
  try {
    const buttons = nodes
      .get("departments")
      .children.flatMap((section) => section.children[1].children);
    assert.equal(buttons.length * sourceData.metrics.length, 32);
    for (const button of buttons) {
      const department = sourceData.departments.find(
        (item) => item.code === button.dataset.department,
      );
      sourceData.metrics.forEach((metric, index) => {
        const value = department.indicators[metric.id];
        assert.equal(
          button.children[index + 2].children[2].textContent,
          value === null
            ? "non disponible"
            : new Intl.NumberFormat("fr-FR", {
                notation: "compact",
                maximumFractionDigits: 2,
              }).format(Math.round(value * (metric.scale ?? 1))),
        );
        if (value !== null) {
          const amount = button.children[index + 2].children[2];
          const fullValue = new Intl.NumberFormat("fr-FR").format(
            Math.round(value * (metric.scale ?? 1)),
          );
          assert.equal(amount.attributes.title, fullValue);
          assert.equal(amount.attributes["aria-label"], fullValue);
        }
      });
    }
  } finally {
    cleanup();
  }
});
test("labels density classes without overlapping bounds", () => {
  assert.match(referenceMarkup, /<\/i>&lt; 100<\/li>/);
  assert.match(referenceMarkup, /<\/i>100 à moins de 500<\/li>/);
  assert.match(referenceMarkup, /<\/i>500 à moins de 2 000<\/li>/);
  assert.match(referenceMarkup, /<\/i>≥ 2 000<\/li>/);
});
test("keeps map content without obsolete data exports", () => {
  assert.doesNotMatch(referenceMarkup, /Méthode et limites|class="method"/);
  assert.doesNotMatch(
    referenceMarkup,
    /Explorer les données|class="data"|<table|download-csv|id="poles-details"|table-count|poles-rows|lines-rows/,
  );
  const { nodes, cleanup } = mount();
  try {
    assert.equal(nodes.get("load-status").hidden, true);
    for (const id of [
      "table-count",
      "poles-rows",
      "lines-rows",
      "download-csv",
    ])
      assert.equal(nodes.has(id), false);
    assert.equal(
      nodes.get("map").children.find((node) => node.classList.contains("poles"))
        .children.length,
      87,
    );
    assert.equal(nodes.get("size-legend").children.length, 1);
  } finally {
    cleanup();
  }
});
test("keeps the interactive map without export controls", () => {
  assert.match(referenceMarkup, /<svg id="map"/);
  assert.doesNotMatch(
    referenceMarkup,
    /download-csv|export-svg|export-status|Exporter la carte en SVG/,
  );
  const { nodes, cleanup } = mount();
  try {
    assert.equal(nodes.has("export-svg"), false);
    assert.equal(nodes.has("export-status"), false);
    assert.ok(
      nodes
        .get("map")
        .children.some((node) => node.classList.contains("poles")),
    );
    assert.equal(nodes.has("download-csv"), false);
  } finally {
    cleanup();
  }
});
function mount(prefix = "", options, fixture = sourceData) {
  const nodes = new Map();
  const root = {
    dataset: { chartPrefix: prefix },
    querySelector: (selector) => {
      const id = selector.slice(1);
      if (!nodes.has(id)) nodes.set(id, new Node());
      return nodes.get(id);
    },
    querySelectorAll: () => [],
  };
  globalThis.document = {
    createElementNS: () => new Node(),
    createElement: () => new Node(),
    body: new Node(),
    addEventListener() {},
  };
  globalThis.window = {
    innerWidth: 1440,
    innerHeight: 900,
    addEventListener() {},
  };
  globalThis.location = { href: "http://localhost/?departement=92", hash: "" };
  let savedUrl;
  const navigationState = { __NA: true, tree: ["story"] };
  let savedState;
  globalThis.history = {
    state: navigationState,
    replaceState: (state, __, url) => {
      savedState = state;
      savedUrl = String(url);
    },
  };
  const cleanup = initializeReference(root, fixture, options);
  return {
    root,
    nodes,
    cleanup,
    url: () => savedUrl,
    savedState: () => savedState,
    navigationState,
  };
}
test("explains flower positions, current colours, periods and area without colour alone", () => {
  assert.match(referenceMarkup, /id="flower-legend-title"/);
  assert.match(referenceMarkup, /id="flower-legend-items"/);
  const { nodes, cleanup } = mount();
  try {
    const items = nodes.get("flower-legend-items").children;
    assert.equal(items.length, 4);
    items.forEach((item, index) => {
      const metric = sourceData.metrics[index];
      assert.equal(item.children[0].attributes.fill, palette[metric.id]);
      assert.equal(
        item.children[1].children[0].textContent,
        `${index + 1}. ${metric.name}`,
      );
      assert.equal(item.children[1].children[1].textContent, metric.period);
    });
    const diagram = nodes.get("flower-legend-diagram").children[0];
    assert.deepEqual(
      diagram.children
        .filter((node) => node.attributes.transform)
        .map((node) => node.attributes.transform),
      ["rotate(-45)", "rotate(45)", "rotate(135)", "rotate(225)"],
    );
    assert.deepEqual(
      diagram.children
        .filter((node) => node.textContent)
        .map((node) => node.textContent),
      ["1", "2", "3", "4"],
    );
    assert.match(referenceMarkup, /surface.*proportionnelle/s);
    assert.match(referenceMarkup, /indicateurs différents ne se comparent pas/);
    assert.match(referenceMarkup, /zéro.*ne dessine pas de pétale/s);
    assert.match(referenceMarkup, /pointillés.*donnée absente/s);
  } finally {
    cleanup();
  }
});
test("keeps zero and missing values distinct in department flowers", () => {
  const fixture = structuredClone(sourceData);
  fixture.departments.find((item) => item.code === "75").indicators.salarie = 0;
  fixture.departments.find((item) => item.code === "92").indicators.salarie =
    null;
  const { nodes, cleanup } = mount("", undefined, fixture);
  try {
    const buttons = nodes
      .get("departments")
      .children.flatMap((section) => section.children[1].children);
    const zero = buttons.find((button) => button.dataset.department === "75");
    const missing = buttons.find(
      (button) => button.dataset.department === "92",
    );
    assert.match(zero.children[0].children[0].attributes.d, /A0 0/);
    assert.equal(zero.children[2].children[2].textContent, "0");
    assert.equal(
      missing.children[0].children[0].attributes.class,
      "petal-missing",
    );
    assert.doesNotMatch(missing.children[0].children[0].attributes.d, /A0 0/);
    assert.equal(missing.children[2].children[2].textContent, "non disponible");
  } finally {
    cleanup();
  }
});
test("preserves selection, URL and zoom", () => {
  const { nodes, cleanup, url } = mount();
  assert.equal(nodes.get("load-status").hidden, true);
  const buttons = nodes
    .get("departments")
    .children.flatMap((section) => section.children[1].children);
  assert.equal(buttons.length, 8);
  assert.match(nodes.get("selection-text").textContent, /92/);
  buttons
    .find((button) => button.dataset.department === "77")
    .listeners.click();
  assert.match(nodes.get("selection-text").textContent, /77/);
  assert.equal(new URL(url()).searchParams.get("departement"), "77");
  const map = nodes.get("map"),
    initial = map.attributes.viewBox;
  map.listeners.keydown({ key: "+", target: map });
  assert.notEqual(map.attributes.viewBox, initial);
  map.listeners.keydown({ key: "0", target: map });
  assert.equal(map.attributes.viewBox, initial);
  cleanup();
});
test("combines map and tooltip flowers and cleans up remounts", () => {
  const { root, nodes, cleanup } = mount();
  const map = nodes.get("map"),
    layer = map.children.find((node) =>
      node.classList.contains("prototype-flowers"),
    );
  assert.equal(layer.children.length, 8);
  const flower = layer.children.find(
    (node) => node.dataset.department === "77",
  );
  assert.equal(flower.querySelector(".disc").attributes.r, "23");
  assert.equal(flower.attributes.tabindex, "0");
  map.listeners.click({ target: flower, clientX: 200, clientY: 200 });
  const tooltip = nodes.get("map-tooltip");
  assert.equal(tooltip.hidden, false);
  const detail = tooltip.children.find(
    (node) => node.className === "prototype-tooltip-flower",
  );
  assert.ok(detail);
  assert.ok(
    detail.children[0].children.some(
      (node) => node.attributes.fill === palette.salarie,
    ),
  );
  assert.ok(
    detail.children[0].children.some(
      (node) => node.attributes.fill === palette.interim,
    ),
  );
  assert.equal(
    layer.children.filter((node) => node.attributes["aria-pressed"] === "true")
      .length,
    1,
  );
  map.listeners.click({ target: flower, clientX: 200, clientY: 200 });
  assert.equal(
    flower.attributes["aria-pressed"],
    "false",
    "a second click clears the department",
  );
  assert.equal(
    sourceData.metrics[0].color === palette.salarie,
    false,
    "source data is not mutated",
  );
  cleanup();
  assert.equal(map.listeners.click, undefined, "unmount aborts listeners");
  const cleanupAgain = initializeReference(root, sourceData);
  assert.equal(
    map.children.filter((node) => node.classList.contains("prototype-flowers"))
      .length,
    1,
  );
  assert.equal(nodes.get("departments").children.length, 2);
  cleanupAgain();
});

test("keyboard pole focus replaces the previous tooltip department and its flower values", () => {
  const { nodes, cleanup } = mount();
  try {
    const map = nodes.get("map");
    const poles = map.children.find((node) => node.classList.contains("poles"));
    const flowers = map.children.find((node) =>
      node.classList.contains("prototype-flowers"),
    );
    const tooltip = nodes.get("map-tooltip");
    const pole92 = poles.children.find(
      (node) => node.dataset.department === "92",
    );
    const pole93 = poles.children.find(
      (node) => node.dataset.department === "93",
    );
    function assertDepartment(code) {
      const department = sourceData.departments.find(
        (item) => item.code === code,
      );
      const detail = tooltip.children.find(
        (node) => node.className === "prototype-tooltip-flower",
      );
      assert.equal(tooltip.hidden, false);
      assert.ok(detail, "keyboard focus provides a departmental flower");
      const values = detail.children[1].children;
      assert.equal(values[0].textContent, `${department.nom} (${code})`);
      for (const metric of sourceData.metrics.filter(
        (metric) => department.indicators[metric.id] !== null,
      )) {
        const expected = new Intl.NumberFormat("fr-FR").format(
          Math.round(department.indicators[metric.id] * (metric.scale ?? 1)),
        );
        assert.ok(
          values.some(
            (row) =>
              row.textContent ===
              `${metric.name} (${metric.period}) : ${expected}`,
          ),
        );
      }
    }
    // Focus must also work before any pointer action has set a department.
    poles.listeners.focusin({ target: pole92 });
    assertDepartment("92");
    // Seed a different department through the real pointer path.
    map.listeners.pointermove({
      target: flowers.children.find((node) => node.dataset.department === "77"),
      clientX: 200,
      clientY: 200,
      pointerType: "mouse",
    });
    assertDepartment("77");
    poles.listeners.focusin({ target: pole92 });
    assertDepartment("92");
    poles.listeners.focusin({ target: pole93 });
    assertDepartment("93");
  } finally {
    cleanup();
  }
});

test("direct mounting uses chart IDs and preserves the existing navigation state", () => {
  const { nodes, cleanup, savedState, navigationState } = mount("g3-");
  assert.equal(nodes.get("g3-load-status").hidden, true);
  assert.equal(nodes.has("map"), false);
  assert.equal(savedState(), navigationState);
  const map = nodes.get("g3-map"),
    initial = map.attributes.viewBox;
  map.listeners.keydown({ key: "+", target: map });
  assert.notEqual(map.attributes.viewBox, initial);
  cleanup();
});

test("does not mount Highmaps or update the interface after disposal during loading", async () => {
  let resolve;
  const pending = new Promise((done) => {
    resolve = done;
  });
  let mounts = 0;
  const { nodes, cleanup } = mount("", { loadHighmaps: () => pending });
  assert.equal(nodes.get("map").children.length, 0);
  cleanup();
  resolve({
    mapChart() {
      mounts++;
    },
  });
  await pending;
  await Promise.resolve();
  assert.equal(mounts, 0);
  assert.equal(nodes.get("map").children.length, 0);
});

test("engine loading failure keeps a retry control and never reports a loaded map", async () => {
  const originalError = console.error;
  console.error = () => {};
  const { nodes, cleanup } = mount("", {
    loadHighmaps: async () => {
      throw Error("Offline");
    },
  });
  try {
    await Promise.resolve();
    await Promise.resolve();
    const status = nodes.get("load-status");
    assert.notEqual(status.hidden, true);
    assert.match(status.children[0].textContent, /n’a pas pu charger/);
    assert.equal(status.children[1].textContent, "Réessayer");
    assert.equal(typeof status.children[1].listeners.click, "function");
    assert.equal(nodes.get("map").children.length, 0);
  } finally {
    cleanup();
    console.error = originalError;
  }
});

test("a rejected engine request after disposal does not replace the interface", async () => {
  let reject;
  const pending = new Promise((resolve, fail) => {
    reject = fail;
  });
  const { nodes, cleanup } = mount("", { loadHighmaps: () => pending });
  const status = nodes.get("load-status");
  cleanup();
  reject(Error("Late network failure"));
  await pending.catch(() => {});
  await Promise.resolve();
  assert.equal(status.children.length, 0);
});

test("clearing a focused department control returns focus to the visible map", () => {
  const { nodes, cleanup, url } = mount();
  try {
    document.activeElement = nodes.get("clear-selection");
    nodes.get("clear-selection").listeners.click();
    assert.equal(nodes.get("selection").hidden, true);
    assert.equal(new URL(url()).searchParams.has("departement"), false);
    assert.equal(nodes.get("map").focused, true);
  } finally {
    cleanup();
  }
});

test("commune tooltip preserves missing employment and density", () => {
  const fixture = structuredClone(sourceData);
  const commune = fixture.communes.find(
    (item) => !fixture.poles.some((pole) => pole.code === item.code),
  );
  commune.emploi_2015 = null;
  commune.emploi_2025 = null;
  commune.densite_2025 = null;
  const { nodes, cleanup } = mount("", undefined, fixture);
  try {
    const texts = (node) =>
      node.children.map((item) => item.textContent).join(" ");
    const map = nodes.get("map");
    const shapes = map.children.find((node) =>
      node.classList.contains("communes"),
    );
    const shape = shapes.children.find(
      (node) => node.dataset.commune === commune.code,
    );
    map.listeners.pointermove({
      target: shape,
      clientX: 200,
      clientY: 200,
      pointerType: "mouse",
    });
    const tooltipText = texts(nodes.get("map-tooltip"));
    assert.match(tooltipText, /fin 2015 : non disponibles/);
    assert.match(tooltipText, /fin 2025 : non disponibles/);
    assert.match(tooltipText, /Densité d’emploi fin 2025 : non disponible/);
    assert.doesNotMatch(tooltipText, /NaN|0 emplois|0 %/);
    assert.equal(
      shapes.children.some((node) => "tabindex" in node.attributes),
      false,
    );
  } finally {
    cleanup();
  }
});
