import test from "node:test";
import assert from "node:assert/strict";
import { createMapNavigation } from "./map-navigation.mjs";

function mount(t) {
  const previousWindow = globalThis.window;
  globalThis.window = {};
  const listeners = {};
  const hints = [];
  const map = {
    getBoundingClientRect: () => ({
      left: 100,
      top: 50,
      width: 1000,
      height: 720,
    }),
    classList: { add() {}, remove() {} },
    setPointerCapture() {},
  };
  const navigation = createMapNavigation({
    map,
    frame: { clientWidth: 1000, clientHeight: 720 },
    listen: (target, name, callback) => {
      if (target === map) listeners[name] = callback;
    },
    requestRender() {},
    onHover() {},
    hideTooltip() {},
    showHint: (hint) => hints.push(hint),
  });
  navigation.initialize([0, 0, 100000, 72000]);
  t.after(() => {
    navigation.destroy();
    globalThis.window = previousWindow;
  });
  const wheel = (options = {}) => {
    let prevented = false;
    listeners.wheel({
      clientX: 400,
      clientY: 300,
      deltaY: -100,
      wheelDelta: 120,
      preventDefault: () => {
        prevented = true;
      },
      ...options,
    });
    return prevented;
  };
  return { navigation, listeners, hints, wheel };
}

function anchor(navigation) {
  const { view } = navigation;
  const units = navigation.currentUnits();
  return {
    x: view.x + view.width / 2 - 200 * units,
    y: view.y + view.height / 2 - 110 * units,
  };
}

function nearlyEqual(actual, expected) {
  assert.ok(Math.abs(actual - expected) < 1e-8, `${actual} ≈ ${expected}`);
}

test("ordinary wheel keeps the pointer anchor and uses native Highmaps sensitivity", (t) => {
  const { navigation, hints, wheel } = mount(t);
  const before = anchor(navigation);
  const width = navigation.view.width;
  assert.equal(wheel(), true);
  nearlyEqual(navigation.view.width / width, 2 ** -0.1);
  nearlyEqual(anchor(navigation).x, before.x);
  nearlyEqual(anchor(navigation).y, before.y);
  assert.deepEqual(hints, [], "wheel needs no modifier instruction");
  assert.equal(wheel({ wheelDelta: -120 }), true);
  nearlyEqual(navigation.view.width, width);
});

test("zoom limits release page scrolling and zero wheel input does nothing", (t) => {
  const { navigation, wheel } = mount(t);
  navigation.setView({ ...navigation.view, width: 1, height: 1 });
  assert.equal(navigation.currentUnits(), 6);
  const close = { ...navigation.view };
  assert.equal(wheel(), false);
  assert.deepEqual(navigation.view, close);
  assert.equal(wheel({ wheelDelta: 0, deltaY: 0 }), false);
  assert.equal(wheel({ wheelDelta: -120 }), true);
  navigation.setView({ ...navigation.view, width: 1e9, height: 1e9 });
  const far = { ...navigation.view };
  assert.equal(wheel({ wheelDelta: -120 }), false);
  assert.deepEqual(navigation.view, far);
});

test("trackpad deltas and rapid wheel bursts follow the native guard", async (t) => {
  const { navigation, wheel } = mount(t);
  const width = navigation.view.width;
  assert.equal(wheel({ wheelDelta: undefined, deltaY: -0.5 }), true);
  nearlyEqual(navigation.view.width / width, 2 ** -0.05);
  for (let i = 0; i < 9; i++) assert.equal(wheel(), true);
  const guarded = { ...navigation.view };
  assert.equal(wheel(), false);
  assert.deepEqual(navigation.view, guarded);
  await new Promise((resolve) => setTimeout(resolve, 60));
  assert.equal(wheel(), true, "a fresh wheel gesture can zoom again");
});

test("keyboard halves and doubles scale, while zero restores the home view", (t) => {
  const { navigation } = mount(t);
  const home = { ...navigation.view };
  navigation.handleKeyDown({ key: "+" });
  nearlyEqual(navigation.view.width, home.width / 2);
  navigation.handleKeyDown({ key: "−" });
  nearlyEqual(navigation.view.width, home.width);
  navigation.handleKeyDown({ key: "=" });
  navigation.handleKeyDown({ key: "0" });
  assert.deepEqual(navigation.view, home);
});

test("mouse movement through ten pixels keeps selection, then becomes a drag", (t) => {
  const { navigation, listeners } = mount(t);
  const initial = { ...navigation.view };
  listeners.pointerdown({
    button: 0,
    pointerType: "mouse",
    clientX: 300,
    clientY: 300,
  });
  listeners.pointermove({ pointerType: "mouse", clientX: 310, clientY: 300 });
  assert.deepEqual(navigation.view, initial);
  assert.equal(navigation.suppressClick, false);
  listeners.pointermove({ pointerType: "mouse", clientX: 311, clientY: 300 });
  assert.notDeepEqual(navigation.view, initial);
  assert.equal(navigation.suppressClick, true);
});
