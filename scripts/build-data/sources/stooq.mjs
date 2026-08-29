// Layer 1 — Stooq. No key, no signup, a plain CSV download. Historically
// the most reliable fully-anonymous source for US-listed tickers, so it
// goes first. Symbol format: lowercase ticker + ".us".
//
// Observed: failed for 100% of tickers on the first real GitHub Actions
// run (see data/run-report.json), while every other layer worked fine
// from the same runner. A uniform, ticker-independent failure like that
// usually means Stooq is rate-limiting or blocking the shared GitHub
// Actions IP ranges outright, not a code bug on our end — a Referer
// header (added below) is a reasonable, low-cost thing to try, but an
// IP-range block wouldn't be fixable from here even if that's the cause.
// Kept as layer 1 anyway: harmless if it keeps failing (layer 2 catches
// it in under a second), and it may well work fine from a non-GH-Actions
// runner or if Stooq's blocklist changes.
import { fetchWithTimeout } from "../lib/fetchWithTimeout.mjs";
import { normalizeSeries } from "../lib/normalize.mjs";

export const name = "stooq";

export async function fetchDaily(ticker) {
  const sym = `${ticker.toLowerCase()}.us`;
  const url = `https://stooq.com/q/d/l/?s=${encodeURIComponent(sym)}&i=d`;
  const res = await fetchWithTimeout(url, { timeoutMs: 8000, headers: { Referer: "https://stooq.com/", Origin: "https://stooq.com" } });
  const text = await res.text();
  if (!text || /^Not Found|No data/i.test(text.trim())) return null;
  const lines = text.trim().split("\n").slice(1); // drop header row
  const rows = lines.map((line) => {
    const [date, , , , close, volume] = line.split(",");
    return { date, close: Number(close), volume: Number(volume) };
  });
  return normalizeSeries(rows);
}
