import assert from "node:assert/strict";
import { test } from "node:test";
import { bindMapNavigation } from "../lib/map-navigation.mjs";

function setup() {
  const host = new EventTarget();
  const attributes = new Map();
  host.setAttribute = (key, value) => attributes.set(key, value);
  host.getAttribute = (key) => attributes.get(key) ?? null;
  host.removeAttribute = (key) => attributes.delete(key);
  const zooms = [];
  const views = [];
  const chart = {
    plotWidth: 1000,
    plotHeight: 600,
    mapView: {
      zoom: 4,
      pixelsToLonLat: ({ x, y }) => ({ lon: x / 100, lat: y / 100 }),
      zoomBy: (...args) => zooms.push(args),
      setView: (...args) => views.push(args),
    },
  };
  const dispose = bindMapNavigation(host, chart);
  const key = (value, properties = {}) => {
    const event = new Event("keydown", { cancelable: true });
    Object.assign(event, { key: value, ...properties });
    host.dispatchEvent(event);
    return event;
  };
  return { host, chart, attributes, zooms, views, dispose, key };
}

test("focused map controls zoom by two and reset without intercepting modified shortcuts", () => {
  const app = setup();
  assert.equal(app.attributes.get("tabindex"), "0");
  assert.equal(app.key("+").defaultPrevented, true);
  app.key("=");
  app.key("-");
  app.key("0");
  app.key("+", { ctrlKey: true });
  app.key("-", { metaKey: true });
  app.key("=", { altKey: true });
  assert.deepEqual(app.zooms, [[1], [1], [-1], []]);
  app.dispose();
  app.key("+");
  assert.equal(app.zooms.length, 4);
  assert.equal(app.attributes.has("tabindex"), false);
});

test("arrows pan by a fifth of the visible map, using its projection", () => {
  const app = setup();
  for (const key of ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"])
    assert.equal(app.key(key).defaultPrevented, true);
  assert.deepEqual(app.views, [
    [[3, 3], 4, true, false],
    [[7, 3], 4, true, false],
    [[5, 1.8], 4, true, false],
    [[5, 4.2], 4, true, false],
  ]);
  app.dispose();
});

test("one finger preserves page scrolling while two fingers reach Highmaps", () => {
  const app = setup();
  for (const count of [1, 2]) {
    const event = new Event("touchmove", { cancelable: true });
    let stopped = false;
    Object.assign(event, {
      touches: Array(count).fill({}),
      stopPropagation() {
        stopped = true;
      },
    });
    app.host.dispatchEvent(event);
    assert.equal(stopped, count === 1);
    assert.equal(event.defaultPrevented, false);
  }
  app.dispose();
});

test("panning uses the current zoom and resized plot rather than the initial view", () => {
  const app = setup();
  app.chart.plotWidth = 500;
  app.chart.plotHeight = 300;
  app.chart.mapView.zoom = 6;
  app.chart.mapView.pixelsToLonLat = ({ x, y }) => ({
    lon: x / 200,
    lat: y / 200,
  });
  app.key("ArrowRight");
  assert.deepEqual(app.views, [[[1.75, 0.75], 6, true, false]]);
  app.dispose();
});
