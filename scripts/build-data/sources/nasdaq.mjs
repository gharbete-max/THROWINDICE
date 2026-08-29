// Layer 6 — Nasdaq's own public quote API. No key, but it 403s without a
// browser-shaped request (Origin/Referer + Accept), so those are set
// explicitly here rather than relying on the shared default headers.
import { fetchWithTimeout } from "../lib/fetchWithTimeout.mjs";
import { normalizeSeries } from "../lib/normalize.mjs";

export const name = "nasdaq";

export async function fetchDaily(ticker) {
  const to = new Date();
  const from = new Date(to);
  from.setFullYear(from.getFullYear() - 5);
  const fmt = (d) => d.toISOString().slice(0, 10);
  const url = `https://api.nasdaq.com/api/quote/${encodeURIComponent(ticker)}/historical?assetclass=etf&fromdate=${fmt(from)}&todate=${fmt(to)}&limit=9999`;
  const res = await fetchWithTimeout(url, {
    timeoutMs: 8000,
    headers: { Accept: "application/json", Origin: "https://www.nasdaq.com", Referer: "https://www.nasdaq.com/" },
  });
  const json = await res.json();
  const rows = json?.data?.tradesTable?.rows;
  if (!Array.isArray(rows) || !rows.length) return null;
  const mapped = rows.map((r) => ({
    date: toISO(r.date),
    close: Number(String(r.close ?? "").replace(/[$,]/g, "")),
    volume: Number(String(r.volume ?? "").replace(/,/g, "")),
  }));
  return normalizeSeries(mapped);
}

function toISO(mdY) {
  // Nasdaq returns "MM/DD/YYYY".
  const [m, d, y] = String(mdY).split("/");
  if (!y) return "";
  return `${y}-${m.padStart(2, "0")}-${d.padStart(2, "0")}`;
}
