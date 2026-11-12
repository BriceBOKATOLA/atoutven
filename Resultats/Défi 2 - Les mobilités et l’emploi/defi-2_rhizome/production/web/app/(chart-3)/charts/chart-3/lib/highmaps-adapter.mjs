import {
  analyse,
  BASE_YEAR,
  densityColor,
  densityKey,
  poleKey,
  petalPath,
  DENSITY_CLASSES,
  MISSING_DENSITY_COLOR,
  geometryPath,
  poleRadius,
  unitsPerPixel,
} from "./geometry.mjs";
import { palette } from "./flowers.mjs";

// The reference SVG remains the accessible interaction surface. Highmaps owns
// the geographical series, while the established flower/label layout stays intact.
export function mapSeries(data) {
  const insights = analyse(data);
  const paths = (lines) =>
    lines.map((line) => ({ path: geometryPath(line.geometry) }));
  const recent = insights.recentLines.map((line) => ({
    path: line.segments
      .map((segment) => geometryPath(segment.geometry))
      .join(" "),
  }));
  return [
    {
      type: "map",
      id: "density",
      data: data.communes.map((commune) => ({
        path: geometryPath(commune.geometry),
        color: densityColor(commune.densite_2025),
        custom: {
          legendKey: densityKey(commune.densite_2025),
          densityColor: densityColor(commune.densite_2025),
        },
      })),
      borderColor: "#fff",
      borderWidth: 0.5,
    },
    {
      type: "map",
      id: "departments",
      data: data.departments.map((department) => ({
        id: `department-${department.code}`,
        path: geometryPath(department.geometry),
        color: "rgba(0,0,0,0)",
      })),
      borderColor: "#d9739f",
      borderWidth: 1.2,
    },
    {
      type: "map",
      id: "selection",
      data: data.departments.map((department) => ({
        id: `selection-${department.code}`,
        path: geometryPath(department.geometry),
        color: "rgba(0,0,0,0)",
      })),
      borderWidth: 0,
    },
    {
      type: "mapline",
      id: "rail-earlier",
      data: paths(data.lines.filter((line) => line.an <= BASE_YEAR)),
      color: "#8b929b",
      lineWidth: 1,
    },
    {
      type: "mapline",
      id: "rail-casing",
      data: recent,
      color: "rgba(255,255,255,.85)",
      lineWidth: 5.5,
    },
    {
      type: "mapline",
      id: "rail-recent",
      data: recent,
      color: "#0e1b2c",
      lineWidth: 2.6,
    },
    {
      type: "mappoint",
      id: "poles",
      data: insights.poles.map((pole) => ({
        id: pole.code,
        x: pole.geometry.coordinates[0],
        y: -pole.geometry.coordinates[1],
        custom: { employment: pole.emploi_2025, legendKey: poleKey(pole) },
        marker: {
          symbol: "circle",
          radius: 0,
          fillColor:
            pole.code === "75056"
              ? "rgba(230,159,0,.14)"
              : pole.change < 0
                ? "#fffefa"
                : "#e69f00",
          lineColor: pole.isNew
            ? "#d55e00"
            : pole.change < 0 || pole.code === "75056"
              ? "#a86f00"
              : "#3d2700",
          lineWidth: pole.isNew
            ? 3
            : pole.code === "75056"
              ? 2.4
              : pole.change < 0
                ? 2.2
                : 1,
        },
      })),
    },
  ].map((series) => ({
    ...series,
    enableMouseTracking: false,
    animation: false,
    dataLabels: { enabled: false },
    turboThreshold: 0,
    states: { inactive: { opacity: 1 } },
  }));
}

