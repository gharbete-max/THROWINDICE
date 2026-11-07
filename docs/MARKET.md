# Runner game: market redesign (plan)

Turn the runner from "collect coins" into "grow a portfolio", while keeping the spirit: a happy bouncy ball, short runs, forgiving, readable on a phone. Each step below ships on its own. Animation rules live in `ANIMATION.md`.

## 0. Guardrails (apply to every step)

- **It's still a game about a bouncing ball.** Losses are rare, telegraphed and partial. The market never ends a run by itself (only the existing crashes do).
- **No real tickers, logos or prices.** Nothing that reads as advice. Rugpulls are framed as a scam lesson (Token World).
- **Phone readability:**
  - Token value is shown by colour and size. A number appears only in the pickup pop.
  - One headline number on the HUD (the % return); the portfolio value is small.
- **Reduced motion:** every new effect falls back to a static state change.

## 1. Score = portfolio, gains are open until banked

- The run starts at **100** (index points; shown as "$1,000" in the results card).
- **Open gains** (`R.open`, %) are what pickups add to. They are shaky:
  - red candles, rugpulls and sloppy landings take from them
  - they show as a pulsing green/red bar under the HUD number
- **Banked** (`R.bank`): the briefcase checkpoint becomes **TAKE PROFIT**.
  - Open gains compound into the portfolio: `value *= 1 + open/100`, then `open = 0`.
  - A dividend shower of ticks plays, and "+12.4% banked" pops.
- **HUD headline:** total return `value·(1+open/100)/100 − 1` as **+38.2%**.
- **Pushback, built in:**
  - Compounding happens **only when banking**. Between checkpoints gains add linearly, so early ticks aren't worthless and the numbers stay sane.
  - `open` is capped at +60% per stretch: the "bubble". Reaching the cap makes the bar glow and hints "take profit!".
- **High scores** become the best return. Old coin high scores are migrated once by showing them as "classic best".

## 2. Currency: ticks

| Was | Now | Value | Look |
|---|---|---|---|
| coin tier 1 / 2 / 3 | **tick** small / medium / big | +1% / +3% / +10% open | glossy green up-candle with a wick; bigger ones get a glow |
| — | **red tick** | −2% / −5% open | red down-candle; dodge it (or short it, see 4) |
| briefcase cash | **dividend** | +2% per banked checkpoint, ×streak | banknotes burst from the case on TAKE PROFIT |

- **Rendering:** add `o_tick(tier, red)` to `scripts/icons/objects.py`. Re-use the coin's spin and proximity code; only the sprite and the value change.
- **Sounds:** the coin "ding" pitch rises with tier. The red tick gets a soft "bonk" plus a down-blip.

## 3. Power-ups → finance concepts (same forms, new meaning)

| Power-up | Now called | Effect |
|---|---|---|
| shield (purple-red glass) | **STOP-LOSS** | blocks one loss: a red tick, a rugpull drain or a sloppy-landing fee |
| magnet (blue glass) | **INDEX FUND** | pulls every tick nearby: "own the whole market" |
| 2x (green, $ eyes) | **LEVERAGE 2x** | doubles gains **and** losses on open. More honest than plain 2x. |
| combo (rainbow) | **BULL RUN** | everything stacks; ticks spawn denser |

Only the labels, pop texts and the loss doubling change; the forms and sheets stay.

## 4. Tricks as trading moves

The swipe tricks stop being score garnish and become how you **interact with the market**. Each keeps its existing animation.

| Flick | Trick | Market move | What it does |
|---|---|---|---|
| ↙ | Corkspin | **SHORT** | For the duration, **red ticks pay instead of hurt**: touching one gives its value as a gain, and it bursts green. Turns hazards into skill pickups. |
| ↘ | Spin | **SCALP** | A small spin vortex pulls ticks within about 140 px. Ticks caught mid-spin are worth +50%. A quick, greedy grab. |
| ↑ | Split | **STOCK SPLIT** | Legs out = a wide pickup hitbox (+80% width). Every tick caught in the split is split 2:1 into two pops (same total, double count toward chains). Also **breaks resistance** (see 5). |
| ↓ | Pancake goo | **BUY THE DIP** | Slamming onto a dip, support line or cup bottom = "BOUGHT THE BOTTOM", +5% open. Goo squashes red ticks it lands on (no loss). **Goo is sticky:** goo when a rug pulls means you stick, and keep half the open gains (see 6). |

