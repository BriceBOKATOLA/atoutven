import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { mountExplorer } from '../../app/(graphique-2)/charts/graphique-2/lib/explorer.ts';

export async function deliveredData() {
  return JSON.parse(await readFile(new URL('../../public/data/jobseekers-employment-zones.json', import.meta.url), 'utf8'));
}

// A deliberately small DOM boundary double, not a browser/layout implementation.
// Tests enter through mountExplorer and the handlers it installs on these controls.
class Element {
  constructor(tagName = 'div') {
    this.tagName = tagName;
    this.children = [];
    this.attributes = {};
    this.style = { setProperty(name, value) { this[name] = value; } };
    this.dataset = {};
    this.listeners = new Map();
    this.value = '';
    this.text = '';
    this.clientWidth = 1000;
    this.scrolls = 0;
  }
  set textContent(value) { this.text = value; this.children = []; }
  get textContent() { return this.text + this.children.map(child => typeof child === 'string' ? child : child.textContent).join(''); }
  get firstElementChild() { return this.children.find(child => child instanceof Element); }
  append(...children) {
    for (const child of children) {
      if (child.tagName === '#fragment') this.children.push(...child.children);
      else this.children.push(child);
    }
  }
  replaceChildren(...children) { this.children = []; this.text = ''; this.append(...children); }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  getAttribute(name) { return this.attributes[name] ?? null; }
  removeAttribute(name) { delete this.attributes[name]; }
  addEventListener(type, handler, { signal } = {}) {
    const handlers = this.listeners.get(type) ?? [];
    handlers.push({ handler, signal });
    this.listeners.set(type, handlers);
  }
  dispatch(type, event = {}) {
    for (const { handler, signal } of this.listeners.get(type) ?? []) {
      if (!signal?.aborted) handler({ target: this, ...event });
    }
    this[`on${type}`]?.({ target: this, ...event });
  }
  querySelector(selector) {
    return this.querySelectorAll(selector)[0] ?? null;
  }
  querySelectorAll(selector) {
    const matches = child => {
      const input = /^input\[value="(.*)"\]$/.exec(selector);
      return input ? child.tagName === 'input' && child.value === input[1] : child.tagName === selector;
    };
    return this.children.filter(child => child instanceof Element).flatMap(child => [
      ...(matches(child) ? [child] : []), ...child.querySelectorAll(selector)
    ]);
  }
  scrollIntoView() { this.scrolls++; }
}

export async function mountedExplorer(t, dataset, { map: suppliedMap, fetch: suppliedFetch, geojson = () => [] } = {}) {
  const originals = { document: globalThis.document, fetch: globalThis.fetch };
  const nodes = new Map();
  const control = id => {
    if (!nodes.has(id)) nodes.set(id, new Element());
    return nodes.get(id);
  };
  control('zone-options').append(new Element('legend'));
  control('map-scale').append(new Element('span'), new Element('i'));
  globalThis.document = { createElement: tag => new Element(tag), createElementNS: (namespace, tag) => new Element(tag), createDocumentFragment: () => new Element('#fragment') };
  globalThis.fetch = suppliedFetch ?? (async (url, options) => {
    assert.equal(url, '/data/jobseekers-employment-zones.json');
    assert.equal(options.signal.aborted, false);
    return { ok: true, json: async () => dataset };
  });
  const graphics = [];
  function graphic(kind, geometry) {
    const item = { kind, geometry, attributes: {}, element: new Element('g'),
      attr(attributes) { Object.assign(this.attributes, attributes); return this; },
      css() { return this; }, add(parent) { this.parent = parent; return this; },
      destroy() { this.destroyed = true; }
    };
    graphics.push(item);
    return item;
  }
  let zoom = 1;
  const map = {
    plotWidth: 1200, plotHeight: 1000, plotLeft: 12, plotTop: 8,
    mapView: {
      lonLatToPixels: ({ lon, lat }) => ({ x: 400 + (lon - 2) * 100 * zoom, y: 400 + (lat - 49) * 100 * zoom }),
      pixelsToLonLat: () => ({ lon: 2.35, lat: 48.85 })
    },
    renderer: { g: name => graphic('group', name), circle: (...args) => graphic('circle', args), path: path => graphic('path', path), text: (...args) => graphic('text', args) },
    get: () => undefined,
    destroy() { this.destroyed = true; },
    ...suppliedMap
  };
  let chartOptions;
  let dispose;
  t.after(() => {
    dispose?.();
    globalThis.document = originals.document;
    globalThis.fetch = originals.fetch;
  });
  dispose = mountExplorer({ querySelector: selector => control(selector.slice(1)), querySelectorAll: () => [] }, {
    setOptions() { assert.fail('Explorer must not change shared Highcharts defaults'); }, geojson,
    mapChart(container, options) { chartOptions = options; return map; }
  });
  await new Promise(resolve => setImmediate(resolve));
  if (!suppliedFetch) assert.ok(chartOptions, control('load-status').textContent);
  return {
    control, map, graphics, options: chartOptions, dispose,
    redraw() { chartOptions.chart.events.render.call(map); },
    setZoom(value) { zoom = value; },
    markers() { return graphics.filter(item => item.geometry === 'zone-marker' && item.parent === map.flowerLayer); },
    children(marker) { return graphics.filter(item => item.parent === marker); },
    select(code) { control('zone-options').dispatch('change', { target: { value: code } }); }
  };
}
