// Offline browser fixture: real production modules, data and installed Highmaps.
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import ts from "typescript";
import { shell } from "../../app/(chart-2)/charts/chart-2/lib/shell.ts";
import { chartMarkup } from "../../lib/chart-markup.mjs";

const base = new URL("../../app/(chart-2)/charts/chart-2/", import.meta.url);
export async function browserFixture() {
  const read = (name) => readFile(new URL(name, base), "utf8");
  const modules = await Promise.all(
    [
      "../../../../../lib/map-navigation.mjs",
      "geometry.mjs",
      "map-model.mjs",
      "evolution-scale.mjs",
      "explorer.ts",
    ].map(async (name) => {
      let source = await read(`lib/${name}`);
      const parsed = ts.createSourceFile(name, source, ts.ScriptTarget.Latest);
      const removals = parsed.statements.flatMap((statement) =>
        ts.isImportDeclaration(statement)
          ? [statement]
          : (ts.getModifiers(statement) ?? []).filter(
              (modifier) => modifier.kind === ts.SyntaxKind.ExportKeyword,
            ),
      );
      for (const node of removals.reverse()) {
        source =
          source.slice(0, node.getStart(parsed)) + source.slice(node.end);
      }
      return ts.transpileModule(source, {
        compilerOptions: {
          target: ts.ScriptTarget.ES2022,
          module: ts.ModuleKind.None,
        },
      }).outputText;
    }),
  );
  const highmaps = await readFile(
    new URL("../../node_modules/highcharts/highmaps.js", import.meta.url),
    "utf8",
  );
  const accessibility = await readFile(
    new URL(
      "../../node_modules/highcharts/modules/accessibility.js",
      import.meta.url,
    ),
    "utf8",
  );
  const sharedStyles = await readFile(
    new URL("../../app/sources.css", import.meta.url),
    "utf8",
  );
  const styles = (await read("globals.css")).replace(
    /^@import\s+["'][^"']*sources\.css["'];\s*/,
    "",
  );
  const data = await readFile(
    new URL(
      "../../public/data/jobseekers-employment-zones.json",
      import.meta.url,
    ),
    "utf8",
  );
  return `<!doctype html><meta charset="utf-8"><style>${sharedStyles}\n${styles}</style><div class="chart-frame"><div class="chart-two" id="root" data-chart-prefix="g2-">${chartMarkup(shell, "g2-")}</div></div><script>${highmaps}</script><script>${accessibility}</script><script>${modules.join("\n")}\nwindow.fetch=async()=>({ok:true,json:async()=>(${data})});window.cleanup=mountExplorer(document.querySelector('#root'),Highcharts);</script>`;
}
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const destination = new URL(
    "../../.playwright-mcp/g2-browser.js",
    import.meta.url,
  );
  await mkdir(new URL(".", destination), { recursive: true });
  await writeFile(
    destination,
    `async (page) => {await page.route('https://graphique2.test/**',route=>route.fulfill({contentType:'text/html',body:${JSON.stringify(await browserFixture())}})); await page.goto('https://graphique2.test/'); await page.waitForFunction(()=>document.querySelector('#g2-load-status')?.hidden); return 'Graphique 2 chargé avec Highmaps npm';}`,
  );
  console.log(fileURLToPath(destination));
}
