import test from "node:test";
import assert from "node:assert/strict";
import { Script } from "node:vm";
import { browserFixture } from "./browser-fixture.mjs";

test("the offline fixture compiles its real modules as classic browser scripts", async () => {
  const html = await browserFixture();
  const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];

  assert.equal(
    scripts.length,
    3,
    "Highmaps, accessibility and the explorer are embedded",
  );
  for (const [index, [, source]] of scripts.entries()) {
    assert.doesNotThrow(
      () => new Script(source),
      `fixture script ${index + 1}`,
    );
  }
});
