import { test } from "node:test";
import assert from "node:assert/strict";
import { access, readFile, readdir } from "node:fs/promises";
import { referenceMarkup } from "../app/(chart-3)/charts/chart-3/lib/reference-markup.mjs";

test("the charts have no standalone routes or links to them", async () => {
  for (const path of [
    "../app/(chart-2)/charts/chart-2/page.tsx",
    "../app/(chart-3)/charts/chart-3/page.js",
    "../app/(chart-3)/charts/chart-3/highcharts/page.js",
  ]) {
    await assert.rejects(access(new URL(path, import.meta.url)), {
      code: "ENOENT",
    });
  }
  assert.doesNotMatch(referenceMarkup, /href="\/charts\/chart-3\//);
});

test("all local module imports in both chart sources resolve", async () => {
  async function inspect(directory) {
    for (const entry of await readdir(directory, { withFileTypes: true })) {
      const file = new URL(
        entry.name + (entry.isDirectory() ? "/" : ""),
        directory,
      );
      if (entry.isDirectory()) await inspect(file);
      else if (/\.(?:tsx?|jsx?|mjs)$/.test(entry.name)) {
        const source = await readFile(file, "utf8");
        for (const [, dependency] of source.matchAll(
          /(?:from\s*|import\s*)['"]([^'"]+)['"]/g,
        )) {
          if (!dependency.startsWith(".")) continue;
          const candidates = /\.[a-z]+$/.test(dependency)
            ? [dependency]
            : [dependency + ".ts", dependency + ".tsx", dependency + ".js"];
          const results = await Promise.allSettled(
            candidates.map((candidate) => access(new URL(candidate, file))),
          );
          assert.ok(
            results.some((result) => result.status === "fulfilled"),
            `${file.pathname}: ${dependency}`,
          );
        }
      }
    }
  }
  await inspect(new URL("../app/(chart-2)/", import.meta.url));
  await inspect(new URL("../app/(chart-3)/", import.meta.url));
});

test("direct chart markup has unique identifiers and keeps every local reference inside its chart", async () => {
  const { chartMarkup } = await import("../lib/chart-markup.mjs");
  const shellSource = await readFile(
    new URL("../app/(chart-2)/charts/chart-2/lib/shell.ts", import.meta.url),
    "utf8",
  );
  const shell = shellSource.slice(
    shellSource.indexOf("`") + 1,
    shellSource.lastIndexOf("`"),
  );
  const allIds = new Set();
  for (const [markup, prefix] of [
    [shell, "g2-"],
    [referenceMarkup, "g3-"],
  ]) {
    const result = chartMarkup(markup, prefix);
    assert.doesNotMatch(result, /<\/?main\b/);
    const ids = new Set(
      [...result.matchAll(/\bid="([^"]+)"/g)].map((match) => match[1]),
    );
    for (const id of ids) {
      assert.ok(id.startsWith(prefix));
      assert.ok(!allIds.has(id), `duplicate ID: ${id}`);
      allIds.add(id);
    }
    for (const [, attribute, value] of result.matchAll(
      /\b(for|aria-labelledby|aria-describedby|aria-controls|href)="([^"]+)"/g,
    )) {
      if (attribute === "href" && !value.startsWith("#")) continue;
      for (const id of value.replace(/^#/, "").split(/\s+/))
        assert.ok(ids.has(id), `${attribute} references missing ${id}`);
    }
  }
});

test("the story mounts the source explorers directly", async () => {
  const story = await readFile(
    new URL("../app/(story)/page.tsx", import.meta.url),
    "utf8",
  );
  assert.doesNotMatch(story, /EmbeddedVisualization|iframe/);
  assert.match(
    story,
    /import EmploymentExplorer from "\.\.\/\(chart-2\)\/charts\/chart-2\/Explorer"/,
  );
  assert.match(
    story,
    /import TerritoriesExplorer from "\.\.\/\(chart-3\)\/charts\/chart-3\/explorer"/,
  );
  assert.match(story, /<EmploymentExplorer \/>/);
  assert.match(story, /<TerritoriesExplorer \/>/);
});

test("the original territory explorer keeps Highcharts Maps and its original legend", async () => {
  const source = await readFile(
    new URL("../app/(chart-3)/charts/chart-3/explorer.js", import.meta.url),
    "utf8",
  );
  const adapter = await readFile(
    new URL(
      "../app/(chart-3)/charts/chart-3/lib/highmaps-adapter.mjs",
      import.meta.url,
    ),
    "utf8",
  );
  assert.match(
    source,
    /initializeReference\(\s*root\.current,\s*data,\s*\{\s*loadHighmaps:\s*loadVendors\s*\}\s*\)/,
  );
  assert.match(adapter, /H\.mapChart\(/);
  for (const label of [
    "Densité d’emploi",
    "Pôles d’emploi",
    "Réseau ferré",
    "Les huit départements",
  ]) {
    assert.ok(
      referenceMarkup.includes(label),
      `missing original section: ${label}`,
    );
  }
});

test("the second chart does not link to a README", async () => {
  const shell = await readFile(
    new URL("../app/(chart-2)/charts/chart-2/lib/shell.ts", import.meta.url),
    "utf8",
  );
  assert.doesNotMatch(shell, /href=["'][^"']*README\.md/i);
});

test("migrated maps contain no public vendor copies or script references", async () => {
  for (const chart of ["chart-2", "chart-3"]) {
    for (const library of ["highmaps.js", "accessibility.js"]) {
      await assert.rejects(
        access(
          new URL(
            `../public/charts/${chart}/vendor/${library}`,
            import.meta.url,
          ),
        ),
        { code: "ENOENT" },
      );
    }
  }
  for (const file of [
    "../app/(chart-2)/charts/chart-2/Explorer.tsx",
    "../app/(chart-2)/charts/chart-2/lib/vendors.ts",
    "../app/(chart-3)/charts/chart-3/explorer.js",
  ]) {
    const source = await readFile(new URL(file, import.meta.url), "utf8");
    assert.doesNotMatch(source, /window\.Highcharts|\/vendor\/|next\/script/);
  }
});
