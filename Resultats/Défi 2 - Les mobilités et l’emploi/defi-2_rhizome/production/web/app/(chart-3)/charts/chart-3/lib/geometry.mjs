export const POLE_THRESHOLD = 10000;
// Employment is counted at the end of 2015: a line counts as new when it opened after that year.
export const BASE_YEAR = 2015;
export const OUTER_RING = ["77", "78", "91", "95"];

export const DENSITY_CLASSES = [
  { from: 0, name: "< 100", color: "#F1EFEA" },
  { from: 100, name: "100 à moins de 500", color: "#DCE3EC" },
  { from: 500, name: "500 à moins de 2 000", color: "#B3C3D9" },
  { from: 2000, name: "≥ 2 000", color: "#7F9BC2" },
];
export const MISSING_DENSITY_COLOR = "#ffffff";
export function densityKey(value) {
  if (value === null || !Number.isFinite(value)) return "density-missing";
  for (let index = DENSITY_CLASSES.length - 1; index > 0; index--)
    if (value >= DENSITY_CLASSES[index].from) return `density-${index}`;
  return "density-0";
}
export function poleKey(pole) {
  return pole.isNew
    ? "poles-new"
    : pole.change < 0
      ? "poles-declining"
      : "poles-growing";
}
export function densityColor(value) {
  if (value === null || !Number.isFinite(value)) return MISSING_DENSITY_COLOR;
  for (let index = DENSITY_CLASSES.length - 1; index > 0; index--) {
    if (value >= DENSITY_CLASSES[index].from)
      return DENSITY_CLASSES[index].color;
  }
  return DENSITY_CLASSES[0].color;
}
// The petal shape grows in both directions, so its area is proportional to the value.
export function petalLength(value, maximum, size = 40) {
  if (value === null) return size * 0.575;
  if (maximum <= 0 || value <= 0) return 0;
  return size * Math.sqrt(value / maximum);
}
export function petalPath(length) {
  const s = length / Math.SQRT2,
    r = s * 0.8,
    t = s * 0.2;
  return `M0 0 L0 ${-t} A${r} ${r} 0 0 1 ${r} ${-s} L${s} ${-s} L${s} ${-t} A${r} ${r} 0 0 1 ${t} 0 Z`;
}
export function geometryPath(geometry) {
  function line(coordinates, close = false) {
    return (
      coordinates
        .map(([x, y], index) => `${index ? "L" : "M"}${x} ${-y}`)
        .join(" ") + (close ? " Z" : "")
    );
  }
  if (geometry.type === "LineString") return line(geometry.coordinates);
  if (geometry.type === "MultiLineString")
    return geometry.coordinates.map((ring) => line(ring)).join(" ");
  if (geometry.type === "Polygon")
    return geometry.coordinates.map((ring) => line(ring, true)).join(" ");
  if (geometry.type === "MultiPolygon")
    return geometry.coordinates
      .flatMap((polygon) => polygon.map((ring) => line(ring, true)))
      .join(" ");
  throw new Error(`Unsupported geometry: ${geometry.type}`);
}

// Largest value of each indicator, or null when no department has one.
export function metricMaxima(departments, metrics) {
  return metrics.map((metric) => {
    const values = departments
      .map((department) => department.indicators[metric.id])
      .filter((value) => value !== null);
    return values.length ? Math.max(0, ...values) : null;
  });
}
// An indicator without any value is left out; a single missing value keeps a dashed petal.
export function flowerPetals(department, metrics, maxima, size = 40) {
  return metrics
    .map((metric, index) => ({
      metric,
      index,
      maximum: maxima[index],
      value: department.indicators[metric.id],
    }))
    .filter((petal) => petal.maximum !== null)
    .map((petal) => ({
      ...petal,
      missing: petal.value === null,
      rotation: -45 + petal.index * 90,
      length: petalLength(petal.value, petal.maximum, size),
    }));
}

