# Runner game: the market pivot (decisions + build plan)

**Status: decided.** This file is the single source of truth for the pivot from "collect coins" to "trade the chart". Sections marked ✅ are built; the rest are tasks for Claude Code, in order (section 10). All 3D models the plan needs are already rendered and committed (section 9), so the remaining work is game code only.

## 0. Spirit (non-negotiable)

- It's a happy bouncing ball first. Runs are short, controls are one finger, and the market **never ends a run** (only the existing crashes do). Losses are telegraphed and partial.
- **Teach by playing:** long/short/cash, taking profit, leverage risk, chart patterns and scam tells are learned by doing, never by text walls.
- **No real tickers, logos, prices or advice.** Rugpulls are framed as a scam lesson.
- **Phone first:** one headline number, values shown by colour and size, numbers only in pops.
- **Reduced motion** (`RMQ.matches`): every effect has a static fallback.

## 1. Core loop ✅ (built)

**The ground is the price chart.** Your **position** (set by swiping) earns or loses as the price under the runner moves. The **diamond bull checkpoint** banks it. **The body colour shows the position:**

| Swipe (on the ground) | Key | Trick | Position | Look |
|---|---|---|---|---|
| ↑ | E | split | **LONG 1x**; ↑ again → **2x** (sticky: stays until the next ↑/↓) | light green body (`runner-lgreen`); 2x = strong translucent green glass (`runner-ggreen`) |
| ↓ | S / ↓ | goo | **SHORT 1x**; ↓ again → **2x** | light red (`runner-lred`); 2x = strong translucent red glass (`runner-gred`) |
| ← | A / ← | corkspin | **CASH**: open P&L realized into the cash bar | gold, carrying a briefcase, bills flutter behind (`runner-cash`) |
| → | D / → | spin | **ALL IN**: cash + open back in at **3x in your last ↑/↓ direction** | **riding a skateboard**, strong green (long) or strong red (short) (`runner-skate-ggreen/-gred`); ↑/↓ on the board flip the direction and stay on it |

- **On the skateboard (ALL IN):**
  - **Ride:** the frames are rendered for 5 slopes (−30, −15, 0, 15, 30°), and the nearest one to the ground slope is chosen. The board pitches while the body stays balanced.
  - **Jumps:** the first jump is an **ollie**, the double jump a **kickflip**.
  - **↑ / ↓ always set LONG / SHORT**, in the air too, which steps you off the board.
  - **← in the air** is **JESUS** (arms out wide, board in the front hand); a second ← in the same jump is a **360 SHOVE-IT**.
  - **→** (ground or air) is a **TRE FLIP**; a second → in the same jump is an **INDY GRAB**. On the ground, → jumps first.
  - **← on the ground** goes to CASH (steps off).
  - Board tricks chain and score like the ball tricks. The alternation counters (`R.skL`, `R.skR`) reset on landing.
- **Power-ups are auras**, never a body colour:
  - **STOP-LOSS** (shield): a pink-violet bubble.
  - **INDEX FUND** (magnet): blue field arcs circling.
  - **2x**: gold `$` orbiting.
  - **Combo:** they stack, plus a turning rainbow ring.
  - Code: `auraFront()`, with the glow behind in `player()`.
- **Hats:** 3 purchasable hats are drawn on every frame's head anchor (`HEADS`, exported by the renderer as `head.json`) and tilt with the head.
  - **Prices:** top hat 150, propeller 250, crown 400 points.
  - **Wallet:** every run's score is added to the wallet (`cp-wallet`). Owned hats are in `cp-hats`; the equipped one in `cp-hat`.
- **Menus:** the start and game-over card has **Play / Style / Options** tabs.
  - **Play:** the swipe legend.
  - **Style:** the wallet, a live preview of the runner wearing the hat, and the hat shop (buy / wear).
  - **Options:** the pause menu's settings sections, moved into the card (`hostSettings()`), so there's one set of controls.
