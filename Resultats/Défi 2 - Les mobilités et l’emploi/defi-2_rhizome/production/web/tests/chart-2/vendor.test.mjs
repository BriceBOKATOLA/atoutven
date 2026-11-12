import { test } from "node:test";
import { execFileSync } from "node:child_process";

const loader = new URL(
  "../../app/(chart-2)/charts/chart-2/lib/vendors.ts",
  import.meta.url,
).href;

function isolated(source) {
  execFileSync(process.execPath, ["--input-type=module", "-e", source], {
    cwd: new URL("../../", import.meta.url),
    stdio: "pipe",
  });
}

test("npm loading is deferred during SSR and concurrent mounts receive the same accessible engine", () => {
  isolated(`
    import assert from 'node:assert/strict';
    const { loadVendors } = await import(${JSON.stringify(loader)});
    await assert.rejects(loadVendors(), /browser/i);
    globalThis.window = { navigator: { userAgent: '' } };
    const first = loadVendors();
    assert.equal(loadVendors(), first);
    const H = await first;
    assert.equal(H.version, '13.1.1');
    assert.equal(typeof H.mapChart, 'function');
    assert.equal(typeof H.AccessibilityComponent, 'function');
    assert.equal(await loadVendors(), H);
  `);
});

test("a failed accessibility import can be retried without replacing the npm map engine", () => {
  isolated(`
    import assert from 'node:assert/strict';
    import { registerHooks } from 'node:module';
    globalThis.window = { navigator: { userAgent: '' } };
    const { loadVendors } = await import(${JSON.stringify(loader)});
    const hooks = registerHooks({ resolve(specifier, context, next) {
      if (specifier === 'highcharts/modules/accessibility.js') throw new Error('temporary accessibility failure');
      return next(specifier, context);
    } });
    await assert.rejects(loadVendors(), /temporary accessibility failure/);
    hooks.deregister();
    const H = await loadVendors();
    assert.equal(H, (await import('highcharts/highmaps.js')).default);
    assert.equal(typeof H.AccessibilityComponent, 'function');
  `);
});

for (const networkFirst of [false, true]) {
  test(`both maps share npm Highmaps with accessibility when ${networkFirst ? "network" : "explorer"} loads first`, () => {
    isolated(`
      import assert from 'node:assert/strict';
      globalThis.window = { navigator: { userAgent: '' } };
      const { loadVendors } = await import(${JSON.stringify(loader)});
      let network, explorer;
      async function loadNetwork() {
        network = (await import('highcharts/highmaps.js')).default;
        await import('highcharts/modules/accessibility.js');
      }
      ${networkFirst ? "await loadNetwork(); explorer = await loadVendors();" : "explorer = await loadVendors(); await loadNetwork();"}
      assert.equal(explorer, network);
      assert.equal(typeof network.AccessibilityComponent, 'function');
      assert.equal(window.Highcharts, undefined, 'no global script engine is installed');
    `);
  });
}
