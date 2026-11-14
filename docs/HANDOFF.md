# RELEASE STATE (Nov 2026): finished, ready to host as its own page

- **Done:** queue items 1-13, 15-19, 21, and the Nov 14 audit queue (all non-owner items); B8 closed in `BALANCE.md` section 8; Tokens page replaces Token World (Token World pages and rug-pull code stay in the file, unreachable); ETF browser = fund cards; Low graphics is the only mode; stance rules (long 1x default, ALL IN toggles off, ticks pay by side).
- **Styling matches throwpaper** (`gharbete-max/throwpaper` `DESIGN.md`): the `tpStyle` block at the end of `<head>`. Paper `#fafaf8`, ink `#0e0e10`, gold `#cea85c` fill, bronze `#8f6b3a` words, platinum greys, flat cards, glass only on the header, menu, dialogs and toasts, 44 px controls, Inter 16/1.55, dark derived (page `#0e0e10`, cards `#1c1c1e`).
- **Hosting:** `docs/EMBEDDING.md` + `scripts/package.sh` (also used by the Pages workflow). `?embed` hides the wordmark; `#play` opens the game.
- **Not built (deliberately):** rendered trick bridges; deleting the dormant Token World code; bundling the Inter font (same as throwpaper).
- **Owner still to do:** play five phone runs; enable Pages if using GitHub Pages; upload `dist/throwindice/` to the website.

# Handoff: throwindice, Nov 14 2026

**Read this first, then `CLAUDE.md`.** One page: what exists, then the ordered queue. Finished history is in `docs/archive/HANDOFF-2026-11.md`.

## What exists

- **Site:** throwpaper-matched UI (paper/ink/gold, flat cards, glass only on floating things), light/dark, a Tokens page (Token World retired, code dormant). Scroll-scrubbed 3D hero (tap it to play; `#play` deep link opens the game), region guessed from the time zone (no first-visit gate; a "Funds for … · change" chip in each fund list), 3D icons in list slots, ETF fund cards (fee, rates, spread, holdings). Fund "Full details" opens as a sheet over the cards. Brand: `throw·indice` wordmark, die-into-tag mark, favicons, app icons, share image (`CLAUDE.md` → Brand). First visit is ~0.85 MB; `index.html` ~420 KB.
- **Game (Live Ball Bounce):** one-finger runner on a candle chart.
  - **Positions:** ↑ long, ↓ short (1x–2x–3x ladder), ← cash, → ALL IN on a skateboard. Runs start holding LONG 1x.
  - **Market:** bull/bear phases (first bull 1-2 stretches, then bull 2-3 / bear 1-2, ~35% bear; half the green ticks in a bear), diamond bull / ruby bear checkpoints that bank P&L, chart patterns as terrain, rugpulls in Token World.
  - **Economy:** score = compounded profit, Dolla notes (1/5/20/100), wallet, hats, missions, portfolio level, Big Ball ETF.
  - **Look:** glass family. Gold glass runner with a $ coin heart, 105-frame run cycle, 24-frame tricks, 96-frame bull/bear, adaptive resolution, 60 fps.
  - **Run log:** each run's length / checkpoints / score / cause goes to `localStorage['cp-runs']` (last 20); the results card shows the last runs and the typical length, and a **Share** button (1200×630 card of the chart you rode, via the share sheet or a download; the text carries the `#play` link).
  - **Today's chart:** one seeded chart per UTC day for everyone, daily best + streak (`cp-daily`), `#daily` link.
  - **Trick combos:** same flick again = double/triple cork or a longer split; tricks nudge the arc.
  - **Haptics** (Android; iOS has no `navigator.vibrate`): PERFECT, ticks, banks, crashes.
- **Tools:** balance harness `scripts/balance/sim.js`, Blender generators `scripts/icons/`, brand build `scripts/brand/`.

## Queue (top to bottom)

