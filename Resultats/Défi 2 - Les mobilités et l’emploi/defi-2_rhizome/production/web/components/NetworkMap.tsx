"use client";

import { useEffect, useRef, useState } from "react";
import type Highcharts from "highcharts/highmaps";
import { loadVendors } from "../lib/highmaps";
import { bindMapNavigation } from "../lib/map-navigation.mjs";

type MapPath = { name: string; path: string };
type MapPoint = {
  name: string;
  x: number;
  y: number;
  line?: string;
  year?: number;
};
type Period = {
  name: string;
  color: string;
  openings: { line: string; year: number }[];
  tracks: MapPath[];
  stations: MapPoint[];
};
type NetworkData = {
  summary: { lines: number; stations: number; kilometres: number };
  communes: MapPath[];
  paris: MapPath[];
  departments: MapPath[];
  existing: MapPath[];
  periods: Period[];
  labels: MapPoint[];
  termini: MapPoint[];
  departmentLabels: MapPoint[];
};

function createOptions(data: NetworkData): Highcharts.Options {
  const periodSymbols = ["circle", "square", "diamond"] as const;
  const periodDashes: Highcharts.DashStyleValue[] = [
    "Solid",
    "ShortDash",
    "ShortDot",
  ];
  const mapLayer = (
    name: string,
    shapes: MapPath[],
    color: string,
    borderColor: string,
    borderWidth: number,
  ): Highcharts.SeriesMapOptions => ({
    type: "map",
    name,
    mapData: shapes,
    data: shapes.map(() => 1),
    joinBy: "_i",
    color,
    nullColor: color,
    borderColor,
    borderWidth,
    enableMouseTracking: false,
    showInLegend: false,
    accessibility: { enabled: false },
    states: { inactive: { opacity: 1 }, hover: { enabled: false } },
  });
  const lineLayer = (
    name: string,
    shapes: MapPath[],
    color: string,
    lineWidth: number,
    interactive = false,
    dashStyle: Highcharts.DashStyleValue = "Solid",
  ): Highcharts.SeriesMaplineOptions => ({
    type: "mapline",
    name,
    mapData: shapes,
    data: shapes.map(() => 1),
    joinBy: "_i",
    color,
    lineWidth,
    dashStyle,
    enableMouseTracking: interactive,
    showInLegend: false,
    accessibility: { enabled: false },
    states: { inactive: { opacity: 1 }, hover: { lineWidthPlus: 1 } },
    tooltip: { pointFormat: "{point.name}" },
  });
  const labelLayer = (
    name: string,
    points: MapPoint[],
    color: string,
    size: string,
    backgroundColor?: string,
    alwaysShow = false,
  ): Highcharts.SeriesMappointOptions => ({
    type: "mappoint",
    name,
    data: points.map((point) => ({
      ...point,
      labelrank: backgroundColor ? 2 : 1,
    })),
    enableMouseTracking: false,
    showInLegend: false,
    marker: { enabled: false },
    accessibility: { enabled: false },
    dataLabels: {
      enabled: true,
      format: "{point.name}",
      padding: backgroundColor ? 2 : 0,
      backgroundColor,
      borderRadius: 0,
      allowOverlap: alwaysShow,
      style: {
        color,
        fontSize: size,
        fontWeight: backgroundColor ? "bold" : "normal",
        textOutline: backgroundColor ? "none" : "2px #F1EFEA",
      },
    },
  });
  return {
    chart: {
      backgroundColor: "#F1EFEA",
      spacing: [8, 8, 8, 8],
      animation: false,
      style: { fontFamily: "Arial, Helvetica, sans-serif" },
    },
    title: { text: undefined },
    credits: { enabled: true, style: { fontSize: "12px", color: "#526071" } },
    legend: {
      enabled: true,
      align: "center",
      verticalAlign: "bottom",
      layout: "vertical",
      width: "90%",
      padding: 12,
      margin: 24,
      symbolWidth: 36,
      symbolPadding: 12,
      itemMarginTop: 6,
      itemMarginBottom: 6,
      events: {
        itemClick(event) {
          const series = event.legendItem;
          if ("linkedParent" in series && series.linkedParent) {
            // A station legend item controls its whole opening period too.
            event.preventDefault();
            series.linkedParent.setVisible();
          }
        },
      },
      title: {
        text: "Périodes et repères",
        style: { color: "#0E1B2C", fontSize: "14px", fontWeight: "bold" },
      },
      itemStyle: {
        color: "#344052",
        fontSize: "14px",
        fontWeight: "normal",
        textOverflow: undefined,
      },
      itemHoverStyle: { color: "#0E1B2C" },
      itemHiddenStyle: { color: "#526071", textDecoration: "line-through" },
    },
    mapView: { padding: 0 },
    mapNavigation: {
      enabled: true,
      enableButtons: false,
      enableMouseWheelZoom: true,
      enableDoubleClickZoom: false,
    },
    lang: { zoomIn: "Agrandir la carte", zoomOut: "Réduire la carte" },
    accessibility: {
      description: `Extensions du réseau ferré francilien entre 2015 et 2025. ${data.summary.lines} lignes créées ou prolongées, ${data.summary.stations} gares ouvertes et ${data.summary.kilometres} kilomètres de voies nouvelles. Les couleurs indiquent les périodes d’ouverture. Les tronçons du prolongement du métro 11 sont présents dans la source mais sans date : ils sont exclus de cette carte et du total ; ses gares de 2024 figurent.`,
      landmarkVerbosity: "one",
      keyboardNavigation: { enabled: true },
      point: {
        valueDescriptionFormat:
          "{point.name}, {point.line}, ouverture en {point.year}.",
      },
    },
    tooltip: {
      useHTML: false,
      headerFormat: "",
      pointFormat: "<b>{point.name}</b><br/>{point.line} — {point.year}",
      animation: false,
    },
    plotOptions: {
      series: { animation: false, states: { inactive: { opacity: 1 } } },
    },
    series: [
      mapLayer("Communes", data.communes, "#E3E4DF", "#FFFFFF", 0.35),
      mapLayer("Paris", data.paris, "#D4D9D4", "#FFFFFF", 0.35),
      {
        ...lineLayer("Limite départementale", data.departments, "#D9739F", 0.8),
        showInLegend: true,
        legendIndex: 7,
      },
      {
        ...lineLayer("Réseau existant avant 2015", data.existing, "#8B929B", 1),
        showInLegend: true,
        legendIndex: 6,
      },
      ...data.periods.flatMap((period, index) => {
        const openings: Highcharts.SeriesMaplineOptions = {
          ...lineLayer(
            `${period.name} : ${period.openings
              .map((opening) => `${opening.line} (${opening.year})`)
              .join(", ")}`,
            period.tracks,
            period.color,
            2.6,
            true,
            periodDashes[index],
          ),
          id: `network-period-${index}`,
          showInLegend: true,
          legendIndex: index * 2,
        };
        return [
          {
            ...lineLayer(`Contour ${period.name}`, period.tracks, "#FFFFFF", 5),
            linkedTo: openings.id,
          },
          openings,
        ];
      }),
      ...data.periods.map(
        (
          period,
          index,
        ): Highcharts.SeriesMappointOptions & { linkedTo: string } => ({
          type: "mappoint",
          name: `Gares ouvertes en ${period.name}`,
          linkedTo: `network-period-${index}`,
          data: period.stations,
          color: period.color,
          showInLegend: true,
          legendIndex: index * 2 + 1,
          marker: {
            radius: 2.8,
            lineWidth: 1.4,
            lineColor: period.color,
            fillColor: "#FFFFFF",
            symbol: periodSymbols[index],
          },
          dataLabels: { enabled: false },
          accessibility: {
            point: {
              valueDescriptionFormat:
                "{point.name}, {point.line}, ouverture en {point.year}.",
            },
          },
        }),
      ),
      mapLayer(
        "Nord",
        [
          {
            name: "Nord",
            path: "M 69.5 -57.2 L 69.9 -55.4 L 71.7 -55 L 69.9 -54.6 L 69.5 -52.8 L 69.1 -54.6 L 67.3 -55 L 69.1 -55.4 Z",
          },
        ],
        "#0E1B2C",
        "#0E1B2C",
        0,
      ),
      lineLayer(
        "Échelle 0 à 2,5 km",
        [{ name: "", path: "M 2.5 -2.2 L 5 -2.2" }],
        "#0E1B2C",
        4,
      ),
      lineLayer(
        "Échelle 2,5 à 5 km",
        [{ name: "", path: "M 5 -2.2 L 7.5 -2.2" }],
        "#6B7280",
        4,
      ),
      labelLayer(
        "Orientation et échelle",
        [
          { name: "N", x: 69.5, y: -58 },
          { name: "0", x: 2.5, y: -3 },
          { name: "2,5", x: 5, y: -3 },
          { name: "5 km", x: 7.5, y: -3 },
        ],
        "#0E1B2C",
        "12px",
        undefined,
        true,
      ),
      labelLayer("Départements", data.departmentLabels, "#526071", "12px"),
      labelLayer(
        "Terminus des nouvelles sections",
        data.termini,
        "#344052",
        "12px",
      ),
      labelLayer(
        "Lignes et années d’ouverture",
        data.labels,
        "#0E1B2C",
        "12px",
        "#FFFEFA",
      ),
    ],
  };
}

