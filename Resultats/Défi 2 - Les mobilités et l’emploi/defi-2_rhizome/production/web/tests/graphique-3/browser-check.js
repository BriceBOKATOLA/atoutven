async (page) => {
  const check = async label => { await page.waitForTimeout(100); return page.evaluate(label => {
    const chart = Highcharts.charts.find(Boolean);
    const overlay = document.querySelector('#g3-map');
    const box = chart.container.getBoundingClientRect();
    const paris = chart.get('75056');
    if ((paris.graphic && paris.graphic.attr('fill') !== 'rgba(230,159,0,.14)') || paris.options.marker.lineWidth !== 2.4) throw Error('Paris marker style was lost during resizing');
    let maximumError = 0;
    for (const point of chart.get('poles').points) {
      const circle = overlay.querySelector(`.pole-symbol[data-commune="${point.id}"]`);
      const xy = overlay.createSVGPoint();
      xy.x = Number(circle.getAttribute('cx')); xy.y = Number(circle.getAttribute('cy'));
      const position = xy.matrixTransform(circle.getScreenCTM());
      maximumError = Math.max(maximumError, Math.hypot(position.x - box.left - point.plotX, position.y - box.top - point.plotY));
    }
    if (maximumError > 1) throw Error(`${label}: misalignment ${maximumError}px`);
    return {label, maximumError};
  }, label); };
  const results = [await check('initial')];
  for (let i = 0; i < 5; i++) await page.locator('#g3-zoom-in').click();
  results.push(await check('zoom'));
  for (let i = 0; i < 4; i++) {
    await page.locator('[data-pan="right"]').click();
    await page.locator('[data-pan="up"]').click();
  }
  results.push(await check('pan'));
  for (let i = 0; i < 12; i++) {
    await page.waitForTimeout(100);
    if (await page.locator('#g3-zoom-out').isDisabled()) break;
    await page.locator('#g3-zoom-out').click();
  }
  results.push(await check('maximum extent'));
  await page.locator('#g3-reset-view').click();
  await page.locator('.department[data-department="77"]').click();
  const selected = await page.evaluate(() => ({
    code: new URL(location.href).searchParams.get('departement'),
    count: Highcharts.charts.find(Boolean).get('departments').points.filter(point => point.color === 'rgba(23,78,154,.1)').length,
    selected: document.querySelector('.department[aria-pressed="true"]')?.dataset.department
  }));
  if (selected.code !== '77' || selected.count !== 1 || selected.selected !== '77') throw Error(`selection: ${JSON.stringify(selected)}`);
  await page.locator('.department[data-department="77"]').click();
  if (await page.evaluate(() => new URL(location.href).searchParams.has('departement'))) throw Error('second click did not clear selection');
  await page.locator('#g3-map').focus();
  await page.keyboard.press('Tab');
  await page.keyboard.press('ArrowRight');
  const focus = await page.evaluate(() => ({
    pole: document.activeElement.dataset.commune,
    stroke: getComputedStyle(document.activeElement).stroke,
    tooltip: !document.querySelector('#g3-map-tooltip').hidden
  }));
  if (focus.pole !== '92026' || focus.stroke !== 'rgb(46, 107, 255)' || !focus.tooltip) throw Error(`keyboard: ${JSON.stringify(focus)}`);
  for (const width of [320, 768, 1024, 1440]) {
    await page.setViewportSize({width, height: 844});
    await page.waitForTimeout(150);
    results.push(await check(`width ${width}`));
  }
  await page.evaluate(() => window.cleanup());
  if (await page.evaluate(() => Highcharts.charts.filter(Boolean).length || document.querySelectorAll('.reference-highmaps').length)) throw Error('cleanup leaked a chart');
  return {results, selected, focus, cleanup: 'passed'};
}