- **P&L:** `open += (prevGround − ground) · PNLK · dir · lev`. **Five states:** START (gold, `pos.flat`: already holding LONG 1x, like owning the stock, until the first swipe), LONG, SHORT, CASH and ALL IN. The first ↑ gives LONG 1x.
- **Bull checkpoint** (`cp-bull`): launches up and forward (`R.surge`), and **banks** `open + cash` into the score.
- **Code:** `skinOf`, `skateFrame` (`SKT`/`SKN`), `drawHat`, `auraFront` sit before `player()`; `setPos`, `bank`, `paintPnl`, `PNLK` sit next to `trick()`; the menu functions (`gcTab`, `paintStyle`, `prevRun`, `hostSettings`) sit before `setPause()`.

## 2. Score model (decision)

- **The score stays in points.** Goals, high scores and the daily-goal system keep working unchanged.
- Market P&L reaches the score **only by banking at the bull** (1% = 1 pt). Coins/ticks and tricks also give points as today. This keeps one number and no migration.
- **Open P&L cap:** ±60% per checkpoint stretch ("bubble"/"margin call"). At the cap the HUD glows and hints "take profit!" (or "cut losses!"). *Task M1.*

## 3. Currency: ticks (task M1)

Coins become **tick candles** (rendered, with faces). They add to **open %**, so they are only *yours* once banked. That is the lesson.

| Old coin tier (`CT`) | New sprite | Value |
|---|---|---|
| 0 (1 pt), 1 (2 pts) | `tick-1` | +1% open |
| 2 (5 pts) | `tick-2` | +3% open |
| 3 (15 pts) | `tick-3` (gold band, sparkle) | +10% open |
| new hazard | `tick-r1` / `tick-r2` (red down-candles) | −2% / −5% open |

- **Leverage multiplies ticks too** (`lev`), so ALL IN also triples pickups (and red ticks).
- **SHORT flips red ticks:** they pay +2% / +5% and burst green. Red ticks become something to hunt while short.
- **CASH: ticks pass through you** (dim them to 40% alpha while in cash). Cash is safe, but it doesn't grow.
- **Spawning:** red ticks appear from level 2, about 1 per 6 green, more in bear phases. Never put a red tick on the only safe line through a gap.
- **Draw:** reuse the coin spin, proximity and pickup code; swap `COINI` for tick sprites (`tick-1..3`, `tick-r1..2`), keeping the coin's scale-X spin. Pickup pop shows "+3%".
- The coin sheets `coin-1..4.webp` can be deleted once ticks ship.

## 4. Power-ups → finance (task M2)

Same pickups and forms (glass skins); only names, pops and behaviour change:

| Pickup | New name | Behaviour |
|---|---|---|
| shield | **STOP-LOSS** | Blocks the next **loss event**: a crash (as now), a red tick, or a rugpull drain. Also floors open P&L at 0 while active. |
| magnet | **INDEX FUND** | Pulls every tick in range (green only; red ticks are not pulled unless SHORT). |
| 2x | **DIVIDEND 2x** | Tick values ×2 (stacks with leverage). |
| combo | **BULL RUN** | All of the above, and ticks spawn 1.5× denser. |

**Changed in B8:** STOP-LOSS now lasts 15 s and is used up after absorbing 3% of losses (it floored every loss for as long as it was up, which was too strong).

**Built (M2):** `PU` names are STOP-LOSS / INDEX FUND / DIVIDEND 2x. STOP-LOSS floors open P&L at 0 while it is up and is used up by the next loss: a crash (respawn), a red tick or slippage. DIVIDEND doubles gains only (not red ticks). BULL RUN is all three at once (`R.bullRun`, a pop and message on the rising edge): green ticks spawn 1.5x denser (measured 1.46x). The balance harness no longer uses the shield; bots are kept alive by respawning on a crash (`__L.immortal`).

## 5. Chart patterns as terrain (task M3)

Add pattern segments to the terrain generator's segment picker (`ground()` heights). Each one is a height recipe, optionally with a line object drawn on canvas. Pop the pattern's name once per run when it's cleared without a crash ("CUP & HANDLE ✓").

