# Runner game: the market pivot (decisions + build plan)

**Status: decided.** This file is the single source of truth for the pivot from "collect coins" to "trade the chart". Sections marked ✅ are built; the rest are tasks for Claude Code, in order (section 10). All 3D models the plan needs are already rendered and committed (section 9), so the remaining work is game code only.

## 0. Spirit (non-negotiable)

- It's a happy bouncing ball first. Runs are short, controls are one finger, and the market **never ends a run** (only the existing crashes do). Losses are telegraphed and partial.
- **Teach by playing:** long/short/cash, taking profit, leverage risk, chart patterns and scam tells are learned by doing, never by text walls.
- **No real tickers, logos, prices or advice.** Rugpulls are framed as a scam lesson.
- **Phone first:** one headline number, values shown by colour and size, numbers only in pops.
- **Reduced motion** (`RMQ.matches`): every effect has a static fallback.

## 1. Core loop ✅ (built)

**The ground is the price chart.** Your **position** (set by swiping) earns or loses as the price under the runner moves. The **diamond bull checkpoint** banks it.

| Swipe | Key | Trick | Position | Look |
|---|---|---|---|---|
| ↑ | E | split | **LONG 1x**; ↑ again → **LONG 2x** | 1 / 2 green 3D arrows out of the head |
| ↓ | S / ↓ | goo | **SHORT 1x**; ↓ again → **SHORT 2x** | 1 / 2 red 3D arrows pointing down from the crotch |
| ← | A / ← | corkspin | **CASH**: open P&L is realized into the cash bar (safe, frozen, earns nothing) | runs carrying a briefcase, bills flutter behind (`runner-cash*`) |
| → | D / → | spin | **ALL IN**: cash + open back in at **LONG 3x** | confident strut, big sunglasses, 3 arrows (`runner-allin*`) |

- **P&L:** `open += (prevGround − ground) · PNLK · dir · lev`, with `PNLK = 0.004` % per px. Gaps are real price gaps. A run starts LONG 1x.
- **Bull checkpoint** (`cp-bull`, 16 frames, one slow turn per 4 s, diamond glow): launches the runner **up and forward** (`R.surge` 1.6 s, speed ×1.55) and **banks** `open + cash` into the score (1% = 1 pt, score floor 0), popping "+x% BANKED".
- **HUD** `#gPnl`: open % (green/red), plus "· cash ±x%" when it isn't zero. Position changes flash through `msg()`.
- **Code:** `setPos`, `bank`, `paintPnl`, `PNLK` next to `trick()`; the P&L and bill-trail tick at the top of the step's trick block; the sheet override (`CASHI`/`ALLINI`, `PROP_X0`) and arrows in `player()`; bills as fx with `f.b`.
- **Tricks and chains** (`ANIMATION.md`) are unchanged: they still score style points through `chainName()` and `3·n²`.

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

## 6. Market phases (task M4)

- **Phase shifts:** bull ⇄ bear every 45–70 s.
  - A small icon slides in top-left: the diamond bull (`cp-bull` frame 2) or the ruby bear (`bear.webp`), with "BULL MARKET" / "BEAR MARKET".
  - The bear tints the background slightly red/cool and makes terrain trend downward more often (shorts thrive).
- **Real World events** (rare): **circuit breaker** (a sudden −drop, 0.4 s hit-stop, "TRADING HALTED" canvas stamp) and **earnings day** (a stretch of random gaps).

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

## 8. Results card (task M6)

Show:
- banked P&L total, best bank and best chain
- patterns spotted
- rugs dodged or shorted

Plus one **lesson line** chosen by what happened, for example:
- "Taking profit at the bull locked in 18%."
- "Going to cash before the rug saved you."
- "Leverage tripled your losses on that drop."

## 9. Asset inventory (all rendered, in `assets/game/`)

