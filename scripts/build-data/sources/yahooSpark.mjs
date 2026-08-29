// Layer 4 — Yahoo's lightweight "spark" endpoint. A different path, no
// key, and observed to stay reachable in some networks that block the
// full /v8/finance/chart path. Thinner payload (no volume in some
// responses), which is fine — the orchestrator still validates length.
import { fetchWithTimeout } from "../lib/fetchWithTimeout.mjs";
import { normalizeSeries } from "../lib/normalize.mjs";

export const name = "yahoo-spark";

export async function fetchDaily(ticker) {
  const url = `https://query1.finance.yahoo.com/v7/finance/spark?symbols=${encodeURIComponent(ticker)}&range=2y&interval=1d`;
  const res = await fetchWithTimeout(url, { timeoutMs: 8000 });
  const json = await res.json();
  // Two response shapes have been observed in the wild for this
  // undocumented endpoint; handle both defensively.
  const entry = json?.spark?.result?.find((r) => r.symbol === ticker)?.response?.[0] ?? json?.[ticker];
  const ts = entry?.timestamp;
  const closes = entry?.indicators?.quote?.[0]?.close;
  if (!ts || !closes) return null;
  const rows = ts.map((t, i) => ({ date: new Date(t * 1000).toISOString().slice(0, 10), close: closes[i] }));
  return normalizeSeries(rows);
}
