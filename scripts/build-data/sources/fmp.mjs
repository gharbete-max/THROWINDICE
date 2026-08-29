// Layer 8 — Financial Modeling Prep free tier. Needs FMP_API_KEY (free
// signup, 250 requests/day at time of writing). Skipped entirely — not
// counted as a failure — when the key isn't set, so the pipeline still
// runs on the fully-anonymous layers alone.
import { fetchWithTimeout } from "../lib/fetchWithTimeout.mjs";
import { normalizeSeries } from "../lib/normalize.mjs";

export const name = "fmp";

export async function fetchDaily(ticker) {
  const key = process.env.FMP_API_KEY;
  if (!key) return null;
  const url = `https://financialmodelingprep.com/api/v3/historical-price-full/${encodeURIComponent(ticker)}?timeseries=1825&apikey=${key}`;
  const res = await fetchWithTimeout(url, { timeoutMs: 8000 });
  const json = await res.json();
  const rows = json?.historical;
  if (!Array.isArray(rows) || !rows.length) return null;
  return normalizeSeries(rows.map((r) => ({ date: r.date, close: r.adjClose ?? r.close, volume: r.volume })));
}