| Pattern | Shape | Interaction |
|---|---|---|
| **Support** | thin green horizontal line | One-way platform: lands you from above, can bridge a gap. |
| **Resistance** | thin red line above the path | A ceiling you bounce off, unless you hit it during a **split** (↑) or while ALL IN: then **BREAKOUT** (+3% open, a burst). |
| **Moving average** | the existing smooth line | Grind rail: landing on it during a trick slides you along it with sparks; ticks line it. |
| **Cup & handle** | U bowl, small dip, rise | A half-pipe. Going ↑ LONG at the handle lip = BREAKOUT. |
| **Bull flag** | steep pole, then a gently falling channel | A speed ramp with ticks along the channel. |
| **Head & shoulders** | 3 humps, then a drop at the neckline | Telegraphs a fall: red ticks after it. Shorts profit naturally. |
| **Double bottom** | W | Goo-slam (↓↓) both bottoms = DOUBLE BOTTOM +2%. |

Bull phases favour cups, flags and support; bear phases favour head & shoulders, resistance and red ticks.

**Built (M3):** one pattern every 200-300 candles from a shuffled bag of the seven (`nextPattern(phase)` favours cup, flag, support, rail in a bull and head & shoulders, resistance, double bottom in a bear), so each shows up within one bag (about 100 s). Each is a `kind` in `addSeg` and a `pat()` record in `R.pats` (`x0`, `x1`, extras). Things placed relative to candles (`y` of lines, tick heights, guide ticks) are resolved after the phase tilt (`R.fix`).
- **Support:** a pit with a one-way line 115 px above the left edge; `gnd(x)` is the floor in step (you land from above, pass through from below), the line bridges the gap.
- **Resistance:** a red dashed ceiling 300 px above the end of a rising stretch (and 900 px beyond); a bump sends you back down; breaking it needs a split (swipe up) or ALL IN: BREAKOUT +3% alpha.
- **Moving average rail:** a smooth 14-candle rail with a gold glow lined with 4 ticks; landing on it mid-trick grinds (+0.5% alpha, sparks, a short surge) instead of slipping.
- **Cup and handle:** a bowl, a small dip (the handle), a rise; swipe up within 420 px of the lip for BREAKOUT +3%.
- **Bull flag:** steep pole, then a falling channel with 3 ticks and a 0.7 s speed ramp.
- **Head and shoulders:** three humps, then the neckline gap down and 2 red ticks.
- **Double bottom:** a W; goo-slam (down, then down again) near each bottom, both = +2%.
- Each name pops once per run (`R.patSeen`) when cleared without a crash. Not drawn yet: pattern outlines (necklines, the cup rim). Test hook: `_cp.gen(kind)`.

## 6. Market phases (task M4)

- **Phase shifts:** bull ⇄ bear every 45–70 s.
  - A small icon slides in top-left: the diamond bull (`cp-bull` frame 2) or the ruby bear (`bear.webp`), with "BULL MARKET" / "BEAR MARKET".
  - The bear tints the background slightly red/cool and makes terrain trend downward more often (shorts thrive).
- **Real World events** (rare): **circuit breaker** (a sudden −drop, 0.4 s hit-stop, "TRADING HALTED" canvas stamp) and **earnings day** (a stretch of random gaps).

**Built (M4 phases only; circuit breaker and earnings day are not built yet):** `phaseOf(n)` picks bull or bear per stretch (2-3 stretches each, the run starts in a bull), `R.phase` is the current one, the badge `#gPhase` slides in top-left with `cp-bull` frame 2 or `bear.webp` and a label that fades after 3 s, and a bear tints the sky red (`R.phT`).

## 7. Rugpulls: Token World only (task M5)

All the art is rendered: `rug.webp` (tile), `rug-roll.webp` (mid-yank), `rocket.webp`, `devwallet.webp`, `sign-100x.webp`.

1. **Tell (2–3 s ahead):**
   - A too-good pump stretch: steep green climb with `rocket` tokens as ticks (+3% each).
   - A floating `sign-100x` above it, and a blinking `devwallet` icon at the top of the pump.
   - The pump floor is drawn with the `rug` tile on top of the candles.
