import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mountExplorer } from '../../app/(graphique-2)/charts/graphique-2/lib/explorer.ts';

test('unmount aborts requests and controls; a late response cannot render', async t => {
  const signals = [];
  let requestSignal;
  let complete;
  let rendered = 0;
  const control = {
    addEventListener(type, handler, options) { signals.push(options.signal); },
    replaceChildren() { rendered++; },
  };
  const root = { querySelector: () => control, querySelectorAll: () => [] };
  const originalFetch = globalThis.fetch;
  t.after(() => { globalThis.fetch = originalFetch; });
  globalThis.fetch = (url, options) => {
    assert.equal(url, '/data/jobseekers-employment-zones.json');
    requestSignal = options.signal;
    return new Promise(resolve => { complete = resolve; });
  };
  const dispose = mountExplorer(root, { setOptions() {}, mapChart() { rendered++; } });
  t.after(dispose);
  assert.equal(requestSignal.aborted, false);
  assert.equal(signals.length, 4);
  dispose();
  assert.equal(requestSignal.aborted, true);
  assert.ok(signals.every(signal => signal.aborted));
  // Deliberately ignore cancellation at the mocked transport boundary.
  complete({ ok: true, json: async () => ({}) });
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(rendered, 0);
});
