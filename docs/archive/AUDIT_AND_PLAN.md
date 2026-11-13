# THROWINDICE — audit, brainstorm, plan

Audit date: 2026-10-27. Sources: the repo as found (the old "Isobar" app) and the V31 prototype from the master prompt.

## 1. What THROWINDICE is

A dumbed-down, index-focused atlas: read about ETFs, indices, commodities and tokenized assets in one sentence each, save what you like, and click through to a broker to buy. Think Yahoo Finance with 90% removed. No individual stocks, no forecasts, no scores, no opinions. Only dated, sourced facts.

## 2. Audit: what exists

### A. `throwindice.html` (V31 + saved profile, from PR #6)

Static checks, run on the V31 source:

| Check | Result |
|---|---|
| Duplicate IDs | 0 |
| Broken `#` links | 0 |
| Undefined inline handlers | 0 |
| `getElementById` targets missing | 0 |
| `node --check` on the script | passes |
| External links | 44, all with `rel=noopener`, no `javascript:` URLs |
| Network calls (`fetch`) | 0 (fully offline, static snapshot) |

Problems found:

| # | Problem | Why it matters |
|---|---|---|
| 1 | 9 `<style>` blocks, 86 KB CSS, **778 `!important`**, the same selectors redefined up to 18 times (`.active`, `.shell`, `.navbtn` …) | Every change fights earlier layers. Root cause of the light-mode black-on-black hero. |
| 2 | Lime / magenta / rose per-card gradients and glows | The spec forbids them; the user wants calm palettes. |
| 3 | No theme toggle. Only `prefers-color-scheme` (11 queries) | Spec requires a light/dark switch. |
| 4 ✅ | Only 1 `aria-expanded`, 1 `tabindex`, clickable `div.exploreCard` | Keyboard and screen-reader gaps. |
| 5 | Real World is one long page, `body.token-world` hides the rest with `display:none!important` | Works, but fragile. Nav is a 6-button bottom bar where "Dashboard" is a raised centre button. |
| 6 ✅ | Copy is jargon-heavy ("bid–ask spread", "benchmark / focus", "holdings-based valuation") | Opposite of "simpletons understand". |
| 7 ✅ | Four Fs card shows labels only ("Historical volatility & drawdown") with **no numbers** | Looks empty. The repo has real data to fill it (see B). |
| 8 ✅ | Fund list = 10 ETFs only. The bar says "SOURCED SNAPSHOTS · NOT LIVE QUOTES", the page says "CONCEPT" | Needs the indices-first catalogue, and honest labelling kept. |
| 9 | Fonts load from Google Fonts | One external request. Fine, but not "fully offline". |
| 10 | Inline `onclick` everywhere, ~18 KB of JS with data mixed into the logic | Hard to extend. Move data into one JSON block. |

Good, keep: logo SVGs, coin toggle, portal swirl, bounce animations (`.bounce-click`), loading skeleton, Quick Tour, token-world content, news cards, fee calculator, data-label discipline (dates + sources).

### B. The repo as found (Isobar, React/Vite PWA)

| Part | What it is | Verdict |
|---|---|---|
| `src/` (React screens, components, `weather.ts`, `build.ts`, mock data) | "Market weather" UI, 0-100 scores, Holt forecast, mood copy | **Delete.** Forecast, opinion and a composite score are explicitly out. |
| `package.json`, `vite.config.ts`, `tsconfig*`, `.oxlintrc.json`, `package-lock.json` (228 KB), `public/` | React 19, router, PWA, TypeScript toolchain | **Delete.** THROWINDICE is one self-contained HTML file; no build. Recoverable from git history. |
| `scripts/build-data/sources/*` (13 fallback price sources) | Keyless Yahoo/Stooq/Nasdaq/… fetchers, last-good cache floor | **Keep.** This is the valuable part. |
| `scripts/build-data/lib/normalize.mjs`, `fetchWithTimeout.mjs` | Series validation, timeouts | **Keep.** |
| `scripts/build-data/lib/scoring.mjs`, `holtwinters.mjs` | Scores and forecast | **Delete.** |
| `scripts/build-data/content.mjs` (families, "head/intro/body" prose, `FEES`) | Opinionated copy, unsourced hand-typed fees | **Delete the prose and fees.** Keep only the ticker lists. |
| `scripts/build-data/holdings.mjs` | Hand-typed "top 5 holdings" with weights | **Delete.** Unsourced numbers (breaks "never invent") and individual stocks. |
| `scripts/build-data/learn.mjs` | Educational blurbs | Delete. Rewrite from scratch in plain words. |
| `data/cache/*.json` (67 tickers, 5 years of daily close + volume, 5.3 MB) | Real price history | **Keep.** Source for real Fluctuation and Flow numbers. |
| `.github/workflows/monthly-data.yml` | Free monthly refresh, commits data | **Keep, adapt** (new output file, rename the bot, add the inject step). |
| `data/run-report.json` | Which source won per ticker | Keep. |

