# Handoff to Claude Code: runner game, Nov 2026

## Status (Claude Code, items 1-13 done; stopped before 14)

**Done and pushed to `main`, one commit per item, hashes in the table below.** Each item was tested with scripted headless runs of the game (stepping `_cp.step`, Playwright) and, for numbers, `node scripts/balance/sim.js`. No page errors or 4xx in any run.

| Item | Result |
|---|---|
| B1 portfolio | score = `V - V0` (compounded profit); chains pay alpha, PERFECT +0.25%, slippage -1%; no `R.score+=` outside `bank()` |
| B2 pacing | bulls every 24-26 s (20000 px, +1500 per bull, cap 28000); `PNLK .006`; hint at 45% |
| B4 PERFECT | 55 ms window; random taps 3.6-6 a minute; deliberate timing still lands |
| O1 onboarding | `cp-learn` 1-5, swipes gated until taught, cue per run, legend highlights the new direction |
| M2 power-ups | STOP-LOSS / INDEX FUND / DIVIDEND 2x / BULL RUN (ticks x1.46 denser); stop-loss blocks crash, red tick, slippage, rug drain |
| B5/M4 phases | bull/bear every 2-3 stretches, tilt, red ticks x2 in a bear, badge + red sky. 300 s: passive long +8..11% per bull stretch, -8..-13% per bear stretch; phase reader 5.9x passive |
| B3 momentum | clean chain n>=2 surges; trickster bulls 10% sooner (20.0 s vs 22.3 s) |
| M3 patterns | all seven, each seen within 180 s in 100% of runs; every interaction tested by stepping |
| M5 rugpulls | Token World, from bull 3, max 2 a run, never fatal; long 1x -3.7%, long 2x -6%, all in -10.2%, short +13.2%, cash 0, stop-loss blocks |
| M6 results | banked total, best bank/chain, patterns, rugs, one lesson line |
| B6 economy | hats 300 / 900 / 2500, +100 first run of the day; ETF saves 0-1 day (table in `BALANCE.md`) |
| B7 missions | ten missions, three a day on the Play tab with wallet rewards; a full set = portfolio level (+5% start, max +50%) |
| P1 performance | page load 2 KB of game images (was about 2.6 MB), game open 480 KB, other skins/sheets on demand (a full tour of all positions is 1.3 MB) |

**Harness at the end (`BALANCE.md` section 7 rows).** 60 s x5: bull interval PASS (24.3 s), passive PERFECTs PASS, no passive cap PASS, errors PASS. FAIL: passive 229 pts/min (target 20-60), trader/passive 1.7x, reader/passive 0.8x (a 60 s run only banks about 2 stretches, so the phase read does not pay yet), trickster alpha share 62% (35-55). 300 s x3: trader share 78% PASS, trader and reader well above passive PASS, every pattern PASS; FAIL: trickster alpha share 89% and trickster hits the cap in 3/3 runs (compounding plus alpha is strong over 5 minutes), bull interval 21.2 s (the speed ramp shortens later stretches).

**Deviations from the docs (all logged in the `BALANCE.md` changelog):** tick values halved (+0.5 / +1.5 / +5, red -1 / -2.5) and green tick spacing x1.5, because ticks were most of a passive player's income; terrain tilt `{bull: -1, bear: 11}` because the generator itself leans up; rocket ticks +2% and an 8% x leverage rug drain; the harness bots now fast-forward, hold their jumps and respawn instead of using a shield.