export function NetworkMap() {
  const container = useRef<HTMLDivElement>(null);
  const chart = useRef<Highcharts.MapChart | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  const [attempt, setAttempt] = useState(0);
  const [data, setData] = useState<NetworkData | null>(null);

  useEffect(() => {
    let disposed = false;
    const controller = new AbortController();
    let disposeNavigation: (() => void) | undefined;
    async function initialize() {
      try {
        const [network, highchartsModule] = await Promise.all([
          fetch("/data/rail-network.json", { signal: controller.signal }).then(
            async (response) => {
              if (!response.ok) throw new Error("Network map data unavailable");
              const network: NetworkData = await response.json();
              if (!disposed) setData(network);
              return network;
            },
          ),
          loadVendors(),
        ]);
        if (disposed || !container.current) return;
        chart.current = highchartsModule.mapChart(
          container.current,
          createOptions(network),
        );
        disposeNavigation = bindMapNavigation(
          container.current.parentElement!,
          chart.current,
        );
        setState("ready");
      } catch {
        if (!disposed) setState("error");
      }
    }
    void initialize();
    return () => {
      disposed = true;
      controller.abort();
      disposeNavigation?.();
      chart.current?.destroy();
      chart.current = null;
    };
  }, [attempt]);

  return (
    <figure
      className="visualization network-visualization"
      aria-labelledby="network-map-title"
    >
      <figcaption className="visualization-caption">
        <h3 id="network-map-title">Dix ans d’extension du réseau ferré</h3>
        <span>2015 — 2025</span>
      </figcaption>
      <div className="network-atlas">
        <div className="network-map-area">
          <div
            className={`network-map-canvas${state !== "ready" ? " network-map-pending" : ""}`}
            ref={container}
            aria-hidden={state !== "ready"}
          />
          <p
            className={`network-map-status${state === "ready" ? " network-map-status-ready" : ""}`}
            role="status"
            aria-live="polite"
            aria-atomic="true"
          >
            {state === "loading" ? (
              "Chargement de la carte interactive…"
            ) : state === "error" ? (
              <>
                La carte interactive n’a pas pu être chargée. Vérifiez votre
                connexion, puis réessayez.{" "}
                <button
                  type="button"
                  onClick={() => {
                    setState("loading");
                    setAttempt((value) => value + 1);
                  }}
                >
                  Réessayer
                </button>
              </>
            ) : (
              "Carte interactive chargée."
            )}
          </p>
        </div>
        {data && (
          <>
            <aside
              className="network-map-key"
              aria-label="Chiffres clés du réseau"
            >
              <h4>Le réseau de 2015 à 2025</h4>
              <dl className="network-map-stats">
                <div>
                  <dt>{data.summary.lines}</dt>
                  <dd>
                    lignes créées
                    <br />
                    ou prolongées
                  </dd>
                </div>
                <div>
                  <dt>{data.summary.stations}</dt>
                  <dd>
                    gares
                    <br />
                    ouvertes
                  </dd>
                </div>
                <div>
                  <dt>{data.summary.kilometres} km</dt>
                  <dd>
                    de voies
                    <br />
                    nouvelles
                  </dd>
                </div>
              </dl>
              <p className="network-key-note">
                La plupart des nouvelles lignes desservent la petite couronne,
                où se concentrent les emplois.
              </p>
            </aside>
          </>
        )}
      </div>
      <div
        className="chart-sources network-map-sources"
        role="group"
        aria-labelledby="network-sources-title"
      >
        <h4 id="network-sources-title">Sources et notes</h4>
        <p>
          <a href="/data/LICENCES.txt">
            Conditions de réutilisation des données
          </a>
        </p>
        <div className="sources-grid">
          <div className="source-group">
            <p>
              <strong>Île-de-France Mobilités.</strong>{" "}
              <a href="https://data.iledefrance-mobilites.fr/explore/dataset/traces-du-reseau-ferre-idf/">
                Tracés du réseau ferré
              </a>{" "}
              et{" "}
              <a href="https://data.iledefrance-mobilites.fr/explore/dataset/emplacement-des-gares-idf/">
                gares par ligne
              </a>
              . Données sous{" "}
              <a href="https://github.com/etalab/licence-ouverte/blob/master/LO.md">
                Licence Ouverte 2.0
              </a>
              .
            </p>
            <p>
              <strong>Fonds de carte.</strong> La documentation de l’équipe cite{" "}
              <a href="https://github.com/gregoiredavid/france-geojson">
                France GeoJSON
              </a>{" "}
              (tracés IGN Admin Express COG et codes Insee, édition 2018).
              L’extraction et les transformations initiales des copies locales
              ne sont pas documentées. La provenance et la licence des copies
              locales restent à confirmer.
            </p>
          </div>
          <div className="source-group">
            <p>
              <strong>Notes de lecture.</strong> Les tronçons du prolongement du
              métro 11 sont présents dans la source mais sans date : ils sont
              exclus de cette carte et du total ; ses gares de 2024 figurent.
            </p>
            <p>
              Le T14, renommé en 2025, reprend une ligne ancienne entre Esbly et
              Crécy-la-Chapelle : il figure dans le réseau existant et ne compte
              pas parmi les ouvertures.
            </p>
          </div>
        </div>
      </div>
      <noscript>
        <p className="visualization-description">
          JavaScript est nécessaire pour afficher la carte, ses chiffres clés et
          sa légende.
        </p>
      </noscript>
    </figure>
  );
}
