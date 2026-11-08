# Runner game: integration and balancing plan

**For Claude Code.** This is how all the systems should fit together, what the game measures today, what comparable games do, and the exact tuning tasks (B1–B8) with numeric targets. Work through it after `MARKET.md` M2–M6, or interleave. Every change is checked with the balance harness (§7).

## 1. What "balanced" means here (pillars)

1. **The market is the game; tricks are the style.**
   - A skilled player's score should come **about 55–65% from reading the market** (position choice, cash, all in, banking) and **35–45% from tricks**.
   - Today it's the reverse (§3).
2. **Push your luck, every stretch.** Gains sit in *open* P&L and are only yours when the bull banks them. The tension between banking and pushing on is the core of push-your-luck design. It needs a stretch long enough to build real gains and real risk.
3. **Forgiving, short runs.** The market never ends a run. Target a run of **60–120 s for new players and 3–5 min for skilled players**, and a session of a few runs (§2).
4. **Visible progress across runs:**
   - **Wallet** → hats (cosmetic only).
   - **Missions** → portfolio level (a small permanent boost, as in Subway Surfers).

## 2. What comparable games do (and what we take)

| Game | What they do | What we take |
|---|---|---|
| **Alto's Adventure / Odyssey** | Each trick in one jump adds to the multiplier; the chain total is multiplied by the trick count (e.g. 4 tricks worth 380 → ×4 = 1,520). Backflips also give speed. | Chain value = base × n (our `n²` is the same shape). Tricks also give a little **speed** (momentum), so style helps you reach the bull. |
| **Tony Hawk's Pro Skater** | Trick values add to a base, and each trick adds to the multiplier; the combo ends on landing. Later games added combo-extenders (manuals), which made scores "easier and cheesier". | Chains end on landing; air time caps the length; **no infinite extenders** (queue max 2, no grind-forever). |
| **Subway Surfers** | Score multiplier starts at 1x; mission sets raise it permanently, up to 30x. | **Portfolio level**: mission sets raise the starting portfolio (B7). |
| **Jetpack Joyride** | Always three missions active, including accumulation missions, which says the game is about many runs, not one. | Three rotating **market missions** that pay into the wallet (B7). |
| **Crossy Road** | 100 coins buy a random character; free gifts arrive at intervals. Purely cosmetic. | Cosmetics are priced in "a few good runs" (B6). No pay-to-win: hats never change stats. |
| **Push-your-luck designs** | Players either settle for current gains or risk them for more, and the tension is "the game working". | Open P&L vs bank; cash as the safe option; all in as the "push". |
| **Mobile session benchmarks** | GameAnalytics: median session 6 min 42 s for hyper-casual (2019); 2025 averages are about 5–6 min (median titles) and 8–9 min (top tier). Hyper-casual sessions run about 60–180 s. | Design for runs of 1–2 min and sessions of about 6 min. |

## 3. Baseline (measured Nov 2026 with `scripts/balance/sim.js`, 60 s per bot, shield kept on)

| Bot | Score / min | From banking | From chains (`3·n²`) | From PERFECT (+2) | Bull every | Open P&L range |
|---|---|---|---|---|---|---|
| passive (long 1x, random jumps) | 47 | 13 | 0 | 34 (17 perfects!) | ~13 s | −2 .. +7.5% |
| trader (swipes ↑/↓, ← when up 8%) | 193 | 57 | ~126 | 10 | ~12 s | −3.7 .. +14.6% |
| trickster (random air swipes) | 337 (797 in a 20 s sample) | 27 | ~250+ | 58 | ~13 s | −7.9 .. +26.6% (all in) |

**Diagnosis:**
- **Bulls are too frequent:** `CPD = 11000` at about 820 px/s, so roughly every 12–13 s. Stretches are too short to build tension, and the ±60% `OPENCAP` is never reached.
- **Banking is worth too little:** 1% = 1 point, so a great stretch (+15%) pays 15 while a single 3-trick chain pays 27. The market is cosmetic in score terms.
- **PERFECT is far too generous:** random tapping lands 17–29 per minute.
- **Terrain has no trend:** passive long earns small and noisy amounts, so position choice barely matters. M4 phases fix this.

## 4. The integrated model (decision)

Everything flows into one portfolio. Points are the profit.