2. **The pull:** once the runner is about 60% across, the rug slides out (draw `rug-roll` rolling away to the right). The floor under the pump **drops** into a deep red gap-down: a real price crash, so the P&L does the lesson by itself.
   - **LONG** loses (×lev).
   - **SHORT** makes a fortune ("SHORTED THE RUG").
   - **CASH** is safe ("DODGED THE RUG").
   - **STOP-LOSS** blocks the loss.
3. **Rules:** never a run-ender (always land on something). Max 2 per run. Not before level 2.

**Built (M5):** the `rugp` pattern kind (Token World only: `isTW()`, from bull 3, max 2 per run via `R.rugN`, in the pattern bag with weight 2). Layout: 14 flat candles, a 16-candle pump (800 px) with 4 rocket ticks (`TK[5]`, +2% each), a 14-candle plateau covered with the `rug` tile, a 100x sign floating above the base and a blinking dev wallet at the top; the cliff behind the plateau is 1700 px deep. When the runner is 62% across (`pullX`) `rugPull(q)` lowers the floor ahead to the landing level (a real gap-down edge 3 candles ahead), rolls the rug away (`R.rugAnim`, `rug-roll`), and applies the position: LONG pays an 8% x leverage dev-wallet drain on top of the crash, SHORT gets "SHORTED THE RUG" (the crash pays), CASH "DODGED THE RUG", STOP-LOSS is used up and freezes P&L for 2 s. Headless result (one rug, from a long 1x start): long 1x -3.7%, long 2x -6%, all in -10.2%, short +13.2%, cash 0, long with stop-loss +13.6%; nobody died. Reduced motion: the roll sprite does not slide, the sign does not bob.

## 8. Results card (task M6)

Show:
- banked P&L total, best bank and best chain
- patterns spotted
- rugs dodged or shorted

Plus one **lesson line** chosen by what happened, for example:
- "Taking profit at the bull locked in 18%."
- "Going to cash before the rug saved you."
- "Leverage tripled your losses on that drop."

**Built (M6):** the results card shows the banked total (`V/V0 - 1`), best bank, best chain, the patterns spotted (`R.patSeen`), the rug outcomes (`R.rugEv`) and one lesson line from `lessonLine()` (priority: rug outcome, unbanked open gains lost at death, a levered loss, best bank, slippage, alpha, default). Test hooks: `_cp.lesson()`, `_cp.results()`.

**Built (B7):** market missions and the portfolio level, see `BALANCE.md` changelog (B7). Test hooks: `_cp.goals()`, `_cp.plevel()`.

## 9. Asset inventory (all rendered, in `assets/game/`)

| File | What | Generator (`scripts/icons/objects.py`) |
|---|---|---|
| `runner{,-lgreen,-ggreen,-lred,-gred}.webp` | position skins: gold, light/strong green, light/strong red | run/jog/walk/take-off/rise/fall, 35 frames | `o_runner` |
| `runner-cash.webp` | cash run with a briefcase, crop x0 = 26 (`PROP_X0`) | `RUNNER_PROP=case` |
| `runner-skate.webp` | ALL IN: ride loops at 5 slopes + ollie, kickflip, shove-it, tre flip, indy, jesus (74 frames, 10 columns) | `o_skate` |
| `hat-top/prop/crown.webp` | purchasable hats (anchor in `HAT_META`) | `o_hat` |
| `runner-trick*.webp` (5) | 4 tricks × 12 frames | `o_trick` |
| `runner-love*.webp` (5) | checkpoint flight | `RUNNER_FACE=love-noeyes` |
| `cp-bull.webp` | 16-frame diamond bull turn | `o_bull` |
| `bear.webp` | ruby bear icon | `o_bear` |
| `bill.webp` | banknote for the cash trail and dividend showers | `o_bill` |
| `tick-1..3.webp`, `tick-r1..2.webp` | currency candles | `o_tick` |
| `rug.webp`, `rug-roll.webp`, `rocket.webp`, `devwallet.webp`, `sign-100x.webp` | rugpull set | `o_rug`, `o_rocket`, `o_devwallet`, `o_sign100x` |
| `heart.webp`, `dance.webp` | love eyes, game-over dance | existing |
| `pu-shield.webp`, `pu-magnet.webp`, `pu-x2.webp` | STOP-LOSS (glass shield, gold rim), INDEX FUND (sapphire glass magnet), DIVIDEND (money plant: glass pot, gold coin leaves) | `pu2-shield`, `pu2-magnet`, `pu2-dividend` (24-frame turntable) |