### Chains = alpha

- A clean landing of an n-trick chain adds **+0.5·n² % open**, on top of the trick points: 1 → +0.5%, 2 → +2%, 3 → +4.5%. It shows in the chain pop: "TWISTER +2% alpha".
- **Sloppy landing** (mid-rotation) = **slippage**: −1% open. The stop-loss blocks it.
- **Market names for chain combos** (`chainName()` swaps these in when the market mode is on):

| Chain | Name |
|---|---|
| cork → spin | **HEDGED** (short + long) |
| split → goo | **SPLIT & DIP** |
| spin → spin | **HIGH FREQUENCY** |
| cork → cork | **DOUBLE SHORT** |
| goo slam | **CAPITULATION** |
| 3+ tricks | **ALPHA ×n** |

## 5. Technical patterns as terrain

The terrain generator already draws a candle chart with gaps and a smooth moving-average line. Add **pattern segments** to the generator's segment picker: each is a short height recipe, plus an optional object.

| Pattern | Shape in the run | Interaction |
|---|---|---|
| **Cup & handle** | U bowl, small dip, rise | A half-pipe. A trick launched off the handle lip = **BREAKOUT**, ×2 on that chain's alpha. |
| **Bull flag** | steep pole, then a gently falling channel | A speed ramp: ticks line the channel. |
| **Double bottom (W)** | two dips | Goo-slam both bottoms = **DOUBLE BOTTOM** bonus. |
| **Head & shoulders** | three humps, then a drop at the "neckline" | Telegraphs a fall: red ticks after it; SHORT through it to profit. |
| **Support** | a thin green horizontal line | A one-way platform: catches you from above (and saves you over a gap). |
| **Resistance** | a thin red horizontal line above the path | A ceiling you bonk (bounce down) unless you hit it in **split** or with leverage active: then you smash through for **BREAKOUT +3%**. |
| **Moving average** | the existing smooth line | A **grind rail**: land on it in split pose (legs straddling) and slide with sparks; ticks along it. |
| **Gaps** | already there | Pits. Support lines sometimes bridge them. |

- Clearing a pattern segment cleanly pops its name ("CUP & HANDLE ✓") once per run. Players learn the names by playing.
- Patterns are chosen by phase (6): bull phases favour cups, flags and support; bear phases favour head & shoulders, resistance and red ticks.

## 6. Market moods and rugpulls

- **Bull / bear phases:** every 45–70 s.
  - The background tint, music filter and speed shift.
  - In a **bear** phase ticks are worth +1 tier ("buy the dip") but red ticks are denser.
  - The phase name slides in small at the top: "BEAR MARKET".
- **Circuit breaker** (Real World): a sudden red cascade triggers a 0.4 s hit-stop with a "TRADING HALTED" stamp, then play resumes.
- **Earnings day** (Real World): a stretch of random gap-ups and gap-downs.
- **Rugpull (Token World only):**
  - **Telegraph:** a too-good pump stretch with rocket ticks, a "100x" sign and a little "dev wallet" icon that blinks, 2–3 s ahead.
  - **The pull:** the floor segment is yanked away like a rug sliding out, and you drop to the next level.
  - **Cost:** open gains drain with a red ticker roll. Never the run.
  - **Saves:** stop-loss blocks it; goo sticks (keep half); jumping before the yank avoids it entirely ("DODGED THE RUG").
  - **At most twice per run.**

## 7. Results card

Show:
- total return
- banked versus lost to rugpulls and slippage
- best chain
- patterns spotted
- a one-line "lesson" chosen by what happened (for example "Taking profit protected 18% of your gains"), matched to the site's education tone

## 8. Build order

1. **Ticks + % scoring + TAKE PROFIT** (sections 1–2, coin swap only). This changes the feel the most for the least work.
2. **Power-up renames, and leverage doubling losses** (3).
3. **Tricks as trading moves + chain alpha + market chain names** (4). Uses today's animations.
4. **Patterns: support, resistance, MA grind rail, cup & handle, bull flag** (5).
5. **Bull/bear phases, rugpulls in Token World, circuit breaker and earnings day** (6).
6. **Results card lessons** (7).

Each step: test in the browser (`_test.html` harness, never committed), check reduced motion, and update this file's status.
