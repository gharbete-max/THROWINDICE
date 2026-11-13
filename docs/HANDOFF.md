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

For each item: implement, test (headless harness from `CLAUDE.md`; `sim.js` for anything that moves numbers), reduced motion and 0 page errors, one commit per item, rebase on `origin/main`, push, tick it here.

| # | Item | Done when |
|---|---|---|
| 1 | **B8 balance re-tune: skill must beat standing still.** Baseline (Nov 13, 120 s × 4 runs, trader bot fixed for the ladder): passive **290**/min, trader **119** (0.4×), reader **144** (0.5×); bull gap 25.6 s PASS; PERFECTs PASS; errors 0. Cause: since runs start holding LONG 1x (`d7218de`), a passive long rides every bull stretch, and bear stretches don't reliably drop (passive banked +6% to +23% in some bear stretches). Levers: `TILT` (bull 150 / bear -2000) and the drift controller, `PNLK` (.0045), tick values/spacing, bear red-tick density. Re-read `BALANCE.md` §7: the passive target should be about 60–140/min at 120 s (the 20–60 band contradicts §6). Run ≥ 4 runs per check: variance is large. | reader ≥ 2× passive and trader ≥ 1.5× at 120 s; passive long loses in bear stretches on average; changelog at the bottom of `BALANCE.md` |
| 2 | **Owner: 5 phone runs.** Nothing to build: the run log records them. The owner plays 5 runs and reads the results card (typical run length; target median 60–120 s for a new player). | numbers noted in `BALANCE.md` |
| 3 | **Remove the dead non-Apple UI.** `<body class="apple">` is hard-coded, so the old bottom nav, tiles, invest popup, coin bubble, the `.e3d` inline-emoji machinery outside the slots, and their CSS/JS are dead weight in a 450 KB `index.html`. Delete in small, tested steps (screenshots light/dark/Token World before and after each). | `index.html` noticeably smaller; no visual change; 0 errors |
| 4 | **Trick combos stages 2–4** (segment re-renders, double rotations, spin rewind, bridges) | `ANIMATION.md` "Trick combos" |
| 5 | **Deploy** (owner): Settings → Pages → Source: GitHub Actions, re-run Deploy. | site live; share card shows |

## Ideas if the queue is done (keep the spirit: market never ends a run, no real tickers or advice, one finger, phone first)

- **Share a run:** a results-card button that renders a 1200×630 image of the run (score, best bank, the chart you rode) with the brand, via `navigator.share`.
- **Daily chart:** one seeded run per day that everyone plays (seed = day key), with a local best.
- **Sound pass:** short glassy sfx to match the glass art (tick pickup chime per tier, bank cash-register, bear growl), with the existing mute.
- **More patterns:** ascending triangle, gap-up / gap-down, dead-cat bounce, each with a name pop and a one-line lesson.
- **Haptics per event** where `navigator.vibrate` exists (already used for crashes): ticks, banks, PERFECT.

## Notes

- Two sessions may push to `main`: always `git fetch && git rebase origin/main` first. On an `index.html` conflict, re-apply your edits by exact-string script on top of `origin/main`.
- Assets are rendered, not drawn: follow `CLAUDE.md` (contact sheet first, head anchors for hats, 60 fps rules).
- When you stop, update the "What exists" list and the queue here.
