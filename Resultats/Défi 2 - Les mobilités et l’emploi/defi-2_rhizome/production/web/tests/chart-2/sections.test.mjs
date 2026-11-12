import { test } from "node:test";
import assert from "node:assert/strict";
import { shell } from "../../app/(chart-2)/charts/chart-2/lib/shell.ts";

test("the explorer retains map selections and portraits without search, tables, method sections or export controls", () => {
  assert.doesNotMatch(
    shell,
    /Chercher une commune|Données sous forme de tableaux|Méthode et limites/,
  );
  assert.doesNotMatch(
    shell,
    /type="search"|<table\b|commune-results|commune-search|tables-title|method-title/,
  );
  assert.doesNotMatch(shell, /\bdownload(?:\s|=|>)|Exporter|Télécharger/i);
  assert.match(shell, /id="commune-detail" role="status"><\/p>/);
  for (const id of [
    "map",
    "zone-options",
    "legend-flower",
    "flower-preview",
    "details",
  ]) {
    assert.ok(shell.includes(`id="${id}"`), `${id} remains available`);
  }
});

test("native legend replaces custom keys", () => {
  assert.doesNotMatch(
    shell,
    /map-legend|legend-ramp|legend-keys|legend-swatch/,
  );
});
