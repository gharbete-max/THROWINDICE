// Turns a daily price/volume series into the same 0–100 composite score
// and five factors the Method screen describes — computed for real here,
// versus the mock dataset's seeded random walk. Every "as of" function is
// windowed strictly to data available on/before that date, so a 24-month
// history is 24 honest historical readings, not today's number smeared
// backwards.
const TRADING_DAYS_YEAR = 252;

export function clamp(x, lo, hi) {
  return Math.max(lo, Math.min(hi, x));
}

/** Linear map x from [x0,x1] to [y0,y1], clamped to the output range. */
export function linMap(x, x0, x1, y0, y1) {
  if (x0 === x1) return (y0 + y1) / 2;
  const t = (x - x0) / (x1 - x0);
  return clamp(y0 + t * (y1 - y0), Math.min(y0, y1), Math.max(y0, y1));
}

/** Simple moving average series, same length as input, NaN until enough history. */
function sma(values, window) {
  const out = new Array(values.length).fill(NaN);
  let sum = 0;
  for (let i = 0; i < values.length; i++) {
    sum += values[i];
    if (i >= window) sum -= values[i - window];
    if (i >= window - 1) out[i] = sum / window;
  }
  return out;
}

/** The five 0–100 factor scores, and their composite average, as of the
 * last point in `daily` (caller windows the array to "as of" a date). */
export function scoreAsOf(daily) {
  const closes = daily.map((r) => r.close);
  const n = closes.length;
  const last = closes[n - 1];

  // 1. Going up? — blend of 1-month and 3-month return, monthlyized.
  const at = (back) => closes[Math.max(0, n - 1 - back)];
  const ret1m = last / at(21) - 1;
  const ret3m = last / at(63) - 1;
  const blended = 0.4 * ret1m + 0.6 * (ret3m / 3);
  const fUp = linMap(blended, -0.08, 0.08, 0, 100);

  // 2. Bumpy? — annualized realized volatility over the trailing quarter, inverted.
  const win = Math.min(63, n - 1);
  const rets = [];
  for (let i = n - win; i < n; i++) if (i > 0) rets.push(closes[i] / closes[i - 1] - 1);
  const mean = rets.reduce((a, b) => a + b, 0) / (rets.length || 1);
  const variance = rets.reduce((a, b) => a + (b - mean) ** 2, 0) / (rets.length || 1);
  const annVol = Math.sqrt(variance) * Math.sqrt(TRADING_DAYS_YEAR);
  const fBumpy = linMap(annVol, 0.1, 0.45, 100, 0);

  // 3. Broad? — proxy for cross-sectional breadth: % of the last 60
  // sessions the price closed above its own 50-day trend. Real breadth
  // needs constituent-level data (which company holdings), not free to
  // pull for every fund every month — this trend-persistence proxy is
  // the documented substitute (see scripts/build-data/README.md).
  const sma50 = sma(closes, 50);
  const breadthWin = Math.min(60, n);
  let above = 0, counted = 0;
  for (let i = n - breadthWin; i < n; i++) {
    if (i < 0 || Number.isNaN(sma50[i])) continue;
    counted++;
    if (closes[i] > sma50[i]) above++;
  }
  const fBroad = counted ? (above / counted) * 100 : 50;

  // 4. Near its high? — distance below the trailing-year max close.
  const hiWin = Math.min(TRADING_DAYS_YEAR, n);
  const hi = Math.max(...closes.slice(n - hiWin));
  const offHigh = last / hi - 1; // <= 0
  const fHigh = linMap(offHigh, -0.3, 0, 0, 100);

  // 5. Busy? — recent volume vs. its own trailing baseline.
  const volumes = daily.map((r) => r.volume).filter((v) => Number.isFinite(v));
  let fBusy = 50;
  if (volumes.length >= 40) {
    const v20 = avg(volumes.slice(-20));
    const v120 = avg(volumes.slice(-Math.min(120, volumes.length)));
    fBusy = linMap(v120 ? v20 / v120 : 1, 0.5, 1.5, 0, 100);
  }

  const f = [round1(fUp), round1(fBumpy), round1(fBroad), round1(fHigh), round1(fBusy)];
  const temp = Math.round(f.reduce((a, b) => a + b, 0) / f.length);
  return { temp, f, ret1m, ret3m, annVol, offHigh };
}

function avg(arr) {
  return arr.reduce((a, b) => a + b, 0) / (arr.length || 1);
}

const HIGH_ADJ = ["rising", "calm", "broad-based", "near its high", "actively traded"];
const LOW_ADJ = ["falling", "choppy", "narrow — a few names doing the work", "well off its high", "quiet"];

/** A best-effort one-line take, auto-written from the computed factors —
 * clearly templated, not hand-crafted prose. Meant as a reasonable
 * default the generated JSON can be hand-edited to improve before
 * committing, not a substitute for real editorial judgment. */
export function describeMonth({ temp, delta, f }) {
  const maxI = f.indexOf(Math.max(...f));
  const minI = f.indexOf(Math.min(...f));
  const dir = delta > 3 ? "improved" : delta < -3 ? "weakened" : "held steady";
  let s = `This month ${dir}, most helped by being ${HIGH_ADJ[maxI]}`;
  if (minI !== maxI && f[minI] < 40) s += `, though it is still ${LOW_ADJ[minI]}`;
  return s + ".";
}
function round1(x) {
  return Math.round(x * 10) / 10;
}

/** Resample a daily series to the last close on/before each of the last
 * `months` month-ends (calendar), ascending, latest last. */
export function monthEnds(daily, months = 24) {
  const byMonth = new Map();
  for (const r of daily) byMonth.set(r.date.slice(0, 7), r); // last write per YYYY-MM wins (ascending input)
  const keys = [...byMonth.keys()].sort().slice(-months);
  return keys.map((k) => byMonth.get(k));
}

/** Equal-weight blend of several tickers' daily series into one synthetic
 * index series (each rebased to 100 at the common start date, then
 * averaged) — how a theme's 1–3 ETFs become "the theme". */
export function blendSeries(seriesList) {
  const starts = seriesList.map((s) => s[0]?.date).filter(Boolean);
  const commonStart = starts.sort().pop(); // latest of the start dates = the common window
  const trimmed = seriesList.map((s) => s.filter((r) => r.date >= commonStart));
  const dates = trimmed[0]?.map((r) => r.date) ?? [];
  const bases = trimmed.map((s) => s[0]?.close ?? 1);
  const byDate = trimmed.map((s) => new Map(s.map((r) => [r.date, r])));
  const out = [];
  for (const date of dates) {
    let sum = 0, vol = 0, count = 0;
    for (let i = 0; i < trimmed.length; i++) {
      const row = byDate[i].get(date);
      if (!row) continue;
      sum += (row.close / bases[i]) * 100;
      vol += row.volume ?? 0;
      count++;
    }
    if (count === trimmed.length) out.push({ date, close: sum / count, volume: vol });
  }
  return out;
}
