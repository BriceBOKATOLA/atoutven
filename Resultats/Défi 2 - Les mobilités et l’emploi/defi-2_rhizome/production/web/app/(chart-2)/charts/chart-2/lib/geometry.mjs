/** Test a point against one polygon ring with ray casting.
 * @param {number[][]} ring
 * @param {number} lon
 * @param {number} lat
 */
export function ringContains(ring, lon, lat) {
  let inside = false;
  for (
    let index = 0, previous = ring.length - 1;
    index < ring.length;
    previous = index++
  ) {
    const [x, y] = ring[index];
    const [previousX, previousY] = ring[previous];
    if (
      y > lat !== previousY > lat &&
      lon < ((previousX - x) * (lat - y)) / (previousY - y) + x
    )
      inside = !inside;
  }
  return inside;
}

/** Find coordinate bounds across nested GeoJSON geometry.
 * @param {{ coordinates: unknown }} geometry
 */
export function geometryBounds(geometry) {
  const bounds = {
    west: Infinity,
    east: -Infinity,
    south: Infinity,
    north: -Infinity,
  };
  /** @param {unknown} coordinates */
  function visit(coordinates) {
    if (!Array.isArray(coordinates)) return;
    if (
      typeof coordinates[0] === "number" &&
      typeof coordinates[1] === "number"
    ) {
      bounds.west = Math.min(bounds.west, coordinates[0]);
      bounds.east = Math.max(bounds.east, coordinates[0]);
      bounds.south = Math.min(bounds.south, coordinates[1]);
      bounds.north = Math.max(bounds.north, coordinates[1]);
    } else coordinates.forEach(visit);
  }
  visit(geometry.coordinates);
  return bounds;
}
