// Every source layer, whatever shape it fetches, must resolve to this:
// [{ date: "YYYY-MM-DD", close: number, volume?: number }], ascending,
// deduplicated by date. `validate` is the gate the orchestrator uses to
// decide "did this layer actually work" vs. "silently gave us garbage" —
// a 2-year daily series should have somewhere north of 400 rows; anything
// much thinner (a truncated response, a holiday-only stub, an error page
// that happened to parse) gets rejected so the next layer gets a turn.
export function normalizeSeries(rows) {
  const byDate = new Map();
  for (const r of rows) {
    if (!r || !r.date || !Number.isFinite(r.close)) continue;
    byDate.set(r.date, { date: r.date, close: r.close, volume: Number.isFinite(r.volume) ? r.volume : undefined });
  }
  return [...byDate.values()].sort((a, b) => (a.date < b.date ? -1 : 1));
}

export function validateSeries(series, { minPoints = 400 } = {}) {
  if (!Array.isArray(series) || series.length < minPoints) return false;
  // Reject a series where prices are implausible (zero/negative, or a
  // provider that returned the same stale value for every row).
  const closes = series.map((r) => r.close);
  if (closes.some((c) => !(c > 0))) return false;
  const distinct = new Set(closes.map((c) => c.toFixed(4))).size;
  if (distinct < Math.max(10, series.length * 0.05)) return false;
  return true;
}
