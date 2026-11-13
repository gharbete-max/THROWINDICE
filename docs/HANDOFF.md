# RELEASE STATE (Nov 2026): finished, ready to host as its own page

- **Done:** queue items 1-13, 16-19, 21; B8 closed in `BALANCE.md` section 8; Tokens page replaces Token World (Token World pages and rug-pull code stay in the file, unreachable); ETF browser = fund cards; Low graphics is the only mode; stance rules (long 1x default, ALL IN toggles off, ticks pay by side).
- **Styling matches throwpaper** (`gharbete-max/throwpaper` `DESIGN.md`): the `tpStyle` block at the end of `<head>`. Paper `#fafaf8`, ink `#0e0e10`, gold `#cea85c` fill, bronze `#8f6b3a` words, platinum greys, flat cards, glass only on the header, menu, dialogs and toasts, 44 px controls, Inter 16/1.55, dark derived (page `#0e0e10`, cards `#1c1c1e`).
- **Hosting:** `docs/EMBEDDING.md` + `scripts/package.sh` (also used by the Pages workflow). `?embed` hides the wordmark; `#play` opens the game.
- **Not built (deliberately):** trick combos (15) and higher notes (20); deleting the dormant Token World code; bundling the Inter font (same as throwpaper).
- **Owner still to do:** play five phone runs; enable Pages if using GitHub Pages; upload `dist/throwindice/` to the website.

# Handoff: throwindice, Nov 13 2026

**Read this first, then `CLAUDE.md`.** One page: what exists, then the ordered queue. Finished history is in `docs/archive/HANDOFF-2026-11.md`.

## What exists

- **Site:** throwpaper-matched UI (paper/ink/gold, flat cards, glass only on floating things), light/dark, a Tokens page (Token World retired, code dormant). Scroll-scrubbed 3D hero (tap it to play; `#play` deep link opens the game), region guessed from the time zone (no first-visit gate; a "Funds for … · change" chip in each fund list), 3D icons in list slots, ETF fund cards (fee, rates, spread, holdings). Brand: `throw·indice` wordmark, die-into-tag mark, favicons, app icons, share image (`CLAUDE.md` → Brand). First visit is ~0.85 MB; `index.html` 417 KB (the dead pre-Apple nav/popup layer is gone).
- **Game (Live Ball Bounce):** one-finger runner on a candle chart.
  - **Positions:** ↑ long, ↓ short (1x–2x–3x ladder), ← cash, → ALL IN on a skateboard. Runs start holding LONG 1x.
  - **Market:** bull/bear phases (first bull 1-2 stretches, then bull 2-3 / bear 1-2, ~35% bear; half the green ticks in a bear), diamond bull / ruby bear checkpoints that bank P&L, chart patterns as terrain, rugpulls in Token World.
  - **Economy:** score = compounded profit, Dolla notes (1/5/20/100), wallet, hats, missions, portfolio level, Big Ball ETF.
  - **Look:** glass family. Gold glass runner with a $ coin heart, 105-frame run cycle, 24-frame tricks, 96-frame bull/bear, adaptive resolution, 60 fps.
  - **Run log:** each run's length / checkpoints / score / cause goes to `localStorage['cp-runs']` (last 20); the results card shows the last runs and the typical length, and a **Share** button (1200×630 card of the chart you rode, via the share sheet or a download; the text carries the `#play` link).
  - **Haptics** (Android; iOS has no `navigator.vibrate`): PERFECT, ticks, banks, crashes.
- **Tools:** balance harness `scripts/balance/sim.js`, Blender generators `scripts/icons/`, brand build `scripts/brand/`.

## Queue (top to bottom)