export function mountHighmaps(H, frame, overlay, data) {
  const container = document.createElement("div");
  container.className = "reference-highmaps";
  container.setAttribute("aria-hidden", "true");
  frame.insertBefore(container, overlay);
  const surface = document.createElement("div");
  container.append(surface);
  let chart;
  try {
    chart = H.mapChart(surface, {
      chart: {
        backgroundColor: "transparent",
        animation: false,
        spacing: 0,
        margin: 0,
        reflow: false,
      },
      title: { text: undefined },
      legend: { enabled: false },
      credits: { enabled: false },
      accessibility: { enabled: false },
      tooltip: { enabled: false },
      mapNavigation: {
        enabled: false,
        enableMouseWheelZoom: false,
        enableTouchZoom: false,
        enableDoubleClickZoom: false,
      },
      mapView: { padding: 0, projection: { name: undefined } },
      plotOptions: { series: { animation: false } },
      series: mapSeries(data),
    });
  } catch (error) {
    container.remove();
    throw error;
  }
  // The accessible SVG owns map interactions above Highmaps. Keep the credit
  // outside that overlay, using the library's attribution text and destination.
  const credit = document.createElement("a");
  credit.className = "reference-highmaps-credit";
  credit.href = chart.options.credits.href;
  credit.textContent = chart.options.credits.text;
  frame.append(credit);
  frame.classList.add("highmaps-active");
  let lastUnits;
  return {
    render(view, size) {
      if (chart.chartWidth !== size.width || chart.chartHeight !== size.height)
        chart.setSize(size.width, size.height, false);
      const units = unitsPerPixel(view, size.width, size.height);
      // fitToBounds uses precisely the same letterboxed bounds as SVG viewBox.
      chart.mapView.minZoom = -Infinity;
      chart.mapView.fitToBounds(
        {
          x1: view.x,
          y1: view.y,
          x2: view.x + view.width,
          y2: view.y + view.height,
        },
        0,
        false,
        false,
      );
      // The interaction owner already constrains the view to the region.
      // Highmaps would otherwise recenter the padded bounds on its data.
      chart.mapView.center = [
        view.x + view.width / 2,
        view.y + view.height / 2,
      ];
      if (units !== lastUnits) {
        for (const point of chart.get("poles").points)
          point.update(
            {
              marker: {
                ...point.options.marker,
                radius: poleRadius(point.custom.employment, units) / units,
              },
            },
            false,
          );
        lastUnits = units;
      }
      chart.mapView.redraw(false);
    },
    visibility(key, visible) {
      if (key.startsWith("density-") || key.startsWith("poles-")) {
        const series = chart.get(
          key.startsWith("density-") ? "density" : "poles",
        );
        for (const point of series.points)
          if (point.custom.legendKey === key) {
            if (key.startsWith("density-"))
              point.update(
                {
                  color: visible ? point.custom.densityColor : "rgba(0,0,0,0)",
                  borderWidth: visible ? 0.5 : 0,
                },
                false,
              );
            else
              // Point.update replaces marker options. Keep each pole's color,
              // outline and current zoom radius when changing visibility.
              point.update(
                { marker: { ...point.options.marker, enabled: visible } },
                false,
              );
          }
      } else {
        const ids =
          key === "rail-recent" ? ["rail-recent", "rail-casing"] : [key];
        for (const id of ids) chart.get(id)?.setVisible(visible, false);
      }
      chart.redraw(false);
    },
    select(code) {
      for (const point of chart.get("selection").points) {
        const selected = point.id === `selection-${code}`;
        point.update(
          {
            color: selected ? "rgba(23,78,154,.1)" : "rgba(0,0,0,0)",
            borderColor: "#174e9a",
            borderWidth: selected ? 2.5 : 0,
          },
          false,
        );
      }
      chart.redraw(false);
    },
    destroy() {
      chart.destroy();
      credit.remove();
      container.remove();
      frame.classList.remove("highmaps-active");
    },
  };
}

// These charts use Highcharts' native legend renderer outside the geographic
// chart. Its plot must remain exactly aligned with the interactive SVG overlay.
export function mapLegendOptions(
  group,
  onToggle = () => {},
  onRender = () => {},
) {
  const circle = (name, fillColor, lineColor, lineWidth) => ({
    type: "scatter",
    name,
    color: fillColor,
    marker: { symbol: "circle", radius: 6, fillColor, lineColor, lineWidth },
  });
  const line = (name, color, lineWidth) => ({
    type: "line",
    name,
    color,
    lineWidth,
    marker: { enabled: false },
  });
  const groups = {
    density: [
      ...DENSITY_CLASSES,
      { name: "Donnée non disponible", color: MISSING_DENSITY_COLOR },
    ].map(({ name, color }) => ({
      type: "scatter",
      name,
      color,
      legendSymbol: "rectangle",
      marker: { lineColor: "#c9cdd3", lineWidth: 1 },
    })),
    poles: [
      circle("Plus d’emplois qu’en 2015", "#e69f00", "#3d2700", 1),
      circle("Moins d’emplois qu’en 2015", "#fffefa", "#a86f00", 2.2),
      circle("Nouveau pôle depuis 2015", "#e69f00", "#d55e00", 3),
    ],
    network: [
      line("Ligne ouverte depuis 2015", "#0e1b2c", 2.6),
      line("Ligne déjà en service", "#8b929b", 1),
      line("Limite de département", "#d9739f", 1.2),
      circle("Départements", "#344052", "#344052", 1),
    ],
  };
  return {
    chart: {
      backgroundColor: "transparent",
      animation: false,
      spacing: 0,
      margin: 0,
      height: 160,
      events: {
        render() {
          onRender(this);
          // Use the actual wrapped text height, including after a narrow resize.
          const height = Math.ceil(this.legend.legendHeight);
          if (height > 0 && this.chartHeight !== height)
            this.setSize(undefined, height, false);
        },
      },
    },
    title: { text: undefined },
    credits: { enabled: false },
    accessibility: { enabled: false },
    tooltip: { enabled: false },
    xAxis: { visible: false },
    yAxis: { visible: false },
    legend: {
      enabled: true,
      floating: true,
      align: "left",
      verticalAlign: "top",
      layout: "vertical",
      padding: 0,
      margin: 0,
      borderWidth: 0,
      symbolWidth: 22,
      symbolHeight: 12,
      symbolRadius: 0,
      itemMarginTop: 3,
      itemMarginBottom: 4,
      itemStyle: {
        color: "#303b49",
        fontFamily: "Arial, Helvetica, sans-serif",
        fontSize: "13px",
        fontWeight: "normal",
        cursor: "pointer",
        textOverflow: undefined,
      },
      itemHoverStyle: { color: "#303b49" },
      navigation: { enabled: false },
      events: {
        itemClick(event) {
          event.preventDefault();
          const item = event.legendItem;
          if (!item) return;
          const visible = !item.visible;
          onToggle(item.options.id, visible);
          item.setVisible(visible);
        },
      },
    },
    plotOptions: {
      series: {
        animation: false,
        enableMouseTracking: false,
        states: { inactive: { opacity: 1 } },
      },
    },
    series: groups[group].map((series, index) => ({
      id: {
        density: [
          "density-0",
          "density-1",
          "density-2",
          "density-3",
          "density-missing",
        ],
        poles: ["poles-growing", "poles-declining", "poles-new"],
        network: ["rail-recent", "rail-earlier", "departments", "flowers"],
      }[group][index],
      ...series,
      data: [],
      showInLegend: true,
    })),
  };
}

