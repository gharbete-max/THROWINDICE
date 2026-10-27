# build-data — free monthly facts pipeline

`node scripts/build-data/index.mjs` fetches daily prices for every ticker in
`tickers.mjs` and writes `data/facts.json`: per ticker, price change over
1/3/5 years, 3-year annualised volatility, worst peak-to-trough fall, 3-month
average volume and 60 monthly closes — each with an as-of date. No scores, no
forecasts, no prose. Nothing in the site calls an API at runtime; GitHub
Actions runs this on the 1st of each month and commits the result.

## Fallback chain

Each ticker walks these in order until one returns a plausible ≥400-point
series (`lib/normalize.mjs`). Keyed layers are skipped when their env var is
unset.

| # | Source | Key |
|---|---|---|
| 1 | Stooq CSV | no |
| 2–4 | Yahoo chart (query1, query2) and spark | no |
| 5 | stockanalysis.com | no |
| 6 | Nasdaq | no |
| 7–8 | MarketWatch, WSJ CSV | no |
| 9–12 | FMP, Tiingo, Twelve Data, Alpha Vantage | `FMP_API_KEY` etc. |
| 13 | last-known-good `data/cache/<TICKER>.json` | — |

`data/run-report.json` records which layer won per ticker and what was stale.
Last real run: everything resolved on Yahoo; Stooq is blocked from Actions IPs;
layers 5–8 are untested against live traffic.

## Caveats

- Closes are adjusted (dividends folded in) when the source provides it.
- A value is `null` when the series is too short (e.g. 5-year change on a
  ~5-year cache). The site shows "—", never zero.
- Country indices are tracked through a single-country ETF, labelled as such.
- Fees are not here; they are kept beside their issuer source in the site.
- New tickers only get data once the Action (or a networked run) fetches them.
