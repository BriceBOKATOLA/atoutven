import { test } from "node:test";
import assert from "node:assert/strict";
import { deliveredData, mountedExplorer } from "./explorer-harness.mjs";
import {
  expectedPetal,
  fills,
  indicatorValues,
  strokes,
} from "./expected-encoding.mjs";

// Exercise the mount's drawing and interaction contract with a substitute SVG renderer.
// Real Highmaps positioning and SVG rendering still require a browser check.
test("map flowers preserve indicator encoding, fixed pixel sizes and selection", async (t) => {
  const dataset = await deliveredData();
  const app = await mountedExplorer(t, dataset);
  const selectedZone = dataset.zones.features[0].properties;
  app.select(selectedZone.code);
  const markers = app.markers();
  assert.equal(markers.length, dataset.zones.features.length);
  const selectedMarker = markers.find(
    (item) => item.element.getAttribute("aria-pressed") === "true",
  );
  assert.deepEqual(selectedMarker.attributes, {
    translateX: 400 + (selectedZone.center[0] - 2) * 100,
    translateY: 400 + (selectedZone.center[1] - 49) * 100,
  });
  const maxima = Array.from({ length: 5 }, (_, index) =>
    Math.max(
      ...dataset.zones.features.map(({ properties }) =>
        Math.abs(indicatorValues(properties)[index] ?? 0),
      ),
    ),
  );
  for (const marker of markers) {
    const children = app.children(marker);
    const zone = dataset.zones.features.find(
      (feature) =>
        feature.properties.nom ===
        children.find((item) => item.kind === "text").geometry[0],
    ).properties;
    assert.equal(
      children[0].geometry[2],
      34.5,
      "The target covers all petals and their gaps",
    );
    const paths = children.filter((item) => item.kind === "path");
    assert.equal(paths.length, 5);
    indicatorValues(zone).forEach((value, index) => {
      const length =
        value === null
          ? 12
          : maxima[index] === 0
            ? 0
            : (42 * Math.abs(value)) / maxima[index];
      assert.deepEqual(paths[index].geometry, expectedPetal(length * 0.75));
      assert.equal(paths[index].attributes.rotation, -15 + index * 72);
      assert.equal(
        paths[index].attributes.fill,
        value === null ? "none" : value < 0 ? "#fff" : fills[index],
      );
      assert.equal(
        paths[index].attributes.stroke,
        value === null ? "#7f8894" : strokes[index],
      );
      assert.equal(
        paths[index].attributes["stroke-dasharray"],
        value === null ? "3 2" : undefined,
      );
    });
  }
  const marker = markers.find((item) => item !== selectedMarker);
  const label = app.children(marker).find((item) => item.kind === "text");
  assert.equal(label.attributes.opacity, 0);
  marker.element.onmouseenter();
  assert.equal(label.attributes.opacity, 1);
  marker.element.onmouseleave();
  assert.equal(label.attributes.opacity, 0);
  const previousLayer = app.map.flowerLayer;
  const previousPaths = app
    .children(marker)
    .filter((item) => item.kind === "path")
    .map((item) => item.geometry);
  app.setZoom(2);
  app.redraw();
  assert.equal(
    previousLayer.destroyed,
    true,
    "Redraw removes old flowers and their handlers",
  );
  const newMarker = app.markers()[0];
  assert.notEqual(
    marker.attributes.translateX,
    newMarker.attributes.translateX,
  );
  assert.deepEqual(
    app
      .children(newMarker)
      .filter((item) => item.kind === "path")
      .map((item) => item.geometry),
    previousPaths,
    "Zoom moves the center without scaling petals",
  );
  // Use the newly rendered marker to exercise the live handler.
  newMarker.element.dispatch("click", {
    stopPropagation() {},
    preventDefault() {},
  });
  assert.equal(app.control("zone-name").textContent, label.geometry[0]);
  assert.equal(app.control("explorer").scrolls, 0);
  const selected = app
    .markers()
    .find((item) => item.element.getAttribute("aria-pressed") === "true");
  const selectedLabel = app
    .children(selected)
    .find((item) => item.kind === "text");
  selected.element.onmouseleave();
  assert.equal(selectedLabel.attributes.opacity, 1);
  assert.equal(selectedLabel.geometry[0], label.geometry[0]);
});

