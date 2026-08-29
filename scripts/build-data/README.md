# build-data — the free, layered data pipeline

Produces `src/data/generated.json` (exact shape: `src/data/types.ts`'s
`SourceRoot`) from real prices, at zero cost, once a month. This is the
answer to "how do we load ETF data without paying for it or scraping a
huge chunk every month": don't fetch live at request time at all — fetch
**once a month**, from a chain of independent free sources, and ship the
computed result as a static JSON file the app just reads. Nothing in the
running app ever calls an external API.

```
node scripts/build-data/index.mjs
```

Run from the repo root. Takes well under a minute for the full
~66-ticker dataset. `.github/workflows/monthly-data.yml` runs it
automatically on the 1st of every month via GitHub Actions (free) and
commits the result.

## The fallback chain (13 layers)

Every ticker walks this list in order until one source returns a
plausible ≥400-point daily series (`lib/normalize.mjs`'s `validateSeries`
is the gate). Most tickers resolve on layer 1 or 2; the rest exist for
the days those are down, rate-limited, or blocked.

| # | Source | Key needed? | File |
|---|---|---|---|
| 1 | Stooq CSV | no | `sources/stooq.mjs` |
| 2 | Yahoo Finance chart API (query1 host) | no | `sources/yahooChartQ1.mjs` |
| 3 | Yahoo Finance chart API (query2 host) | no | `sources/yahooChartQ2.mjs` |
| 4 | Yahoo Finance "spark" endpoint | no | `sources/yahooSpark.mjs` |
| 5 | stockanalysis.com JSON API | no | `sources/stockanalysis.mjs` |
| 6 | Nasdaq public quote API | no | `sources/nasdaq.mjs` |
| 7 | MarketWatch CSV download | no | `sources/marketwatch.mjs` |
| 8 | Wall Street Journal CSV download | no | `sources/wsj.mjs` |
| 9 | Financial Modeling Prep | free tier key | `sources/fmp.mjs` |
| 10 | Tiingo | free tier key | `sources/tiingo.mjs` |
| 11 | Twelve Data | free tier key | `sources/twelvedata.mjs` |
| 12 | Alpha Vantage | free tier key | `sources/alphavantage.mjs` |
| 13 | Last-known-good cache (`data/cache/`) | — | `sources/cache.mjs` |

Layers 9–12 are **skipped, not failed**, when their env var
(`FMP_API_KEY` / `TIINGO_API_KEY` / `TWELVEDATA_API_KEY` /
`ALPHAVANTAGE_API_KEY`) isn't set — the pipeline runs fully anonymously
on layers 1–8 + 13 out of the box. Add free-tier keys as GitHub Actions
secrets only if you want the extra redundancy; none are required.

**What actually happened on the first real run** (see
`data/run-report.json` in the repo): all 67 tickers resolved, but every
single one came from layer 2 (Yahoo) — layer 1 (Stooq) failed uniformly
across every ticker, which looks like Stooq blocking/rate-limiting the
shared GitHub Actions IP ranges rather than anything ticker-specific
(see the comment in `sources/stooq.mjs`). Left in place regardless —
harmless when it fails (costs under a second before falling through),
and it may work fine from a different runner. Layers 5–8 have not yet
been exercised for real (Yahoo has caught everything so far); their
correctness is written to match each provider's documented/observed
shape but, same caveat as before, unverified against live traffic from
this session specifically.

Layer 11 is the floor: whatever the last successful fetch for that
ticker was (committed to `data/cache/<TICKER>.json` by whichever layer
won that run), so a total outage across every live source still produces
a working app with last month's real prices rather than a crash or a
blank screen. `data/run-report.json` records which layer won for every
ticker on the last run, and how many were stale — that's your signal for
"is a source quietly rotting" over time.

**Adding another layer**: copy any file in `sources/` as a template — it
just needs to export `name` and an async `fetchDaily(ticker)` returning
`normalizeSeries(rows)` or `null`. Add it to the `LAYERS` array in
`index.mjs` wherever you want it ranked.

