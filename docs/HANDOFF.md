# Handoff to Claude Code: runner game, Nov 2026

**Read this first, then `CLAUDE.md`.** It's the ordered work queue. Each item points to the doc with the details. Work top to bottom.

For each item:
1. Implement it.
2. Test it: the headless harness from `CLAUDE.md`, plus `node scripts/balance/sim.js` for anything that changes numbers.
3. Check reduced motion and 0 page errors.
4. Commit one item per commit, rebase on `origin/main`, push.
5. Tick the item here (✅ plus the commit hash).

If an item is blocked or a target can't be met, write why under it and move on.

## Where things stand (built)

- **Market core:**
  - Swipe positions: ↑ long (2x), ↓ short (2x), ← cash, → all in on a skateboard.
  - Terrain P&L, and the diamond bull that banks and launches you.
  - Ticks and red ticks (M1), and the ±60% cap.
- **Looks:**
  - Body colour = position.
  - Power-ups = auras.
  - Rendered 3D tricks and board tricks (Jesus, indy, shove-it, tre flip, ollie, kickflip).
  - Trick chains with queue and speed-up; blending under spam (`ANIMATION.md`).
- **Meta:**
  - Hats (3) with wallet, and the Play / Style / Invest / Options menu.
  - **Big Ball ETF:** invest the wallet; it grows while away (`MARKET.md` §11).
- **Tools:** the balance bot harness `scripts/balance/sim.js`, with its baseline in `BALANCE.md` §3.

## Work queue

| # | Item | Details | Done when |
|---|---|---|---|
| 1 ✅ `82312ed` | **B1 Unified portfolio**: score = compounded profit; chains → alpha, PERFECT → +0.25%, slippage | `BALANCE.md` §4, B1 | harness: trader ≥ 60% market share; no `R.score+=` outside `bank()`; harness anchors updated |
| 2 ✅ `089f9b4` | **B2 Pacing**: bull spacing 20000 → +1500 → 28000, `PNLK` 0.006, take-profit hint at 45% | `BALANCE.md` §5, B2 | bull interval 22–28 s |
| 3 ✅ `3aa9d7c` | **B4 PERFECT window** | B4 | random taps ≤ 6 per minute |
| 4 ✅ `b7501ef` | **O1 Onboarding** (new, see below) | below | a first-time player sees one new control per run |
| 5 ✅ `798c189` | **M2 Power-up renames and behaviour**: stop-loss, index fund, 2x | `MARKET.md` §4 | pops use the new names; stop-loss blocks a red tick and slippage |
| 6 ✅ `4904035` | **B5 / M4 Bull & bear phases**: terrain drift, red-tick density, phase icon (`cp-bull` frame / `bear.webp`) | `MARKET.md` §6, `BALANCE.md` B5 | passive long earns in bull and loses in bear; phase-reading trader bot ≥ 2× passive |
| 7 ✅ | **B3 Momentum** (chain → small surge) | B3 | trickster bull interval about 10% shorter |
| 8 | **M3 Chart patterns as terrain**: support, resistance + breakout, MA grind rail, cup & handle, bull flag, head & shoulders, double bottom | `MARKET.md` §5 | each appears within about 3 min; name pop once per run |
| 9 | **M5 Rugpulls** (Token World only), with the rendered rug set | `MARKET.md` §7 | tell → yank → P&L follows the position; ≤ 2 per run; never fatal |
| 10 | **M6 Results card lessons** | `MARKET.md` §8 | lesson line chosen from the run's events |
| 11 | **B6 Economy**: hat prices 300 / 900 / 2500, daily gift; account for ETF yield | `BALANCE.md` §6 | prices updated; days-to-crown checked with and without the ETF |
| 12 | **B7 Missions + portfolio level** | B7 | 3 missions on the Play tab; `cp-plevel` persists |
| 13 | **P1 Performance** (new, see below) | below | game opens with ≤ 0.9 MB of game images; other skins load on demand |
| 14 | **B8 Re-tune pass + 5 human phone runs** (the owner plays; prepare a short checklist for them) | B8 | every `BALANCE.md` target holds; changelog at the bottom of `BALANCE.md` |
| 15 | *(later)* Trick combos stages 2–4: segment re-renders, double rotations, spin rewind, bridges | `ANIMATION.md` "Trick combos" | optional, after 14 |

### O1: Onboarding (new)

The game now has many verbs for one finger. Teach one per run, with the same 2-second `msg()` cues already used for tips. Use a `cp-learn` level stored in `localStorage`; existing players (best > 0) skip straight to level 5.

1. **Run 1:** jump only. Swipes are ignored, and the bull banks the default LONG.
2. **Run 2:** "Swipe ↑ = LONG, ↓ = SHORT". The green/red colour is the cue.
3. **Run 3:** "← CASH keeps your gains safe".
4. **Run 4:** "→ ALL IN rides the board: 3x".
5. **Run 5+:** everything, plus a one-time "swipe in the air on the board for tricks".

The Play tab's swipe legend highlights the newly unlocked direction.

### P1: Performance (new)

The game loads about 2.6 MB of sprite sheets when it opens: 5 skins × runner, trick and love sheets, plus the skateboard sheet and props.

- **Load at open:** the gold and light-green sheets only (the start skin).
- **Load on demand:** the others the first time that position is taken (fallback to gold until loaded; the blend system already fades the swap in).
- **Measure:** page weight at game open with the browser's network panel, or Playwright `page.on('response')` sizes.

## Final notes from the planning session

- **Balance before content.** Items 1–3 change what every other system is worth. Don't tune patterns or rugs on the old scoring.
- **Keep the spirit** (`MARKET.md` §0): the market never ends a run; no real tickers or advice; cosmetics never change stats.
- **Two sessions may push to `main`.** Always `git fetch && git rebase origin/main` before pushing. If a rebase conflicts in `index.html`, re-apply your edits by exact-string script on top of `origin/main` rather than hand-merging.
- **Deploy:** nothing is live until the owner enables GitHub Pages (Settings → Pages → Source: GitHub Actions) and reruns the Deploy workflow. Mention it in your final report if it's still failing.
- **Rendering new art:** follow `CLAUDE.md` (contact sheet first; head anchors for hats; blending rules for any new sheet).
- **Report back:** when you stop, write a short status at the top of this file: what's done, numbers from the harness, and what's next.