```
swipe ↑/↓/←/→ ──> position (dir × lev, cash, all in) ──┐
terrain price moves ───────────────────────────────────┼─> OPEN P&L (%)  ──bull──> PORTFOLIO V (compounds) ──> SCORE = V − V0
ticks (+1/+3/+10, red −2/−5; × lev; short flips red) ──┤        ▲  ±60% cap ("bubble")                       │
trick chains: alpha +0.25·n² % (skill, not levered) ───┤        │                                            ├─> wallet (+score per run) ─> hats
PERFECT jump: +0.25 % ─────────────────────────────────┤   slippage −1% on a sloppy landing                  └─> missions ─> portfolio level (V0 up)
power-ups: stop-loss (blocks one loss) · index fund ───┘   stop-loss floors open at 0 while active
           (pull ticks) · 2x (tick values ×2)
```

- **Portfolio:**
  - `V` starts at `V0 = 1000`.
  - A bank does `V *= 1 + clamp(open + cash, −60, 60) / 100`, then resets open and cash to 0.
  - **Score = max(0, round(V − V0))**, so profit is points. The HUD headline shows total return `(V/V0 − 1)` as % plus the open %.
  - Compounding makes later stretches worth more in points, the same "it gets juicier the longer you survive" shape as Subway's multiplier, but earned.
- **Tricks become alpha, not raw points.**
  - A clean chain of n tricks adds `+0.25·n²` % to open: 1 → .25, 2 → 1, 3 → 2.25, 4 → 4, max n = 5 → 6.25.
  - Alpha is **not** multiplied by leverage, so skill stays skill.
  - Like everything open, alpha is lost if the stretch goes badly. Labels and names stay the same.
- **Momentum (from Alto):** a clean chain of n ≥ 2 gives a short speed surge (`R.surge = .25·n` s), so style helps you reach the bull sooner.
- **Slippage:** landing mid-trick costs −1% open (stop-loss blocks it).
- **PERFECT:** +0.25% open (no raw points), with a narrower timing window (B4).
- **Wallet:** at run end, `wallet += score`, as now.

## 5. Pacing targets

| Knob | Now | Target | Why |
|---|---|---|---|
| Bull spacing `CPD` | 11000 px (~13 s) | **20000 at checkpoint 1, +1500 per bull, cap 28000** (~22–26 s at the rising speed) | A stretch long enough to push luck; about 3–5 bulls in a 2-minute run |
| `PNLK` | 0.004 %/px | **0.006** (re-measure) | A typical 1x stretch moves ±6–12%, 3x moves ±20–35% |
| `OPENCAP` | ±60 | keep ±60 | Reached only with all in + ticks + alpha. A "take profit!" hint at 45%. |
| Terrain trend (M4 phases) | none | bull phase: average drift up of about 6–10% of a stretch's price range; bear: down. Phases last 2–3 stretches, telegraphed by the bull/bear icon. | Makes long/short/cash a real read |
| Red ticks | from level 2 | from bull 2, about 1 per 6 green; 1 per 3 in bear phases | Shorts get prey, longs get hazards |
| Speed ramp | +7% per checkpoint, cap ×1.7 | keep, but reach the cap at bull 8, not earlier | Difficulty comes from speed, as in classic runners |
| Rugpull (M5) | — | max 2 per run, never before bull 3, 2.5 s tell | Rare spike of drama |

## 6. Economy targets (wallet and hats)

- **Expected earnings after B1–B5:**
  - A new player, about 90 s run with 3 bulls at about +5% each → about 150 pts.
  - A decent run, 4 bulls at +10% → about 460 pts.
  - A great run with all-in streaks → 1,000+.
- **Prices (cosmetic only, never stats):**

| Hat | Now | Target | About |
|---|---|---|---|
| top hat | 150 | **300** | 1–2 decent runs: the first unlock lands in session 1 |
| propeller | 250 | **900** | about 1–2 sessions |
| crown | 400 | **2500** | a goal for the first week |

- **Future hats:** add at 4,000–8,000 so long-term players keep a target.
- **Big Ball ETF interaction** (built, `MARKET.md` §11):
  - **Yield:** idle wallet points can compound at the replayed index: about 7.8%/yr of market time, i.e. roughly +2% per real day on average, with crashes of up to about −50% over a couple of real weeks (2008).
  - **Pricing:** price hats so that a player who invests their wallet reaches a hat about 10–20% sooner, not instantly.
  - **Re-check:** if hat prices change, check how long a typical wallet (say 600) takes to reach the crown, both with and without investing.
- **Free gift** (Crossy Road style, optional): +100 wallet when the first run of each day ends. It brings players back without timers in the run.

