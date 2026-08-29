#!/usr/bin/env node
// Entry point — run monthly (see ../../.github/workflows/monthly-data.yml,
// or by hand: `node scripts/build-data/index.mjs` from app/). Walks the
// fallback chain for every ticker the dataset needs, scores 24 months of
// real history per instrument, fits a Holt forecast, and writes
// src/data/generated.json in the exact shape src/data/types.ts expects.
//
// See README.md in this folder for the full picture — the ranked source
// list, the documented approximations (breadth, index-as-ETF-proxy), and
// how to flip the app over from the mock dataset to this output.
import { writeFile, mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { FAMILIES, COUNTRIES, MACRO, FEES, HOLDINGS, LEARN } from "./content.mjs";
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
import { scoreAsOf, monthEnds, blendSeries, describeMonth } from "./lib/scoring.mjs";
import { holtForecast } from "./lib/holtwinters.mjs";

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

/** 24 months of real, honestly-windowed composite scores + this month's
 * factor breakdown + a Holt forecast, from one daily price series. */
function computeInstrument(dailySeries) {
  const candidateEnds = monthEnds(dailySeries, 30); // pad — some early ones may lack lookback
  const hist = [];
  let lastFactors = null;
  for (const row of candidateEnds) {
    const idx = dailySeries.findIndex((r) => r.date === row.date);
    const windowed = dailySeries.slice(0, idx + 1);
    if (windowed.length < 70) continue; // not enough trailing data to score honestly yet
    const { temp, f } = scoreAsOf(windowed);
    hist.push(temp);
    lastFactors = f;
  }
  const trimmed = hist.slice(-24);
  const temp = trimmed[trimmed.length - 1];
  const delta = trimmed.length >= 2 ? temp - trimmed[trimmed.length - 2] : 0;
  const forecast = holtForecast(trimmed);
  return {
    temp,
    delta,
    f: lastFactors,
    hist: trimmed,
    forecast: forecast ?? undefined,
    line: describeMonth({ temp, delta, f: lastFactors }),
  };
}

async function buildTheme(t) {
  const tickers = t.etfs.split("·").map((s) => s.trim()).filter(Boolean);
  const fetched = (await pMap(tickers, seriesFor)).filter(Boolean);
  if (!fetched.length) {
    console.error(`[build-data] theme "${t.key}": no ticker resolved (${tickers.join(", ")}) — omitted from this run`);
    return null;
  }
  const blended = fetched.length > 1 ? blendSeries(fetched) : fetched[0];
  if (blended.length < 260) {
    console.error(`[build-data] theme "${t.key}": blended series too short after alignment — omitted`);
    return null;
  }
  return { key: t.key, emoji: t.emoji, name: t.name, proxy: t.proxy, etfs: t.etfs, ...computeInstrument(blended) };
}

async function buildCountry(c) {
  const s = await seriesFor(c.proxyTicker);
  if (!s) {
    console.error(`[build-data] country "${c.key}": proxy ticker ${c.proxyTicker} unresolved — omitted from this run`);
    return null;
  }
  return { key: c.key, emoji: c.emoji, name: c.name, proxy: c.proxy, etfs: "", ...computeInstrument(s) };
}

async function main() {
  const allTickers = [
    ...FAMILIES.flatMap((F) => F.themes.flatMap((t) => t.etfs.split("·").map((s) => s.trim()))),
    ...COUNTRIES.map((c) => c.proxyTicker),
  ];
  // Warm the fetch pool for every unique ticker up front (bounded
  // concurrency), so the per-theme/per-country builders below just await
  // already-in-flight promises instead of serializing on each other.
  await pMap([...new Set(allTickers)], seriesFor, 6);

  const families = [];
  for (const F of FAMILIES) {
    const themes = (await Promise.all(F.themes.map(buildTheme))).filter(Boolean);
    if (!themes.length) {
      console.error(`[build-data] family "${F.key}": every theme failed — omitted entirely`);
      continue;
    }
    families.push({ key: F.key, emoji: F.emoji, name: F.name, head: F.head, intro: F.intro, body: F.body, themes });
  }
  const countries = (await Promise.all(COUNTRIES.map(buildCountry))).filter(Boolean);

  const now = new Date();
  const asOf = `${now.getUTCFullYear()}-${String(now.getUTCMonth() + 1).padStart(2, "0")}`;
  const next = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth() + 1, 1));
  const nextReport = `1 ${next.toLocaleDateString("en-US", { month: "long", timeZone: "UTC" })}`;

  const output = { asOf, nextReport, families, countries, macro: MACRO, holdings: HOLDINGS, fees: FEES, learn: LEARN };

  const here = fileURLToPath(import.meta.url);
  const outPath = path.resolve(here, "../../../src/data/generated.json");
  await mkdir(path.dirname(outPath), { recursive: true });
  await writeFile(outPath, JSON.stringify(output, null, 2) + "\n");

  const reportPath = path.resolve(here, "../../../data/run-report.json");
  await mkdir(path.dirname(reportPath), { recursive: true });
  await writeFile(reportPath, JSON.stringify(report, null, 2) + "\n");

  const values = Object.values(report.tickers);
  const failed = values.filter((t) => t.failed).length;
  const stale = values.filter((t) => t.stale).length;
  const byLayer = {};
  for (const t of values) if (t.layer) byLayer[t.layer] = (byLayer[t.layer] ?? 0) + 1;
  console.log(`[build-data] wrote ${outPath}`);
  console.log(`[build-data] ${values.length} tickers — ${failed} failed on every layer, ${stale} served from stale cache.`);
  console.log(`[build-data] layer usage:`, byLayer);
  if (families.length < FAMILIES.length || countries.length < COUNTRIES.length) {
    console.warn(`[build-data] output is missing ${FAMILIES.length - families.length} families / ${COUNTRIES.length - countries.length} countries — see errors above.`);
  }
}

main().catch((e) => {
  console.error("[build-data] fatal:", e);
  process.exitCode = 1;
});
