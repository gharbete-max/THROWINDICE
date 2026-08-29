// Layer — Tiingo free tier. Needs TIINGO_API_KEY (free signup, no card;
// at time of writing free accounts get ~50 requests/hour and full EOD
// history on US equities/ETFs, one of the more generous free tiers
// going). Skipped, not failed, if unset — same pattern as the other
// keyed layers.
import { fetchWithTimeout } from "../lib/fetchWithTimeout.mjs";
import { normalizeSeries } from "../lib/normalize.mjs";

export const name = "tiingo";

export async function fetchDaily(ticker) {
  const key = process.env.TIINGO_API_KEY;
  if (!key) return null;
  const to = new Date();
  const from = new Date(to);
  from.setFullYear(from.getFullYear() - 5);
  const fmt = (d) => d.toISOString().slice(0, 10);
  const url =
    `https://api.tiingo.com/tiingo/daily/${encodeURIComponent(ticker)}/prices` +
    `?startDate=${fmt(from)}&endDate=${fmt(to)}&format=json&token=${key}`;
  const res = await fetchWithTimeout(url, { timeoutMs: 8000, headers: { Accept: "application/json" } });
  const json = await res.json();
  if (!Array.isArray(json) || !json.length) return null;
  return normalizeSeries(
    json.map((r) => ({ date: String(r.date).slice(0, 10), close: r.adjClose ?? r.close, volume: r.adjVolume ?? r.volume }))
  );
}
