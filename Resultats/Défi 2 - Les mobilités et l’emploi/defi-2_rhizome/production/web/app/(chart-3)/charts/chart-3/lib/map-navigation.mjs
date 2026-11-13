import {
  constrainView,
  unitsPerPixel,
  viewFromBounds,
  zoomAt,
} from "./geometry.mjs";

// Own the geographical viewport and input mechanics. Selection, tooltips and
// symbol rendering stay with the chart controller through these callbacks.
export function createMapNavigation({
  map,
  frame,
  listen,
  requestRender,
  onHover,
  hideTooltip,
  showHint,
}) {
  let view;
  let homeView;
  let regionView;
  let dragging;
  let pinch;
  let swipe;
  let dragTimer;
  let suppressClickUntil = 0;
  let totalWheelDelta = 0;
  let wheelTimer;
  const mapSize = () => ({
    width: frame.clientWidth || 1,
    height: frame.clientHeight || 1,
  });
  const currentUnits = () =>
    unitsPerPixel(view, mapSize().width, mapSize().height);
  function limits() {
    const size = mapSize();
    return {
      minUnits: 6,
      maxUnits: unitsPerPixel(regionView, size.width, size.height) * 1.1,
      region: regionView,
    };
  }
  function toMap(clientX, clientY) {
    const box = map.getBoundingClientRect(),
      units = currentUnits();
    return {
      x: view.x + view.width / 2 + (clientX - box.left - box.width / 2) * units,
      y:
        view.y + view.height / 2 + (clientY - box.top - box.height / 2) * units,
    };
  }

  function setView(next) {
    view = constrainView(next, limits(), mapSize());
    requestRender();
  }
  function zoomBy(factor) {
    setView(
      zoomAt(
        view,
        factor,
        { x: view.x + view.width / 2, y: view.y + view.height / 2 },
        limits(),
        mapSize(),
      ),
    );
  }
  function pan(dx, dy) {
    const size = mapSize(),
      units = currentUnits();
    setView({
      ...view,
      x: view.x + dx * size.width * units * 0.2,
      y: view.y + dy * size.height * units * 0.2,
    });
  }

  listen(map, "pointerdown", (event) => {
    if (!view || event.button !== 0 || event.pointerType === "touch") return;
    dragging = {
      x: event.clientX,
      y: event.clientY,
      view: { ...view },
      moved: false,
    };
  });
  listen(map, "pointermove", (event) => {
    if (!view || event.pointerType === "touch") return;
    if (!dragging) {
      return onHover(event);
    }
    const dx = event.clientX - dragging.x,
      dy = event.clientY - dragging.y;
    if (Math.hypot(dx, dy) <= 10 && !dragging.moved) return;
    if (!dragging.moved) {
      map.setPointerCapture(event.pointerId);
      hideTooltip();
    }
    dragging.moved = true;
    map.classList.add("dragging");
    const units = unitsPerPixel(
      dragging.view,
      mapSize().width,
      mapSize().height,
    );
    setView({
      ...dragging.view,
      x: dragging.view.x - dx * units,
      y: dragging.view.y - dy * units,
    });
  });
  function endDrag() {
    map.classList.remove("dragging");
    // The click follows pointerup; retain its movement guard until after that event.
    clearTimeout(dragTimer);
    dragTimer = setTimeout(() => {
      dragging = undefined;
    }, 0);
  }
  listen(map, "pointerup", endDrag);
  listen(map, "pointercancel", endDrag);
  listen(map, "pointerleave", () => {
    if (!dragging) hideTooltip();
  });

  // One finger scrolls the page; two fingers move and zoom the map.
  function touchCentre(touches) {
    const [a, b] = touches;
    return {
      x: (a.clientX + b.clientX) / 2,
      y: (a.clientY + b.clientY) / 2,
      distance: Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY) || 1,
    };
  }
  listen(
    map,
    "touchstart",
    (event) => {
      if (!view) return;
      if (event.touches.length === 2) {
        event.preventDefault();
        const start = touchCentre(event.touches);
        pinch = {
          distance: start.distance,
          units: currentUnits(),
          anchor: toMap(start.x, start.y),
        };
        swipe = undefined;
        hideTooltip();
      } else if (event.touches.length === 1)
        swipe = { x: event.touches[0].clientX, y: event.touches[0].clientY };
    },
    { passive: false },
  );
  listen(
    map,
    "touchmove",
    (event) => {
      if (pinch && event.touches.length === 2) {
        event.preventDefault();
        const now = touchCentre(event.touches),
          bounds = limits(),
          box = map.getBoundingClientRect();
        const units = Math.min(
          bounds.maxUnits,
          Math.max(
            bounds.minUnits,
            (pinch.units * pinch.distance) / now.distance,
          ),
        );
        const factor = units / currentUnits(),
          width = view.width * factor,
          height = view.height * factor;
        setView({
          x:
            pinch.anchor.x -
            (now.x - box.left - box.width / 2) * units -
            width / 2,
          y:
            pinch.anchor.y -
            (now.y - box.top - box.height / 2) * units -
            height / 2,
          width,
          height,
        });
        suppressClickUntil = performance.now() + 350;
      } else if (swipe && event.touches.length === 1) {
        const dx = event.touches[0].clientX - swipe.x,
          dy = event.touches[0].clientY - swipe.y;
        if (Math.abs(dx) > 28 && Math.abs(dx) > Math.abs(dy) * 1.5) {
          showHint("Deux doigts pour déplacer la carte");
          swipe = undefined;
        }
      }
    },
    { passive: false },
  );
  for (const name of ["touchend", "touchcancel"])
    listen(map, name, (event) => {
      if (event.touches.length < 2) pinch = undefined;
      if (!event.touches.length) swipe = undefined;
    });
  listen(
    map,
    "wheel",
    (event) => {
      if (!view) return;
      // Match Highmaps' wheel normalization, sensitivity and trackpad guard.
      const delta =
        (event.wheelDelta && -event.wheelDelta / 120) ||
        event.deltaY ||
        event.detail;
      if (!Number.isFinite(delta) || delta === 0) return;
      if (Math.abs(delta) >= 1) {
        totalWheelDelta += Math.abs(delta);
        clearTimeout(wheelTimer);
        wheelTimer = setTimeout(() => {
          totalWheelDelta = 0;
        }, 50);
      }
      if (totalWheelDelta >= 10) return;
      const next = zoomAt(
        view,
        2 ** (delta * 0.1),
        toMap(event.clientX, event.clientY),
        limits(),
        mapSize(),
      );
      // At a zoom limit, leave page scrolling available as Highmaps does.
      if (
        unitsPerPixel(next, mapSize().width, mapSize().height) ===
        currentUnits()
      )
        return;
      event.preventDefault();
      setView(next);
    },
    { passive: false },
  );

  listen(window, "resize", () => {
    if (view) setView(view);
  });

  return {
    get view() {
      return view;
    },
    get homeView() {
      return homeView;
    },
    get suppressClick() {
      return dragging?.moved || performance.now() < suppressClickUntil;
    },
    mapSize,
    currentUnits,
    setView,
    initialize(bounds) {
      regionView = viewFromBounds(bounds, 6500);
      homeView = { ...regionView };
      setView({ ...homeView });
    },
    // Keyboard focus needs a synchronous reveal before its tooltip is measured.
    reveal({ x, y }) {
      const size = mapSize(),
        units = currentUnits();
      if (
        Math.abs(x - view.x - view.width / 2) <= size.width * units * 0.42 &&
        Math.abs(y - view.y - view.height / 2) <= size.height * units * 0.42
      )
        return false;
      view = constrainView(
        { ...view, x: x - view.width / 2, y: y - view.height / 2 },
        limits(),
        size,
      );
      return true;
    },
    handleKeyDown(event) {
      const arrows = {
        ArrowLeft: [-1, 0],
        ArrowRight: [1, 0],
        ArrowUp: [0, -1],
        ArrowDown: [0, 1],
      };
      if (arrows[event.key]) {
        event.preventDefault();
        pan(...arrows[event.key]);
      } else if (event.key === "+" || event.key === "=") zoomBy(0.5);
      else if (event.key === "-" || event.key === "−") zoomBy(2);
      else if (event.key === "0") setView({ ...homeView });
    },
    destroy() {
      clearTimeout(dragTimer);
      clearTimeout(wheelTimer);
      map.classList.remove("dragging");
      dragging = pinch = swipe = undefined;
    },
  };
}
