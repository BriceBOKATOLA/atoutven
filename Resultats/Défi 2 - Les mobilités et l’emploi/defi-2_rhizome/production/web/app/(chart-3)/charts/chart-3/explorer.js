"use client";
import { useEffect, useRef } from "react";
import data from "../../../../public/data/employment-centers-departments.json";
import { chartMarkup } from "../../../../lib/chart-markup.mjs";
import "./styles.css";
import { referenceMarkup } from "./lib/reference-markup.mjs";
import { loadVendors } from "../../../../lib/highmaps";
import { initializeReference } from "./lib/reference-engine.mjs";

const markup = chartMarkup(referenceMarkup, "g3-");

export default function Explorer() {
  const root = useRef(null);
  useEffect(
    () =>
      initializeReference(root.current, data, { loadHighmaps: loadVendors }),
    [],
  );
  return (
    <div className="chart-frame">
      <div
        className="chart-three"
        ref={root}
        data-chart-prefix="g3-"
        dangerouslySetInnerHTML={{ __html: markup }}
      />
    </div>
  );
}