| File | What | Generator (`scripts/icons/objects.py`) |
|---|---|---|
| `runner*.webp` (5 skins) | run/jog/walk/take-off/rise/fall, 35 frames | `o_runner` |
| `runner-cash*.webp` (5) | same 35 frames, carrying a briefcase; crop x0 = 26 (`PROP_X0`) | `RUNNER_PROP=case` |
| `runner-allin*.webp` (5) | same 35 frames, strut + sunglasses | `RUNNER_PROP=shades` |
| `runner-trick*.webp` (5) | 4 tricks × 12 frames | `o_trick` |
| `runner-love*.webp` (5) | checkpoint flight | `RUNNER_FACE=love-noeyes` |
| `cp-bull.webp` | 16-frame diamond bull turn | `o_bull` |
| `bear.webp` | ruby bear icon | `o_bear` |
| `arrow-up.webp` / `arrow-down.webp` | position arrows | `o_arrow` |
| `bill.webp` | banknote for the cash trail and dividend showers | `o_bill` |
| `tick-1..3.webp`, `tick-r1..2.webp` | currency candles | `o_tick` |
| `rug.webp`, `rug-roll.webp`, `rocket.webp`, `devwallet.webp`, `sign-100x.webp` | rugpull set | `o_rug`, `o_rocket`, `o_devwallet`, `o_sign100x` |
| `heart.webp`, `dance.webp`, `pu-*.webp` | love eyes, game-over dance, power-ups | existing |

Render recipes are in `CLAUDE.md` (repo root).

## 10. Build order (each task: implement, test with the `_test.html` harness, check reduced motion, update this file's ✅)

| Task | Scope | Done when |
|---|---|---|
| ✅ M0 | Swipe positions, terrain P&L, bull banking and surge, arrows, cash/all-in runs | built |
| ✅ M1 | Ticks replace coins (values, leverage, SHORT flips red, CASH passes through), red ticks, ±60% cap | built: see the M1 notes below |
| M2 | Power-up renames and behaviours (section 4) | pops/messages use the new names; stop-loss blocks a red tick |
| M3 | Patterns: support, resistance + breakout, MA grind, cup & handle, bull flag, head & shoulders, double bottom | each pattern appears within ~3 min of play; name pop once per run |
| M4 | Bull/bear phases, circuit breaker, earnings day | phase icon slides in; bear trends down |
| M5 | Rugpulls (Token World) | tell → yank → P&L follows the position; max 2 per run, never fatal |
| M6 | Results card lessons | the card shows the lesson line chosen by the run's events |
| M7 | Balance pass: PNLK, tick values, phase lengths | a median run banks between −10% and +40% over 3 bulls |

## M1 notes (built)

- **Code names:** `R.coins`, `CT`, `COINI`, `placeCoins` are now `R.ticks`, `TK`, `TICKI`, `placeTicks` (`tickX` is the green spawn cursor, `redX` the red one). `TK[t]` = `{v, im, r, c, g, sfx}`; `t` 0-2 green (`tick-1..3`), 3-4 red (`tick-r1..2`). Sheets `coin-1..4.webp` are deleted.
- **Pickup:** `open += v · lev`, doubled when it is a gain and DIVIDEND 2x is on, clamped to ±`OPENCAP` (60). SHORT turns a red tick's `v` positive. In CASH the tick is skipped entirely (drawn at 40% alpha). Pops show `+3%`; a red tick pop is red, resets the chain, shakes and flashes.
- **Spawning:** green ticks keep the old cadence (one every 2000-3400 px, guide ticks over gaps). Red ticks come from level 2 on their own cursor (`redX`, one every 5000-10000 px, about 1 per 7 green in a headless sample), 70% `tick-r1` and 30% `tick-r2`, and only on open ground: `nearGap(x)` (14 candles each side) must be false, so a red tick is never on the only safe line through a gap.
- **Points:** ticks no longer give score directly; only banking at the bull does. The chain counter still runs on green pickups (`CHAIN x5` pops, the "Chain 3 ticks" goal) but the old ×2/×3 multiplier is gone, so the HUD shows `chain n`.
- **Cap:** terrain P&L and ticks both clamp at ±60. At the cap the HUD shows "take profit!" / "cut losses!", glows (`.gPnl.cap`, no pulse under reduced motion) and `msg()` says it once until the open % drops 5 below the cap. Banking resets it.
- **Tested headlessly:** tick values 1/3/10, red -2/-5, SHORT flips to +5, ALL IN triples (+9 for a tick-2, -6 for a red tick-r1), CASH passes through, DIVIDEND doubles, cap at +60/-60 with hint, no red ticks below level 2 and none near gaps, reduced motion and no 4xx.
- **Not done here (later tasks):** STOP-LOSS blocking a red tick (M2), bear phases adding more red ticks (M4), balance of values against `PNLK` (M7).