Render recipes are in `CLAUDE.md` (repo root).

## 10. Build order: done

M0-M7 are all built (Nov 2026; history in `docs/archive/HANDOFF-2026-11.md`, balance numbers in `BALANCE.md`). Code names from M1: `R.ticks`, `TK`, `TICKI`, `placeTicks` (`tickX` green spawn cursor, `redX` red); `TK[t] = {v, im, r, c, g, sfx}`, `t` 0-2 green (`tick-1..3`), 3-4 red (`tick-r1..2`). Open P&L and ticks clamp at ±`OPENCAP`; red ticks never spawn near a gap (`nearGap(x)`).

## 10b. Currency: the Dolla (built)

- **What it is:** points are **Dolla**, a banknote in the Washington-bill layout with an engraved smiley in the portrait oval. "THE UNITED BALLS OF BOUNCE", "IN BULLS WE TRUST", "ONE DOLLA", a `$` seal and a `D` seal.
- **Name:** "Dolla", never "dollar", so it can't be mistaken for real money. Plural: Dolla.
- **Where it shows:**
  - The HUD score (note icon + Inter 900; the old 8-bit pixel digits are gone).
  - The wallet ("Dolla to spend"), hat prices, ETF value and away report, missions, and the daily gift.
  - The cash-run trail (`bill.webp` is a padded Dolla note).
- **Assets:** `dolla.webp` (tight, about 2.2:1) and `bill.webp` (square, for particles). Texture: `scripts/icons/dolla_texture.py` → `dolla_tex.png`; 3D curl and lighting: `o_dolla` in `objects.py`.
- **Ideas for later (HANDOFF 19–20):** notes fly to the counter on banking; higher denominations (5 / 20 / 100) with other smiley portraits as cosmetics and for big pops.

## 11. Big Ball ETF (built)

Long-term investing for wallet points, in the menu's **Invest** tab (start and game-over card).

- **What it is:** buy or sell in 100s or all. Value = units × price. Selling returns points to the wallet. No fees.
- **The price is a replay of a big-cap index, 2000–2025:**
  - It uses the yearly total returns (`BBE_Y`). Each year is split into 12 months of seeded noise, adjusted so the year sums to the real return.
  - Famous shock months are kept (`BBE_SHOCK`: Sep 2001, Sep 2002, Oct/Nov 2008, Mar 2009, Feb–Apr 2020, Jun 2022).
  - **Randomizer:** every player gets a random seed and a random start year (2000–2015) on first visit. After Dec 2025 it loops to 2000 and keeps compounding.
- **Time:** 1 real day = 3 market months (`BBE_MPD`), advanced from the last visit (`cp-bbe.t`), so it moves while you're away.
- **News:** on opening the game, the Play tab shows "▲ Big Ball ETF +x% while you were away →" (tap → Invest), and the Invest tab explains the move (from → to market date, %, points).
- **Chart:** the last 3 market years, green or red, with the market date.
- **Self-check** (`_cp.bbe`): `price(312)/price(0)` ≈ 7.5 for any seed, i.e. 2000–2025 total growth. Real data is about 7×; the year values are rounded.
- **Storage:** `cp-bbe = {u units, b invested basis, c market month cursor, t last real ms, s seed}`; the wallet is still `cp-wallet`.
- **Code:** the `BBE_*`, `bbeSeries`, `bbePrice`, `bbeAdvance`, `bbeAway` and `paintBBE` functions, plus the buy/sell buttons, sit just before the menu tabs code.
- **Spirit:** labelled "a game, not advice"; no real ticker names (it's "Big Ball ETF"; the years are shown as history).
