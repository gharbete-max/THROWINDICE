// Layer 5 — stockanalysis.com's public JSON API (the same data their own
// charts fetch). No key. Unofficial and can change shape without notice —
// that's fine, it's one of many layers, not a load-bearing one.
import { fetchWithTimeout } from "../lib/fetchWithTimeout.mjs";
import { normalizeSeries } from "../lib/normalize.mjs";

export const name = "stockanalysis";

export async function fetchDaily(ticker) {
  const url = `https://stockanalysis.com/api/symbol/e/${encodeURIComponent(ticker)}/history?range=2Y&period=Daily`;
  const res = await fetchWithTimeout(url, { timeoutMs: 8000, headers: { Referer: "https://stockanalysis.com/" } });
  const json = await res.json();
  const rows = json?.data ?? json?.body ?? [];
  if (!Array.isArray(rows) || !rows.length) return null;
  const mapped = rows.map((r) => ({
    date: (r.date ?? r.d ?? "").slice(0, 10),
    close: Number(r.close ?? r.c ?? r.adjClose),
    volume: Number(r.volume ?? r.v),
  }));
  return normalizeSeries(mapped);
}
