import { analyse, BASE_YEAR, densityColor, geometryPath, poleRadius, unitsPerPixel } from './geometry.mjs';

// The reference SVG remains the accessible interaction surface. Highmaps owns
// the geographical series, while the established flower/label layout stays intact.
export function mapSeries(data) {
  const insights = analyse(data);
  const paths = lines => lines.map(line => ({path: geometryPath(line.geometry)}));
  const recent = insights.recentLines.map(line => ({path: line.segments.map(segment => geometryPath(segment.geometry)).join(' ')}));
  return [
    {type: 'map', id: 'density', data: data.communes.map(commune => ({path: geometryPath(commune.geometry), color: densityColor(commune.densite_2025)})), borderColor: '#fff', borderWidth: .5},
    {type: 'map', id: 'departments', data: data.departments.map(department => ({id: `department-${department.code}`, path: geometryPath(department.geometry), color: 'rgba(0,0,0,0)'})), borderColor: '#d9739f', borderWidth: 1.2},
    {type: 'mapline', id: 'rail-earlier', data: paths(data.lines.filter(line => line.an <= BASE_YEAR)), color: '#8b929b', lineWidth: 1},
    {type: 'mapline', id: 'rail-casing', data: recent, color: 'rgba(255,255,255,.85)', lineWidth: 5.5},
    {type: 'mapline', id: 'rail-recent', data: recent, color: '#0e1b2c', lineWidth: 2.6},
    {type: 'mappoint', id: 'poles', data: insights.poles.map(pole => ({id: pole.code, x: pole.geometry.coordinates[0], y: -pole.geometry.coordinates[1], custom: {employment: pole.emploi_2025}, marker: {
      symbol: 'circle', radius: 0,
      fillColor: pole.code === '75056' ? 'rgba(230,159,0,.14)' : pole.change < 0 ? '#fffefa' : '#e69f00',
      lineColor: pole.isNew ? '#d55e00' : pole.change < 0 || pole.code === '75056' ? '#a86f00' : '#3d2700',
      lineWidth: pole.isNew ? 3 : pole.code === '75056' ? 2.4 : pole.change < 0 ? 2.2 : 1
    }}))}
  ].map(series => ({...series, enableMouseTracking: false, animation: false, dataLabels: {enabled: false}, turboThreshold: 0, states: {inactive: {opacity: 1}}}));
}

export function mountHighmaps(H, frame, overlay, data) {
  const container = document.createElement('div');
  container.className = 'reference-highmaps';
  container.setAttribute('aria-hidden', 'true');
  frame.insertBefore(container, overlay);
  let chart;
  try {
    chart = H.mapChart(container, {
      chart: {backgroundColor: 'transparent', animation: false, spacing: 0, margin: 0, reflow: false},
      title: {text: undefined}, legend: {enabled: false}, credits: {enabled: false},
      accessibility: {enabled: false}, tooltip: {enabled: false},
      mapNavigation: {enabled: false, enableMouseWheelZoom: false, enableTouchZoom: false, enableDoubleClickZoom: false},
      mapView: {padding: 0, projection: {name: undefined}},
      plotOptions: {series: {animation: false}}, series: mapSeries(data)
    });
  } catch (error) { container.remove(); throw error; }
  // The accessible SVG owns map interactions above Highmaps. Keep the credit
  // outside that overlay, using the library's attribution text and destination.
  const credit = document.createElement('a');
  credit.className = 'reference-highmaps-credit';
  credit.href = chart.options.credits.href;
  credit.textContent = chart.options.credits.text;
  frame.append(credit);
  frame.classList.add('highmaps-active');
  let lastUnits;
  return {
    render(view, size) {
      if (chart.chartWidth !== size.width || chart.chartHeight !== size.height) chart.setSize(size.width, size.height, false);
      const units = unitsPerPixel(view, size.width, size.height);
      // fitToBounds uses precisely the same letterboxed bounds as SVG viewBox.
      chart.mapView.minZoom = -Infinity;
      chart.mapView.fitToBounds({x1: view.x, y1: view.y, x2: view.x + view.width, y2: view.y + view.height}, 0, false, false);
      // The interaction owner already constrains the view to the region.
      // Highmaps would otherwise recenter the padded bounds on its data.
      chart.mapView.center = [view.x + view.width / 2, view.y + view.height / 2];
      if (units !== lastUnits) {
        for (const point of chart.get('poles').points) point.update({marker: {...point.options.marker, radius: poleRadius(point.custom.employment, units) / units}}, false);
        lastUnits = units;
      }
      chart.mapView.redraw(false);
    },
    select(code) {
      for (const point of chart.get('departments').points) {
        const selected = point.id === `department-${code}`;
        point.update({color: selected ? 'rgba(23,78,154,.1)' : 'rgba(0,0,0,0)', borderColor: selected ? '#174e9a' : '#d9739f', borderWidth: selected ? 2.5 : 1.2}, false);
      }
      chart.redraw(false);
    },
    destroy() { chart.destroy(); credit.remove(); container.remove(); frame.classList.remove('highmaps-active'); }
  };
}
