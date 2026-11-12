import { test } from 'node:test';
import assert from 'node:assert/strict';
import { deliveredData, mountedExplorer } from './explorer-harness.mjs';
import { expectedPetal, fills, indicatorValues, strokes } from './expected-encoding.mjs';

// Exercise the mount's drawing and interaction contract with a substitute SVG renderer.
// Real Highmaps positioning and SVG rendering still require a browser check.
test('map flowers preserve indicator encoding, fixed pixel sizes and selection', async t => {
  const dataset = await deliveredData();
  const app = await mountedExplorer(t, dataset);
  const selectedZone = dataset.zones.features[0].properties;
  app.select(selectedZone.code);
  const markers = app.markers();
  assert.equal(markers.length, dataset.zones.features.length);
  const selectedMarker = markers.at(-1);
  assert.deepEqual(selectedMarker.attributes, { translateX: 400 + (selectedZone.center[0] - 2) * 100, translateY: 400 + (selectedZone.center[1] - 49) * 100 });
  const maxima = Array.from({ length: 5 }, (_, index) => Math.max(...dataset.zones.features.map(({ properties }) => Math.abs(indicatorValues(properties)[index] ?? 0))));
  for (const marker of markers) {
    const children = app.children(marker);
    const zone = dataset.zones.features.find(feature => feature.properties.nom === children.find(item => item.kind === 'text').geometry[0]).properties;
    assert.equal(children[0].geometry[2], 34.5, 'The target covers all petals and their gaps');
    const paths = children.filter(item => item.kind === 'path');
    assert.equal(paths.length, 5);
    indicatorValues(zone).forEach((value, index) => {
      const length = value === null ? 12 : maxima[index] === 0 ? 0 : 42 * Math.abs(value) / maxima[index];
      assert.deepEqual(paths[index].geometry, expectedPetal(length * .75));
      assert.equal(paths[index].attributes.rotation, -15 + index * 72);
      assert.equal(paths[index].attributes.fill, value === null ? 'none' : value < 0 ? '#fff' : fills[index]);
      assert.equal(paths[index].attributes.stroke, value === null ? '#7f8894' : strokes[index]);
      assert.equal(paths[index].attributes['stroke-dasharray'], value === null ? '3 2' : undefined);
    });
  }
  const marker = markers[0];
  const label = app.children(marker).find(item => item.kind === 'text');
  assert.equal(label.attributes.opacity, 0);
  marker.element.onmouseenter();
  assert.equal(label.attributes.opacity, 1);
  marker.element.onmouseleave();
  assert.equal(label.attributes.opacity, 0);
  const previousLayer = app.map.flowerLayer;
  const previousPaths = app.children(marker).filter(item => item.kind === 'path').map(item => item.geometry);
  app.setZoom(2);
  app.redraw();
  assert.equal(previousLayer.destroyed, true, 'Redraw removes old flowers and their handlers');
  const newMarker = app.markers()[0];
  assert.notEqual(marker.attributes.translateX, newMarker.attributes.translateX);
  assert.deepEqual(app.children(newMarker).filter(item => item.kind === 'path').map(item => item.geometry), previousPaths, 'Zoom moves the center without scaling petals');
  // Use the newly rendered marker to exercise the live handler.
  newMarker.element.onclick();
  assert.equal(app.control('zone-name').textContent, label.geometry[0]);
  assert.equal(app.control('explorer').scrolls, 1);
  const selected = app.markers().at(-1);
  const selectedLabel = app.children(selected).find(item => item.kind === 'text');
  selected.element.onmouseleave();
  assert.equal(selectedLabel.attributes.opacity, 1);
  assert.equal(selectedLabel.geometry[0], label.geometry[0]);
});
