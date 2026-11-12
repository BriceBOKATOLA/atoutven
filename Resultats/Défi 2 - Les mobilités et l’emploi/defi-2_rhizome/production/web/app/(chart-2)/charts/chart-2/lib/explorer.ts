import { geometryBounds, ringContains } from "./geometry.mjs";

// The npm Highmaps engine is supplied by the browser-only loader.
// This local contract describes only the Highmaps API used by this application.
type MapSVGPathArray = (string | number)[][];
type MapGeoJSON = unknown;
type MapPointOptionsObject = { name?: string; code?: string };
interface MapSVGElement {
  element: SVGElementTagNameMap["g"];
  attr(attributes: Record<string, unknown>): MapSVGElement;
  css(styles: Record<string, unknown>): MapSVGElement;
  add(parent?: MapSVGElement): MapSVGElement;
  destroy(): void;
}
interface MapPoint {
  select?(selected: boolean, accumulate?: boolean): void;
  options: MapPointOptionsObject;
  graphic?: MapSVGElement;
  properties?: Record<string, unknown>;
}
interface MapSeries {
  points: MapPoint[];
}
interface MapChart {
  destroy(): void;
  chartWidth: number;
  chartHeight: number;
  plotWidth: number;
  plotHeight: number;
  plotLeft: number;
  plotTop: number;
  mapView?: {
    center: [number, number];
    zoom: number;
    pixelsToLonLat(point: {
      x: number;
      y: number;
    }): { lon: number; lat: number } | undefined;
    setView(
      center: [number, number],
      zoom?: number,
      redraw?: boolean,
      animation?: boolean,
    ): void;
    zoomBy(amount?: number): void;
    lonLatToPixels(point: {
      lon: number;
      lat: number;
    }): { x: number; y: number } | undefined;
    fitToBounds(
      bounds?: unknown,
      padding?: unknown,
      redraw?: boolean,
      animation?: boolean,
    ): void;
    update(
      options: Record<string, unknown>,
      redraw?: boolean,
      animation?: boolean,
    ): void;
  };
  renderer: {
    g(name: string): MapSVGElement;
    circle(x: number, y: number, r: number): MapSVGElement;
    path(path: MapSVGPathArray): MapSVGElement;
    text(text: string, x: number, y: number): MapSVGElement;
  };
  get(id: string): MapSeries | undefined;
}
type Highmaps = {
  mapChart(
    container: string | HTMLElement,
    options: Record<string, unknown>,
  ): MapChart;
  geojson(data: MapGeoJSON, type: string): unknown;
};

type Feature<P> = {
  type: "Feature";
  properties: P;
  geometry: { type: string; coordinates: unknown };
};
type Collection<P> = { type: "FeatureCollection"; features: Feature<P>[] };
type Commune = {
  code: string;
  nom: string;
  defm2016: number | null;
  defm2024: number | null;
  evolution: number | null;
};
type Zone = {
  code: string;
  nom: string;
  indicators: Record<string, Record<string, number | null>>;
  center: [number, number];
};
type Metric = { name: string; unit: string; source: string; scope: string };
type Data = {
  communes: Collection<Commune>;
  zones: Collection<Zone>;
  lines: Collection<Record<string, unknown>>;
  oldLines?: Collection<Record<string, unknown>>;
  stations?: Collection<Record<string, unknown>>;
  metrics: Metric[];
};
type FlowerChart = MapChart & {
  flowerLayer?: MapSVGElement;
  zoneLayer?: MapSVGElement;
};
type Indicator = {
  label: string;
  unit: string;
  signed: boolean;
  fill: string;
  stroke: string;
  value(zone: Zone): number | null;
};

