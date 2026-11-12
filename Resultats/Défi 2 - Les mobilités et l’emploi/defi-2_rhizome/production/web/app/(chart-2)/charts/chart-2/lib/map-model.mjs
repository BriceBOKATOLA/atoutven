// @ts-check
import { geometryBounds, ringContains } from "./geometry.mjs";

/**
 * Geographic data and derived map annotations. These calculations do not depend
 * on DOM state, map projection or the Highmaps renderer.
 *
 * @template P
 * @typedef {{ type: "Feature", properties: P, geometry: { type: string, coordinates: unknown } }} Feature
 */
/** @template P
 * @typedef {{ type: "FeatureCollection", features: Feature<P>[] }} Collection
 */
/** @typedef {{ code: string, nom: string, defm2016: number | null, defm2024: number | null, evolution: number | null }} Commune */
/** @typedef {{ code: string, nom: string, indicators: Record<string, Record<string, number | null>>, center: [number, number] }} Zone */

/** @param {Collection<Zone>} zones
 * @param {{ lon: number, lat: number }} position
 */
export function zoneAt(zones, { lon, lat }) {
  return zones.features.find(({ geometry }) => {
    const polygons =
      geometry.type === "MultiPolygon"
        ? /** @type {number[][][][]} */ (geometry.coordinates)
        : [/** @type {number[][][]} */ (geometry.coordinates)];
    return polygons.some(
      ([outer, ...holes]) =>
        ringContains(outer, lon, lat) &&
        !holes.some((hole) => ringContains(hole, lon, lat)),
    );
  })?.properties;
}
// geojson(..., 'mapline') expects line geometry, not polygon geometry.
/** @param {Collection<Zone>} zones
 * @returns {Collection<Zone>}
 */
export function zoneBoundaries(zones) {
  return {
    type: "FeatureCollection",
    features: zones.features.map((feature) => ({
      ...feature,
      geometry: {
        type: "MultiLineString",
        coordinates:
          feature.geometry.type === "MultiPolygon"
            ? /** @type {number[][][][]} */ (
                feature.geometry.coordinates
              ).flat()
            : feature.geometry.coordinates,
      },
    })),
  };
}
// Labels use the commune's own evolution, never a rounded substitute in the dataset.
/** @param {Collection<Commune>} communes */
export function communeLabels(communes) {
  const names = [
    "Épinay-sur-Seine",
    "Saint-Ouen-sur-Seine",
    "Romainville",
    "Rosny-sous-Bois",
    "Clamart",
    "Villejuif",
    "Antony",
    "Thiais",
    "Massy",
    "Ris-Orangis",
    "Paris",
  ];
  return communes.features
    .filter(
      (feature) =>
        names.includes(feature.properties.nom) &&
        feature.properties.evolution !== null,
    )
    .map((feature) => {
      const bounds = geometryBounds(feature.geometry);
      const evolution = Math.round(
        /** @type {number} */ (feature.properties.evolution),
      );
      return {
        lon: (bounds.west + bounds.east) / 2,
        lat: (bounds.south + bounds.north) / 2,
        name: `${feature.properties.nom === "Paris" ? "PARIS" : feature.properties.nom} | ${evolution > 0 ? "+" : ""}${evolution} %`,
        dataLabels:
          feature.properties.nom === "Paris"
            ? { backgroundColor: "#f6f4ef" }
            : undefined,
      };
    });
}
/** @param {string} name */
export function lineName(name) {
  const [kind, number] = name.split(" ");
  if (kind === "TRAM") return { tag: `T${number}`, full: `Tram T${number}` };
  if (kind === "METRO") return { tag: `M${number}`, full: `Métro ${number}` };
  if (kind === "CABLE") return { tag: `C${number}`, full: `Câble C${number}` };
  return { tag: name, full: name };
}
/** @param {Collection<Record<string, unknown>>} transportLines
 * @param {{ lon: number, lat: number }[]} labels
 */
export function lineTags(transportLines, labels) {
  const scale = Math.cos((48.8 * Math.PI) / 180);
  /** @param {number[]} a @param {number[]} b */
  const span = (a, b) => Math.hypot((a[0] - b[0]) * scale, a[1] - b[1]);
  /** @type {Map<string, number[][][]>} */
  const lines = new Map();
  for (const feature of transportLines.features) {
    const name = String(feature.properties.nom);
    if (name !== "TRAM 4")
      lines.set(name, [
        ...(lines.get(name) ?? []),
        /** @type {number[][]} */ (feature.geometry.coordinates),
      ]);
  }
  const taken = labels.map((label) => [label.lon, label.lat]);
  /** @param {number[]} at */
  const wideLabelClearance = (at) =>
    Math.min(
      ...taken.map((other) =>
        Math.hypot((at[0] - other[0]) * scale * 0.4, at[1] - other[1]),
      ),
    );
  return [...lines]
    .map(([name, paths]) => ({
      name,
      paths,
      length: paths.reduce(
        (sum, path) =>
          sum +
          path
            .slice(1)
            .reduce(
              (total, point, index) => total + span(point, path[index]),
              0,
            ),
        0,
      ),
    }))
    .sort((a, b) => b.length - a.length)
    .map(({ name, paths, length }) => {
      const ends = paths.flatMap((path) => [
        {
          at: path[0],
          from: path[Math.max(1, Math.round((path.length - 1) / 3))],
        },
        {
          at: path[path.length - 1],
          from: path[
            Math.min(path.length - 2, Math.round(((path.length - 1) * 2) / 3))
          ],
        },
      ]);
      const termini = ends.filter(
        (end) =>
          ends.filter((other) => span(other.at, end.at) < 0.002).length === 1,
      );
      const { at, from } = (termini.length ? termini : ends).reduce(
        (best, end) =>
          wideLabelClearance(end.at) > wideLabelClearance(best.at) ? end : best,
      );
      taken.push(at);
      const tag = lineName(name).tag,
        reach = span(at, from) || 1,
        east = ((at[0] - from[0]) * scale) / reach,
        north = (at[1] - from[1]) / reach;
      const pastTerminus =
        Math.abs(east) * (tag.length * 3.5 + 6) + Math.abs(north) * 10 + 5;
      return {
        lon: at[0],
        lat: at[1],
        name: tag,
        dataLabels: {
          x: east * pastTerminus,
          y: -north * pastTerminus,
          labelrank: length,
        },
      };
    });
}
/** @param {Collection<Commune>} communeCollection */
export function tramT4Bounds(communeCollection) {
  // Source: Amar, scripts/base/groupes_lignes.json, T4 (2019).
  const codes = ["93014", "93046", "93047"];
  const communes = communeCollection.features
    .filter((feature) => codes.includes(feature.properties.code))
    .map((feature) => geometryBounds(feature.geometry));
  return {
    west: Math.min(...communes.map((bounds) => bounds.west)) - 0.012,
    east: Math.max(...communes.map((bounds) => bounds.east)) + 0.012,
    south: Math.min(...communes.map((bounds) => bounds.south)) - 0.008,
    north: Math.max(...communes.map((bounds) => bounds.north)) + 0.008,
  };
}
