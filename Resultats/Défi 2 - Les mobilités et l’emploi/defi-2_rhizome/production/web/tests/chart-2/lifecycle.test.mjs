import { test } from "node:test";
import assert from "node:assert/strict";
import { mountExplorer } from "../../app/(chart-2)/charts/chart-2/lib/explorer.ts";

test("unmount aborts requests and controls; a late response cannot render", async (t) => {
  const signals = [];
  let requestSignal;
  let complete;
  let rendered = 0;
  let handledChanges = 0;
  const control = new (class extends EventTarget {
    style = { setProperty() {} };
    addEventListener(type, handler, options) {
      assert.ok(["change", "mouseenter", "mouseleave"].includes(type));
      signals.push(options.signal);
      super.addEventListener(
        type,
        (event) => {
          handledChanges++;
          handler(event);
        },
        options,
      );
    }
    replaceChildren() {
      rendered++;
    }
  })();
  const root = { querySelector: () => control, querySelectorAll: () => [] };
  const originalFetch = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = originalFetch;
  });
  globalThis.fetch = (url, options) => {
    assert.equal(url, "/data/jobseekers-employment-zones.json");
    requestSignal = options.signal;
    return new Promise((resolve) => {
      complete = resolve;
    });
  };
  const dispose = mountExplorer(root, {
    setOptions() {},
    mapChart() {
      rendered++;
    },
  });
  t.after(dispose);
  assert.equal(requestSignal.aborted, false);
  assert.ok(signals.length > 0, "the zone control has an abortable listener");
  assert.ok(signals.every((signal) => !signal.aborted));
  dispose();
  assert.equal(requestSignal.aborted, true);
  assert.ok(signals.every((signal) => signal.aborted));
  control.dispatchEvent(new Event("change"));
  assert.equal(handledChanges, 0);
  // Deliberately ignore cancellation at the mocked transport boundary.
  complete({ ok: true, json: async () => ({}) });
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(rendered, 0);
});
