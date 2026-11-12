import { test } from 'node:test';
import assert from 'node:assert/strict';
import { shell } from '../../app/(graphique-2)/charts/graphique-2/lib/shell.ts';

test('the explorer retains map selections and portraits without search, tables or method sections', () => {
  assert.doesNotMatch(shell, /Chercher une commune|Données sous forme de tableaux|Méthode et limites/);
  assert.doesNotMatch(shell, /type="search"|<table\b|commune-results|commune-search|tables-title|method-title/);
  assert.match(shell, /id="commune-detail" role="status">Sélectionnez une commune sur la carte pour consulter ses données\.<\/p>/);
  for (const id of ['map', 'map-legend', 'zone-options', 'legend-flower', 'flower-preview', 'details']) {
    assert.ok(shell.includes(`id="${id}"`), `${id} remains available`);
  }
});
