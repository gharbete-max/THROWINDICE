// Plain facts from one daily series [{date, close, volume?}] (ascending).
// close is adjusted (dividends folded in) when the source provides it.
// Nothing here scores, ranks or predicts.
const DAY = 864e5;
const r2 = (n) => Math.round(n * 100) / 100;
const ago = (date, years) => new Date(new Date(date).getTime() - years * 365.25 * DAY).toISOString().slice(0, 10);

function change(series, years) {
  const last = series[series.length - 1];
  const start = ago(last.date, years);
  if (series[0].date > start) return null; // not enough history
  const base = [...series].reverse().find((r) => r.date <= start);
  return r2((last.close / base.close - 1) * 100);
}

/** Annualised volatility (%) of daily returns over the last `years`. */
function volatility(series, years) {
  const from = ago(series[series.length - 1].date, years);
  const rows = series.filter((r) => r.date >= from);
  const rets = rows.slice(1).map((r, i) => Math.log(r.close / rows[i].close));
  if (rets.length < 200) return null;
  const mean = rets.reduce((a, b) => a + b, 0) / rets.length;
  const sd = Math.sqrt(rets.reduce((a, b) => a + (b - mean) ** 2, 0) / (rets.length - 1));
  return r2(sd * Math.sqrt(252) * 100);
}

/** Worst peak-to-trough fall (%) in the series. */
function worstFall(series) {
  let peak = 0, worst = 0;
  for (const { close } of series) {
    peak = Math.max(peak, close);
    worst = Math.min(worst, close / peak - 1);
  }
  return r2(worst * 100);
}

/** Last close of each calendar month, newest 60. */
function monthly(series) {
  const m = new Map();
  for (const r of series) m.set(r.date.slice(0, 7), r.close);
  return [...m.values()].slice(-60).map(r2);
}

export function computeFacts(series) {
  const vols = series.slice(-63).map((r) => r.volume).filter(Number.isFinite);
  return {
    asOf: series[series.length - 1].date,
    from: series[0].date,
    change1y: change(series, 1),
    change3y: change(series, 3),
    change5y: change(series, 5),
    volatility3y: volatility(series, 3),
    worstFall: worstFall(series),
    avgVolume3m: vols.length ? Math.round(vols.reduce((a, b) => a + b, 0) / vols.length) : null,
    monthly: monthly(series),
  };
}