Known pipeline caveat (from its own README): every ticker resolved on Yahoo (layer 2), Stooq is blocked from Actions IPs, and layers 5–8 were never exercised live. Prices use ETF proxies for country indices (SPY for the S&P 500, EWG for DAX, …). That is acceptable if labelled "tracked by this ETF".

Gap: the cache has the theme/country ETFs, but **not V31's ten funds** (VT, VOO, BND, AGG, GLD, IAU, VWO, IEMG, VGT, QQQM) nor any commodity or token series. The pipeline needs those tickers added.

## 3. Brainstorm

**Identity:** "The one-sentence market." Every card answers *What is it? What does it cost? How bumpy was it? Easy to trade?* and then offers **Save** and **Where to buy**.

Creative:
1. **Four plain questions** replace the Four Fs on every fund: *Is the price fair? What does it cost? How bumpy? Easy to trade?* Each answer is a number plus a 4-word label, and a "?" for the one-line explanation.
2. **Bumpiness meter:** a 5-dot row (●●●○○) derived from real volatility bands, with the number next to it. A fact bucketed, not a score.
3. **"Ride" sparkline:** 5-year line from the cached closes, so beginners see what "bumpy" looks like.
4. **Cost in euros:** "€10,000 in this fund costs about €6 a year." Replaces percentages for beginners (keeps % beside it).
5. **Index cards over fund cards:** the headline is "World stocks", "US stocks", "Gold", "Global bonds"; the specific ETFs hang underneath as "ways to own it".
6. **Real-world / Token coin toggle** stays as the signature move. Token cards use the same layout so a beginner learns one pattern.
7. **Saved = "My list":** star anywhere, one panel, buy links per item, share/export as text. Local only, no accounts.
8. **Compare two:** pick two saved funds, see cost, bumpiness and size side by side. (Later.)
9. **Bouncy motion** kept, but respects reduced motion.

Functional:
- One `data` JSON block (instruments, fees, sources, dates) rendered by small functions; no copy-pasted card HTML.
- Real numbers from the pipeline for Fluctuation (annualised volatility, worst fall) and Flow (average daily volume). **Never** a combined score.
- Buy links go through one function so affiliate URLs are swapped in one place, always `rel="sponsored"`, always disclosed.
- A theme toggle (light/dark) and the two accent palettes as CSS tokens.

## 4. Plan

| Step | Work | Output |
|---|---|---|
| 0 | This audit | `docs/AUDIT_AND_PLAN.md` |
| 1 ✅ | Remove the Isobar app and its toolchain; rename everything to THROWINDICE; `throwindice.html` becomes `index.html` | Clean repo |
| 2 ✅ | Trim the pipeline: drop scoring/forecast/holdings/prose; emit `data/facts.json` with 1y/3y/5y price change, volatility, worst fall, average volume per ticker, each with an as-of date. Add V31's ten funds + a handful of commodity ETFs to the ticker list | Real numbers, no opinion |
| 3 ✅ | Rebuild the CSS as a token system: pure black/white, calm green and blue accent, no gradients, theme toggle, real focus states. Delete the 778 `!important` layers | One small stylesheet |
| 4 ✅ | Move content into one JSON block; plain-word copy (one sentence per card, "More" for detail); index-first catalogue | Simple content |
| 5 ✅ | Fund page: four plain questions with real numbers from `facts.json` + 5-year ride sparkline + cost in euros | Fills the empty Four Fs |
| 6 ✅ | My list: stars everywhere, share/export, affiliate hook | Profile v2 |
| 7 ✅ | Token World: same card layout, dated sourced numbers, verified issuer docs | Token parity |
| 8 ✅ | QA: both worlds × both themes × 3 widths, keyboard, reduced motion, contrast, offline | Report |

Open items that need the owner, not me: real affiliate programs and URLs, and a final domain.