export function mountExplorer(
  root: HTMLElement,
  Highcharts: Highmaps,
): () => void {
  let disposed = false;
  const requests = new AbortController();
  const listeners = new AbortController();
  function on(
    target: EventTarget,
    type: string,
    handler: (event: Event) => void,
  ): void {
    target.addEventListener(type, handler, { signal: listeners.signal });
  }
  const PETAL_MAX = 42,
    PETAL_MISSING = 12,
    MISSING_STROKE = "#7f8894";
  const MAP_FLOWER_SCALE = 0.75,
    MAP_FLOWER_RADIUS = PETAL_MAX * MAP_FLOWER_SCALE + 3;
  const format = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 12 });
  const integer = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 });
  const decimal = new Intl.NumberFormat("fr-FR", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  });
  const signed = new Intl.NumberFormat("fr-FR", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
    signDisplay: "exceptZero",
  });
  const element = <T extends HTMLElement>(id: string): T =>
    root.querySelector(`#${root.dataset?.chartPrefix ?? ""}${id}`) as T;
  const status = element<HTMLDivElement>("load-status");
  let data: Data;
  let chart: FlowerChart | undefined;
  let selectedCode = "";
  let selectedCommuneCode = "";
  let selectedCommuneZoneCode = "";
  let peaks: { value: number; zone: string }[] = [];
  const markers = new Map<
    string,
    {
      marker: MapSVGElement;
      target: MapSVGElement;
      center: MapSVGElement;
      label: MapSVGElement;
    }
  >();
  const tooltip = element<HTMLDivElement>("map-tooltip");

  let tooltipClose: ReturnType<typeof setTimeout> | undefined;
  function cancelTooltipClose(): void {
    clearTimeout(tooltipClose);
    tooltipClose = undefined;
  }
  function hideTooltip(): void {
    cancelTooltipClose();
    tooltip.hidden = true;
  }
  function leaveTooltip(): void {
    cancelTooltipClose();
    tooltipClose = setTimeout(hideTooltip, 120);
  }
  function showTooltip(zone: Zone, anchor: SVGGElement): void {
    if (disposed) return;
    cancelTooltipClose();
    const title = document.createElement("strong");
    title.textContent = zone.nom;
    const details = document.createElement("dl");
    for (const indicator of indicators) {
      const row = document.createElement("div");
      const label = document.createElement("dt");
      label.append(indicatorDot(indicator), indicator.label);
      const value = document.createElement("dd");
      value.textContent = indicatorText(indicator, zone);
      row.append(label, value);
      details.append(row);
    }
    const content = document.createElement("div");
    content.className = "map-tooltip-content";
    content.append(flower(zone), details);
    tooltip.replaceChildren(title, content);
    tooltip.hidden = false;
    const bounds = anchor.getBoundingClientRect();
    const origin = tooltip.offsetParent?.getBoundingClientRect() ?? {
      left: 0,
      top: 0,
    };
    const viewport = root.ownerDocument?.defaultView;
    const width = tooltip.offsetWidth;
    const height = tooltip.offsetHeight;
    const x = bounds.left + bounds.width / 2;
    const y = bounds.bottom;
    tooltip.style.left = `${Math.max(8, Math.min(x + 14, (viewport?.innerWidth ?? 1024) - width - 8)) - origin.left}px`;
    tooltip.style.top = `${Math.max(8, y + 14 + height > (viewport?.innerHeight ?? 768) - 8 ? bounds.top - height - 12 : y + 14) - origin.top}px`;
  }
  function syncFlowerSelection(): void {
    for (const [code, { marker, target, center, label }] of markers) {
      const selected = code === selectedCode;
      marker.element.setAttribute("aria-pressed", String(selected));
      target.attr({ stroke: selected ? "#06264d" : "none" });
      center.attr({
        r: selected ? 3 : 2,
        fill: selected ? "#06264d" : "#fffefa",
      });
      label.attr({ opacity: selected ? 1 : 0 });
      if (selected) {
        const focused = root.ownerDocument?.activeElement === marker.element;
        marker.element.parentNode?.appendChild(marker.element);
        if (focused) marker.element.focus({ preventScroll: true });
      }
    }
  }

  function raw(zone: Zone, name: string, year: string): number | null {
    return zone.indicators[name]?.[year] ?? null;
  }
  function growth(from: number | null, to: number | null): number | null {
    return from === null || to === null || from === 0
      ? null
      : (to / from - 1) * 100;
  }
  function per100(part: number | null, total: number | null): number | null {
    return part === null || total === null || total === 0
      ? null
      : (part / total) * 100;
  }
  const indicators: Indicator[] = [
    {
      label: "Salariés du secteur privé, évolution 2016–2024",
      unit: "%",
      signed: true,
      fill: "#B3CF78",
      stroke: "#7A9A3A",
      value: (zone) =>
        growth(
          raw(zone, "Salariés privés", "2016"),
          raw(zone, "Salariés privés", "2024"),
        ),
    },
    {
      label: "Demandeurs d’emploi (catégories A, B et C), évolution 2016–2024",
      unit: "%",
      signed: true,
      fill: "#E06A55",
      stroke: "#B5452F",
      value: (zone) =>
        growth(
          raw(zone, "Demandeurs ABC", "2016"),
          raw(zone, "Demandeurs ABC", "2024"),
        ),
    },
    {
      label: "Taux de chômage localisé, 2024",
      unit: "%",
      signed: false,
      fill: "#E0A52A",
      stroke: "#A87400",
      value: (zone) => raw(zone, "Taux de chômage localisé", "2024"),
    },
    {
      label: "Demandeurs d’emploi pour 100 salariés du secteur privé, 2024",
      unit: "pour 100 salariés",
      signed: false,
      fill: "#F2BFC8",
      stroke: "#BF6A80",
      value: (zone) =>
        per100(
          raw(zone, "Demandeurs ABC", "2024"),
          raw(zone, "Salariés privés", "2024"),
        ),
    },
    {
      label: "Emplois dans la zone pour 100 actifs occupés résidents, 2016",
      unit: "pour 100 actifs occupés résidents",
      signed: false,
      fill: "#9A5A90",
      stroke: "#6E3C66",
      value: (zone) =>
        per100(
          raw(zone, "Emplois au lieu de travail", "2016"),
          raw(zone, "Actifs occupés résidents", "2016"),
        ),
    },
  ];

  // Same rounded petal geometry as version-8/fleur.js. Its bounding diagonal is length.
  function petalPath(length: number): MapSVGPathArray {
    const s = length / Math.SQRT2,
      r = s * 0.8,
      t = s * 0.2;
    return [
      ["M", 0, 0],
      ["L", 0, -t],
      ["A", r, r, 0, 0, 1, r, -s],
      ["L", s, -s],
      ["L", s, -t],
      ["A", r, r, 0, 0, 1, t, 0],
      ["Z"],
    ];
  }
  function petalLength(value: number | null, max: number): number {
    if (value === null) return PETAL_MISSING;
    if (value === 0 || max === 0) return 0;
    return (PETAL_MAX * Math.abs(value)) / max;
  }
  function petalRotation(index: number): number {
    return -15 + (index * 360) / indicators.length;
  }
  function petal(
    length: number,
    rotation: number,
    fill: string,
    stroke: string,
    dashed = false,
  ): SVGPathElement {
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute(
      "d",
      petalPath(length)
        .map((segment) => segment.join(" "))
        .join(" "),
    );
    path.setAttribute("transform", `rotate(${rotation})`);
    path.setAttribute("fill", fill);
    path.setAttribute("stroke", stroke);
    path.setAttribute("vector-effect", "non-scaling-stroke");
    if (dashed) path.setAttribute("stroke-dasharray", "3 2");
    return path;
  }
  function legendSvg(viewBox: string): SVGSVGElement {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", viewBox);
    svg.setAttribute("aria-hidden", "true");
    return svg;
  }
  function flower(zone: Zone): SVGSVGElement {
    const svg = legendSvg("-46 -46 92 92");
    indicators.forEach((indicator, index) => {
      const value = indicator.value(zone);
      svg.append(
        value === null
          ? petal(
              PETAL_MISSING,
              petalRotation(index),
              "none",
              MISSING_STROKE,
              true,
            )
          : petal(
              petalLength(value, Math.abs(peaks[index].value)),
              petalRotation(index),
              value < 0 ? "#fff" : indicator.fill,
              indicator.stroke,
            ),
      );
    });
    return svg;
  }
  function indicatorDot(indicator: Indicator): HTMLSpanElement {
    const dot = document.createElement("span");
    dot.className = "dot";
    dot.style.setProperty("--swatch", indicator.fill);
    dot.style.borderColor = indicator.stroke;
    dot.setAttribute("aria-hidden", "true");
    return dot;
  }
  function renderFlowerLegend(): void {
    const svg = legendSvg("-58 -58 116 116");
    const list = element("flower-colors");
    list.replaceChildren();
    indicators.forEach((indicator, index) => {
      svg.append(
        petal(
          PETAL_MAX,
          petalRotation(index),
          indicator.fill,
          indicator.stroke,
        ),
      );
      const angle = ((petalRotation(index) - 45) * Math.PI) / 180;
      const number = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "text",
      );
      number.setAttribute("x", (50 * Math.cos(angle)).toFixed(1));
      number.setAttribute("y", (50 * Math.sin(angle)).toFixed(1));
      number.textContent = String(index + 1);
      svg.append(number);
      const item = document.createElement("li");
      item.append(indicatorDot(indicator), indicator.label);
      list.append(item);
    });
    element("legend-flower").replaceChildren(svg);
  }
  function renderZoneOptions(): void {
    const group = element("zone-options");
    group.replaceChildren(
      group.firstElementChild!,
      ...[...data.zones.features]
        .sort((a, b) => a.properties.nom.localeCompare(b.properties.nom, "fr"))
        .map(({ properties: zone }) => {
          const option = document.createElement("label");
          option.className = "zone-option";
          const input = document.createElement("input");
          input.type = "radio";
          input.name = "zone";
          input.value = zone.code;
          const name = document.createElement("span");
          name.textContent = zone.nom;
          option.append(input, flower(zone), name);
          return option;
        }),
    );
  }
  function escapeHTML(value: string): string {
    return value.replace(
      /[&<>"']/g,
      (character) =>
        ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;",
        })[character]!,
    );
  }
  function colorFor(value: number | null): string {
    if (value === null) return "#F1EFEA";
    if (value < -5) return "#2C7FB8";
    if (value < 0) return "#A6CEE3";
    if (value < 5) return "#FBE6CC";
    if (value < 15) return "#F5AE6B";
    return "#D9531E";
  }
  function communeText(commune: Commune): string {
    const count = (value: number | null) =>
      value === null ? "indisponible" : format.format(value);
    const evolution =
      commune.evolution === null
        ? "évolution indisponible"
        : `évolution : ${new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 1 }).format(commune.evolution)} %`;
    return `${commune.nom} (${commune.code}) ; 2016 : ${count(commune.defm2016)} ; 2024 : ${count(commune.defm2024)} ; ${evolution}`;
  }
  function selectCommune(code: string): void {
    const feature = data.communes.features.find(
      (feature) => feature.properties.code === code,
    );
    if (!feature) return;
    selectedCommuneCode = code;
    selectedCommuneZoneCode = selectedCode;
    element("commune-detail").textContent = communeText(feature.properties);
    for (const point of chart?.get("communes")?.points ?? [])
      point.select?.(point.options.code === code, true);
  }
  function clearCommune(): void {
    selectedCommuneCode = "";
    selectedCommuneZoneCode = "";
    element("commune-detail").textContent =
      "Sélectionnez une commune sur la carte pour consulter ses données.";
    for (const point of chart?.get("communes")?.points ?? [])
      point.select?.(false, true);
  }
  function scaleDistance(pixelsPerKm: number): number | null {
    if (!Number.isFinite(pixelsPerKm) || pixelsPerKm <= 0) return null;
    const target = 100 / pixelsPerKm;
    const magnitude = 10 ** Math.floor(Math.log10(target));
    return [1, 2, 5, 10]
      .map((step) => step * magnitude)
      .reduce((best, value) =>
        Math.abs(value * pixelsPerKm - 100) < Math.abs(best * pixelsPerKm - 100)
          ? value
          : best,
      );
  }
  function updateScale(map: FlowerChart): void {
    const origin = map.mapView?.lonLatToPixels({ lon: 2.35, lat: 48.85 });
    const east = map.mapView?.lonLatToPixels({ lon: 2.36, lat: 48.85 });
    const scale = element("map-scale");
    if (!origin || !east) {
      scale.hidden = true;
      return;
    }
    const pixelsPerKm =
      Math.hypot(east.x - origin.x, east.y - origin.y) /
      (111.32 * Math.cos((48.85 * Math.PI) / 180) * 0.01);
    const distance = scaleDistance(pixelsPerKm);
    if (distance === null) {
      scale.hidden = true;
      return;
    }
    scale.hidden = false;
    scale.querySelector("span")!.textContent =
      distance < 1
        ? `${integer.format(distance * 1000)} m`
        : `${format.format(distance)} km`;
    (scale.querySelector("i") as HTMLElement).style.width =
      `${distance * pixelsPerKm}px`;
  }
  function drawZoneOutlines(map: FlowerChart): void {
    if (!map.mapView || !data) return;
    map.zoneLayer?.destroy();
    // Keep zone boundaries below Highcharts' data-label layer (zIndex 6).
    map.zoneLayer = map.renderer
      .g("zone-outlines")
      .attr({ zIndex: 4, translateX: map.plotLeft, translateY: map.plotTop })
      .add();
    for (const feature of zoneBoundaries(data.zones).features) {
      const segments: MapSVGPathArray = [];
      for (const ring of feature.geometry.coordinates as number[][][]) {
        let first = true;
        for (const [lon, lat] of ring) {
          const point = map.mapView.lonLatToPixels({ lon, lat });
          if (point) {
            segments.push([first ? "M" : "L", point.x, point.y]);
            first = false;
          }
        }
      }
      const selected = feature.properties.code === selectedCode;
      if (!selected)
        map.renderer
          .path(segments)
          .attr({
            fill: "none",
            stroke: "#fffefa",
            "stroke-width": 2.6,
            "stroke-opacity": 0.75,
          })
          .add(map.zoneLayer).element.style.pointerEvents = "none";
      const outline = map.renderer
        .path(segments)
        .attr({
          fill: "none",
          stroke: selected ? "#06264d" : "#66727f",
          "stroke-width": selected ? 2.2 : 1,
        })
        .add(map.zoneLayer);
      outline.element.style.pointerEvents = "none";
    }
  }
  function drawFlowers(map: FlowerChart): void {
    if (!map.mapView || !data) return;
    hideTooltip();
    markers.clear();
    drawZoneOutlines(map);
    map.flowerLayer?.destroy();
    map.flowerLayer = map.renderer
      .g("flowers")
      .attr({ zIndex: 7, translateX: map.plotLeft, translateY: map.plotTop })
      .add();
    // Only the centers follow the projection; petals keep a fixed size in pixels.
    const zones = [...data.zones.features].sort(
      (a, b) =>
        Number(a.properties.code === selectedCode) -
        Number(b.properties.code === selectedCode),
    );
    for (const feature of zones) {
      const zone = feature.properties;
      const position = map.mapView.lonLatToPixels({
        lon: zone.center[0],
        lat: zone.center[1],
      });
      if (
        !position ||
        position.x < -MAP_FLOWER_RADIUS ||
        position.x > map.plotWidth + MAP_FLOWER_RADIUS ||
        position.y < -MAP_FLOWER_RADIUS ||
        position.y > map.plotHeight + MAP_FLOWER_RADIUS
      )
        continue;
      const selected = zone.code === selectedCode;
      const marker = map.renderer
        .g("zone-marker")
        .attr({ translateX: position.x, translateY: position.y })
        .add(map.flowerLayer);
      marker.element.setAttribute(
        "class",
        "highcharts-zone-marker zone-marker",
      );
      marker.element.setAttribute("role", "button");
      marker.element.setAttribute("tabindex", "0");
      marker.element.setAttribute(
        "aria-label",
        `Voir les cinq indicateurs de ${zone.nom}`,
      );
      marker.element.setAttribute("aria-pressed", String(selected));
      marker.element.setAttribute("aria-describedby", tooltip.id);
      marker.element.style.cursor = "pointer";
      // Cover the full flower, including the spaces between its petals.
      const target = map.renderer
        .circle(0, 0, MAP_FLOWER_RADIUS)
        .attr({
          fill: "#fff",
          "fill-opacity": 0.001,
          stroke: selected ? "#06264d" : "none",
          "stroke-width": 1.5,
        })
        .add(marker);
      indicators.forEach((indicator, index) => {
        const value = indicator.value(zone);
        map.renderer
          .path(
            petalPath(
              petalLength(value, Math.abs(peaks[index].value)) *
                MAP_FLOWER_SCALE,
            ),
          )
          .attr({
            rotation: petalRotation(index),
            fill: value === null ? "none" : value < 0 ? "#fff" : indicator.fill,
            stroke: value === null ? MISSING_STROKE : indicator.stroke,
            "stroke-width": 1,
            ...(value === null ? { "stroke-dasharray": "3 2" } : {}),
          })
          .add(marker);
      });
      const center = map.renderer
        .circle(0, 0, selected ? 3 : 2)
        .attr({
          fill: selected ? "#06264d" : "#fffefa",
          stroke: "#06264d",
          "stroke-width": 1,
        })
        .add(marker);
      const label = map.renderer
        .text(zone.nom, 0, -MAP_FLOWER_RADIUS - 5)
        .attr({ "text-anchor": "middle", opacity: selected ? 1 : 0 })
        .css({
          fontSize: "12px",
          fontWeight: "700",
          color: "#20382b",
          textOutline: "4px #fffefa",
        })
        .add(marker);
      label.element.style.pointerEvents = "none";
      markers.set(zone.code, { marker, target, center, label });
      marker.element.onmouseenter = () => {
        label.attr({ opacity: 1 });
        showTooltip(zone, marker.element);
      };
      marker.element.onmouseleave = () => {
        label.attr({ opacity: zone.code === selectedCode ? 1 : 0 });
        leaveTooltip();
      };
      marker.element.onfocus = () => showTooltip(zone, marker.element);
      marker.element.onblur = hideTooltip;
      const activate = (event: Event) => {
        event.preventDefault();
        event.stopPropagation();
        selectZone(zone.code);
        showTooltip(zone, marker.element);
      };
      // Highmaps also interprets pointer events as geographic selections.
      marker.element.onpointerdown = (event) => event.stopPropagation();
      marker.element.onclick = activate;
      marker.element.onkeydown = (event) => {
        if (event.key === "Enter" || event.key === " ") activate(event);
        else if (event.key === "Escape") {
          event.preventDefault();
          event.stopPropagation();
          hideTooltip();
        }
      };
    }
  }
  function indicatorText(indicator: Indicator, zone: Zone): string {
    const value = indicator.value(zone);
    if (value === null) return "Donnée indisponible";
    const number = indicator.signed ? signed : decimal;
    return `${number.format(value)}${indicator.unit ? `\u00a0${indicator.unit}` : ""}`;
  }
  function renderDetails(zone: Zone): void {
    element("zone-name").textContent = zone.nom;
    element("flower-preview").replaceChildren(flower(zone));
    const details = element("details");
    details.replaceChildren();
    indicators.forEach((indicator) => {
      const row = document.createElement("div");
      row.className = "metric";
      const name = document.createElement("dt");
      name.append(indicatorDot(indicator), indicator.label);
      const value = indicator.value(zone);
      const number = indicator.signed ? signed : decimal;
      const unit = indicator.unit ? `\u00a0${indicator.unit}` : "";
      const amount = document.createElement("dd");
      amount.textContent =
        value === null ? "Donnée indisponible" : number.format(value);
      const suffix = document.createElement("small");
      suffix.textContent = value === null ? "" : unit;
      amount.append(suffix);
      row.append(name, amount);
      details.append(row);
    });
  }
  function selectZone(code: string): void {
    const zone = data.zones.features.find(
      (feature) => feature.properties.code === code,
    )?.properties;
    if (!zone) return;
    if (selectedCommuneCode && selectedCommuneZoneCode !== code) clearCommune();
    selectedCode = code;
    const option = element("zone-options").querySelector<HTMLInputElement>(
      `input[value="${code}"]`,
    );
    if (option) option.checked = true;
    renderDetails(zone);
    hideTooltip();
    if (chart) drawZoneOutlines(chart);
    syncFlowerSelection();
  }
  function zoneAt({
    lon,
    lat,
  }: {
    lon: number;
    lat: number;
  }): Zone | undefined {
    return data.zones.features.find(({ geometry }) => {
      const polygons =
        geometry.type === "MultiPolygon"
          ? (geometry.coordinates as number[][][][])
          : [geometry.coordinates as number[][][]];
      return polygons.some(
        ([outer, ...holes]) =>
          ringContains(outer, lon, lat) &&
          !holes.some((hole) => ringContains(hole, lon, lat)),
      );
    })?.properties;
  }
  function selectZoneAt(
    map: FlowerChart,
    event: { chartX: number; chartY: number },
    scroll = true,
  ): void {
    const x = event.chartX - map.plotLeft;
    const y = event.chartY - map.plotTop;
    if (x < 0 || y < 0 || x > map.plotWidth || y > map.plotHeight) return;
    const position = map.mapView?.pixelsToLonLat({ x, y });
    const zone = position && zoneAt(position);
    if (zone) {
      selectZone(zone.code);
      if (scroll) element("explorer").scrollIntoView({ block: "nearest" });
    }
  }
  // geojson(..., 'mapline') expects line geometry, not polygon geometry.
  function zoneBoundaries(zones: Collection<Zone>): Collection<Zone> {
    return {
      type: "FeatureCollection",
      features: zones.features.map((feature) => ({
        ...feature,
        geometry: {
          type: "MultiLineString",
          coordinates:
            feature.geometry.type === "MultiPolygon"
              ? (feature.geometry.coordinates as number[][][][]).flat()
              : feature.geometry.coordinates,
        },
      })),
    };
  }
  // Labels use the commune's own evolution, never a rounded substitute in the dataset.
  function communeLabels(): unknown[] {
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
    return data.communes.features
      .filter(
        (feature) =>
          names.includes(feature.properties.nom) &&
          feature.properties.evolution !== null,
      )
      .map((feature) => {
        const bounds = geometryBounds(feature.geometry);
        const evolution = Math.round(feature.properties.evolution!);
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
  function lineName(name: string): { tag: string; full: string } {
    const [kind, number] = name.split(" ");
    if (kind === "TRAM") return { tag: `T${number}`, full: `Tram T${number}` };
    if (kind === "METRO") return { tag: `M${number}`, full: `Métro ${number}` };
    if (kind === "CABLE")
      return { tag: `C${number}`, full: `Câble C${number}` };
    return { tag: name, full: name };
  }
  function lineTags(labels: { lon: number; lat: number }[]): unknown[] {
    const scale = Math.cos((48.8 * Math.PI) / 180);
    const span = (a: number[], b: number[]) =>
      Math.hypot((a[0] - b[0]) * scale, a[1] - b[1]);
    const lines = new Map<string, number[][][]>();
    for (const feature of data.lines.features) {
      const name = String(feature.properties.nom);
      if (name !== "TRAM 4")
        lines.set(name, [
          ...(lines.get(name) ?? []),
          feature.geometry.coordinates as number[][],
        ]);
    }
    const taken = labels.map((label) => [label.lon, label.lat]);
    const wideLabelClearance = (at: number[]) =>
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
            wideLabelClearance(end.at) > wideLabelClearance(best.at)
              ? end
              : best,
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
  function tramT4Bounds(): {
    west: number;
    east: number;
    south: number;
    north: number;
  } {
    // Source: Amar, scripts/base/groupes_lignes.json, T4 (2019).
    const codes = ["93014", "93046", "93047"];
    const communes = data.communes.features
      .filter((feature) => codes.includes(feature.properties.code))
      .map((feature) => geometryBounds(feature.geometry));
    return {
      west: Math.min(...communes.map((bounds) => bounds.west)) - 0.012,
      east: Math.max(...communes.map((bounds) => bounds.east)) + 0.012,
      south: Math.min(...communes.map((bounds) => bounds.south)) - 0.008,
      north: Math.max(...communes.map((bounds) => bounds.north)) + 0.008,
    };
  }
  function createChart(): void {
    const t4 = tramT4Bounds();
    const compact = element("map").clientWidth < 520;
    const t4Label = { lon: t4.east, lat: t4.north + 0.012, name: "TRAM T4" };
    const labels = communeLabels() as { lon: number; lat: number }[];
    const communes = data.communes.features.map((feature) => ({
      code: feature.properties.code,
      name: feature.properties.nom,
      value: feature.properties.evolution,
      color: colorFor(feature.properties.evolution),
    }));
    chart = Highcharts.mapChart(element("map"), {
      chart: {
        backgroundColor: "transparent",
        animation: false,
        spacing: [0, 0, 0, 0],
        events: {
          render(this: FlowerChart) {
            drawFlowers(this);
            updateScale(this);
          },
          click(this: FlowerChart, event: { chartX: number; chartY: number }) {
            selectZoneAt(this, event);
          },
        },
      },
      lang: {
        zoomIn: "Agrandir",
        zoomOut: "Réduire",
        resetZoom: "Vue initiale",
        accessibility: {
          defaultChartTitle: "Carte de l’Île-de-France",
          chartContainerLabel: "{title}. Carte interactive.",
          svgContainerLabel: "Carte interactive",
          zoom: {
            mapZoomIn: "Agrandir la carte",
            mapZoomOut: "Réduire la carte",
            resetZoomButton: "Vue initiale",
          },
          screenReaderSection: {
            endOfChartMarker: "Fin de la carte interactive.",
          },
          series: {
            summary: {
              map: "{series.name}, carte de {series.points.length} communes.",
              mapCombination:
                "{series.name}, série {seriesNumber} sur {chart.series.length}. Carte de {series.points.length} communes.",
            },
          },
          chartTypes: {
            unknownMap: "Carte avec {numSeries} séries de données.",
            mapTypeDescription:
              "Carte de {mapTitle} avec {numSeries} séries de données.",
          },
        },
      },
      title: { text: undefined },
      mapView: {
        projection: { name: "WebMercator", rotation: [0, 0, 0] },
        fitToGeometry: {
          type: "MultiPoint",
          coordinates: [
            [1.90310856, 48.520179],
            [2.89053166, 49.06481],
          ],
        },
        padding: 0,
      },
      accessibility: {
        description:
          "Évolution communale des demandeurs d’emploi entre 2016 et 2024. Parcourez les communes avec les flèches et activez-les avec Entrée ou Espace pour consulter leurs données. Le choix de zone permet de lire les indicateurs des fleurs au clavier.",
        series: { pointDescriptionEnabledThreshold: false },
        keyboardNavigation: {
          seriesNavigation: {
            mode: "serialize",
            pointNavigationEnabledThreshold: false,
            skipNullPoints: false,
          },
        },
      },
      legend: { enabled: false },
      credits: { enabled: true, style: { fontSize: "12px", color: "#526071" } },
      mapNavigation: {
        enabled: true,
        enableButtons: false,
        enableMouseWheelZoom: true,
        buttonOptions: {
          align: "left",
          verticalAlign: "bottom",
          theme: { fill: "#fffefa", stroke: "#7c8d7e", r: 0 },
        },
      },
      tooltip: {
        useHTML: false,
        backgroundColor: "#fffefa",
        borderColor: "#758575",
        borderRadius: 2,
        shadow: false,
        style: { fontSize: "12px" },
        formatter(this: MapPoint) {
          const code = (
            this.options as MapPointOptionsObject & { code?: string }
          ).code;
          const commune = data.communes.features.find(
            (feature) => feature.properties.code === code,
          )?.properties;
          if (commune)
            return escapeHTML(communeText(commune)).replace(/ ; /g, "<br>");
          if (typeof this.properties?.nom === "string")
            return `${escapeHTML(lineName(this.properties.nom).full)}<br>Mise en service (donnée IDFM) : ${Number(this.properties.annee)}`;
          return false;
        },
      },
      plotOptions: {
        series: {
          animation: false,
          states: { inactive: { enabled: false } },
          point: {
            events: {
              click(event: { chartX: number; chartY: number }) {
                if (chart) selectZoneAt(chart, event);
              },
            },
          },
        },
      },
      series: [
        {
          type: "map",
          id: "communes",
          name: "Demandeurs d’emploi",
          mapData: data.communes as unknown as MapGeoJSON,
          joinBy: ["code", "code"],
          data: communes,
          borderColor: "#fffefa",
          borderWidth: 0.3,
          nullColor: "#F1EFEA",
          states: {
            hover: { borderColor: "#273f31", borderWidth: 1, brightness: 0.08 },
          },
          point: {
            events: {
              click(
                this: MapPoint,
                event: { chartX: number; chartY: number; point?: MapPoint },
              ) {
                if (chart) selectZoneAt(chart, event, event.point !== this);
                const code = (
                  this.options as MapPointOptionsObject & { code?: string }
                ).code;
                const commune = data.communes.features.find(
                  (feature) => feature.properties.code === code,
                )?.properties;
                if (commune) selectCommune(commune.code);
              },
            },
          },
          accessibility: {
            enabled: true,
            point: {
              descriptionFormatter(point: MapPoint) {
                const commune = data.communes.features.find(
                  (feature) => feature.properties.code === point.options.code,
                )?.properties;
                return commune
                  ? communeText(commune)
                  : (point.options.name ?? "");
              },
            },
          },
        },
        ...(data.oldLines
          ? [
              {
                type: "mapline",
                name: "Réseau ferré antérieur à 2015",
                className: "no-pointer",
                mapData: Highcharts.geojson(
                  data.oldLines as unknown as MapGeoJSON,
                  "mapline",
                ),
                color: "#a3aab5",
                nullColor: "#a3aab5",
                lineWidth: 0.7,
                enableMouseTracking: false,
                accessibility: { enabled: false },
              },
            ]
          : []),
        {
          type: "mapline",
          name: "Lignes ouvertes entre 2015 et 2025",
          data: Highcharts.geojson(
            data.lines as unknown as MapGeoJSON,
            "mapline",
          ),
          color: "#fffefa",
          nullColor: "#fffefa",
          nullInteraction: true,
          lineWidth: compact ? 3.6 : 5,
          states: { hover: { enabled: false } },
          accessibility: { enabled: false },
        },
        {
          type: "mapline",
          name: "Tracé des lignes ouvertes entre 2015 et 2025",
          className: "no-pointer",
          mapData: Highcharts.geojson(
            data.lines as unknown as MapGeoJSON,
            "mapline",
          ),
          color: "#0e1b2c",
          nullColor: "#0e1b2c",
          lineWidth: compact ? 1.6 : 2.2,
          enableMouseTracking: false,
          accessibility: { enabled: false },
        },
        ...(data.stations
          ? [
              {
                type: "mappoint",
                name: "Gares ouvertes entre 2015 et 2025",
                className: "no-pointer",
                data: Highcharts.geojson(
                  data.stations as unknown as MapGeoJSON,
                  "mappoint",
                ),
                marker: {
                  radius: compact ? 2 : 2.6,
                  fillColor: "#fff",
                  lineColor: "#0e1b2c",
                  lineWidth: 1,
                },
                enableMouseTracking: false,
                accessibility: { enabled: false },
              },
            ]
          : []),
        {
          type: "mapline",
          name: "Communes du Tram T4",
          className: "no-pointer",
          data: [
            {
              geometry: {
                type: "LineString",
                coordinates: [
                  [t4.west, t4.south],
                  [t4.east, t4.south],
                  [t4.east, t4.north],
                  [t4.west, t4.north],
                  [t4.west, t4.south],
                ],
              },
            },
          ],
          color: "#1e3442",
          lineWidth: 1.5,
          dashStyle: "Dash",
          zIndex: 6,
          enableMouseTracking: false,
          accessibility: { enabled: false },
        },
        {
          type: "mappoint",
          name: "Tram T4",
          className: "no-pointer",
          data: [t4Label],
          marker: { enabled: false },
          dataLabels: {
            enabled: true,
            format: "{point.name}",
            align: "right",
            labelrank: 2,
            backgroundColor: "#ffd400",
            padding: 2,
            style: {
              color: "#0e1b2c",
              fontSize: "12px",
              fontFamily: "Arial Narrow, Arial, sans-serif",
              textOutline: "none",
            },
          },
          zIndex: 6,
          enableMouseTracking: false,
          accessibility: { enabled: false },
        },
        {
          type: "mappoint",
          name: "Repères communaux",
          className: "no-pointer",
          data: labels,
          marker: { enabled: false },
          dataLabels: {
            enabled: true,
            format: "{point.name}",
            labelrank: 2,
            backgroundColor: "#ffd400",
            padding: 2,
            borderRadius: 0,
            style: {
              color: "#0e1b2c",
              fontSize: "12px",
              fontFamily: "Arial Narrow, Arial, sans-serif",
              fontWeight: "600",
              textOutline: "none",
            },
          },
          zIndex: 6,
          enableMouseTracking: false,
          accessibility: { enabled: false },
        },
        ...(compact
          ? []
          : [
              {
                type: "mappoint",
                name: "Noms des lignes",
                className: "no-pointer",
                data: lineTags([
                  ...labels,
                  t4Label,
                  ...data.zones.features.map(({ properties: zone }) => ({
                    lon: zone.center[0],
                    lat: zone.center[1],
                  })),
                ]),
                marker: { enabled: false },
                dataLabels: {
                  enabled: true,
                  format: "{point.name}",
                  align: "center",
                  verticalAlign: "middle",
                  backgroundColor: "#0e1b2c",
                  padding: 3,
                  borderRadius: 0,
                  style: {
                    color: "#fff",
                    fontSize: "12px",
                    fontFamily: "Arial Narrow, Arial, sans-serif",
                    fontWeight: "700",
                    textOutline: "none",
                  },
                },
                zIndex: 6,
                enableMouseTracking: false,
                accessibility: { enabled: false },
              },
            ]),
      ],
    }) as FlowerChart;
  }
  async function load(): Promise<void> {
    try {
      const response = await fetch("/data/jobseekers-employment-zones.json", {
        signal: requests.signal,
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const loaded = (await response.json()) as Data;
      if (disposed) return;
      data = loaded;
      if (
        !data.communes?.features.length ||
        !data.zones?.features.length ||
        !data.metrics?.length
      )
        throw new Error("Données vides");
      peaks = indicators.map((indicator) =>
        data.zones.features.reduce(
          (peak, { properties: zone }) => {
            const value = indicator.value(zone) ?? 0;
            return Math.abs(value) > Math.abs(peak.value)
              ? { value, zone: zone.nom }
              : peak;
          },
          { value: 0, zone: "" },
        ),
      );
      renderFlowerLegend();
      renderZoneOptions();
      selectedCode = (
        data.zones.features.find(
          (feature) => feature.properties.nom === "Paris",
        ) ?? data.zones.features[0]
      ).properties.code;
      chart?.destroy();
      chart = undefined;
      createChart();
      if (chart && !markers.size) drawFlowers(chart);
      selectZone(selectedCode);
      status.hidden = true;
      element("coverage").textContent =
        `${format.format(data.communes.features.length)} communes dans le cadrage, ${data.zones.features.length} zones d’emploi et ${indicators.length} indicateurs. Les données absentes ne sont pas interpolées.`;
    } catch (error) {
      if (disposed) return;
      chart?.destroy();
      chart = undefined;
      console.error("La carte ne peut pas être chargée.", error);
      status.replaceChildren();
      const message = document.createElement("p");
      message.textContent =
        "La carte ne peut pas être chargée. Vérifiez la connexion puis réessayez.";
      const retry = document.createElement("button");
      retry.textContent = "Réessayer";
      retry.onclick = () => {
        status.textContent = "Chargement de la carte…";
        void load();
      };
      status.append(message, retry);
      element("zone-name").textContent = "Données indisponibles";
    }
  }
  on(element("zone-options"), "change", (event) =>
    selectZone((event.target as HTMLInputElement).value),
  );

  on(tooltip, "mouseenter", cancelTooltipClose);
  on(tooltip, "mouseleave", hideTooltip);
  if (root.ownerDocument) {
    on(root.ownerDocument, "keydown", (event) => {
      if ((event as KeyboardEvent).key === "Escape") hideTooltip();
    });
    on(root.ownerDocument, "pointerdown", (event) => {
      if (!tooltip.contains(event.target as Node | null)) hideTooltip();
    });
    const viewport = root.ownerDocument.defaultView;
    if (viewport) {
      on(viewport, "scroll", hideTooltip);
      on(viewport, "resize", hideTooltip);
    }
  }
  void load();
  return () => {
    disposed = true;
    requests.abort();
    listeners.abort();
    hideTooltip();
    markers.clear();
    chart?.destroy();
    chart = undefined;
  };
}
