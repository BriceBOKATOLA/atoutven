import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { mapSeries, mountHighmaps } from "./highmaps-adapter.mjs";
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
      created.every((node) => node.removed),
      "both map container and link must be removed",
    );
  } finally {
    globalThis.document = previousDocument;
  }
});
