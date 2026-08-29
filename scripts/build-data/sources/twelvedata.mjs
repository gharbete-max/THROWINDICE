// Layer 9 — Twelve Data free tier. Needs TWELVEDATA_API_KEY (free signup,
// 800 requests/day at time of writing). Skipped, not failed, if unset.
import { fetchWithTimeout } from "../lib/fetchWithTimeout.mjs";
import { normalizeSeries } from "../lib/normalize.mjs";

export const name = "twelvedata";

export async function fetchDaily(ticker) {
  const key = process.env.TWELVEDATA_API_KEY;
  if (!key) return null;
  const url = `https://api.twelvedata.com/time_series?symbol=${encodeURIComponent(ticker)}&interval=1day&outputsize=1300&apikey=${key}`;
  const res = await fetchWithTimeout(url, { timeoutMs: 8000 });
  const json = await res.json();
  if (json?.status === "error" || !Array.isArray(json?.values)) return null;
  return normalizeSeries(json.values.map((r) => ({ date: r.datetime, close: Number(r.close), volume: Number(r.volume) })));
}
