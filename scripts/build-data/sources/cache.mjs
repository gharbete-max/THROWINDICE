// Layer 11 (the floor) — the last daily series that any live layer
// successfully fetched for this ticker, committed to data/cache/. If
// every live source is down the app still ships this month's numbers
// built from stale-but-real prices rather than crashing or going blank;
// the orchestrator flags the run as degraded so it's visible, not silent.
import { readFile, writeFile, mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { normalizeSeries } from "../lib/normalize.mjs";

const CACHE_DIR = path.resolve(fileURLToPath(import.meta.url), "../../../../data/cache");

export const name = "last-known-good-cache";

export async function fetchDaily(ticker) {
  try {
    const raw = await readFile(cachePath(ticker), "utf8");
    const parsed = JSON.parse(raw);
    return normalizeSeries(parsed.series ?? []);
  } catch {
    return null;
  }
}

export async function writeCache(ticker, series) {
  await mkdir(CACHE_DIR, { recursive: true });
  await writeFile(cachePath(ticker), JSON.stringify({ ticker, fetchedAt: new Date().toISOString(), series }, null, 0));
}

export async function cacheAge(ticker) {
  try {
    const raw = await readFile(cachePath(ticker), "utf8");
    return new Date(JSON.parse(raw).fetchedAt);
  } catch {
    return null;
  }
}

function cachePath(ticker) {
  return path.join(CACHE_DIR, `${ticker.toUpperCase()}.json`);
}
