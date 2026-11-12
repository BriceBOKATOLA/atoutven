// `node tests/chart-3/pole-legend.browser.mjs` builds a Playwright runner in
// .playwright-mcp/check-pole-legend.js. Execute that file with browser_run_code.
// No chart/renderer mocks: native Highcharts hover, visibility and redraw run here.
import { mkdir, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { browserFixture } from "./browser-fixture.mjs";

export async function checkPoleLegend(page, touch = false) {
  const expected = [
    ["poles-growing", "#e69f00", "#3d2700", "1"],
    ["poles-declining", "#fffefa", "#a86f00", "2.2"],
    ["poles-new", "#e69f00", "#d55e00", "3"],
  ];
  const results = [];
  // Inspect the visible Highmaps points, not only the transparent SVG hit areas.
  async function mapAppearance(key) {
    return page.evaluate((key) => {
      const chart = Highcharts.charts.find((chart) => chart?.get("poles"));
      return chart
        .get("poles")
        .points.filter((point) => point.custom.legendKey === key)
        .map((point) => {
          const node = point.graphic?.element;
          const style = node && getComputedStyle(node);
          return {
            id: point.id,
            marker: { ...point.options.marker, enabled: undefined },
            attributes:
              node &&
              Object.fromEntries(
                ["d", "fill", "stroke", "stroke-width", "opacity"].map(
                  (name) => [name, node.getAttribute(name)],
                ),
              ),
            styles: style && {
              fill: style.fill,
              stroke: style.stroke,
              strokeWidth: style.strokeWidth,
              opacity: style.opacity,
              display: style.display,
              visibility: style.visibility,
            },
          };
        });
    }, key);
  }
  const baselines = new Map();
  for (const [key] of expected) baselines.set(key, await mapAppearance(key));
  async function check(key, fill, stroke, width, visible, phase) {
    const actual = await page
      .locator(`.native-map-legend [data-legend-key="${key}"]`)
      .evaluate((node) => {
        const symbol = node.querySelector(".highcharts-point");
        return {
          fill: symbol.getAttribute("fill"),
          stroke: symbol.getAttribute("stroke"),
          width: symbol.getAttribute("stroke-width"),
          opacity: Number(getComputedStyle(symbol).opacity),
          pressed: node.getAttribute("aria-pressed"),
          struck: getComputedStyle(node.querySelector("text"))
            .textDecorationLine,
        };
      });
    if (
      actual.fill !== fill ||
      actual.stroke !== stroke ||
      actual.width !== width ||
      actual.pressed !== String(visible) ||
      (visible ? actual.opacity !== 1 : actual.opacity >= 1) ||
      (!visible && !actual.struck.includes("line-through"))
    )
      throw new Error(`${key} ${phase}: ${JSON.stringify(actual)}`);
    const hiddenMapSymbols = await page
      .locator(`#g3-map .pole-symbol[data-legend-key="${key}"]`)
      .evaluateAll(
        (nodes) =>
          nodes.filter((node) => getComputedStyle(node).display === "none")
            .length,
      );
    if (visible ? hiddenMapSymbols !== 0 : hiddenMapSymbols === 0)
      throw new Error(`${key} ${phase}: map visibility disagrees`);
    if (!visible) {
      const rendered = await page.evaluate(
        (key) =>
          Highcharts.charts
            .find((chart) => chart?.get("poles"))
            .get("poles")
            .points.filter((point) => point.custom.legendKey === key)
            .some(
              (point) =>
                point.graphic &&
                getComputedStyle(point.graphic.element).display !== "none" &&
                getComputedStyle(point.graphic.element).visibility !== "hidden",
            ),
        key,
      );
      if (rendered)
        throw new Error(`${key} ${phase}: Highmaps still draws hidden poles`);
    }
    if (visible) {
      const actualMap = await mapAppearance(key);
      const baseline = baselines.get(key);
      const changed = actualMap.findIndex(
        (point, index) =>
          JSON.stringify(point) !== JSON.stringify(baseline[index]),
      );
      if (changed !== -1)
        throw new Error(
          `${key} ${phase}: rendered map marker changed: ${JSON.stringify({ before: baseline[changed], after: actualMap[changed] })}`,
        );
    }
    results.push(`${key}: ${phase}`);
  }
  for (const [key, fill, stroke, width] of expected) {
    const item = page.locator(`.native-map-legend [data-legend-key="${key}"]`);
    const verify = (visible, phase) =>
      check(key, fill, stroke, width, visible, phase);
    await verify(true, "initial");
    if (!touch) {
      await item.hover();
      await verify(true, "hover");
    }
    await (touch ? item.tap() : item.click());
    await verify(false, "click hide");
    await page.evaluate((key) => {
      const chart = window.Highcharts.charts.find((chart) =>
        chart?.series.some((series) => series.options.id === key),
      );
      const series = chart.get(key);
      chart.legend.colorizeItem(series, false);
    }, key);
    await verify(false, "native recolor");
    await page.evaluate((key) => {
      const chart = window.Highcharts.charts.find((chart) =>
        chart?.series.some((series) => series.options.id === key),
      );
      chart.isDirtyLegend = true;
      chart.redraw(false);
    }, key);
    await verify(false, "redraw");
    await page.locator("h1").hover();
    await verify(false, "mouseout");
    await item.focus();
    await item.press("Enter");
    await verify(true, "Enter restore");
    await item.press("Space");
    await verify(false, "Space hide");
    await item.press("Space");
    await verify(true, "Space restore");
  }
  // Keep a department selection and another filter active during pole toggles.
  const paris = page.locator('#g3-map .pole-symbol[data-commune="75056"]');
  await paris.focus();
  await paris.press("Enter");
  await page
    .locator('.native-map-legend [data-legend-key="density-0"]')
    .click();
  const selection = await page.locator("#g3-selection-text").textContent();
  for (const [key, fill, stroke, width] of expected) {
    const item = page.locator(`.native-map-legend [data-legend-key="${key}"]`);
    await item.press("Enter");
    await page.locator("#g3-map").press("+");
    await page.evaluate(() => new Promise(requestAnimationFrame));
    await check(key, fill, stroke, width, false, "zoom while hidden");
    const enabled = await page.evaluate(
      (key) =>
        Highcharts.charts
          .find((chart) => chart?.get("poles"))
          .get("poles")
          .points.filter((point) => point.custom.legendKey === key)
          .some((point) => point.options.marker.enabled !== false),
      key,
    );
    if (enabled) throw new Error(`${key}: zoom reenabled hidden markers`);
    await page.locator("#g3-map").press("0");
    await page.evaluate(() => new Promise(requestAnimationFrame));
    await item.press("Enter");
    await check(
      key,
      fill,
      stroke,
      width,
      true,
      "reset while hidden then restore",
    );
    await page.locator("#g3-map").press("+");
    await page.evaluate(() => new Promise(requestAnimationFrame));
    baselines.set(key, await mapAppearance(key));
    await item.press("Enter");
    await item.press("Enter");
    await check(key, fill, stroke, width, true, "restore while zoomed");
    await page.locator("#g3-map").press("0");
    await page.evaluate(() => new Promise(requestAnimationFrame));
    baselines.set(key, await mapAppearance(key));
    if (
      (await page.locator("#g3-selection-text").textContent()) !== selection ||
      (await page
        .locator('.native-map-legend [data-legend-key="density-0"]')
        .getAttribute("aria-pressed")) !== "false"
    )
      throw new Error(`${key}: another filter or selection changed`);
  }
  return results;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const destination = new URL(
    "../../.playwright-mcp/check-pole-legend.js",
    import.meta.url,
  );
  await mkdir(new URL(".", destination), { recursive: true });
  const html = await browserFixture();
  await writeFile(
    destination,
    `async page => {
      await page.route('https://pole-legend.test/**', route => route.fulfill({
        contentType: 'text/html', body: ${JSON.stringify(html)}
      }));
      await page.goto('https://pole-legend.test/');
      await page.waitForFunction(() => document.querySelector('#g3-load-status')?.hidden);
      const check = ${checkPoleLegend.toString()};
      const desktop = await check(page);
      const context = await page.context().browser().newContext({
        hasTouch: true, viewport: { width: 390, height: 844 }
      });
      try {
        const mobile = await context.newPage();
        await mobile.route('https://pole-legend.test/**', route => route.fulfill({
          contentType: 'text/html', body: ${JSON.stringify(html)}
        }));
        await mobile.goto('https://pole-legend.test/');
        await mobile.waitForFunction(() => document.querySelector('#g3-load-status')?.hidden);
        return { desktop, touch: await check(mobile, true) };
      } finally { await context.close(); }
    }`,
  );
  console.log(fileURLToPath(destination));
}
