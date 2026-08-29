// Holt's linear trend method (double exponential smoothing) — the
// "Holt–Winters" the Method screen names, minus the seasonal component:
// two data points a year apart isn't enough history yet to fit a
// trustworthy 12-month seasonal cycle, and the app only ever needs a
// two-month-ahead point forecast. Level + trend, no seasonality, is the
// honest version of that claim; swap in a full Holt-Winters once a few
// years of monthly history have accumulated (see README.md).
//
// Fits by a small grid search over (alpha, beta) minimizing one-step-
// ahead squared error — good enough for a monthly series this short,
// no external dependency needed.

function fit(series, alpha, beta) {
  let level = series[0];
  let trend = series[1] - series[0];
  const fitted = [level + trend];
  let sse = 0;
  for (let i = 1; i < series.length; i++) {
    const prevLevel = level;
    level = alpha * series[i] + (1 - alpha) * (level + trend);
    trend = beta * (level - prevLevel) + (1 - beta) * trend;
    const forecastNext = level + trend;
    if (i < series.length - 1) sse += (series[i + 1] - forecastNext) ** 2;
    fitted.push(forecastNext);
  }
  return { level, trend, fitted, sse };
}

/** Two-step-ahead forecast from a chronological array of monthly scores.
 * Returns null if there isn't enough history to fit anything meaningful. */
export function holtForecast(series) {
  if (!Array.isArray(series) || series.length < 6) return null;
  const grid = [0.1, 0.3, 0.5, 0.7, 0.9];
  let best = null;
  for (const alpha of grid) {
    for (const beta of grid) {
      const r = fit(series, alpha, beta);
      if (!best || r.sse < best.sse) best = { ...r, alpha, beta };
    }
  }
  const p1 = best.level + best.trend;
  const p2 = best.level + 2 * best.trend;
  // Residual spread from the in-sample one-step errors — how much to
  // trust the trend continuing, used to size the three scenario bands.
  const errors = [];
  for (let i = 0; i < series.length - 1; i++) errors.push(series[i + 1] - best.fitted[i]);
  const resid = Math.sqrt(errors.reduce((a, e) => a + e * e, 0) / (errors.length || 1));
  return { p1: clampScore(p1), p2: clampScore(p2), resid: Math.round(resid * 10) / 10, alpha: best.alpha, beta: best.beta };
}

function clampScore(x) {
  return Math.round(Math.max(0, Math.min(100, x)));
}
