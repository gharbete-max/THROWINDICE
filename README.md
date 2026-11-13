# throwindice

**Investing, simply.** An index-focused atlas of ETFs, commodities and tokenized assets, plus **Live Ball Bounce**: a one-finger runner game where you ride a candle chart and swipe your position (long, short, cash, all in).

Educational, not financial advice: no forecasts, no scores, no individual stocks, only dated and sourced facts. Two worlds: **Real World** and **Token World**.

## Run it

`index.html` is a single self-contained file. Open it, or serve the folder with any static host (`python3 -m http.server`). No build step. Light and dark follow the system.

## Where things are

| | |
|---|---|
| `docs/HANDOFF.md` | **Start here.** What exists and the ordered work queue. |
| `docs/AUDIT-2026-11.md` | Usability and code audit, and where the project goes. |
| `CLAUDE.md` | Rules for working in the repo: editing, testing, rendering, 60 fps, brand. |
| `docs/MARKET.md`, `docs/BALANCE.md`, `docs/ANIMATION.md` | Game design, balance targets and the balance harness, animation rules. |
| `docs/QA.md`, `docs/UPDATING.md` | Site QA log, content updates. |
| `scripts/icons/` | Blender generators for every 3D asset (runner, bull, notes, hero, logo). |
| `scripts/brand/` | Logo, wordmark, favicons, app icons, share image. |
| `scripts/balance/sim.js` | Bot harness for the game economy. |
| `scripts/build-data/` | Monthly refresh of `data/facts.json` (GitHub Actions). |
| `docs/archive/` | Finished plans and history. |

## Deploy

GitHub Pages via GitHub Actions. The owner has to enable it once: **Settings → Pages → Source: GitHub Actions**, then re-run the Deploy workflow. The site will be at `https://gharbete-max.github.io/throwindice/`.
