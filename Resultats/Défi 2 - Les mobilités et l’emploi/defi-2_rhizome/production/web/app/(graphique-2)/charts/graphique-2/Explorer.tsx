'use client';

import { useEffect, useRef, useState } from 'react';
import { mountExplorer } from './lib/explorer';
import { shell } from './lib/shell';
import { chartMarkup } from '../../../../lib/chart-markup.mjs';
import { loadVendors } from './lib/vendors';
import './globals.css';

const markup = chartMarkup(shell, 'g2-');

export default function Explorer() {
  const root = useRef<HTMLDivElement>(null);
  const [attempt, setAttempt] = useState(0);
  const [vendorError, setVendorError] = useState(false);

  useEffect(() => {
    const container = root.current!;
    // React owns this boundary; the legacy renderer owns all its descendants.
    // Restore a clean shell for Strict Mode, retries and future route remounts.
    container.innerHTML = markup;
    let active = true;
    let dispose: (() => void) | undefined;
    loadVendors().then(highmaps => {
      if (!active) return;
      // The legacy renderer uses a narrow, local description of the Highmaps API.
      dispose = mountExplorer(container, highmaps as unknown as Parameters<typeof mountExplorer>[1]);
    }).catch(() => {
      if (active) setVendorError(true);
    });
    return () => { active = false; dispose?.(); };
  }, [attempt]);

  return <div className="chart-frame"><div className="chart-two">
    {vendorError && <div className="vendor-error" role="alert">
      <p>Le moteur de la carte ne peut pas être chargé.</p>
      <button type="button" onClick={() => { setVendorError(false); setAttempt(value => value + 1); }}>Réessayer</button>
    </div>}
    <div ref={root} data-chart-prefix="g2-" dangerouslySetInnerHTML={{ __html: markup }} />
  </div></div>;
}