// Frame shared by every flower: the slots in use at full size, whatever the values, so that flowers stay comparable.
export function flowerFrame(petals, size = 40) {
  const half = size * 0.4,
    slots = new Set(petals.map((petal) => petal.index));
  const left = slots.has(3) ? -size : -half,
    right = slots.has(1) ? size : half,
    top = slots.has(0) ? -size : -half,
    bottom = slots.has(2) ? size : half;
  return [left - 4, top - 4, right - left + 8, bottom - top + 8];
}

export function boundsOf(points) {
  const xs = points.map((point) => point[0]),
    ys = points.map((point) => point[1]);
  return [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)];
}
// Lambert-93 bounds to an SVG view: the northing becomes -y.
export function viewFromBounds([west, south, east, north], padding = 0) {
  return {
    x: west - padding,
    y: -north - padding,
    width: east - west + padding * 2,
    height: north - south + padding * 2,
  };
}
// Metres per screen pixel for a view letterboxed in its element.
export function unitsPerPixel(view, width, height) {
  return Math.max(
    view.width / Math.max(width, 1),
    view.height / Math.max(height, 1),
  );
}
// Keeps the scale within its limits and the centre of the view inside the region.
export function constrainView(view, limits, size) {
  const units = unitsPerPixel(view, size.width, size.height);
  const factor =
    Math.min(limits.maxUnits, Math.max(limits.minUnits, units)) / units;
  const width = view.width * factor,
    height = view.height * factor;
  const region = limits.region;
  const centerX = Math.min(
    region.x + region.width,
    Math.max(region.x, view.x + view.width / 2),
  );
  const centerY = Math.min(
    region.y + region.height,
    Math.max(region.y, view.y + view.height / 2),
  );
  return { x: centerX - width / 2, y: centerY - height / 2, width, height };
}
// Zooms around an anchor in map coordinates; the anchor keeps its place on screen.
export function zoomAt(view, factor, anchor, limits, size) {
  const units = unitsPerPixel(view, size.width, size.height);
  const applied =
    Math.min(limits.maxUnits, Math.max(limits.minUnits, units * factor)) /
    units;
  return constrainView(
    {
      x: anchor.x - (anchor.x - view.x) * applied,
      y: anchor.y - (anchor.y - view.y) * applied,
      width: view.width * applied,
      height: view.height * applied,
    },
    limits,
    size,
  );
}
// Plate 06 sizes circles with the fourth root of employment. The smallest circle follows the map scale within screen limits.
export function poleRadius(employment, units, minimum = 5, maximum = 10) {
  return (
    Math.min(maximum, Math.max(minimum, 460 / units)) *
    units *
    (employment / POLE_THRESHOLD) ** 0.25
  );
}
export function scaleBar(units, maximumPixels = 110) {
  const steps = [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000];
  const meters =
    [...steps].reverse().find((step) => step / units <= maximumPixels) ??
    steps[0];
  return {
    meters,
    pixels: meters / units,
    label: meters >= 1000 ? `${meters / 1000} km` : `${meters} m`,
  };
}