Direction and reasons: `docs/AUDIT-2026-11.md` (usability U1-U9, ponytail cuts, the project's future). **The game is the front door; the atlas is the depth behind it.**

For each item: implement, test (headless harness from `CLAUDE.md`; `sim.js` for anything that moves numbers), reduced motion and 0 page errors, one commit per item, rebase on `origin/main`, push, tick it here.

| # | Item | Done when |
|---|---|---|
| 1 | ✅ `4e6a3dd` **B8 balance.** 120 s × 12: passive **131**/min, trader **300** (2.3x), reader **345** (2.6x); a passive long banks **-12.2%** a bear stretch; all harness rows PASS. Changelog in `BALANCE.md`. | done |
| 2 | **Owner:** turn on GitHub Pages (U1), then play 5 runs on a phone; the results card shows the typical run length (target 60-120 s). | site live; numbers in `BALANCE.md` |
| 3 | **Cut the dead layer.** ✅ `db5ab8c` half done: bottom nav, token coin, invest popup, coin bubble, spin preloaders, vignette script, 70 dead CSS classes, 15 unused keyframes and 29 orphaned icon renders (1.9 MB) deleted; `navGame()` is a direct opener. `index.html` 449 → 417 KB, screenshots light/dark × Real/Token World unchanged. **Left:** fold the ~200 `body.apple` overrides into the base CSS (`<body class="apple">` is hard-coded) and delete what they override. | about -35 KB more, no visual change |
| 4 | ✅ `f406407` **No first-visit gate** (U3): guess the region from `Intl.DateTimeFormat().resolvedOptions().timeZone` / `navigator.language`, show content at once, a small "Funds for Europe · change" chip opens the picker. Ask only if the guess fails. | a fresh visit shows the home page, not a modal; Sweden → Europe |
| 5 | ✅ `5628485` **The game is the front door** (U4): tapping the hero scene starts the game; "Play the market" over it; `#play` deep link opens the game. | from a cold `…/#play` link a visitor is running in one tap |
| 6 | **Deferred (decision, Nov 2026):** needs the terrain/tick generator split from the per-frame `rnd` users before a seed is safe; not worth the risk at release. **Daily chart + streak** (U5); the share half (U6) is ✅ `ced822c`. Seeding needs a seeded RNG for the terrain/tick generator only (not the particles, which run per frame): one seeded run per day (seed = day key, same chart for everyone), a streak and a daily best on the Play tab; a results "Share" renders a 1200 × 630 image (the chart you rode, score, best bank, brand) and uses `navigator.share` (download fallback). | a day's chart is identical across devices; share image renders in light and dark |
| 7 | ✅ (partly) **Bridge game → atlas** (U9, U7, U8): results lesson now has a "Learn why →" link (Tokens for rugs, Basics otherwise); "Pick a pile" → "Pick a country or theme", "Fluctuation" → "Price swings". Still open: details as a sheet over the cards; VOO-vs-savings in one place. Original text: the results lesson links to the matching Basics card or fund pile; "Full details" opens as a sheet over the cards; plain labels ("Pick a country", "Price swings"); VOO-vs-savings in one place only. | each lesson line has a link; no page jump on details |
| 8 | **Repo hygiene** (ponytail #3-7; `__pycache__` untracked and `.gitignore` trimmed; `dolla_tex*.png` kept: `objects.py` renders with them): drop `GLASS_STYLE=0`; untrack `__pycache__`, `dolla_tex*.png`, `last-run.json`; archive the dated history in `QA.md`; one-line the finished task tables; trim `.gitignore`. | about -900 lines |
| 9 | **Trick combos stages 2-4** (`ANIMATION.md`), needs Blender (bpy). Not available in the Nov 14 cloud session (no `bpy`), skipped. | per the doc |

## Ideas if the queue is done (keep the spirit: market never ends a run, no real tickers or advice, one finger, phone first)

- **Sound pass:** short glassy sfx to match the glass art (tick pickup chime per tier, bank cash-register, bear growl), with the existing mute.
- **More patterns:** ascending triangle, gap-up / gap-down, dead-cat bounce, each with a name pop and a one-line lesson.

## Notes

- Two sessions may push to `main`: always `git fetch && git rebase origin/main` first. On an `index.html` conflict, re-apply your edits by exact-string script on top of `origin/main`.
- Assets are rendered, not drawn: follow `CLAUDE.md` (contact sheet first, head anchors for hats, 60 fps rules).
- When you stop, update the "What exists" list and the queue here.
