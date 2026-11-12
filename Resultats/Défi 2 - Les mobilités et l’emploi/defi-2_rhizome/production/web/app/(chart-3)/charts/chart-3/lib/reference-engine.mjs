import {
  BASE_YEAR,
  densityColor,
  petalPath,
  geometryPath,
  metricMaxima,
  flowerPetals,
  flowerFrame,
  viewFromBounds,
  unitsPerPixel,
  constrainView,
  zoomAt,
  poleRadius,
  scaleBar,
  layoutLabels,
  analyse,
} from "./geometry.mjs";
import { palette } from "./flowers.mjs";
import { mountHighmaps } from "./highmaps-adapter.mjs";

// Keep the established interaction surface above the Highmaps geographical series.
// Each mount owns its data and listeners; cleanup also handles React StrictMode.
export function initializeReference(root, sourceData, { loadHighmaps } = {}) {
  let highmaps;
  let mapEngine;
  let disposed = false;
  let tooltipDepartment;
  let flowerLayer;
  const lifecycle = new AbortController();
  function listen(target, type, callback, options = {}) {
    target.addEventListener(type, callback, {
      ...options,
      signal: lifecycle.signal,
    });
  }
  const svgNamespace = "http://www.w3.org/2000/svg";
  const prefix = root.dataset?.chartPrefix ?? "";
  const element = (id) => root.querySelector(`#${prefix}${id}`);
  const map = element("map");
  const frame = element("carte");
  const tooltip = element("map-tooltip");
  const status = element("load-status");
  const countFormat = new Intl.NumberFormat("fr-FR");
  const compactFormat = new Intl.NumberFormat("fr-FR", {
    notation: "compact",
    maximumFractionDigits: 2,
  });
  const decimalFormat = new Intl.NumberFormat("fr-FR", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  });
  const millionFormat = new Intl.NumberFormat("fr-FR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  // The largest reference circle of the legend at the largest symbol scale.
  const sizeLegendHeight = Math.ceil(poleRadius(150000, 1, 10, 10) * 2) + 20;
  const nextFrame =
    globalThis.requestAnimationFrame ??
    ((callback) => {
      callback();
      return 0;
    });
  const measureContext = document.createElement("canvas").getContext?.("2d");
  // Places named in the plates' takeaways; each is tied to the poles it stands for.
  const landmarks = [
    { id: "la-defense", text: "La Défense", codes: ["92026", "92062"] },
    { id: "93066", text: "Saint-Denis", codes: ["93066"] },
    { id: "95527", text: "Roissy", codes: ["95527"] },
  ];
  const rings = [
    ["Paris et petite couronne", ["75", "92", "93", "94"]],
    ["Grande couronne", ["77", "78", "91", "95"]],
  ];
  let data;
  let insights;
  let maxima = [];
  let selected = "";
  let homeView;
  let regionView;
  let view;
  let renderedUnits;
  let frameRequested = false;
  let departmentLayer;
  let poleLayer;
  let labelLayer;
  let poleNodes = new Map();
  let departmentButtons = [];
  let computedTakeaways = [];
  let hovered;
  let dragging;
  let pinch;
  let swipe;
  let suppressClickUntil = 0;
  let hintTimer;
  let lastWheelHint = -Infinity;
  let wheelHints = 0;

  function svgNode(name, attributes = {}) {
    const node = document.createElementNS(svgNamespace, name);
    for (const [key, value] of Object.entries(attributes))
      node.setAttribute(key, String(value));
    return node;
  }
  function htmlNode(name, className, text) {
    const node = document.createElement(name);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }
  const plural = (count, one, many) =>
    `${countFormat.format(count)} ${count > 1 ? many : one}`;
  const percent = (ratio) =>
    `${ratio < 0 ? "−" : ratio > 0 ? "+" : ""}${decimalFormat.format(Math.abs(ratio * 100))} %`;
  const names = (poles) => poles.map((pole) => pole.nom).join(", ");
  const lineYears = (line) => `${line.name} (${line.years.join(", ")})`;
  const metricValue = (metric, value) =>
    countFormat.format(Math.round(value * (metric.scale ?? 1)));
  const mapSize = () => ({
    width: frame.clientWidth || 1,
    height: frame.clientHeight || 1,
  });
  const currentUnits = () =>
    unitsPerPixel(view, mapSize().width, mapSize().height);
  const polePoint = (pole) => ({
    x: pole.geometry.coordinates[0],
    y: -pole.geometry.coordinates[1],
  });
  function limits() {
    const size = mapSize();
    return {
      minUnits: 6,
      maxUnits: unitsPerPixel(regionView, size.width, size.height) * 1.1,
      region: regionView,
    };
  }
  function toMap(clientX, clientY) {
    const box = map.getBoundingClientRect(),
      units = currentUnits();
    return {
      x: view.x + view.width / 2 + (clientX - box.left - box.width / 2) * units,
      y:
        view.y + view.height / 2 + (clientY - box.top - box.height / 2) * units,
    };
  }

  function setView(next) {
    view = constrainView(next, limits(), mapSize());
    if (frameRequested) return;
    frameRequested = true;
    nextFrame(render);
  }
  function render() {
    frameRequested = false;
    if (disposed) return;
    map.setAttribute(
      "viewBox",
      `${view.x} ${view.y} ${view.width} ${view.height}`,
    );
    mapEngine?.render(view, mapSize());
    const units = currentUnits();
    if (units !== renderedUnits) {
      renderedUnits = units;
      drawSymbols(units);
    }
    // The tooltip follows a pole that holds keyboard focus; a pointer tooltip returns with the next move.
    const focused = document.activeElement;
    if (
      focused?.classList?.contains("pole-symbol") &&
      focused.matches(":focus-visible")
    ) {
      const box = focused.getBoundingClientRect();
      showTooltip(undefined, box.left + box.width / 2, box.bottom - 8);
    } else hideTooltip();
    renderMapFlowers();
  }
  function zoomBy(factor) {
    setView(
      zoomAt(
        view,
        factor,
        { x: view.x + view.width / 2, y: view.y + view.height / 2 },
        limits(),
        mapSize(),
      ),
    );
  }
  function pan(dx, dy) {
    const size = mapSize(),
      units = currentUnits();
    setView({
      ...view,
      x: view.x + dx * size.width * units * 0.2,
      y: view.y + dy * size.height * units * 0.2,
    });
  }

  // Symbols and labels keep a screen size, so they are redrawn when the scale changes.
  function drawSymbols(units) {
    for (const pole of insights.poles)
      poleNodes
        .get(pole.code)
        .setAttribute("r", poleRadius(pole.emploi_2025, units));
    drawLabels(units);
    const bar = scaleBar(units);
    element("scale-line").style.width = `${bar.pixels}px`;
    element("scale-label").textContent = bar.label;
    const legend = element("size-legend");
    const radii = [10000, 50000, 150000].map((value) => [
      value,
      poleRadius(value, units) / units,
    ]);
    const height = sizeLegendHeight,
      svg = svgNode("svg", {
        width: 138,
        height,
        viewBox: `0 0 138 ${height}`,
        "aria-hidden": "true",
      });
    radii.forEach(([value, radius], index) => {
      const x = 23 + index * 46,
        label = svgNode("text", { x, y: height - 7, "text-anchor": "middle" });
      label.textContent = `${countFormat.format(value / 1e3)}\u00a0k`;
      svg.append(
        svgNode("circle", { cx: x, cy: height - 20 - radius, r: radius }),
        label,
      );
    });
    legend.replaceChildren(svg);
  }
  function labelWidth(label) {
    if (!measureContext) return undefined;
    measureContext.font = `${label.kind === "minor" ? 400 : label.kind === "new-pole" ? 500 : 600} ${label.size}px Arial, Helvetica, sans-serif`;
    return Math.max(
      ...label.lines.map((line) => measureContext.measureText(line).width),
    );
  }
  function drawLabels(units) {
    labelLayer.replaceChildren();
    const size = mapSize(),
      compact = size.width < 520;
    const zoom = unitsPerPixel(homeView, size.width, size.height) / units;
    const radius = (pole) => poleRadius(pole.emploi_2025, units);
    const byCode = new Map(insights.poles.map((pole) => [pole.code, pole]));
    const labels = [];
    const paris = byCode.get("75056");
    if (paris)
      labels.push({
        id: paris.code,
        ...polePoint(paris),
        lines: [
          "PARIS",
          `${millionFormat.format(paris.emploi_2025 / 1e6)} M d’emplois`,
        ],
        size: 13,
        kind: "paris",
        centered: true,
      });
    const named = new Set(["75056"]);
    if (!compact || zoom > 1.5) {
      for (const mark of landmarks) {
        const members = mark.codes
          .map((code) => byCode.get(code))
          .filter(Boolean);
        if (members.length !== mark.codes.length) continue;
        const points = members.map(polePoint),
          x = points.reduce((sum, point) => sum + point.x, 0) / points.length,
          y = points.reduce((sum, point) => sum + point.y, 0) / points.length;
        const reach = Math.max(
          ...members.map(
            (pole, index) =>
              Math.hypot(points[index].x - x, points[index].y - y) +
              radius(pole),
          ),
        );
        // A name shared by several circles always keeps its leader line.
        labels.push({
          id: mark.id,
          x,
          y,
          radius: reach,
          lines: [mark.text],
          size: 12.5,
          kind: "landmark",
          reach: 4,
          leader: members.length > 1,
        });
        if (members.length === 1) named.add(members[0].code);
      }
      for (const pole of insights.newPoles) {
        labels.push({
          id: pole.code,
          ...polePoint(pole),
          radius: radius(pole),
          lines: [pole.nom],
          size: 12,
          kind: "new-pole",
          reach: 5,
        });
        named.add(pole.code);
      }
    }
    if (zoom > (compact ? 2.4 : 1.7))
      for (const pole of insights.poles)
        if (!named.has(pole.code))
          labels.push({
            id: pole.code,
            ...polePoint(pole),
            radius: radius(pole),
            lines: [pole.nom],
            size: 12,
            kind: "minor",
            reach: 0,
          });
    const obstacles = insights.poles
      .filter((pole) => pole.code !== "75056")
      .map((pole) => {
        const { x, y } = polePoint(pole),
          r = radius(pole);
        return {
          id: pole.code,
          x: x - r,
          y: y - r,
          width: r * 2,
          height: r * 2,
        };
      });
    for (const label of layoutLabels(
      labels.map((label) => ({ ...label, width: labelWidth(label) })),
      units,
      obstacles,
    )) {
      const group = svgNode("g");
      if (label.ring > 0 || label.leader) {
        const dx = label.centerX - label.x,
          dy = label.centerY - label.y,
          length = Math.hypot(dx, dy) || 1;
        const start = label.leader ? 0 : label.radius;
        group.append(
          svgNode("path", {
            class: `label-leader ${label.kind}`,
            d: `M${label.x + (dx / length) * start} ${label.y + (dy / length) * start} L${label.centerX} ${label.centerY}`,
          }),
        );
      }
      const text = svgNode("text", {
        class: `map-label ${label.kind}`,
        x: label.centerX,
        y: label.centerY - (label.lines.length - 1) * label.size * 0.6 * units,
        "font-size": label.size * units,
        "stroke-width": 3 * units,
      });
      label.lines.forEach((line, index) => {
        const span = svgNode("tspan", {
          x: label.centerX,
          dy: index ? label.size * 1.2 * units : 0,
        });
        span.textContent = line;
        text.append(span);
      });
      group.append(text);
      labelLayer.append(group);
    }
  }

  function poleLines(pole) {
    const lines = [
      [pole.nom, "title"],
      [
        `${countFormat.format(pole.emploi_2025)} emplois salariés privés fin 2025`,
      ],
      [
        `${countFormat.format(pole.emploi_2015)} fin 2015, soit ${percent(pole.change)}`,
      ],
    ];
    if (pole.isNew) lines.push(["Nouveau pôle depuis 2015"]);
    lines.push([
      pole.recentLines.length
        ? `Ligne ouverte depuis 2015 : ${pole.recentLines.map(lineYears).join(", ")}`
        : "Aucune ligne ouverte depuis 2015 sur la commune",
      "note",
    ]);
    return lines;
  }
  function describe(target) {
    tooltipDepartment = data.departments.find(
      (item) =>
        item.code === target.closest?.("[data-department]")?.dataset.department,
    );
    const flower = target.closest?.(".prototype-flower");
    if (flower && tooltipDepartment)
      return [
        [`${tooltipDepartment.nom} (${tooltipDepartment.code})`, "title"],
      ];
    const pole = target.closest?.(".pole-symbol");
    if (pole)
      return poleLines(
        insights.poles.find((item) => item.code === pole.dataset.commune),
      );
    const line = target.closest?.("[data-line]");
    if (line) {
      const item = insights.recentLines.find(
        (entry) => entry.code === line.dataset.line,
      );
      return [
        [item.name, "title"],
        [`Mise en service : ${item.years.join(", ")}`],
      ];
    }
    const shape = target.closest?.(".commune");
    if (!shape) return undefined;
    const commune = data.communes.find(
      (item) => item.code === shape.dataset.commune,
    );
    return communeLines(commune);
  }
  function communeLines(commune) {
    const employment = (year) =>
      Number.isFinite(commune[`emploi_${year}`])
        ? `${countFormat.format(commune[`emploi_${year}`])} emplois salariés privés fin ${year}`
        : `Emplois salariés privés fin ${year} : non disponibles`;
    const lines = [
      [commune.nom, "title"],
      [employment(2025)],
      [employment(2015)],
    ];
    if (commune.emploi_2015 > 0 && Number.isFinite(commune.emploi_2025)) {
      lines.push([
        `${percent(commune.emploi_2025 / commune.emploi_2015 - 1)} depuis fin 2015`,
      ]);
    }
    lines.push([
      Number.isFinite(commune.densite_2025)
        ? `${countFormat.format(Math.round(commune.densite_2025))} emplois par km², fin 2025`
        : "Densité d’emploi fin 2025 : non disponible",
      "note",
    ]);
    return lines;
  }
  function hideTooltip() {
    hovered = undefined;
    tooltip.hidden = true;
  }
  function showTooltip(lines, x, y) {
    if (lines)
      tooltip.replaceChildren(
        ...lines.map(([text, kind]) =>
          htmlNode(
            kind === "title" ? "strong" : "span",
            kind === "note" ? "tooltip-note" : "",
            text,
          ),
        ),
      );
    if (lines) appendTooltipFlower();
    tooltip.hidden = false;
    const width = tooltip.offsetWidth,
      height = tooltip.offsetHeight;
    // The chart container controls its own responsive width. Position relative
    // to the map section so containment and story scroll cannot shift the tooltip.
    const origin = tooltip.offsetParent?.getBoundingClientRect() ?? {
      left: 0,
      top: 0,
    };
    tooltip.style.left = `${Math.max(8, Math.min(x + 14, window.innerWidth - width - 8)) - origin.left}px`;
    tooltip.style.top = `${(y + 14 + height > window.innerHeight - 8 ? Math.max(8, y - height - 12) : y + 14) - origin.top}px`;
  }
  function showHint(text) {
    const hint = element("map-hint");
    hint.textContent = text;
    hint.hidden = false;
    clearTimeout(hintTimer);
    hintTimer = setTimeout(() => {
      hint.hidden = true;
    }, 2000);
    hintTimer.unref?.();
  }

  function createMap() {
    mapEngine?.destroy();
    mapEngine = undefined;
    map.replaceChildren();
    flowerLayer = undefined;
    poleNodes = new Map();
    const communes = svgNode("g", { class: "communes" });
    for (const commune of data.communes)
      communes.append(
        svgNode("path", {
          d: geometryPath(commune.geometry),
          fill: densityColor(commune.densite_2025),
          class: "commune",
          "fill-rule": "evenodd",
          "data-department": commune.code.slice(0, 2),
          "data-commune": commune.code,
        }),
      );
    departmentLayer = svgNode("g", { class: "department-shapes" });
    for (const department of data.departments)
      departmentLayer.append(
        svgNode("path", {
          d: geometryPath(department.geometry),
          class: "department-area",
          "fill-rule": "evenodd",
          "data-department": department.code,
        }),
      );
    const earlier = svgNode("path", {
      class: "rail-earlier",
      d: data.lines
        .filter((line) => line.an <= BASE_YEAR)
        .map((line) => geometryPath(line.geometry))
        .join(" "),
    });
    const recent = svgNode("g", { class: "rail-recent" });
    for (const line of insights.recentLines) {
      const d = line.segments
        .map((segment) => geometryPath(segment.geometry))
        .join(" ");
      const group = svgNode("g", { "data-line": line.code });
      group.append(
        svgNode("path", { class: "rail-casing", d }),
        svgNode("path", { class: "rail-new", d }),
        svgNode("path", { class: "rail-hit", d }),
      );
      recent.append(group);
    }
    poleLayer = svgNode("g", {
      class: "poles",
      tabindex: -1,
      role: "group",
      "aria-label": `${insights.poles.length} pôles d’emploi, du plus grand au plus petit`,
    });
    for (const pole of insights.poles) {
      const { x, y } = polePoint(pole);
      const circle = svgNode("circle", {
        cx: x,
        cy: y,
        r: 1,
        role: "button",
        tabindex: pole.rank === 1 ? 0 : -1,
        "data-department": pole.department,
        "data-commune": pole.code,
        class: `pole-symbol${pole.isNew ? " new-pole" : ""}${pole.change < 0 ? " declining" : ""}${pole.code === "75056" ? " paris-pole" : ""}`,
      });
      circle.setAttribute(
        "aria-label",
        `${pole.nom}, pôle numéro ${pole.rank} : ${countFormat.format(pole.emploi_2025)} emplois salariés privés fin 2025, ${percent(pole.change)} depuis fin 2015${pole.isNew ? ", nouveau pôle" : ""}. ${pole.recentLines.length ? `Ligne ouverte depuis 2015 : ${pole.recentLines.map(lineYears).join(", ")}` : "Aucune ligne ouverte depuis 2015 sur la commune"}.`,
      );
      poleNodes.set(pole.code, circle);
    }
    // Small circles are drawn last so that large ones do not hide them.
    for (const pole of insights.poles)
      poleLayer.append(poleNodes.get(pole.code));
    labelLayer = svgNode("g", { class: "labels", "aria-hidden": "true" });
    map.append(
      communes,
      departmentLayer,
      earlier,
      recent,
      poleLayer,
      labelLayer,
    );
    listen(poleLayer, "focusin", (event) => focusPole(event.target));
    listen(poleLayer, "focusout", hideTooltip);
    mapEngine = highmaps
      ? mountHighmaps(highmaps, frame, map, data)
      : undefined;
    regionView = viewFromBounds(data.bounds, 6500);
    homeView = { ...regionView };
    renderedUnits = undefined;
    setView({ ...homeView });
  }
  function focusPole(circle) {
    const pole = insights.poles.find(
      (item) => item.code === circle.dataset?.commune,
    );
    if (!pole) return;
    for (const node of poleNodes.values())
      node.setAttribute("tabindex", node === circle ? "0" : "-1");
    // A pointer already shows the tooltip where it is; only keyboard focus moves the map.
    if (circle.matches && !circle.matches(":focus-visible")) return;
    const { x, y } = polePoint(pole),
      size = mapSize(),
      units = currentUnits();
    if (
      Math.abs(x - view.x - view.width / 2) > size.width * units * 0.42 ||
      Math.abs(y - view.y - view.height / 2) > size.height * units * 0.42
    ) {
      view = constrainView(
        { ...view, x: x - view.width / 2, y: y - view.height / 2 },
        limits(),
        size,
      );
      render();
    }
    const box = circle.getBoundingClientRect();
    tooltipDepartment = data.departments.find(
      (item) => item.code === pole.department,
    );
    showTooltip(poleLines(pole), box.left + box.width / 2, box.bottom - 8);
  }

  function selectDepartment(code) {
    const department = data.departments.find((item) => item.code === code);
    selected = department ? code : "";
    mapEngine?.select(selected);
    for (const shape of departmentLayer.children)
      shape.classList.toggle("selected", shape.dataset.department === selected);
    for (const button of departmentButtons)
      button.setAttribute(
        "aria-pressed",
        String(button.dataset.department === selected),
      );
    let message = "Aucun département sélectionné.";
    if (department) {
      const summary = insights.departments.get(code);
      message = `${department.nom} (${code}) : ${plural(summary.poles, "pôle", "pôles")}${summary.newPoles ? `, dont ${plural(summary.newPoles, "nouveau", "nouveaux")}` : ""} ; ${percent(summary.end / summary.start - 1)} d’emplois salariés privés depuis fin 2015.`;
      element("selection-text").textContent = message;
    }
    element("selection").hidden = !department;
    for (const flower of flowerLayer?.children ?? [])
      flower.setAttribute(
        "aria-pressed",
        String(flower.dataset.department === selected),
      );
    element("announce").textContent = message;
    const url = new URL(location.href);
    // Local files only accept a change of fragment.
    if (url.protocol === "file:")
      history.replaceState(
        history.state,
        "",
        selected ? `#departement=${selected}` : "#",
      );
    else {
      if (selected) url.searchParams.set("departement", selected);
      else url.searchParams.delete("departement");
      history.replaceState(history.state, "", url);
    }
  }
  function renderFlowerLegend() {
    const labelPositions = [
      [0, -48],
      [48, 0],
      [0, 48],
      [-48, 0],
    ];
    const diagram = svgNode("svg", { viewBox: "-60 -60 120 120" });
    const list = element("flower-legend-items");
    list.replaceChildren();
    data.metrics.forEach((metric, index) => {
      diagram.append(
        svgNode("path", {
          d: petalPath(36),
          transform: `rotate(${-45 + index * 90})`,
          fill: metric.color,
          stroke: "#fffefa",
          "stroke-width": 0.7,
        }),
      );
      const [x, y] = labelPositions[index];
      const number = svgNode("text", { x, y });
      number.textContent = String(index + 1);
      diagram.append(number);
      const item = htmlNode("li");
      const swatch = svgNode("svg", {
        viewBox: "0 0 12 12",
        fill: metric.color,
        "aria-hidden": "true",
      });
      swatch.append(svgNode("circle", { cx: 6, cy: 6, r: 5 }));
      const label = htmlNode("span", "flower-legend-label");
      label.append(
        htmlNode("strong", "", `${index + 1}. ${metric.name}`),
        htmlNode("span", "", metric.period),
      );
      item.append(swatch, label);
      list.append(item);
    });
    diagram.append(svgNode("circle", { r: 2, fill: "#344052" }));
    element("flower-legend-diagram").replaceChildren(diagram);
  }
  function renderDepartments() {
    renderFlowerLegend();
    const container = element("departments");
    container.replaceChildren();
    departmentButtons = [];
    const absent = data.metrics.filter(
      (metric, index) => maxima[index] === null,
    );
    element("departments-intro").textContent =
      "Cliquez sur une fleur pour repérer son département sur la carte et consulter ses indicateurs.";
    const note = element("departments-missing");
    note.hidden = !absent.length;
    note.textContent = absent.length
      ? `Non représentés, faute de données : ${absent.map((metric) => metric.name.toLowerCase()).join(", ")}.`
      : "";
    for (const [title, codes] of rings) {
      const section = htmlNode("div", "ring"),
        grid = htmlNode("div", "ring-grid");
      for (const code of codes) {
        const department = data.departments.find((item) => item.code === code);
        if (department) grid.append(departmentButton(department));
      }
      section.append(htmlNode("h3", "", title), grid);
      container.append(section);
    }
  }
  function departmentButton(department) {
    const button = htmlNode("button", "department"),
      petals = flowerPetals(department, data.metrics, maxima);
    button.type = "button";
    button.dataset.department = department.code;
    button.setAttribute("aria-pressed", "false");
    const flower = svgNode("svg", {
      viewBox: flowerFrame(petals).join(" "),
      "aria-hidden": "true",
    });
    for (const petal of petals)
      flower.append(
        svgNode(
          "path",
          petal.missing
            ? {
                d: petalPath(petal.length),
                transform: `rotate(${petal.rotation})`,
                class: "petal-missing",
                stroke: petal.metric.color,
              }
            : {
                d: petalPath(petal.length),
                transform: `rotate(${petal.rotation})`,
                fill: petal.metric.color,
                stroke: "#fffefa",
                "stroke-width": 0.7,
              },
        ),
      );
    flower.append(svgNode("circle", { r: 2, fill: "#344052" }));
    button.append(
      flower,
      htmlNode("span", "name", `${department.nom} (${department.code})`),
    );
    for (const petal of petals) {
      const row = htmlNode("span", "metric"),
        dot = htmlNode("i");
      dot.style.setProperty("--swatch", petal.metric.color);
      const amount = htmlNode(
        "b",
        "",
        petal.missing
          ? "non disponible"
          : compactFormat.format(
              Math.round(petal.value * (petal.metric.scale ?? 1)),
            ),
      );
      if (!petal.missing) {
        const fullValue = metricValue(petal.metric, petal.value);
        amount.setAttribute("title", fullValue);
        amount.setAttribute("aria-label", fullValue);
      }
      row.append(dot, htmlNode("span", "", petal.metric.name), amount);
      button.append(row);
    }
    const { salarie, interim } = department.indicators;
    if (salarie > 0 && interim >= 0 && interim !== null)
      button.append(
        htmlNode(
          "span",
          "ratio",
          `Part de l’intérim : ${decimalFormat.format((interim / salarie) * 100)} % des emplois salariés`,
        ),
      );
    listen(button, "click", () =>
      selectDepartment(selected === department.code ? "" : department.code),
    );
    departmentButtons.push(button);
    return button;
  }

  function figureRow(
    label,
    start,
    end,
    {
      format = countFormat,
      divisor = 1,
      suffix = "",
      source,
      showChange = false,
    } = {},
  ) {
    const row = document.createElement("div");
    row.append(htmlNode("dt", "", label));
    if (showChange)
      row.append(htmlNode("dd", "change", percent(end / start - 1)));
    row.append(
      htmlNode(
        "dd",
        "values",
        `${format.format(start / divisor)}${suffix} à ${format.format(end / divisor)}${suffix}`.replaceAll(
          "\u202f",
          "\u00a0",
        ),
      ),
    );
    if (source) row.append(htmlNode("dd", "source", source));
    return row;
  }
  function renderPanel() {
    const comparison = data.comparison,
      total = insights.poles.length;
    element("pole-count").textContent = countFormat.format(total);
    element("employment-count").textContent =
      `${decimalFormat.format(data.totalEmployment / 1e6)}\u00a0M`;
    element("pole-comparison").textContent =
      `${comparison.poleCount2015} pôles fin 2015, ${total} fin 2025 : ${comparison.newPoleCount} communes ont franchi le seuil de 10\u00a0k emplois, ${comparison.poleCount2015 + comparison.newPoleCount - total} sont repassées dessous.`;
    element("comparison-figures").replaceChildren(
      ...comparison.rows.map((row) =>
        figureRow(row.label, row.start, row.end, {
          format: millionFormat,
          divisor: 1e6,
          suffix: "\u00a0M",
          source: `${row.source}, ${row.years}`,
          showChange: true,
        }),
      ),
    );
    element("top-poles").replaceChildren(
      ...comparison.topPoles.map((pole) =>
        figureRow(pole.nom, pole.start, pole.end, {
          format: decimalFormat,
          divisor: 1e3,
          suffix: "\u00a0k",
        }),
      ),
    );
    for (const item of computedTakeaways) item.remove();
    const fresh = insights.newPoles,
      crossed = insights.newCrossed;
    const crossing = crossed
      .map(
        (pole) =>
          `${pole.nom} (${pole.recentLines.map((line) => line.name.toLowerCase()).join(", ")})`,
      )
      .join(", ");
    computedTakeaways = [
      `${insights.newOuter.length} des ${fresh.length} nouveaux pôles sont en grande couronne (${names(insights.newOuter.slice(0, 3))}…).`,
      `${insights.newNearEarlier.length === fresh.length ? "Tous se trouvent" : `${insights.newNearEarlier.length} sur ${fresh.length} se trouvent`} le long du réseau déjà en service en 2015 ; ${crossed.length === 1 ? `un seul, ${crossing}, est traversé` : crossed.length ? `${crossed.length} sont traversés (${crossing})` : "aucun n’est traversé"} par une ligne ouverte depuis.`,
      `${insights.declining.length} pôles sur ${total} comptent moins d’emplois qu’en 2015.`,
    ].map((text) => htmlNode("li", "", text));
    element("takeaways").append(...computedTakeaways);
    element("coverage").textContent =
      `Données affichées : ${countFormat.format(data.communes.length)} communes, ${total} pôles, ${countFormat.format(data.lines.length)} tronçons de voie ferrée.`;
  }
  async function load() {
    try {
      data = structuredClone(sourceData);
      if (disposed) return;
      for (const metric of data.metrics)
        metric.color = palette[metric.id] ?? metric.color;
      if (
        data.crs !== "EPSG:2154" ||
        !data.departments.length ||
        !data.metrics.length ||
        !data.communes.length ||
        !data.poles.length
      )
        throw new Error("Données incomplètes");
      insights = analyse(data);
      maxima = metricMaxima(data.departments, data.metrics);
      if (loadHighmaps) {
        highmaps = await loadHighmaps();
        if (disposed) return;
      }
      createMap();
      renderDepartments();
      renderPanel();
      status.hidden = true;
      const code =
        new URL(location.href).searchParams.get("departement") ??
        new URLSearchParams(location.hash.slice(1)).get("departement");
      if (data.departments.some((item) => item.code === code))
        selectDepartment(code);
    } catch (error) {
      if (disposed) return;
      status.replaceChildren();
      const retry = htmlNode("button", "", "Réessayer");
      retry.type = "button";
      listen(retry, "click", () => {
        status.textContent = "Chargement de la carte…";
        void load();
      });
      status.append(
        htmlNode("p", "", "La carte n’a pas pu charger ses données."),
        retry,
      );
      console.error("Chargement de la carte impossible.", error);
    }
  }

  listen(element("clear-selection"), "click", () => {
    const restoreFocus = document.activeElement === element("clear-selection");
    selectDepartment("");
    if (restoreFocus) map.focus();
  });
  listen(map, "click", (event) => {
    if (!data || dragging?.moved || performance.now() < suppressClickUntil)
      return;
    const lines = describe(event.target);
    if (lines) showTooltip(lines, event.clientX, event.clientY);
    const code =
      event.target.closest?.("[data-department]")?.dataset.department;
    if (code)
      selectDepartment(
        event.target.closest?.(".prototype-flower") && selected === code
          ? ""
          : code,
      );
  });
  listen(map, "pointerdown", (event) => {
    if (!view || event.button !== 0 || event.pointerType === "touch") return;
    dragging = {
      x: event.clientX,
      y: event.clientY,
      view: { ...view },
      moved: false,
    };
  });
  listen(map, "pointermove", (event) => {
    if (!view || event.pointerType === "touch") return;
    if (!dragging) {
      if (event.target === hovered)
        return showTooltip(undefined, event.clientX, event.clientY);
      const lines = describe(event.target);
      if (!lines) return hideTooltip();
      hovered = event.target;
      return showTooltip(lines, event.clientX, event.clientY);
    }
    const dx = event.clientX - dragging.x,
      dy = event.clientY - dragging.y;
    if (Math.hypot(dx, dy) < 5 && !dragging.moved) return;
    if (!dragging.moved) {
      map.setPointerCapture(event.pointerId);
      hideTooltip();
    }
    dragging.moved = true;
    map.classList.add("dragging");
    const units = unitsPerPixel(
      dragging.view,
      mapSize().width,
      mapSize().height,
    );
    setView({
      ...dragging.view,
      x: dragging.view.x - dx * units,
      y: dragging.view.y - dy * units,
    });
  });
  function endDrag() {
    map.classList.remove("dragging");
    // The click follows pointerup; retain its movement guard until after that event.
    setTimeout(() => {
      dragging = undefined;
    }, 0);
  }
  listen(map, "pointerup", endDrag);
  listen(map, "pointercancel", endDrag);
  listen(map, "pointerleave", () => {
    if (!dragging) hideTooltip();
  });

  // One finger scrolls the page; two fingers move and zoom the map.
  function touchCentre(touches) {
    const [a, b] = touches;
    return {
      x: (a.clientX + b.clientX) / 2,
      y: (a.clientY + b.clientY) / 2,
      distance: Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY) || 1,
    };
  }
  listen(
    map,
    "touchstart",
    (event) => {
      if (!view) return;
      if (event.touches.length === 2) {
        event.preventDefault();
        const start = touchCentre(event.touches);
        pinch = {
          distance: start.distance,
          units: currentUnits(),
          anchor: toMap(start.x, start.y),
        };
        swipe = undefined;
        hideTooltip();
      } else if (event.touches.length === 1)
        swipe = { x: event.touches[0].clientX, y: event.touches[0].clientY };
    },
    { passive: false },
  );
  listen(
    map,
    "touchmove",
    (event) => {
      if (pinch && event.touches.length === 2) {
        event.preventDefault();
        const now = touchCentre(event.touches),
          bounds = limits(),
          box = map.getBoundingClientRect();
        const units = Math.min(
          bounds.maxUnits,
          Math.max(
            bounds.minUnits,
            (pinch.units * pinch.distance) / now.distance,
          ),
        );
        const factor = units / currentUnits(),
          width = view.width * factor,
          height = view.height * factor;
        setView({
          x:
            pinch.anchor.x -
            (now.x - box.left - box.width / 2) * units -
            width / 2,
          y:
            pinch.anchor.y -
            (now.y - box.top - box.height / 2) * units -
            height / 2,
          width,
          height,
        });
        suppressClickUntil = performance.now() + 350;
      } else if (swipe && event.touches.length === 1) {
        const dx = event.touches[0].clientX - swipe.x,
          dy = event.touches[0].clientY - swipe.y;
        if (Math.abs(dx) > 28 && Math.abs(dx) > Math.abs(dy) * 1.5) {
          showHint("Deux doigts pour déplacer la carte");
          swipe = undefined;
        }
      }
    },
    { passive: false },
  );
  for (const name of ["touchend", "touchcancel"])
    listen(map, name, (event) => {
      if (event.touches.length < 2) pinch = undefined;
      if (!event.touches.length) swipe = undefined;
    });
  listen(
    map,
    "wheel",
    (event) => {
      if (!view) return;
      if (!event.ctrlKey && !event.metaKey) {
        // Plain scrolling belongs to the page; the hint is shown twice at most.
        if (wheelHints < 2 && performance.now() - lastWheelHint > 6000) {
          wheelHints++;
          lastWheelHint = performance.now();
          showHint(
            /Mac|iPhone|iPad/.test(globalThis.navigator?.platform ?? "")
              ? "Maintenez ⌘ pour zoomer avec le défilement"
              : "Maintenez Ctrl pour zoomer avec la molette",
          );
        }
        return;
      }
      event.preventDefault();
      setView(
        zoomAt(
          view,
          Math.exp(Math.max(-0.35, Math.min(0.35, event.deltaY * 0.01))),
          toMap(event.clientX, event.clientY),
          limits(),
          mapSize(),
        ),
      );
    },
    { passive: false },
  );
  listen(map, "keydown", (event) => {
    if (!view || event.altKey || event.ctrlKey || event.metaKey) return;
    const circle = event.target.closest?.(".pole-symbol");
    const arrows = {
      ArrowLeft: [-1, 0],
      ArrowRight: [1, 0],
      ArrowUp: [0, -1],
      ArrowDown: [0, 1],
    };
    if (circle) {
      const index = insights.poles.findIndex(
          (pole) => pole.code === circle.dataset.commune,
        ),
        last = insights.poles.length - 1;
      const next = {
        ArrowRight: index + 1,
        ArrowDown: index + 1,
        ArrowLeft: index - 1,
        ArrowUp: index - 1,
        Home: 0,
        End: last,
      }[event.key];
      if (next !== undefined) {
        event.preventDefault();
        return poleNodes
          .get(insights.poles[Math.max(0, Math.min(last, next))].code)
          .focus();
      }
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        return selectDepartment(insights.poles[index].department);
      }
      if (event.key === "Escape") {
        hideTooltip();
        return map.focus();
      }
    } else if (arrows[event.key]) {
      event.preventDefault();
      return pan(...arrows[event.key]);
    }
    if (event.key === "+" || event.key === "=") zoomBy(0.75);
    else if (event.key === "-" || event.key === "−") zoomBy(1 / 0.75);
    else if (event.key === "0") setView({ ...homeView });
    else if (event.key === "Escape") hideTooltip();
  });
  listen(map, "focus", () => {
    if (view && map.matches?.(":focus-visible"))
      showHint(
        "Flèches pour déplacer, + et − pour zoomer, Tab pour parcourir les pôles",
      );
  });
  listen(window, "resize", () => {
    if (view) setView(view);
  });
  // The tooltip is fixed to the window: it leaves with a tap elsewhere or a page scroll.
  listen(window, "scroll", hideTooltip, { passive: true });
  listen(document, "pointerdown", (event) => {
    if (!map.contains(event.target)) hideTooltip();
  });
  document.fonts?.ready.then(() => {
    if (!disposed && view) {
      renderedUnits = undefined;
      setView(view);
    }
  });
  void load();
  function departmentFlower(department) {
    const petals = flowerPetals(department, data.metrics, maxima);
    const flower = svgNode("svg", {
      viewBox: flowerFrame(petals).join(" "),
      "aria-hidden": "true",
    });
    for (const petal of petals)
      flower.append(
        svgNode("path", {
          d: petalPath(petal.length),
          transform: `rotate(${petal.rotation})`,
          fill: petal.missing ? "none" : petal.metric.color,
          stroke: petal.missing ? petal.metric.color : "#fffefa",
          "stroke-width": 1,
          ...(petal.missing ? { "stroke-dasharray": "3 2" } : {}),
        }),
      );
    flower.append(svgNode("circle", { r: 2, fill: "#344052" }));
    return flower;
  }
  function renderMapFlowers() {
    if (!data || !view) return;
    // Preserve focused SVG nodes while zooming or resizing.
    if (!flowerLayer) {
      flowerLayer = svgNode("g", {
        class: "prototype-flowers",
        tabindex: -1,
        "aria-label": "Indicateurs des huit départements",
      });
      map.append(flowerLayer);
      for (const department of data.departments) {
        const group = svgNode("g", {
          class: "prototype-flower",
          "data-department": department.code,
          tabindex: 0,
          role: "button",
          "aria-label": `${department.nom} (${department.code}), afficher les indicateurs et sélectionner le département`,
        });
        const marker = svgNode("g", {
          class: "flower-marker",
          "data-department": department.code,
        });
        marker.append(svgNode("circle", { class: "disc", r: 23 }));
        const flower = departmentFlower(department);
        for (const [name, value] of Object.entries({
          x: -18,
          y: -20,
          width: 36,
          height: 36,
        }))
          flower.setAttribute(name, value);
        marker.append(flower);
        const label = svgNode("text", { x: 0, y: 34 });
        label.textContent = department.code;
        marker.append(label);
        group.append(svgNode("path", { class: "prototype-leader" }), marker);
        flowerLayer.append(group);
      }
      listen(flowerLayer, "focusin", (event) =>
        showFlowerTooltip(event.target),
      );
      listen(flowerLayer, "focusout", hideTooltip);
      listen(flowerLayer, "keydown", (event) => {
        const flower = event.target.closest(".prototype-flower");
        if (!flower) return;
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          event.stopPropagation();
          selectDepartment(
            selected === flower.dataset.department
              ? ""
              : flower.dataset.department,
          );
          showFlowerTooltip(flower);
        } else if (event.key === "Escape") {
          hideTooltip();
          map.focus();
        }
      });
    }
    const offsets = { 75: [0, -20], 92: [-39, 8], 93: [28, -32], 94: [37, 18] };
    for (const group of flowerLayer.children) {
      const department = data.departments.find(
        (item) => item.code === group.dataset.department,
      );
      const [x, north] = department.center,
        [dx, dy] = offsets[department.code] ?? [0, 0];
      group.setAttribute(
        "transform",
        `translate(${x} ${-north}) scale(${currentUnits()})`,
      );
      group
        .querySelector(".prototype-leader")
        .setAttribute("d", `M0 0 L${dx} ${dy}`);
      group
        .querySelector(".flower-marker")
        .setAttribute("transform", `translate(${dx} ${dy})`);
      group.setAttribute("aria-pressed", String(selected === department.code));
    }
  }
  function showFlowerTooltip(target) {
    const lines = describe(target),
      box = target.getBoundingClientRect();
    if (lines) showTooltip(lines, box.left + box.width / 2, box.bottom);
  }
  function appendTooltipFlower() {
    if (!tooltipDepartment) return;
    const box = htmlNode("div", "prototype-tooltip-flower"),
      detail = htmlNode("div");
    detail.append(
      htmlNode(
        "strong",
        "",
        `${tooltipDepartment.nom} (${tooltipDepartment.code})`,
      ),
    );
    for (const petal of flowerPetals(tooltipDepartment, data.metrics, maxima))
      detail.append(
        htmlNode(
          "span",
          "",
          `${petal.metric.name} (${petal.metric.period}) : ${petal.missing ? "non disponible" : metricValue(petal.metric, petal.value)}`,
        ),
      );
    box.append(departmentFlower(tooltipDepartment), detail);
    tooltip.append(box);
  }

  return () => {
    disposed = true;
    mapEngine?.destroy();
    lifecycle.abort();
    clearTimeout(hintTimer);
    hideTooltip();
  };
}