Direction and reasons: `docs/AUDIT-2026-11.md` (usability U1-U9, ponytail cuts, the project's future). **The game is the front door; the atlas is the depth behind it.**

For each item: implement, test (headless harness from `CLAUDE.md`; `sim.js` for anything that moves numbers), reduced motion and 0 page errors, one commit per item, rebase on `origin/main`, push, tick it here.

| # | Item | Done when |
|---|---|---|
| 1 | ✅ `4e6a3dd` **B8 balance.** 120 s × 12: passive **131**/min, trader **300** (2.3x), reader **345** (2.6x); a passive long banks **-12.2%** a bear stretch; all harness rows PASS. Changelog in `BALANCE.md`. | done |
| 2 | **Owner:** turn on GitHub Pages (U1; the Deploy workflow still fails at configure-pages on Nov 14), then play 5 runs on a phone, including Today's chart; the results card shows the typical run length (target 60-120 s). | site live; numbers in `BALANCE.md` |
| 3 | ✅ `db5ab8c`, `50d308e` **Cut the dead layer.** Dead nav/popup/coin layer gone; then 378 CSS declarations (77 whole rules) that later `body.apple`/`tpStyle` rules always override were deleted, plus 6 unused classes (22 screenshots light/dark pixel-identical). `index.html` 417 KB. The remaining `body.apple` prefixes are live rules; folding them into the base would save ~3 KB for a specificity risk, so they stay. | done |
| 4 | ✅ `f406407` **No first-visit gate** (U3). | done |
| 5 | ✅ `5628485` **The game is the front door** (U4). | done |
| 6 | ✅ `d213933` **Today's chart** (U5) + share (U6, `ced822c`): a "Today's chart" button on the Play tab runs one seeded chart per UTC day, the same for everyone (the generator runs under a seeded `Math.random`, reseeded per segment, so screen size and particles never shift it; checked identical at 390/820/1280 px). Daily best and a streak of days in a row (`cp-daily`) on the button and the results card; the share text links `#daily`. | done |
| 7 | ✅ `607a9d7`, `e53aaaf` **Bridge game → atlas** (U9, U7, U8): lesson links, plain labels, "Full details" opens as a sheet over the fund cards (Back/Escape return, focus restored), VOO-vs-savings only on Basics. | done |
| 8 | ✅ `259afa3` **Repo hygiene:** `GLASS_STYLE=0` branches dropped, `QA.md` history → `docs/archive/QA-2026-10.md` (a live checklist remains), finished M/B task tables one-lined. | done |
| 9 | ✅ `7f1b116`, `d3205aa`, `8767448` **Trick combos** (`ANIMATION.md`): double/triple cork (16 rendered loop frames per skin, row 4 of the trick sheets), longer split, SPLAT SPLIT name, physics (spin hangs, split floats, +.35 s budget, cork-again hop). Rendered bridges and spin rewind skipped (spin is not reachable: → is ALL IN). | done |

Harness after this pass (`sim.js 120 passive,trader,reader 6`): passive 111/min, trader 322 (2.9x), reader 315 (2.8x), bull gap 25.8 s, all rows PASS. The passive bear-stretch bank is noisy at 4-6 runs (-1.5% to -12.6%); use 12 runs before changing numbers.

## Ideas if the queue is done (keep the spirit: market never ends a run, no real tickers or advice, one finger, phone first)

- **Sound pass:** short glassy sfx to match the glass art (tick pickup chime per tier, bank cash-register, bear growl), with the existing mute.
- **More patterns:** ascending triangle, gap-up / gap-down, dead-cat bounce, each with a name pop and a one-line lesson.

## Notes

- Two sessions may push to `main`: always `git fetch && git rebase origin/main` first. On an `index.html` conflict, re-apply your edits by exact-string script on top of `origin/main`.
- Assets are rendered, not drawn: follow `CLAUDE.md` (contact sheet first, head anchors for hats, 60 fps rules).
- When you stop, update the "What exists" list and the queue here.
