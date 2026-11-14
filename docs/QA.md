# QA checklist

Run before every push that touches `index.html`. History of past rounds: `docs/archive/QA-2026-10.md`.

- **Headless run** (recipe in `CLAUDE.md`): 0 `pageerror`, 0 4xx, at 390 px and 1280 px, light and dark.
- **Pages:** Home, World, Sectors, Commodities, ETF explorer, Tokens, Basics, Fees, Menu: no horizontal overflow; text meets WCAG AA.
- **Funds:** a pile opens the fund cards; "Full details" opens the sheet over them; Back and Escape return to the cards.
- **Game:** `#play` opens it; a run starts on Start; swipes (long/short/cash/all in) switch the runner; the results card shows the run log, "Learn why →" and Share.
- **Reduced motion** (`reducedMotion:'reduce'`): no looping animation, hero shows the poster frame.
- **CSS-only changes:** screenshot every page in light and dark before and after; they must be pixel-identical unless the change is meant to be visible.
- **Gameplay numbers:** `node scripts/balance/sim.js 120 passive,trader,reader 4`, all rows PASS (`BALANCE.md`).
- `_test.html` deleted, never committed.

## Known limits

- Not tested on Safari/Firefox or real phones by the cloud sessions; no real screen reader pass.
- Fund facts come from the free Yahoo-based pipeline (`docs/UPDATING.md`); fees are dated issuer-page citations. Re-verify before relying on them.
