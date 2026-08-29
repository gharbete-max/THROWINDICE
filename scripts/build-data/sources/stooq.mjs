// Layer 1 — Stooq. No key, no signup, a plain CSV download. Historically
// the most reliable fully-anonymous source for US-listed tickers, so it
// goes first. Symbol format: lowercase ticker + ".us".
import { fetchWithTimeout } from "../lib/fetchWithTimeout.mjs";
import { normalizeSeries } from "../lib/normalize.mjs";

export const name = "stooq";

export async function fetchDaily(ticker) {
  const sym = `${ticker.toLowerCase()}.us`;
  const url = `https://stooq.com/q/d/l/?s=${encodeURIComponent(sym)}&i=d`;
  const res = await fetchWithTimeout(url, { timeoutMs: 8000 });
  const text = await res.text();
  if (!text || /^Not Found|No data/i.test(text.trim())) return null;
  const lines = text.trim().split("\n").slice(1); // drop header row
  const rows = lines.map((line) => {
    const [date, , , , close, volume] = line.split(",");
    return { date, close: Number(close), volume: Number(volume) };
  });
  return normalizeSeries(rows);
}
