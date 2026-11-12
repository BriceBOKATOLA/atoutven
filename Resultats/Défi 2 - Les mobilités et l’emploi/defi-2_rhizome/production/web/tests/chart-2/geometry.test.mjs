import { test } from "node:test";
import assert from "node:assert/strict";
import {
  geometryBounds,
  ringContains,
} from "../../app/(chart-2)/charts/chart-2/lib/geometry.mjs";

test("ring containment preserves orientation and leaves coordinates unchanged", () => {
  const ring = [
    [1, 2],
    [5, 2],
    [5, 6],
    [1, 6],
    [1, 2],
  ];
  const original = structuredClone(ring);
  assert.equal(ringContains(ring, 3, 4), true);
  assert.equal(ringContains([...ring].reverse(), 3, 4), true);
  assert.equal(ringContains(ring, 0, 4), false);
  assert.equal(ringContains(ring, 3, 7), false);
  assert.deepEqual(ring, original);
});

test("bounds include all polygon rings and separate islands without changing geometry", () => {
  const geometry = {
    type: "MultiPolygon",
    coordinates: [
      [
        [
          [1, 2],
          [5, 2],
          [5, 6],
          [1, 6],
          [1, 2],
        ],
        [
          [2, 3],
          [4, 3],
          [4, 5],
          [2, 5],
          [2, 3],
        ],
      ],
      [
        [
          [7, -2],
          [9, -2],
          [9, 0],
          [7, 0],
          [7, -2],
        ],
      ],
    ],
  };
  const original = structuredClone(geometry);
  assert.deepEqual(geometryBounds(geometry), {
    west: 1,
    east: 9,
    south: -2,
    north: 6,
  });
  assert.deepEqual(geometry, original);
});