test("flowers show real indicators on hover and select without scrolling or losing keyboard focus", async (t) => {
  const app = await mountedExplorer(t, await deliveredData());
  const marker = app.markers()[0];
  const name = app.children(marker).find((item) => item.kind === "text")
    .geometry[0];
  const tooltip = app.control("map-tooltip");
  marker.element.dispatch("mouseenter");
  assert.equal(tooltip.hidden, false);
  assert.equal(tooltip.querySelectorAll("svg").length, 1);
  assert.equal(tooltip.querySelectorAll("dt").length, 5);
  assert.match(
    tooltip.textContent,
    /Salariés du secteur privé, évolution 2016–2024/,
  );
  assert.match(tooltip.textContent, /Taux de chômage localisé, 2024/);
  assert.match(
    tooltip.textContent,
    /Emplois dans la zone pour 100 actifs occupés résidents, 2016/,
  );
  assert.match(tooltip.textContent, /%/);
  marker.element.dispatch("mouseleave");
  await new Promise((resolve) => setTimeout(resolve, 150));
  assert.equal(tooltip.hidden, true);
  marker.element.dispatch("focus");
  assert.equal(tooltip.hidden, false);
  for (const key of ["Enter", " "]) {
    let stopped = false;
    let prevented = false;
    marker.element.dispatch("keydown", {
      key,
      stopPropagation() {
        stopped = true;
      },
      preventDefault() {
        prevented = true;
      },
    });
    assert.equal(stopped, true);
    assert.equal(prevented, true);
    assert.equal(app.control("zone-name").textContent, name);
    assert.equal(marker.element.getAttribute("aria-pressed"), "true");
    assert.ok(
      app.markers().includes(marker),
      "Selecting keeps the focused SVG node",
    );
    assert.equal(app.control("explorer").scrolls, 0);
    assert.equal(tooltip.hidden, false);
  }
  marker.element.dispatch("keydown", {
    key: "Escape",
    stopPropagation() {},
    preventDefault() {},
  });
  assert.equal(tooltip.hidden, true);
  marker.element.dispatch("focus");
  app.redraw();
  assert.equal(
    tooltip.hidden,
    true,
    "Zoom and redraw dismiss stale tooltip positions",
  );
  app.markers()[0].element.dispatch("mouseenter");
  app.dispose();
  assert.equal(tooltip.hidden, true);
});

test("flower tooltip keeps delivered Saclay values, periods and ratio units", async (t) => {
  const app = await mountedExplorer(t, await deliveredData());
  const marker = app
    .markers()
    .find((item) =>
      app
        .children(item)
        .some(
          (child) => child.kind === "text" && child.geometry[0] === "Saclay",
        ),
    );
  let stopped = false;
  marker.element.dispatch("click", {
    stopPropagation() {
      stopped = true;
    },
    preventDefault() {},
  });
  assert.equal(
    stopped,
    true,
    "A flower click cannot select the geographic zone below it",
  );
  const tooltip = app.control("map-tooltip");
  assert.deepEqual(
    tooltip.querySelectorAll("dd").map((node) => node.textContent),
    [
      "+9,1\u00a0%",
      "+8,8\u00a0%",
      "5,8\u00a0%",
      "17,9\u00a0pour 100 salariés",
      "91,4\u00a0pour 100 actifs occupés résidents",
    ],
  );
  assert.match(
    tooltip.textContent,
    /Demandeurs d’emploi pour 100 salariés du secteur privé, 2024/,
  );
  assert.equal(
    app.control("zone-options").querySelector('input[value="1113"]').checked,
    true,
  );
  marker.element.dispatch("mouseleave");
  tooltip.dispatch("mouseenter");
  await new Promise((resolve) => setTimeout(resolve, 150));
  assert.equal(
    tooltip.hidden,
    false,
    "The user can move onto the tooltip to read it",
  );
  tooltip.dispatch("mouseleave");
  assert.equal(tooltip.hidden, true);
});

test("flower tooltip announces unavailable observations instead of inventing zero values", async (t) => {
  const dataset = await deliveredData();
  const zone = dataset.zones.features[0].properties;
  zone.indicators = {};
  const app = await mountedExplorer(t, dataset);
  const marker = app
    .markers()
    .find((item) =>
      app
        .children(item)
        .some(
          (child) => child.kind === "text" && child.geometry[0] === zone.nom,
        ),
    );
  marker.element.dispatch("focus");
  assert.deepEqual(
    app
      .control("map-tooltip")
      .querySelectorAll("dd")
      .map((node) => node.textContent),
    Array(5).fill("Donnée indisponible"),
  );
  marker.element.dispatch("blur");
  assert.equal(app.control("map-tooltip").hidden, true);
});

test("tooltip permits pointer use inside its card and dismisses on outside input or viewport changes", async (t) => {
  const app = await mountedExplorer(t, await deliveredData());
  const marker = app.markers()[0];
  const tooltip = app.control("map-tooltip");
  marker.element.dispatch("mouseenter");
  app.document.dispatch("pointerdown", { target: tooltip.querySelector("dd") });
  assert.equal(
    tooltip.hidden,
    false,
    "Touch input inside a tall card must allow scrolling",
  );
  app.document.dispatch("pointerdown");
  assert.equal(tooltip.hidden, true);
  marker.element.dispatch("mouseenter");
  app.document.dispatch("keydown", { key: "Escape" });
  assert.equal(
    tooltip.hidden,
    true,
    "Escape also dismisses a pointer tooltip without marker focus",
  );
  for (const type of ["scroll", "resize"]) {
    marker.element.dispatch("mouseenter");
    app.viewport.dispatch(type);
    assert.equal(tooltip.hidden, true);
  }
});
