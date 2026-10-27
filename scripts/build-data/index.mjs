#!/usr/bin/env node
// Entry point — run monthly by .github/workflows/monthly-data.yml, or by hand:
// `node scripts/build-data/index.mjs`. Walks the fallback chain for every
// ticker in tickers.mjs, turns each series into plain facts (price change,
// volatility, worst fall, average volume) and writes data/facts.json.
import { writeFile, mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { TICKERS } from "./tickers.mjs";
import * as stooq from "./sources/stooq.mjs";
import * as yahooQ1 from "./sources/yahooChartQ1.mjs";
import * as yahooQ2 from "./sources/yahooChartQ2.mjs";
import * as yahooSpark from "./sources/yahooSpark.mjs";
import * as stockanalysis from "./sources/stockanalysis.mjs";
import * as nasdaq from "./sources/nasdaq.mjs";
import * as marketwatch from "./sources/marketwatch.mjs";
import * as wsj from "./sources/wsj.mjs";
import * as fmp from "./sources/fmp.mjs";
import * as tiingo from "./sources/tiingo.mjs";
import * as twelvedata from "./sources/twelvedata.mjs";
import * as alphavantage from "./sources/alphavantage.mjs";
import * as cacheLayer from "./sources/cache.mjs";
import { validateSeries } from "./lib/normalize.mjs";
import { computeFacts } from "./lib/facts.mjs";

// Ranked fallback chain. Order matters: cheapest/most-reliable-first,
// keyed layers (which no-op without their secret) near the end, the
// committed cache as the floor that never fails outright.
const LAYERS = [stooq, yahooQ1, yahooQ2, yahooSpark, stockanalysis, nasdaq, marketwatch, wsj, fmp, tiingo, twelvedata, alphavantage, cacheLayer];

const report = { generatedAt: new Date().toISOString(), layers: LAYERS.map((l) => l.name), tickers: {} };

async function fetchTicker(ticker) {
  for (const layer of LAYERS) {
    try {
      const series = await layer.fetchDaily(ticker);
      if (series && validateSeries(series)) {
        const stale = layer.name === cacheLayer.name;
        report.tickers[ticker] = { layer: layer.name, points: series.length, stale };
        if (!stale) await cacheLayer.writeCache(ticker, series);
        return series;
      }
    } catch (e) {
      // Expected — this is exactly what the fallback chain exists for.
      // Logged at debug level only; a ticker that eventually succeeds
      // further down the chain isn't a real problem.
      if (process.env.BUILD_DATA_VERBOSE) console.warn(`[${layer.name}] ${ticker}: ${e.message}`);
    }
  }
  report.tickers[ticker] = { layer: null, points: 0, stale: false, failed: true };
  console.error(`[build-data] every layer failed for ${ticker} (including the cache — never fetched before)`);
  return null;
}

// Small concurrency pool — independent tickers fetch in parallel, but
// each ticker's own fallback chain still runs its layers in order.
async function pMap(items, fn, concurrency = 6) {
  const results = new Array(items.length);
  let i = 0;
  async function worker() {
    while (i < items.length) {
      const idx = i++;
      results[idx] = await fn(items[idx], idx);
    }
  }
  await Promise.all(Array.from({ length: Math.min(concurrency, items.length) }, worker));
  return results;
}

const tickerPromises = new Map();
function seriesFor(ticker) {
  if (!tickerPromises.has(ticker)) tickerPromises.set(ticker, fetchTicker(ticker));
  return tickerPromises.get(ticker);
}

async function main() {
  const facts = {};
  const all = Object.entries(TICKERS).flatMap(([group, list]) => list.map((t) => [t, group]));
  await pMap(all.map(([t]) => t), seriesFor, 6);
  for (const [ticker, group] of all) {
    const series = await seriesFor(ticker);
    if (series) facts[ticker] = { group, ...computeFacts(series) };
  }

  const output = { generatedAt: new Date().toISOString(), facts };
  const here = fileURLToPath(import.meta.url);
  const outPath = path.resolve(here, "../../../data/facts.json");
  await mkdir(path.dirname(outPath), { recursive: true });
  await writeFile(outPath, JSON.stringify(output) + "\n");

  const reportPath = path.resolve(here, "../../../data/run-report.json");
  await writeFile(reportPath, JSON.stringify(report, null, 2) + "\n");

  const values = Object.values(report.tickers);
  const failed = values.filter((t) => t.failed).length;
  const stale = values.filter((t) => t.stale).length;
  console.log(`[build-data] wrote ${outPath}: ${Object.keys(facts).length}/${all.length} tickers — ${failed} failed on every layer, ${stale} served from stale cache.`);
}

main().catch((e) => {
  console.error("[build-data] fatal:", e);
  process.exitCode = 1;
});
