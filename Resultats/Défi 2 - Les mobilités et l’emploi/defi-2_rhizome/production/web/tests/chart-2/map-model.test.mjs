import { test } from "node:test";
import assert from "node:assert/strict";
import {
  communeLabels,
  lineTags,
  tramT4Bounds,
  zoneAt,
  zoneBoundaries,
} from "../../app/(chart-2)/charts/chart-2/lib/map-model.mjs";
import { deliveredData } from "./explorer-harness.mjs";

function freeze(value) {
  if (!value || typeof value !== "object") return value;
  Object.values(value).forEach(freeze);
  return Object.freeze(value);
}

test("geographic calculations accept frozen delivered collections without changing them", async () => {
  const data = await deliveredData();
  const original = structuredClone(data);
  freeze(data);
  const labels = freeze(communeLabels(data.communes));
  const tags = lineTags(data.lines, labels);
  const boundaries = zoneBoundaries(data.zones);
  const bounds = tramT4Bounds(data.communes);
  assert.ok(labels.length > 0 && tags.length > 0);
  assert.ok(Object.values(bounds).every(Number.isFinite));
  assert.equal(boundaries.features.length, data.zones.features.length);
  for (const [index, feature] of boundaries.features.entries()) {
    assert.equal(feature.geometry.type, "MultiLineString");
    assert.equal(feature.properties, data.zones.features[index].properties);
  }
  for (const { properties: zone } of data.zones.features) {
    const [lon, lat] = zone.center;
    assert.equal(zoneAt(data.zones, { lon, lat }), zone);
  }
  assert.deepEqual(data, original);
});

test("zone queries and boundaries use their supplied polygon collection, including holes and islands", () => {
  const ring = (west, south, east, north) => [
    [west, south],
    [east, south],
    [east, north],
    [west, north],
    [west, south],
  ];
  const outer = ring(0, 0, 10, 10);
  const hole = ring(2, 2, 4, 4);
  const island = ring(20, 20, 22, 22);
  const properties = {
    code: "test",
    nom: "Test",
    center: [1, 1],
    indicators: {},
  };
  const collection = freeze({
    type: "FeatureCollection",
    features: [
      {
        type: "Feature",
        properties,
        geometry: {
          type: "MultiPolygon",
          coordinates: [[outer, hole], [island]],
        },
      },
    ],
  });
  assert.equal(zoneAt(collection, { lon: 1, lat: 1 }), properties);
  assert.equal(zoneAt(collection, { lon: 3, lat: 3 }), undefined);
  assert.equal(zoneAt(collection, { lon: 21, lat: 21 }), properties);
  assert.equal(
    zoneAt({ type: "FeatureCollection", features: [] }, { lon: 1, lat: 1 }),
    undefined,
  );
  assert.deepEqual(
    zoneBoundaries(collection).features[0].geometry.coordinates,
    [outer, hole, island],
  );

  const polygon = freeze({
    ...collection,
    features: [
      {
        ...collection.features[0],
        geometry: { type: "Polygon", coordinates: [outer, hole] },
      },
    ],
  });
  assert.equal(zoneAt(polygon, { lon: 1, lat: 1 }), properties);
  assert.equal(zoneAt(polygon, { lon: 3, lat: 3 }), undefined);
  assert.deepEqual(zoneBoundaries(polygon).features[0].geometry.coordinates, [
    outer,
    hole,
  ]);
});
