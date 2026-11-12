import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import { shell as chartTwo } from "../app/(chart-2)/charts/chart-2/lib/shell.ts";
import { referenceMarkup } from "../app/(chart-3)/charts/chart-3/lib/reference-markup.mjs";

test("business creation credits identify each publication and its publication month", () => {
  assert.ok(
    referenceMarkup.includes("Observatoire de la création d’entreprise"),
  );
  for (const [month, publication] of [
    ["de juillet", "août"],
    ["d’août", "septembre"],
    ["de septembre", "octobre"],
  ]) {
    assert.ok(
      referenceMarkup.includes(
        `La création d’entreprise en Île-de-France — chiffres ${month} 2025`,
      ),
      `missing publication title for ${month}`,
    );
    assert.ok(referenceMarkup.includes(`publication : ${publication} 2025`));
  }
});

const networkMap = await readFile(
  new URL("../components/NetworkMap.tsx", import.meta.url),
  "utf8",
);

test("each chart exposes the established licences beside the sources", () => {
  for (const markup of [chartTwo, referenceMarkup]) {
    assert.ok(markup.includes("ODbL 1.0"));
    assert.ok(
      markup.includes("https://opendatacommons.org/licenses/odbl/1-0/"),
    );
    assert.ok(markup.includes("Licence Ouverte 2.0"));
    assert.ok(
      markup.includes(
        "https://github.com/etalab/licence-ouverte/blob/master/LO.md",
      ),
    );
    assert.ok(markup.includes("https://www.insee.fr/fr/information/2008466"));
    assert.ok(markup.includes("Source : Insee"));
  }
  assert.ok(networkMap.includes("Licence Ouverte 2.0"));
  assert.ok(
    networkMap.includes(
      "https://github.com/etalab/licence-ouverte/blob/master/LO.md",
    ),
  );
});

test("geographic copies keep their unresolved provenance visible", () => {
  for (const markup of [chartTwo, referenceMarkup, networkMap]) {
    assert.ok(
      markup
        .replace(/\s+/g, " ")
        .includes("licence des copies locales restent à confirmer"),
    );
  }
});

test("each chart links to the published data reuse notice", () => {
  for (const markup of [chartTwo, referenceMarkup, networkMap]) {
    assert.match(
      markup,
      /<a href="\/data\/LICENCES\.txt">\s*Conditions de réutilisation des données\s*<\/a>/,
    );
  }
});

test("source notes omit consultation dates and retain publication updates", () => {
  assert.doesNotMatch(networkMap, /consultés le 08\/11\/2026/);
  assert.doesNotMatch(referenceMarkup, /consultées le 12 novembre 2026/);
  assert.ok(referenceMarkup.includes("mise à jour du 18 septembre 2026"));
  assert.ok(referenceMarkup.includes("mise à jour du 28 octobre 2026"));
});