**Next (item 14, B8):** re-tune `PNLK`, tick values, alpha factor and `CPD` until every section 7 row holds (the FAIL rows above, mostly passive earning too much per minute and alpha being too strong over long runs), then the five phone runs; the checklist for the owner is in `BALANCE.md` section 7 ("Humans beat bots"). Not built: circuit breaker and earnings day (M4 extras), pattern outlines (necklines), the Deploy workflow still needs GitHub Pages enabled by the owner.

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
| 7 ✅ `368f9d8` | **B3 Momentum** (chain → small surge) | B3 | trickster bull interval about 10% shorter |
| 8 ✅ `4f948d5` | **M3 Chart patterns as terrain**: support, resistance + breakout, MA grind rail, cup & handle, bull flag, head & shoulders, double bottom | `MARKET.md` §5 | each appears within about 3 min; name pop once per run |
| 9 ✅ `1354e8a` | **M5 Rugpulls** (Token World only), with the rendered rug set | `MARKET.md` §7 | tell → yank → P&L follows the position; ≤ 2 per run; never fatal |
| 10 ✅ `d9a18c4` | **M6 Results card lessons** | `MARKET.md` §8 | lesson line chosen from the run's events |
| 11 ✅ `d214c47` | **B6 Economy**: hat prices 300 / 900 / 2500, daily gift; account for ETF yield | `BALANCE.md` §6 | prices updated; days-to-crown checked with and without the ETF |
| 12 ✅ `eb09826` | **B7 Missions + portfolio level** | B7 | 3 missions on the Play tab; `cp-plevel` persists |
| 13 ✅ `844fe83` | **P1 Performance** (new, see below) | below | game opens with ≤ 0.9 MB of game images; other skins load on demand |
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

## New from the owner (Nov 7, evening): partly built, finish these

**Built already (planning session):**
- **Smoother bull:** 48 frames at 12 fps (`cp-bull.webp`).
- **Ruby bear checkpoint:** in a bear market (`cp-bear.webp`, 48 frames) with a red glow.
- **Bear market share:** about 25% of stretches. `phaseOf`: bull phases 3–5 stretches, bear 1–2.
- **Sticky ↑ / ↓ toggles:**
  - ↑ = LONG and ↓ = SHORT stay set until the next ↑ / ↓ swipe. Again = 2x, and it stays 2x; it never toggles itself off.
  - ← CASH pauses the position but remembers the direction (`R.dirMem`). → ALL IN rides the board in that direction at 3x.
  - On the board, ↑ / ↓ flip the direction and keep you on the board (no ball trick).
- **Board colour:** strong green when ALL IN LONG, strong red when ALL IN SHORT (`runner-skate-ggreen/-gred.webp`, `SKATEI`). Messages: "ALL IN LONG 3x" / "ALL IN SHORT 3x".
- **Dolla:** the currency is now the **Dolla** (note: `dolla.webp`; texture `scripts/icons/dolla_texture.py`; 3D `o_dolla`). The HUD score uses the site font (Inter 900) with the note icon; no pixel digits. Wallet, hats, ETF and missions say "Dolla". The cash-run trail drops Dolla notes.

**Tasks:**

| # | Item | Done when |
|---|---|---|
| 16 | **Bear checkpoint behaviour.** It banks like the bull, but there's no relief rally: launch at 75% height (`CPV*.75`), no forward surge, and a grumpier flight (keep the love face for the bull only; use the normal face, a red aura and a "BEAR MARKET BANKED" pop). If the stretch's open P&L is negative, add the lesson line "Banking in a bear locks the loss: cash or short next time". | the bear launch differs visibly; harness errors 0 |
| 17 | **Re-tune for the 25% bear share** (B8 numbers moved: passive long now earns more on average). Lower bull-phase tilt or `PNLK` until passive is back in its band. | `BALANCE.md` §7 rows re-run; changelog entry |
| 18 | **ALL IN SHORT balance.** Shorting on the board is now possible (3x). Check the trader bot with a bear-phase short-board strategy doesn't exceed 6× passive; if it does, cap all-in short to 2x or cut red-tick values while on the board. | harness numbers logged |
| 19 | **Dolla juice.** On a bank, burst 6–12 Dolla notes (`bill.webp` is now a Dolla note) from the runner to the HUD counter, then tick the counter up. Mission and gift rewards fly to the wallet the same way in the menu. | visible in a headless screenshot sequence; reduced motion = instant |
| 20 | *(later, cosmetics)* **Higher notes:** 5 / 20 / 100 Dolla notes with different smiley portraits (love eyes on 20, sunglasses on 100) for bigger pops and the shop. Same texture script, different portrait. | — |
| 21 ✅ | **NEUTRAL start (built Nov 7):** runs now start in a 5th state: gold, no position (`R.pos.flat`), ticks still collected, no price P&L; the first ↑ = LONG 1x. Check the O1 run-1 copy ("the bull banks the default LONG" is no longer true: say "swipe ↑ to go long" when run 2 teaches it) and re-run the harness (bots go long at the start, so the baselines are comparable). | onboarding text matches; harness rows logged |
