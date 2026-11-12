// Independent expectations for the documented five-indicator encoding.
export const fills = ['#B3CF78', '#E06A55', '#E0A52A', '#F2BFC8', '#9A5A90'];
export const strokes = ['#7A9A3A', '#B5452F', '#A87400', '#BF6A80', '#6E3C66'];
export function indicatorValues(zone) {
  const value = (name, year) => zone.indicators[name]?.[year] ?? null;
  const change = (name) => {
    const before = value(name, '2016'), after = value(name, '2024');
    return before === null || after === null || before === 0 ? null : (after / before - 1) * 100;
  };
  const ratio = (part, total) => part === null || total === null || total === 0 ? null : part / total * 100;
  return [change('Salariés privés'), change('Demandeurs ABC'), value('Taux de chômage localisé', '2024'),
    ratio(value('Demandeurs ABC', '2024'), value('Salariés privés', '2024')),
    ratio(value('Emplois au lieu de travail', '2016'), value('Actifs occupés résidents', '2016'))];
}
export function expectedPetal(length) {
  const side = length / Math.SQRT2;
  return [['M', 0, 0], ['L', 0, -side * .2], ['A', side * .8, side * .8, 0, 0, 1, side * .8, -side],
    ['L', side, -side], ['L', side, -side * .2], ['A', side * .8, side * .8, 0, 0, 1, side * .2, 0], ['Z']];
}