function boxesOverlap(a, b) {
  return (
    a.x < b.x + b.width &&
    a.x + a.width > b.x &&
    a.y < b.y + b.height &&
    a.y + a.height > b.y
  );
}
// Greedy placement in map units, in the order given. `reach` is the number of rings a label may move away
// from its symbol with a leader line; a label that fits nowhere is left out. Obstacles are other symbols.
export function layoutLabels(labels, units, obstacles = []) {
  const placed = [];
  for (const label of labels) {
    const widest =
      label.width ??
      Math.max(...label.lines.map((line) => line.length)) * label.size * 0.54;
    const width = (widest + 8) * units,
      height = (label.lines.length * label.size * 1.2 + 4) * units;
    const radius = label.radius ?? 0;
    const free = (box) =>
      !placed.some((other) => boxesOverlap(box, other.box)) &&
      !obstacles.some(
        (other) => other.id !== label.id && boxesOverlap(box, other),
      );
    let position;
    if (label.centered)
      position = {
        box: { x: label.x - width / 2, y: label.y - height / 2, width, height },
        ring: 0,
      };
    else
      search: for (let ring = 0; ring <= (label.reach ?? 0); ring++) {
        const gap = (3 + ring * 11) * units;
        for (const [dx, dy] of [
          [0, 1],
          [1, 0],
          [-1, 0],
          [0, -1],
          [1, 1],
          [-1, 1],
          [1, -1],
          [-1, -1],
        ]) {
          const reach = (dx && dy ? radius * 0.72 : radius) + gap;
          const box = {
            x: label.x + dx * (reach + width / 2) - width / 2,
            y: label.y + dy * (reach + height / 2) - height / 2,
            width,
            height,
          };
          if (free(box)) {
            position = { box, ring };
            break search;
          }
        }
      }
    if (position)
      placed.push({
        ...label,
        ...position,
        centerX: position.box.x + width / 2,
        centerY: position.box.y + height / 2,
      });
  }
  return placed;
}

function geometryRings(geometry) {
  return geometry.type === "Polygon"
    ? geometry.coordinates
    : geometry.coordinates.flat();
}
function lineParts(geometry) {
  return geometry.type === "LineString"
    ? [geometry.coordinates]
    : geometry.coordinates;
}
function geometryExtent(geometry) {
  return boundsOf(
    geometry.type.endsWith("LineString")
      ? lineParts(geometry).flat()
      : geometryRings(geometry).flat(),
  );
}
export function pointInGeometry([x, y], geometry) {
  let inside = false;
  for (const ring of geometryRings(geometry)) {
    for (
      let index = 0, previous = ring.length - 1;
      index < ring.length;
      previous = index++
    ) {
      const [x1, y1] = ring[index],
        [x2, y2] = ring[previous];
      if (y1 > y !== y2 > y && x < x1 + ((y - y1) * (x2 - x1)) / (y2 - y1))
        inside = !inside;
    }
  }
  return inside;
}
function segmentDistance([px, py], [ax, ay], [bx, by]) {
  const dx = bx - ax,
    dy = by - ay,
    length = dx * dx + dy * dy;
  const t = length
    ? Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / length))
    : 0;
  return Math.hypot(px - ax - t * dx, py - ay - t * dy);
}
function extentGap(a, b) {
  return Math.hypot(
    Math.max(0, a[0] - b[2], b[0] - a[2]),
    Math.max(0, a[1] - b[3], b[1] - a[3]),
  );
}
// Distance in metres between an area and a line; 0 when the line enters the area. Distances beyond `limit` are not refined.
export function distanceToLine(area, line, limit = Infinity) {
  const extent = geometryExtent(area);
  if (extentGap(extent, geometryExtent(line)) >= limit) return Infinity;
  const rings = geometryRings(area);
  let best = limit;
  for (const part of lineParts(line)) {
    for (const point of part) {
      if (
        point[0] >= extent[0] &&
        point[0] <= extent[2] &&
        point[1] >= extent[1] &&
        point[1] <= extent[3] &&
        pointInGeometry(point, area)
      )
        return 0;
    }
    for (const ring of rings) {
      for (let index = 0; index < ring.length; index++) {
        const a = ring[index],
          b = ring[(index + 1) % ring.length];
        for (const point of part)
          best = Math.min(best, segmentDistance(point, a, b));
        for (let step = 1; step < part.length; step++)
          best = Math.min(best, segmentDistance(a, part[step - 1], part[step]));
      }
    }
  }
  return best < limit ? best : Infinity;
}

export function lineName(code) {
  const [kind, ...rest] = code.split(" ");
  const number = rest.join(" ");
  if (kind === "METRO") return `Métro ${number}`;
  if (kind === "TRAM") return `Tram T${number}`;
  if (kind === "CABLE") return `Câble ${number}`;
  if (kind === "TRAIN") return `Train ${number}`;
  return code;
}