export function mountMapLegends(H, hosts, onToggle) {
  const lifecycle = new AbortController();
  const bound = new WeakSet();
  const unbind = [];
  function preservePoleSymbol(series, visible = series.visible) {
    if (!series.options.id?.startsWith("poles-")) return;
    const { fillColor, lineColor, lineWidth } = series.options.marker;
    // Native colorizeItem replaces both fill and stroke with the hidden color.
    // Keep the hollow/ring category encoding and dim the symbol instead.
    series.legendItem?.symbol?.attr({
      fill: fillColor,
      stroke: lineColor,
      "stroke-width": lineWidth,
      opacity: visible ? 1 : 0.3,
    });
  }
  function decorate(chart) {
    chart.renderer?.boxWrapper.element.removeAttribute("aria-hidden");
    chart.renderer?.boxWrapper.element.setAttribute("role", "group");
    chart.renderTo?.setAttribute("role", "presentation");
    for (const series of chart.series) {
      preservePoleSymbol(series);
      const node = series.legendItem?.group?.element;
      if (!node) continue;
      node.setAttribute("role", "button");
      node.setAttribute("tabindex", "0");
      node.setAttribute("aria-label", series.name);
      node.setAttribute("aria-pressed", String(series.visible));
      node.setAttribute("data-legend-key", series.options.id);
      if (series.options.id === "flowers" && !series.legendItem.flower) {
        series.legendItem.symbol?.hide();
        const flower = chart.renderer.g().add(series.legendItem.group);
        Object.values(palette).forEach((color, index, colors) => {
          chart.renderer
            .path(
              chart.renderer.pathToSegments(
                petalPath(7)
                  .match(/[a-zA-Z]|-?\d*\.?\d+/g)
                  .map((part) =>
                    Number.isNaN(Number(part)) ? part : Number(part),
                  ),
              ),
            )
            .attr({
              fill: color,
              stroke: "#fffefa",
              "stroke-width": 0.5,
              rotation: (index * 360) / colors.length,
              translateX: 11,
              translateY: chart.legend.baseline - 4,
            })
            .add(flower);
        });
        series.legendItem.flower = flower;
      }
      series.legendItem.flower?.attr({ opacity: series.visible ? 1 : 0.3 });
      if (bound.has(node)) continue;
      bound.add(node);
      node.addEventListener(
        "keydown",
        (event) => {
          if (event.key !== "Enter" && event.key !== " ") return;
          event.preventDefault();
          if (!event.repeat)
            node.dispatchEvent(new MouseEvent("click", { bubbles: true }));
        },
        { signal: lifecycle.signal },
      );
    }
  }
  const charts = [];
  try {
    for (const [group, host] of Object.entries(hosts)) {
      const options = mapLegendOptions(group, onToggle, decorate);
      host.setAttribute("role", "group");
      host.setAttribute(
        "aria-label",
        options.series.map((series) => series.name).join(" ; "),
      );
      // The accessibility module may rewrite the chart's renderTo attributes.
      // Keep the accessible name on a wrapper that Highcharts does not own.
      const surface = host.ownerDocument.createElement("div");
      surface.setAttribute("role", "presentation");
      const container = host.ownerDocument.createElement("div");
      surface.append(container);
      host.replaceChildren(surface);
      const chart = H.chart(container, options);
      charts.push(chart);
      if (chart.series) decorate(chart);
      if (H.addEvent) {
        unbind.push(
          H.addEvent(chart.legend, "afterColorizeItem", ({ item, visible }) => {
            preservePoleSymbol(item, visible);
          }),
        );
        unbind.push(
          H.addEvent(
            chart,
            "render",
            function () {
              decorate(this);
            },
            { order: 100 },
          ),
        );
      }
    }
  } catch (error) {
    lifecycle.abort();
    for (const remove of unbind) remove();
    for (const chart of charts) chart.destroy();
    throw error;
  }
  return {
    destroy() {
      lifecycle.abort();
      for (const remove of unbind) remove();
      for (const chart of charts) chart.destroy();
    },
  };
}
