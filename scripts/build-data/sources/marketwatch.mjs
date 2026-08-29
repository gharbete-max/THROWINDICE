// Layer 7 — MarketWatch's CSV download endpoint. No key. Session-shaped
// (it can return an HTML page instead of CSV if it doesn't like the
// request), so this is treated as a low-priority, best-effort layer.
import { fetchWithTimeout } from "../lib/fetchWithTimeout.mjs";
import { normalizeSeries } from "../lib/normalize.mjs";

export const name = "marketwatch";

export async function fetchDaily(ticker) {
  const to = new Date();
  const from = new Date(to);
  from.setFullYear(from.getFullYear() - 5);
  const fmt = (d) => `${d.getMonth() + 1}/${d.getDate()}/${d.getFullYear()}`;
  const url =
    `https://www.marketwatch.com/investing/fund/${encodeURIComponent(ticker.toLowerCase())}/downloaddatapartial` +
    `?startdate=${fmt(from)}%2000:00:00&enddate=${fmt(to)}%2000:00:00&daterange=d30&frequency=p1d&csvdownload=true&downloadpartial=false&newdates=false`;
  const res = await fetchWithTimeout(url, { timeoutMs: 8000, headers: { Accept: "text/csv,*/*" } });
  const text = await res.text();
  if (!text.includes(",") || /<html/i.test(text)) return null;
  const lines = text.trim().split("\n").slice(1);
  const rows = lines.map((line) => {
    const cols = line.split(",");
    const [date, , , , close, volume] = cols;
    return { date: toISO(date), close: Number(String(close).replace(/[$,]/g, "")), volume: Number(String(volume ?? "").replace(/,/g, "")) };
  });
  return normalizeSeries(rows);
}

function toISO(mdY) {
  const [m, d, y] = String(mdY).split("/");
  if (!y) return "";
  return `${y}-${m.padStart(2, "0")}-${d.padStart(2, "0")}`;
}
