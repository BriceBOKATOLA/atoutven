import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { runInThisContext } from "node:vm";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import swc from "next/dist/build/swc/index.js";

const data = JSON.parse(
  await readFile(
    new URL("../public/data/rail-network.json", import.meta.url),
    "utf8",
  ),
);

test("the interactive map counts infrastructure openings and all 125 opening stations", () => {
  assert.deepEqual(data.summary, { lines: 15, stations: 125, kilometres: 118 });
  assert.equal(data.periods.flatMap((period) => period.stations).length, 125);
  assert.equal(
    new Set(
      data.periods.flatMap((period) =>
        period.openings.map((opening) => opening.line),
      ),
    ).size,
    15,
  );
});

test("the T14 commercial rename is excluded from recent infrastructure", () => {
  assert.equal(
    data.periods
      .flatMap((period) => period.openings)
      .some((opening) => opening.line === "T14"),
    false,
  );
  assert.equal(
    data.periods
      .flatMap((period) => period.tracks)
      .some((track) => track.name.startsWith("T14 ")),
    false,
  );
  assert.equal(
    data.labels.some((label) => label.name.startsWith("T14 |")),
    false,
  );
});

test("the 2024 M11 extension has stations and a label but no invented track", () => {
  const latest = data.periods[2];
  assert.equal(
    latest.stations.filter((station) => station.line === "M11").length,
    6,
  );
  assert.equal(
    latest.tracks.some((track) => track.name.startsWith("M11")),
    false,
  );
  assert.ok(data.labels.some((label) => label.name === "M11 | 2024*"));
});

test("period colors, years and the Lambert-93 viewport match the source map", () => {
  assert.deepEqual(data.bounds, [0, 73, -60, 0]);
  assert.deepEqual(
    data.periods.map((period) => period.color),
    ["#009E73", "#0072B2", "#D55E00"],
  );
  for (const period of data.periods) {
    for (const station of period.stations) {
      assert.ok(
        station.x >= 0 && station.x <= 73 && station.y >= -60 && station.y <= 0,
      );
    }
  }
});

async function renderMap() {
  const filename = new URL("../components/NetworkMap.tsx", import.meta.url);
  const source = await readFile(filename, "utf8");
  await swc.loadBindings();
  const { code } = await swc.transform(source, {
    filename: filename.pathname,
    jsc: {
      parser: { syntax: "typescript", tsx: true },
      target: "es2020",
      transform: { react: { runtime: "automatic" } },
    },
    module: { type: "commonjs" },
  });
  const exports = {};
  runInThisContext(`(function(require, exports) { ${code} })`)(
    createRequire(filename),
    exports,
  );
  return renderToStaticMarkup(createElement(exports.NetworkMap));
}

test("the map renders a loading state without linking to the missing source image", async () => {
  const markup = await renderMap();
  assert.doesNotMatch(markup, /01_reseau_transport_extens\.png/);
  assert.match(markup, /Chargement de la carte interactive/);
});

test("the no-JavaScript message describes the generated map requirements accurately", async () => {
  const markup = await renderMap();
  assert.match(
    markup,
    /JavaScript est nécessaire pour afficher la carte, ses chiffres clés et sa légende/,
  );
  assert.doesNotMatch(markup, /carte d’origine/);
});