## 7. The balance harness (how every change is checked)

`node scripts/balance/sim.js [seconds=60] [modes=passive,trader,trickster] [runs=1]` (needs `playwright`).

- **What it does:**
  - Instruments a temporary copy of `index.html` (`_test.html`, auto-deleted) and serves it locally.
  - Plays three bots that are kept alive (crashes respawn): it measures the **economy**, not survival.
  - Prints score per minute split into bank, chain and perfect, the bull interval, and the open P&L range. Raw data goes to `scripts/balance/last-run.json`.
- **Keep it in step with the code:**
  - When B1 replaces `3·n²` points with alpha, update the injected anchors and add `alpha` and `slippage` logs.
  - When phases land, give the trader bot a phase read (long in bull, short in bear, ← at +8%).
- **Acceptance targets.** Average 3 runs × 60 s per bot after each B-task; every row must hold before committing:

| Metric | Target |
|---|---|
| bull interval | 22–28 s |
| passive score / min | 20–60 (positive in bull phases, about flat overall) |
| trader score / min | ≥ 2× passive |
| trickster: share of score from alpha | 35–55% |
| trader: share of score from the market (bank minus alpha) | ≥ 60% |
| random-tap PERFECTs / min (passive) | ≤ 6 |
| open P&L reaches the cap | in ≤ 30% of trickster runs, never for passive |
| page errors | 0 |

- **Humans beat bots:** before large balance changes ship, play 5 runs on a phone, and record run length, bulls reached and cause of death. Optional: a local log in `localStorage['cp-runs']` (last 20 runs: seconds, bulls, score, death cause) shown on the pause screen. Targets: median run 60–120 s for a new player, sessions about 6 min.

## 8. Task list

| # | Task | Done when |
|---|---|---|
| **B1** | **Unified portfolio:** `V`, compounding bank, score = profit; chains → alpha `+0.25·n²` % (no raw points), PERFECT → +0.25%, slippage −1%; HUD shows total return % + open %. The results card shows V, best bank and the alpha share. | harness: trader ≥ 60% market share; no `R.score+=` outside `bank()` |
| **B2** | **Pacing:** `CPD` 20000 → +1500 per bull → cap 28000; `PNLK` 0.006; "take profit!" hint at 45% | bull interval 22–28 s; 1x stretch ±6–12% |
| **B3** | **Momentum:** a clean chain of n ≥ 2 adds `R.surge = .25·n` s (stacks with the bull surge; cap 1.6 s) | trickster bull interval about 10% shorter than passive |
| **B4** | **PERFECT window:** shrink `perfectEdge()` until random taps give ≤ 6 per minute; deliberate timing should still land them | harness passive ≤ 6 perfects / min |
| **B5** | **Phases (MARKET M4):** terrain drift per phase; red-tick density per phase; icon + "BULL MARKET" / "BEAR MARKET" | a passive long earns in bull phases and loses in bear; the trader bot reading phases ≥ 2× passive |
| **B6** | **Economy:** hat prices 300 / 900 / 2500; first-run-of-the-day gift +100 | prices in the `HATS` table; gift once per calendar day |
| **B7** | **Missions + portfolio level:** three rotating market missions with wallet rewards (100–300), e.g. "Bank +15% in one stretch", "Short a red drop", "Land a TWISTER", "Dodge a rug in cash". Each completed set of three raises `V0` by +5% (max +50%) for future runs. | missions show in the Play tab; level persists (`cp-plevel`) |
| **B8** | **Re-tune pass:** run the harness 3×, adjust `PNLK`, alpha factor, tick values and `CPD` within ±25% until every acceptance row holds; then play 5 human runs on a phone | the targets table holds; a short changelog of the final numbers is added to the bottom of this file |

**Constraints (unchanged):**
- The market never ends a run.
- Hats and wallet are cosmetic only.
- Reduced motion keeps the same economy.
- Every animation change follows `ANIMATION.md` (blending under spam).

## Sources

