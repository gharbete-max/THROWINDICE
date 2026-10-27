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

## Update — kitten sliders and Basics page
- All range inputs are wrapped: a kitten pushes a rolling ball (right) or drags it back (left); the native input stays underneath so mouse, touch and arrow keys work. Verified by drag (right then left flips the kitten, `moving` toggles), keyboard (Arrow key moves years), and Reset.
- "Fees" is now "Basic skills for saving and investing": fee calculator, the four big questions, and one "Why people invest at all" block (inflation, alternative cost, pensions).
- Re-run: no console errors, no overflow, no contrast failures, no duplicate IDs; buy modal, saved list, tour and nav still work.

## Update — fund list, kittens under the track, typical-fund calculator
- ETF page is now a filterable list of 25 funds (10 with sourced fees; 15 added with no fee and a "check the fund page" note). Clicking a fund shows what is inside, the four questions, and links to justETF / etf.com / stockanalysis holdings / provider. Reviewed quarterly; the monthly price job no longer runs on a schedule.
- UCITS entries carry justETF ISIN links only where the ISIN is certain (VWCE, SWDA, CSPX, EIMI, EQQQ, SGLN); other links are searches or per-ticker URLs and were not click-tested from this sandbox.
- Token cards: added Solana, Chainlink, Paxos Gold, Tether Gold (links to their official sites, not click-tested).
- Calculator starts at a typical fund: 7% growth (a guess; S&P 500 about 10% since 1928, world stocks about 8% since 1970, sources differ) and 0.14% cost (ICI average for index equity ETFs). Figures came from search results; the source pages could not be fetched from this sandbox.
- Kittens moved under the track so the slider no longer covers them.

## Update — tiles lead to ETFs, smug cat, hanging kittens
- Every tile (countries, sectors, themes, commodities, token cards, token category detail) opens the ETF page filtered to that theme (39 themes, each checked to show exactly its listed funds). Token tiles leave Token World through the portal first. "Show all funds" or any category pill clears the filter.
- ETF list grew to 92 funds (10 with sourced fees, the rest linking out). Crypto tiles map to spot bitcoin/ether funds or blockchain-company funds; stablecoin and tokenized-fund tiles map to short T-bill funds as "cousins", with a note that they are not the tokens.
- Smug cat with glasses and a toothy grin guides the ETF page.
- Kittens now hang from the yarn balls. Ball follows the slider with a spring; the cat swings as a damped pendulum with paw friction, heavier than a free pendulum, clamped to about ±60° (measured peak ≈ 50° on a very fast drag; settles in ≤ 250 ms).
- Re-run: no console errors, no overflow, no contrast failures, no duplicate IDs, nav lands.

## Update — glued sliders, awkward dog, clickable fund tiles, TradingView charts
- Ball now sits exactly on the slider thumb (measured gap ≤ 0.3 px while dragging, at rest and with the keyboard). Only the cat has physics (pendulum driven by the ball's smoothed acceleration; peak ≈ 30–50° on a very fast drag).
- Smug cat replaced by an awkward dog (dot eyes, no glasses, tongue out, animated drool).
- Fund tiles are fully clickable and open the details panel with links; token and theme tiles open their ETF lists.
- "Show chart" (US-listed ETFs) and "📈 Chart" (BTC, ETH, SOL, LINK, PAXG, XAUT) open a TradingView mini chart in a modal; it loads only on click. Verified in headless Chromium for SPY, IBIT, EWG, FBTC, BTC and XAUT (real data rendered); UCITS funds and ETCs have no chart button. If the host blocks the script (e.g. the claude.ai preview) the modal shows a fallback message and a TradingView link.
