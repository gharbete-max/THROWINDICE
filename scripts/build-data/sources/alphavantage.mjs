// Layer 10 — Alpha Vantage free tier. Needs ALPHAVANTAGE_API_KEY (free
// signup, only 25 requests/day at time of writing — thin, but free, and
// this far down the chain it's rarely needed). Skipped if unset.
import { fetchWithTimeout } from "../lib/fetchWithTimeout.mjs";
import { normalizeSeries } from "../lib/normalize.mjs";

export const name = "alphavantage";

export async function fetchDaily(ticker) {
  const key = process.env.ALPHAVANTAGE_API_KEY;
  if (!key) return null;
  const url = `https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=${encodeURIComponent(ticker)}&outputsize=full&apikey=${key}`;
  const res = await fetchWithTimeout(url, { timeoutMs: 10000 });
  const json = await res.json();
  const series = json?.["Time Series (Daily)"];
  if (!series) return null;
  const rows = Object.entries(series).map(([date, v]) => ({
    date,
    close: Number(v["5. adjusted close"] ?? v["4. close"]),
    volume: Number(v["6. volume"] ?? v["5. volume"]),
  }));
  return normalizeSeries(rows);
}