- Alto's Odyssey multiplier, with the 4 tricks / 380 → 1,520 example: https://www.keengamer.com/articles/guides/6-tips-for-altos-odyssey/, https://www.imore.com/altos-odyssey-tips-and-tricks-help-you-escape-lemurs-ride-walls-over-chasms-and-more
- THPS combos and multiplier: https://tonyhawkgames.fandom.com/wiki/File:Simplecombointhps3.jpg, https://support.activision.com/tony-hawks-pro-skater-1-2/articles/tony-hawks-pro-skater-1-2-scoring-and-combos. Combo extenders: https://www.osftw.com/features/1547/how-the-manual-ruined-tony-hawks-pro-skater
- Subway Surfers permanent multiplier: https://www.ginx.tv/en/?p=31536, https://sybo.helpshift.com/hc/ar/5-subway-surfers/faq/211-score-multiplier
- Jetpack Joyride missions: https://www.macworld.com/article/215004/jetpack_joyride_for_iphone_and_ipad.html, https://gamedeveloper.com/design/enjoyride
- Crossy Road prize machine: https://en.wikipedia.org/wiki/Crossy_Road, https://www.mobygames.com/game/70612/
- Push your luck: https://meeplescorner.co.uk/blogs/boardgame-glossary/what-are-push-your-luck-games-everything-you-need-to-know-about-this-board-game-mechanic, https://teaching-kids-to-code.pages.dev/lessons/day-13.html
- Session benchmarks: https://gameworldobserver.com/2019/07/02/hyper-casual-167m-sessions-a-year, https://gameindustrylibrary.com/documents/gameanalytics-mobile-gaming-benchmarks-2025/read?page=11, https://mwm.ai/glossary/session-length
- Difficulty ramp pattern: https://seanking11.github.io/gamebootcamp/modules/04-endless-runner

## Changelog (Claude Code, built from HANDOFF.md)

