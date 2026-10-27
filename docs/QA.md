# QA report — 2026-10-27

Headless Chromium (Playwright), `index.html` opened from disk. Everything below was actually run.

## Passed
- Static: 0 duplicate IDs, 0 broken `#` links, 0 undefined inline handlers, every `target=_blank` link has `noopener`, `node --check` on the script.
- 0 console or page errors in every run below.
- Dark and light × Real and Token × 390 / 820 / 1280 px: no horizontal overflow; every visible text node meets WCAG AA (4.5:1, 3:1 for 24px+) in its default state.
- Theme toggle persists after reload; follows `prefers-color-scheme` on first load.
- All 6 bottom-nav buttons in each world land on their section (Token "Issuance" was broken in V31, fixed).
- Quick Tour opens in each world with the right content, focuses its button, closes on Escape.
- Portal overlay contains no text. With reduced motion it finishes in about 45 ms.
- Save / unsave, profile list, persistence across reload, remove, Escape to close, copy list.
- Region filter (Europe shows 5 of 11).
- Fund page: four questions render with real numbers; missing data shows a dash.

## Not tested
- Hover, active, disabled and placeholder contrast states.
- Real screen reader; keyboard focus appeared on the first 8 tab stops but full keyboard-only use of every control was not exercised.
- Safari / Firefox; real phones.
- Clipboard path in a secure context (fallback prompt exists).
- Chart and card values were not independently verified against a second source.

## Known limits
- Fees come from V31's issuer-page citations dated 26 Oct 2026; re-verify before relying on them.
- Facts come from a free Yahoo-based pipeline (one ticker, IRBO, served from stale cache on the last run).
- Token World figures are V31's dated snapshots; the pipeline has no token data yet.
- Buy links are placeholders (`example.com`).

## Update — colourful rebuild
- Market stats (last year, worst fall, bumpiness, volume, price path) removed from the page; `data/facts.json` is still refreshed monthly but not shown.
- Loud colour-block design restored (lime, magenta, amber, cyan, rose, purple; cooler set in Token World), black/white page background, light/dark toggle.
- "Where to buy" opens a modal with placeholder broker names (Interactive Brokers, DEGIRO, Trading 212; Coinbase, Kraken, Binance) linking to their plain homepages. No affiliate tags.
- Re-run after the change: no console errors, no overflow, no contrast failures (dark/light × Real/Token × 390/820/1280); buy modal, saved list, fund tiles, Quick Tour and nav work.

## Update — candy and motion
- Cards are neutral again; colour lives in glossy "candy" accents (icon orbs, buttons, tags, active nav, filters). Gel highlights on pills, gumdrop highlights on circles.
- Motion: scroll-reveal pop-in (staggered), bobbing orbs, jelly squash on hover, sheen sweep across candy buttons, bouncing nav icon, star pop, floating coin. All skipped with `prefers-reduced-motion`.
- Re-checked: no console errors, no overflow, no contrast failures; buy modal, saved list, tiles, tour and nav still work.