## Why ETF proxies for country indices

The design text says "country indices use the index itself." In
practice, raw index tickers (`^GSPC`, `^STOXX50E`, …) are inconsistently
available across free sources, while every country here has a large,
liquid, US-listed single-country ETF that free sources handle exactly
like any other ETF ticker (see `proxyTicker` in `content.mjs` — e.g. the
US uses `SPY`, Germany `EWG`, Japan `EWJ`). This is a deliberate
simplification for the zero-cost constraint, not an oversight — swap in
a real index-data provider later by changing what `computeInstrument()`
is called with; nothing else in the pipeline or the app needs to change.

## What's computed vs. hand-maintained

Real, computed from price/volume history every run:
- the five factors, the 0–100 composite, and 24 months of history
  (`lib/scoring.mjs`) — each historical month is scored using only data
  available up to that date, not smeared back from today
- the two-step-ahead forecast (`lib/holtwinters.mjs`, Holt's linear trend
  method — see below)
- the one-line monthly take (`describeMonth()` — templated, not written
  by a person; hand-edit `generated.json` after a run if you want better
  copy for a specific month)

Hand-maintained (`content.mjs`, `holdings.mjs`, `learn.mjs` — same as
`src/data/mock.ts`, just not imported by the app):
- names, emoji, tickers, family headline/body copy
- **fees** (expense ratios) — not in any price feed, and funds reprice
  rarely, so a static table is the honest choice
- **top-5 holdings** — same reasoning; a free but more-involved upgrade
  path is each fund issuer's own daily holdings CSV (e.g. State Street,
  iShares, and Global X all publish these for free per-ticker), which
  would need its own per-provider parser and isn't wired in yet

## The "broad?" factor is a proxy, not real breadth

True breadth ("% of the ~200 companies inside this ETF that rose") needs
the fund's constituent list, which isn't reliably free per-fund. What's
computed instead: % of the last 60 trading days the price closed above
its own 50-day moving average — a trend-persistence proxy at the
instrument level. It correlates with real breadth reasonably well
(broad rallies tend to also be persistent ones) but isn't the same
thing. Documented here rather than silently approximated.

## The forecast

`lib/holtwinters.mjs` fits Holt's linear trend method (level + trend, no
seasonal term) to each instrument's 24-month score history via a small
grid search, and projects two months ahead. The Method screen calls this
"Holt–Winters" in the loose sense most people mean it (any of the
Holt-family exponential smoothing methods) — a true seasonal
Holt-Winters needs a few years of monthly history to fit a trustworthy
12-month cycle, which the app won't have until it's been running a
while. Swap `holtForecast()` for a seasonal fit once there's 3+ years of
`generated.json` history to train on.

`src/lib/weather.ts`'s `scenarios()` uses this forecast when present
(real pipeline output) and falls back to a temp/factor heuristic when
it's absent (the mock dataset, which has no real trend to fit).

## Wiring it into the app

`src/data/index.ts` currently always uses the mock dataset. Once you've
run this pipeline and are happy with `src/data/generated.json`, switch
the app to it:

```ts
// src/data/index.ts
import generated from "./generated.json";
import type { SourceRoot } from "./types";
export const store = buildStore(generated as SourceRoot);
```

Left as a manual, deliberate step rather than automatic — you should
look at a month of real output before the app starts showing it.

## A note on testing this in the session that wrote it

The sandbox this pipeline was written in has an outbound network
allowlist that blocks Stooq, Yahoo, and the other data hosts by design
(only a small set of dev-tooling domains are reachable). Every *pure*
piece — scoring, Holt's method, series blending, validation — was
verified against synthetic price data and produces sane, bounded output.
The *fetch* layers themselves (URLs, headers, response parsing) are
written to match each provider's documented/observed shape as of this
writing but could not be exercised against the real network from here.
Run `node scripts/build-data/index.mjs` from a normal machine (or let
the GitHub Actions workflow do it) as the first real end-to-end check,
and watch `data/run-report.json` to see which layers actually won.
