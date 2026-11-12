// Build an offline browser fixture from the real modules, dataset and npm engine.
// This avoids substituting Highmaps with a mock when a local HTTP server is denied.
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { referenceMarkup } from '../../app/(graphique-3)/charts/graphique-3/lib/reference-markup.mjs';
import { chartMarkup } from '../../lib/chart-markup.mjs';
const base = new URL('../../app/(graphique-3)/charts/graphique-3/', import.meta.url);
export async function browserFixture() {
  const read = name => readFile(new URL(name, base), 'utf8');
  const modules = await Promise.all(['geometry', 'flowers', 'highmaps-adapter', 'reference-engine'].map(async name =>
    (await read(`lib/${name}.mjs`)).replace(/^import .*;\n/gm, '').replace(/^export /gm, '')));
  const highmaps = await readFile(new URL('../../node_modules/highcharts/highmaps.js', import.meta.url), 'utf8');
  const sharedStyles = await readFile(new URL('../../app/sources.css', import.meta.url), 'utf8');
  const styles = (await read('styles.css')).replace(/^@import\s+["'][^"']*sources\.css["'];\s*/, '');
  return `<!doctype html><meta charset="utf-8"><style>${sharedStyles}\n${styles}</style><div class="chart-frame"><div class="chart-three" id="root" data-chart-prefix="g3-">${chartMarkup(referenceMarkup, 'g3-')}</div></div><script>${highmaps}</script><script>${modules.join('\n')}\nwindow.cleanup=initializeReference(document.querySelector('#root'),${await readFile(new URL('../../public/data/employment-centers-departments.json', import.meta.url), 'utf8')},{loadHighmaps:async()=>Highcharts});</script>`;
}
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const destination = new URL('../../.playwright-mcp/g3-browser.js', import.meta.url);
  await mkdir(new URL('.', destination), {recursive: true});
  await writeFile(destination, `async (page) => {await page.route('https://graphique3.test/**',route=>route.fulfill({contentType:'text/html',body:${JSON.stringify(await browserFixture())}})); await page.goto('https://graphique3.test/'); await page.waitForFunction(()=>document.querySelector('#g3-load-status')?.hidden); return 'Graphique 3 chargé avec Highmaps npm';}`);
  console.log(fileURLToPath(destination));
}