- **Harness:** `sim.js` now fast-forwards (60 Hz steps in a tight loop; 300 s of play take about 10 s), has four bots (passive, trader, trickster, reader), logs per-phase banks, and prints the section 7 acceptance rows. Bots hold their jumps and respawn on a crash (no shield).
- **B1:** `V0 = 1000`, `V *= 1 + clamp(open + cash)/100` on each bank, score = profit. Chains pay alpha `.25·n²` %, PERFECT `+.25` %, slippage `-1` %. Daily goals now "Earn 100 / 250 points".
- **B2:** `CPD` 20000, `+1500` per bull, cap 28000 (`cpX(n)`, `lvlAt(x)`), `PNLK .006`, speed ramp `+8.75%` per bull (cap x1.7 at bull 8), take-profit hint at 45%. Bull interval 22.0-26.5 s in the harness.
- **B4:** PERFECT window 55 ms before the edge and 12 ms after (was 110 / 25). Random taps 4-6 per minute.
- **B5:** phases alternate every 2-3 stretches (first is bull). Terrain tilt `TILT = {bull: -1, bear: 11}` px per candle (the generator itself leans up by about +7% per stretch, so a bull needs little lift and a bear a lot of drop), kind weights shift with the phase, red ticks twice as dense in a bear. Tick values were **halved** (+0.5 / +1.5 / +5, red -1 / -2.5) and green spacing x1.5 (3000-5100 px) so ticks are not most of a passive player's income. Result over 300 s x4: passive long banks about +8-11% in a bull stretch and -8..-13% in a bear one; the phase-reading bot earns 5.9x passive.
- **B3:** a clean chain of n >= 2 adds `.25·n` s to `R.surge` (cap 1.6 s, same x1.55 speed as the bull surge). 300 s x4: trickster bull gap 20.0 s vs passive 22.3 s (10% shorter).
- **M3:** seven chart patterns (see `MARKET.md` section 5, Built). 240 s x5 harness runs: every pattern seen within 180 s in 100% of runs.
- **M5:** rugpulls in Token World: 600 s x4 runs, exactly 2 per run, never before bull 3. Rocket ticks +2% (not +3%) and a drain of 8% x leverage so that a long loses net on the rug.
- **B6:** hat prices 300 / 900 / 2500 (`HATS`), +100 wallet gift at the end of the first run of each calendar day (`cp-gift` = the day key; shown on the results card). Harness, 90 s runs x8 (bots are immortal, so real players earn less): passive 358 per run, trader 486, trickster 756. Taking the doc's 150 (new) / 460 (decent) per run and 3 runs a day plus the gift, days to each hat from an empty wallet: casual (about 250 a day) 2 / 4 / 10 days, new (550 a day) 1 / 2 / 5, decent (1480 a day) 1 / 1 / 2. Investing the wallet in the Big Ball ETF (about +1.9% a real day on average, 1 day = 3 market months) saves 0-1 day: from a 600 wallet a casual player reaches the crown in 7 days instead of 8 (12% sooner), the others in the same whole day. So the ETF yield is a small lever at these horizons (well under the 10-20% target for new and decent players); the hat prices, not the yield, set the pace.
- **B7:** `MIS` is now ten market missions `[id, title, reward, test]` (bank +15% in one stretch 200, bank +3% while short 150, TWISTER 200, dodge a rug in cash 300 (Token World), bank +10% ALL IN 250, break a resistance 200, earn 100 points 100, checkpoint 3 150, 4 PERFECT jumps 100, chain 3 ticks 100); `todays()` picks three by day (`b, b+3, b+7` mod 10). Each pays its reward into the wallet when done. All three done = portfolio level +1 (once a day, `cp-setday`), max level 10: the next run starts with `V0 = 1000 · (1 + .05 · level)` (`cp-plevel`; `R.V0` is fixed per run, so a level-up mid-run does not move the score). The three missions, the level and the start bonus show on the Play tab (`#gcMis`). Checked: rewards add up (100 + 200 + 100), one level per day, next run `V0 = 1050`, a +10% bank scores 105.
- **P1:** game sprite sheets load on demand (`ld()`, `ldStart()`, `ldSkin()`): 2 KB of game images at page load (was about 2.6 MB), 480 KB when the game opens (gold and light-green runner, their trick and love sheets, bull, ticks, hats, dance), the rest the first time a position, power-up or rug needs it (a full tour is 1.3 MB). Drawing falls back to the gold runner until a sheet has arrived.
- **B8 re-tune (HANDOFF 14 / 17 / 18), after the 25% bear share and the neutral start:**
  - **Harness bug found:** a bot that picked up STOP-LOSS kept it (and its P&L floor) for the rest of the run, because the harness respawned on a crash before the shield could be spent. That alone added 20-50% of fake gains per run. The harness now lets a shield absorb a crash first.
  - **STOP-LOSS made weaker:** the P&L floor was too strong when pickups come every stretch. It now lasts 15 s and is used up after absorbing 3% of losses (or any loss event).
  - **Terrain drift controller:** the generator leans up by an amount that changes with the level, so a fixed tilt did not hold. A slow controller (`rawUp`, `TILT = {bull: 150, bear: -2000}` px net drift per stretch) steers each stretch to a small gain in a bull and a real drop in a bear; measured over 6 runs the bull stretches drifted +180 px and the bear ones -1700 px.
  - **Numbers changed:** `PNLK .006 -> .0045`; green tick spacing x1.3 (3900-6600 px); ticks are levered at most 2x (ALL IN still moves the price 3x); alpha `.25·n² -> .2·n²` with a cap of +10% a stretch (`ALPHACAP`); bull spacing `CPS 2000`, `CPM 32000` so the interval stays 22-28 s at full speed; red ticks pay half to an ALL IN short.
  - **Result (120 s x12):** bull interval 25.2 s PASS, trader/passive 2.8x PASS, trader market share 62% PASS, PERFECTs 4.4 a minute PASS, passive never at the cap PASS, errors 0 PASS. **ALL IN SHORT check (item 18):** the `boarder` bot (long in a bull, short then ALL IN on the board in a bear, cash at +12%) earns 1.7x passive at 120 s and 5.1x over 360 s, under the 6x limit, so no cap to 2x was needed (red ticks pay half on the board).
  - **Still failing, and why:** passive earns about 120 pts a minute at 120 s. The 20-60 band contradicts section 6 (a new player earns about 150 per 90 s run, i.e. 100 a minute, and passive is a good proxy for a new player), so the target should be about 60-140 at 120 s; over 360 s passive is about flat. The phase reader beats passive 2.5x only over runs of 300 s or more (a 120 s run has no bear stretch), 1.5x at 120 s. The random-swipe trickster is ALL IN 99% of the time and hits the cap in 8 of 12 runs (target 30%), with alpha above 60% of its bank; it is a stress bot, not a player model.
  - **Not done:** the five human phone runs (the owner plays). Checklist: play 5 runs on a phone; for each note the run length, bulls reached, the cause of the end and the score; targets are a median run of 60-120 s for a new player and a session of about 6 minutes; also note whether swipes felt reliable, whether the bear checkpoint read as different, and whether the Dolla notes were readable.
- **Open at B8 (not done in this pass):** at 60 s the passive bot still earns about 157 pts/min (target 20-60), trader/passive is 1.4x (target 2x), and the market/alpha share rows only make sense over more banks (300 s runs). Re-tune `PNLK`, tick values and alpha inside the +-25% bands, and decide whether the per-minute rows should be measured over 120 s runs.