// Descriptive figures shared by the page and the tests. Nothing here measures access to jobs.
export function analyse(data) {
  const communes = new Map(
    data.communes.map((commune) => [commune.code, commune]),
  );
  const recentByName = new Map();
  for (const line of data.lines.filter((line) => line.an > BASE_YEAR)) {
    const entry = recentByName.get(line.res_com) ?? {
      code: line.res_com,
      name: lineName(line.res_com),
      mode: line.mode,
      years: new Set(),
      segments: [],
    };
    entry.years.add(line.an);
    entry.segments.push(line);
    recentByName.set(line.res_com, entry);
  }
  const recentLines = [...recentByName.values()]
    .map((line) => ({ ...line, years: [...line.years].sort() }))
    .sort(
      (a, b) =>
        a.years[0] - b.years[0] ||
        a.name.localeCompare(b.name, "fr", { numeric: true }),
    );
  const earlier = data.lines.filter((line) => line.an <= BASE_YEAR);
  const poles = [...data.poles]
    .sort((a, b) => b.emploi_2025 - a.emploi_2025)
    .map((pole, index) => {
      const area = communes.get(pole.code).geometry;
      const crossing = recentLines.filter((line) =>
        line.segments.some(
          (segment) => distanceToLine(area, segment.geometry, 1) === 0,
        ),
      );
      return {
        ...pole,
        rank: index + 1,
        department: pole.code.slice(0, 2),
        isNew: Boolean(pole.nouveau_pole),
        change: pole.emploi_2025 / pole.emploi_2015 - 1,
        recentLines: crossing,
      };
    });
  const fresh = poles.filter((pole) => pole.isNew),
    established = poles.filter((pole) => !pole.isNew);
  const outer = fresh.filter((pole) => OUTER_RING.includes(pole.department));
  const nearEarlier = fresh.filter((pole) =>
    earlier.some(
      (line) =>
        distanceToLine(communes.get(pole.code).geometry, line.geometry, 300) <
        300,
    ),
  );
  const lengthByDepartment = new Map(
    data.departments.map((department) => [department.code, 0]),
  );
  for (const line of recentLines)
    for (const segment of line.segments)
      for (const part of lineParts(segment.geometry)) {
        for (let step = 1; step < part.length; step++) {
          const a = part[step - 1],
            b = part[step],
            middle = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
          const department = data.departments.find((item) =>
            pointInGeometry(middle, item.geometry),
          );
          if (department)
            lengthByDepartment.set(
              department.code,
              lengthByDepartment.get(department.code) +
                Math.hypot(b[0] - a[0], b[1] - a[1]),
            );
        }
      }
  const recentLength = [...lengthByDepartment.values()].reduce(
    (sum, value) => sum + value,
    0,
  );
  const innerLength = [...lengthByDepartment]
    .filter(([code]) => !OUTER_RING.includes(code))
    .reduce((sum, [, value]) => sum + value, 0);
  const departments = new Map(
    data.departments.map((department) => {
      const members = data.communes.filter((commune) =>
        commune.code.startsWith(department.code),
      );
      const own = poles.filter((pole) => pole.department === department.code);
      return [
        department.code,
        {
          poles: own.length,
          newPoles: own.filter((pole) => pole.isNew).length,
          start: members.reduce((sum, commune) => sum + commune.emploi_2015, 0),
          end: members.reduce((sum, commune) => sum + commune.emploi_2025, 0),
        },
      ];
    }),
  );
  return {
    poles,
    recentLines,
    departments,
    newPoles: fresh,
    newOuter: outer,
    declining: poles.filter((pole) => pole.change < 0),
    establishedCount: established.length,
    establishedCrossed: established.filter((pole) => pole.recentLines.length),
    newCrossed: fresh.filter((pole) => pole.recentLines.length),
    newNearEarlier: nearEarlier,
    recentKilometres: recentLength / 1000,
    innerShare: recentLength ? innerLength / recentLength : 0,
  };
}
