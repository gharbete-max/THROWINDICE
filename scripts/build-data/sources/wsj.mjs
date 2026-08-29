// Layer — Wall Street Journal market-data CSV download. No key. Same
// publisher family as MarketWatch (both Dow Jones) but a different host,
// path, and CSV shape — a genuinely separate failure domain, not just a
// retry of the MarketWatch layer.
import { fetchWithTimeout } from "../lib/fetchWithTimeout.mjs";
import { normalizeSeries } from "../lib/normalize.mjs";

export const name = "wsj";

export async function fetchDaily(ticker) {
  const to = new Date();
  const from = new Date(to);
  from.setFullYear(from.getFullYear() - 5);
  const fmt = (d) => `${d.getMonth() + 1}/${d.getDate()}/${d.getFullYear()}`;
  const url =
    `https://www.wsj.com/market-data/quotes/${encodeURIComponent(ticker)}/historical-prices/download` +
    `?MOD=mw_quote&startDate=${fmt(from)}&endDate=${fmt(to)}`;
  const res = await fetchWithTimeout(url, { timeoutMs: 8000, headers: { Accept: "text/csv,*/*", Referer: "https://www.wsj.com/" } });
  const text = await res.text();
  if (!text.includes(",") || /<html/i.test(text)) return null;
  const lines = text.trim().split("\n").slice(1);
  const rows = lines.map((line) => {
    // WSJ's columns: Date, Open, High, Low, Close, Volume (headers can
    // carry stray spaces, hence the trim below).
    const cols = line.split(",").map((c) => c.trim());
    const [date, , , , close, volume] = cols;
    return { date: toISO(date), close: Number(close), volume: Number(volume) };
  });
  return normalizeSeries(rows);
}

function toISO(mdY) {
  const [m, d, y] = String(mdY).split("/");
  if (!y) return "";
  return `${y}-${m.padStart(2, "0")}-${d.padStart(2, "0")}`;
}
