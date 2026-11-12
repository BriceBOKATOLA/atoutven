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
  assert.match(
    shell,
    /id="commune-detail" role="status">Sélectionnez une commune sur la carte pour consulter ses données\.<\/p>/,
  );
  for (const id of [
    "map",
    "map-legend",
    "zone-options",
    "legend-flower",
    "flower-preview",
    "details",
  ]) {
    assert.ok(shell.includes(`id="${id}"`), `${id} remains available`);
  }
});

test("evolution legend labels match the half-open color thresholds", () => {
  const legend = shell.match(
    /<ol class="legend-ramp"[^>]*>([\s\S]*?)<\/ol>/,
  )?.[1];
  assert.ok(legend);

  const labels = [
    ...legend.matchAll(/<li><i [^>]*><\/i><span>(.*?)<\/span><\/li>/g),
  ].map(([, label]) => label);

  assert.deepEqual(labels, [
    "Moins de −5 %",
    "−5 % à moins de 0 %",
    "0 % à moins de 5 %",
    "5 % à moins de 15 %",
    "15 % ou plus",
  ]);
});
