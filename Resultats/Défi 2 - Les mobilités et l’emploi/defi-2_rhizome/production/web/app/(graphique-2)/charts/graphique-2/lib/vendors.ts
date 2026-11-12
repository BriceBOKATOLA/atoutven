// Share the npm engine with every map. Import it only after entering the browser.
type Highmaps = typeof import('highcharts/highmaps');
let loading: Promise<Highmaps> | undefined;

export function loadVendors(): Promise<Highmaps> {
  if (typeof window === 'undefined') {
    return Promise.reject(new Error('Highmaps requires a browser'));
  }
  if (!loading) {
    loading = import('highcharts/highmaps.js')
      .then(async ({ default: highmaps }) => {
        await import('highcharts/modules/accessibility.js');
        return highmaps;
      })
      .catch(error => { loading = undefined; throw error; });
  }
  return loading;
}
