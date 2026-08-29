// Layer 2 — Yahoo Finance's unofficial chart API, query1 host. No key.
// Carries adjusted close (dividends folded in), which is why it's
// preferred over query.close when present — matches "dividends included"
// in the Method screen's sourcing note.
import { fetchWithTimeout } from "../lib/fetchWithTimeout.mjs";
import { normalizeSeries } from "../lib/normalize.mjs";

export const name = "yahoo-chart-query1";

export async function fetchDaily(ticker) {
  return fetchYahooChart(ticker, "query1.finance.yahoo.com");
}

export async function fetchYahooChart(ticker, host) {
  // 5y, not 2y: the pipeline builds 24 months of *historical* scores, and
  // the oldest of those needs its own trailing ~1y of daily data to score
  // (near-high, breadth) — so the fetch window has to reach well past the
  // 24-month history window itself.
  const url = `https://${host}/v8/finance/chart/${encodeURIComponent(ticker)}?range=5y&interval=1d&events=div%2Csplits`;
  const res = await fetchWithTimeout(url, { timeoutMs: 8000 });
  const json = await res.json();
  const result = json?.chart?.result?.[0];
  if (!result?.timestamp) return null;
  const ts = result.timestamp;
  const closes = result.indicators?.adjclose?.[0]?.adjclose ?? result.indicators?.quote?.[0]?.close ?? [];
  const volumes = result.indicators?.quote?.[0]?.volume ?? [];
  const rows = ts.map((t, i) => ({
    date: new Date(t * 1000).toISOString().slice(0, 10),
    close: closes[i],
    volume: volumes[i],
  }));
  return normalizeSeries(rows);
}
