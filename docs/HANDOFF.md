# Handoff: throwindice, Nov 13 2026

**Read this first, then `CLAUDE.md`.** One page: what exists, then the ordered queue. Finished history is in `docs/archive/HANDOFF-2026-11.md`.

## What exists

- **Site:** Apple-style glass UI, light/dark, Real World + Token World. Scroll-scrubbed 3D hero, 3D icons in list slots, ETF fund cards (fee, rates, spread, holdings). Brand: `throw·indice` wordmark, die-into-tag mark, favicons, app icons, share image (`CLAUDE.md` → Brand). First visit is ~0.85 MB.
- **Game (Live Ball Bounce):** one-finger runner on a candle chart.
  - **Positions:** ↑ long, ↓ short (1x–2x–3x ladder), ← cash, → ALL IN on a skateboard. Runs start holding LONG 1x.
  - **Market:** bull/bear phases (~25% bear), diamond bull / ruby bear checkpoints that bank P&L, chart patterns as terrain, rugpulls in Token World.
  - **Economy:** score = compounded profit, Dolla notes (1/5/20/100), wallet, hats, missions, portfolio level, Big Ball ETF.
  - **Look:** glass family. Gold glass runner with a $ coin heart, 105-frame run cycle, 24-frame tricks, 96-frame bull/bear, adaptive resolution, 60 fps.
  - **Run log:** each run's length / checkpoints / score / cause goes to `localStorage['cp-runs']` (last 20); the results card shows the last runs and the typical length.
- **Tools:** balance harness `scripts/balance/sim.js`, Blender generators `scripts/icons/`, brand build `scripts/brand/`.

## Queue (top to bottom)

Direction and reasons: `docs/AUDIT-2026-11.md` (usability U1-U9, ponytail cuts, the project's future). **The game is the front door; the atlas is the depth behind it.**

For each item: implement, test (headless harness from `CLAUDE.md`; `sim.js` for anything that moves numbers), reduced motion and 0 page errors, one commit per item, rebase on `origin/main`, push, tick it here.

| # | Item | Done when |
|---|---|---|
| 1 | **B8 balance: skill must beat standing still** (U2). Baseline Nov 13 (120 s × 4): passive 290/min, trader 119 (0.4x), reader 144 (0.5x). Cause: runs start holding LONG 1x, and bear stretches don't reliably drop. Levers: `TILT` + drift controller, `PNLK` (.0045), tick values/spacing, bear red-tick density. Passive target about 60-140/min at 120 s. ≥ 4 runs per check. *(A Claude Code session started on this at 00:04 Nov 14; check `git log` before starting it again.)* | reader ≥ 2x passive, trader ≥ 1.5x at 120 s; a passive long loses in bear stretches on average; changelog in `BALANCE.md` |
| 2 | **Owner:** turn on GitHub Pages (U1), then play 5 runs on a phone; the results card shows the typical run length (target 60-120 s). | site live; numbers in `BALANCE.md` |
| 3 | **Cut the dead layer** (ponytail #1-2): fold the 143 `body.apple` overrides into the base CSS and delete what they override; delete the hidden bottom nav, token coin, invest popup, coin bubble, spin preloaders, vignette script and the 16 `*-spin.webp`. `navGame()` uses `.navbtn[data-page=game]` as a handle: give it a direct opener. Small steps; screenshots light/dark/Token World before and after each. | about -45 KB `index.html`, -1.8 MB assets, no visual change, 0 errors |
| 4 | **No first-visit gate** (U3): guess the region from `Intl.DateTimeFormat().resolvedOptions().timeZone` / `navigator.language`, show content at once, a small "Funds for Europe · change" chip opens the picker. Ask only if the guess fails. | a fresh visit shows the home page, not a modal; Sweden → Europe |
| 5 | **The game is the front door** (U4): tapping the hero scene starts the game; "Play the market" over it; `#play` deep link opens the game. | from a cold `…/#play` link a visitor is running in one tap |
| 6 | **Daily chart + streak + share** (U5, U6): one seeded run per day (seed = day key, same chart for everyone), a streak and a daily best on the Play tab; a results "Share" renders a 1200 × 630 image (the chart you rode, score, best bank, brand) and uses `navigator.share` (download fallback). | a day's chart is identical across devices; share image renders in light and dark |
| 7 | **Bridge game → atlas** (U9, U7, U8): the results lesson links to the matching Basics card or fund pile; "Full details" opens as a sheet over the cards; plain labels ("Pick a country", "Price swings"); VOO-vs-savings in one place only. | each lesson line has a link; no page jump on details |
| 8 | **Repo hygiene** (ponytail #3-7): drop `GLASS_STYLE=0`; untrack `__pycache__`, `dolla_tex*.png`, `last-run.json`; archive the dated history in `QA.md`; one-line the finished task tables; trim `.gitignore`. | about -900 lines |
| 9 | **Trick combos stages 2-4** (`ANIMATION.md`), needs Blender (bpy). | per the doc |

## Ideas if the queue is done (keep the spirit: market never ends a run, no real tickers or advice, one finger, phone first)

- **Sound pass:** short glassy sfx to match the glass art (tick pickup chime per tier, bank cash-register, bear growl), with the existing mute.
- **More patterns:** ascending triangle, gap-up / gap-down, dead-cat bounce, each with a name pop and a one-line lesson.
- **Haptics per event** where `navigator.vibrate` exists (already used for crashes): ticks, banks, PERFECT.

## Notes

- Two sessions may push to `main`: always `git fetch && git rebase origin/main` first. On an `index.html` conflict, re-apply your edits by exact-string script on top of `origin/main`.
- Assets are rendered, not drawn: follow `CLAUDE.md` (contact sheet first, head anchors for hats, 60 fps rules).
- When you stop, update the "What exists" list and the queue here.
