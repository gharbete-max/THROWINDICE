# QA report — 2026-10-27

Headless Chromium (Playwright), `index.html` opened from disk. Everything below was actually run.

## Passed
- Static: 0 duplicate IDs, 0 broken `#` links, 0 undefined inline handlers, every `target=_blank` link has `noopener`, `node --check` on the script.
- 0 console or page errors in every run below.
- Dark and light × Real and Token × 390 / 820 / 1280 px: no horizontal overflow; every visible text node meets WCAG AA (4.5:1, 3:1 for 24px+) in its default state.
- Theme toggle persists after reload; follows `prefers-color-scheme` on first load.
- All 6 bottom-nav buttons in each world land on their section (Token "Issuance" was broken in V31, fixed).
- Quick Tour opens in each world with the right content, focuses its button, closes on Escape.
- Portal overlay contains no text. With reduced motion it finishes in about 45 ms.
- Save / unsave, profile list, persistence across reload, remove, Escape to close, copy list.
- Region filter (Europe shows 5 of 11).
- Fund page: four questions render with real numbers; missing data shows a dash.

## Not tested
- Hover, active, disabled and placeholder contrast states.
- Real screen reader; keyboard focus appeared on the first 8 tab stops but full keyboard-only use of every control was not exercised.
- Safari / Firefox; real phones.
- Clipboard path in a secure context (fallback prompt exists).
- Chart and card values were not independently verified against a second source.

## Known limits
- Fees come from V31's issuer-page citations dated 26 Oct 2026; re-verify before relying on them.
- Facts come from a free Yahoo-based pipeline (one ticker, IRBO, served from stale cache on the last run).
- Token World figures are V31's dated snapshots; the pipeline has no token data yet.
- Buy links are placeholders (`example.com`).

## Update — colourful rebuild
- Market stats (last year, worst fall, bumpiness, volume, price path) removed from the page; `data/facts.json` is still refreshed monthly but not shown.
- Loud colour-block design restored (lime, magenta, amber, cyan, rose, purple; cooler set in Token World), black/white page background, light/dark toggle.
- "Where to buy" opens a modal with placeholder broker names (Interactive Brokers, DEGIRO, Trading 212; Coinbase, Kraken, Binance) linking to their plain homepages. No affiliate tags.
- Re-run after the change: no console errors, no overflow, no contrast failures (dark/light × Real/Token × 390/820/1280); buy modal, saved list, fund tiles, Quick Tour and nav work.

## Update — candy and motion
- Cards are neutral again; colour lives in glossy "candy" accents (icon orbs, buttons, tags, active nav, filters). Gel highlights on pills, gumdrop highlights on circles.
- Motion: scroll-reveal pop-in (staggered), bobbing orbs, jelly squash on hover, sheen sweep across candy buttons, bouncing nav icon, star pop, floating coin. All skipped with `prefers-reduced-motion`.
- Re-checked: no console errors, no overflow, no contrast failures; buy modal, saved list, tiles, tour and nav still work.

## Update — kitten sliders and Basics page
- All range inputs are wrapped: a kitten pushes a rolling ball (right) or drags it back (left); the native input stays underneath so mouse, touch and arrow keys work. Verified by drag (right then left flips the kitten, `moving` toggles), keyboard (Arrow key moves years), and Reset.
- "Fees" is now "Basic skills for saving and investing": fee calculator, the four big questions, and one "Why people invest at all" block (inflation, alternative cost, pensions).
- Re-run: no console errors, no overflow, no contrast failures, no duplicate IDs; buy modal, saved list, tour and nav still work.

## Update — fund list, kittens under the track, typical-fund calculator
- ETF page is now a filterable list of 25 funds (10 with sourced fees; 15 added with no fee and a "check the fund page" note). Clicking a fund shows what is inside, the four questions, and links to justETF / etf.com / stockanalysis holdings / provider. Reviewed quarterly; the monthly price job no longer runs on a schedule.
- UCITS entries carry justETF ISIN links only where the ISIN is certain (VWCE, SWDA, CSPX, EIMI, EQQQ, SGLN); other links are searches or per-ticker URLs and were not click-tested from this sandbox.
- Token cards: added Solana, Chainlink, Paxos Gold, Tether Gold (links to their official sites, not click-tested).
- Calculator starts at a typical fund: 7% growth (a guess; S&P 500 about 10% since 1928, world stocks about 8% since 1970, sources differ) and 0.14% cost (ICI average for index equity ETFs). Figures came from search results; the source pages could not be fetched from this sandbox.
- Kittens moved under the track so the slider no longer covers them.

## Update — tiles lead to ETFs, smug cat, hanging kittens
- Every tile (countries, sectors, themes, commodities, token cards, token category detail) opens the ETF page filtered to that theme (39 themes, each checked to show exactly its listed funds). Token tiles leave Token World through the portal first. "Show all funds" or any category pill clears the filter.
- ETF list grew to 92 funds (10 with sourced fees, the rest linking out). Crypto tiles map to spot bitcoin/ether funds or blockchain-company funds; stablecoin and tokenized-fund tiles map to short T-bill funds as "cousins", with a note that they are not the tokens.
- Smug cat with glasses and a toothy grin guides the ETF page.
- Kittens now hang from the yarn balls. Ball follows the slider with a spring; the cat swings as a damped pendulum with paw friction, heavier than a free pendulum, clamped to about ±60° (measured peak ≈ 50° on a very fast drag; settles in ≤ 250 ms).
- Re-run: no console errors, no overflow, no contrast failures, no duplicate IDs, nav lands.

## Update — glued sliders, awkward dog, clickable fund tiles, TradingView charts
- Ball now sits exactly on the slider thumb (measured gap ≤ 0.3 px while dragging, at rest and with the keyboard). Only the cat has physics (pendulum driven by the ball's smoothed acceleration; peak ≈ 30–50° on a very fast drag).
- Smug cat replaced by an awkward dog (dot eyes, no glasses, tongue out, animated drool).
- Fund tiles are fully clickable and open the details panel with links; token and theme tiles open their ETF lists.
- "Show chart" (US-listed ETFs) and "📈 Chart" (BTC, ETH, SOL, LINK, PAXG, XAUT) open a TradingView mini chart in a modal; it loads only on click. Verified in headless Chromium for SPY, IBIT, EWG, FBTC, BTC and XAUT (real data rendered); UCITS funds and ETCs have no chart button. If the host blocks the script (e.g. the claude.ai preview) the modal shows a fallback message and a TradingView link.

## Update — glide on release
- Flicking a slider and letting go keeps it gliding with friction (soft bounce at the ends, then it eases onto the nearest step). Measured: a fast flick released at 21 years glided 27 → 32 → 35 → 37 → 38 and stopped; a slow release does not glide; ball stays glued to the thumb (gap ≤ 0.3 px); calculator updates during the glide. Skipped under `prefers-reduced-motion`.

## Update — bubble pit
- The ETF page no longer lists all funds. It shows 45 "piles" (themes grouped under Countries, Sectors, Big ideas, Everything & bonds, Commodities, Crypto & tokens). Every fund belongs to at least one pile (checked).
- Clicking any theme tile or pile opens a full-screen pit where that theme's funds drop in as heavy, glossy bubbles (gravity, wall/floor/bubble collisions with low bounce, squash on impact, sized to fill roughly half the screen). Clicking a bubble pops it (sparks) and opens that fund's details; from Token World the portal runs first. A wobbling "go back!" arrow, Escape, or the pop closes the pit. Reduced motion shows a plain wrapped grid instead of physics.
- Checked in headless Chromium: all 45 themes open with the expected bubble count; on the 7 themes sampled for physics, bubbles never overlap or leave the field and ease to rest within about 10 s; back/Escape close, reduced motion shows a static grid, pop enters the fund (also from Token World), save/buy/chart still work. One console message from TradingView's own iframe on close ("Cannot listen to the event from the provided iframe") is third-party noise.
- Not tested: touch taps on bubbles, Firefox/Safari, very small phones.

## Update — zoom + confetti pop, throwable bubbles, fund-specific four questions
- Tap a bubble: it zooms ~30% while the others dim, pops with a 54-piece confetti burst (confetti keeps flying after the pit closes), then the fund opens. Keyboard (Enter/Space) pops too; reduced motion skips straight to the fund.
- Press and hold (≈0.2 s) or drag a bubble to grab it; release to throw (velocity from the pointer, capped); grabbed bubbles shove others. Verified with a mouse (grabbed flag set, throw velocity after release) and a touch tap on a 390 px viewport (opens the fund, no overflow). A touch drag/throw was not run.
- The four questions are now fund-specific: 16 fund profiles (broad world, S&P 500, Nasdaq, single country, sector, narrow theme, broad/long bonds, T-bill cash, physical metal, futures, commodity companies, coins, crypto companies, dividend, small caps) give each fund its own plain-language answer, a "Look at:" tip for where to check, and extras (UCITS currency note, accumulating vs distributing, futures roll cost). All 92 funds map to a profile and render without gaps. The text is general guidance, not numbers, and has not been checked fund-by-fund against factsheets.

## Update — selected glow, orb beside the title, softer drop, hidden size tiers
- The selected-fund panel now has a pulsing glowing border in the fund's own candy colour, a "✓ SELECTED FUND" tag, and the fund's bubble (same colour and icon) beside its name; it flashes when a new fund is picked.
- Initial drop is less bouncy: first rebound ≈ 21% of the impact speed (was about 40%).
- Bubble size follows a hidden tier per fund (volume based, 4 tiers); e.g. in Crypto IBIT is the biggest and the company funds the smallest. Tiers are never shown. 40 of 92 tiers are rough estimates because those funds have no data in facts.json.
- Re-run: no console errors, no overflow, no contrast failures; pit, pop, throw, reduced motion and mobile tap still work. Bubble fill reduced to ~32% of the screen and a stronger calm-down so the bigger tier-4 bubbles come to rest without overlapping (7 themes checked at 9 s).

## Round: Token World space revamp (2026-10-27)
- Crypto/token piles moved from Real World ETF page to Token Home ("Token fund orbit"); popped funds dock in Token World.
- Very slow nebula (300s) + star drift (600s) background, forced dark palette in Token World, ringed candy planets; reduced motion = static.
- Checked: qa.js (overflow/contrast, both themes, 3 widths) clean; no console errors; real world pile list has no crypto group.

## Round: Digest mode (2026-10-27)
- Paragraphs over 90 characters show 2 lines with a "More ▾" pill; Token World intro points folded into one "What to watch" fold.
- qa.js clean (overflow/contrast, both themes, 3 widths); no console errors.

## Round: Less text (2026-10-27)
- Page intros, section blurbs, disclaimers and news summaries hide behind an ⓘ button; other long text clamps to 2 lines with More.
- Token World market context and case studies folded into one "📚" fold.
- qa.js clean; no console errors.

## Round: Token fold + alien cat (2026-10-27)
- Brokers, Issuance and Real examples folded; bottom nav opens the fold before scrolling.
- Selected fund resets and page scrolls to top when switching worlds.
- Alien cat (green, two antennas) replaces the old Token fund orbit title; mobile content zoomed 1.12x.
- qa.js clean; no console errors.

## Round: Basics nav, sticker, currencies, chart iframe (2026-10-27)
- Basics is the bottom-right nav button in both worlds (in Token World it shows the Basics page without leaving the world).
- Fee calculator: 85 currencies (EU, other Europe, Americas, Asia) with scaled slider ranges.
- Starburst sticker on the fee card.
- TradingView chart now a direct iframe (widgetembed), no script injection. Not renderable in the offline test sandbox; verify on a live connection.
- qa.js clean; no console errors.

## Round: Balloon More + focus pages (2026-10-27)
- Long text is fully hidden behind a "🎈 More" button; tapping pops the balloon with confetti and pops the text in (reduced motion: plain toggle).
- "Follows via X" tags removed. Country, sector and commodity cards open a focus page with a TradingView news feed (country filter or fund ticker) plus Google News links. Feeds need a live connection to render; not renderable in the offline test sandbox.
- Coin hint bubble now hides after 3.5 s.
- qa.js clean; no console errors.

## Round: TradingView CSP (2026-10-27)
- The artifact preview blocks all third-party frames and scripts (ERR_BLOCKED_BY_CSP). Embeds now use TradingView's script loader, fall back to an s.tradingview.com iframe, and on a CSP violation show link buttons instead of an error page. Verified with a simulated CSP; live rendering still needs the hosted site or a local file.

## Round: Carousels, balloon M, Office-style smileys (2026-10-29)
- Every tile row is a one-tile swipe carousel with prev/next and a counter.
- "More" is a red balloon with a white M: floats, wobbles on hover, bursts into confetti and red scraps, re-inflates on Less. Hand-built SVG/CSS.
- Real-World and Token World coins are glossy Office-97-style smileys (yellow, blue), hand-drawn SVG.
- Hugging Face generation (Qwen-Image, Wan 2.2) was tried but anonymous ZeroGPU quota is exhausted; needs an HF token in the environment.
- qa.js clean; no console errors.

## Round: Roll wheel (2026-10-29)
- Tile rows no longer slide: only the current tile shows and the arrows (or a swipe) roll it out and the next in, lucky-wheel style, looping at the ends. Filters re-sync the roll. Reduced motion swaps instantly.
- qa.js clean; no console errors.

## Round: Deflated balloon (2026-10-29)
- After the pop, the leftover is a limp deflated balloon (not an X); clicking it re-inflates the balloon and hides the text again.
- qa.js clean; no console errors.

## Round: Hotdog roll (2026-10-29)
- Tile changes now roll like a hotdog on a grill: the tile becomes a rounded capsule and turns about its long horizontal axis while the next one rolls in at the same time (Web Animations, 760 ms). Next and previous roll opposite ways. Reduced motion swaps instantly.
- qa.js clean; no console errors.

## Round: Roll keeps its shape (2026-10-29)
- During a roll both tiles keep their exact size and corner radius (overlaid absolutely, container height eased between tiles); no grid or capsule re-layout. Verified by measuring both tiles at 30/200/400/600 ms.
- qa.js clean; no console errors.

## Round: Momentum spin (2026-10-29)
- Arrow clicks add to a target; the roll chases it with a speed that grows with clicks in the last 650 ms, so spamming accelerates, and it locks on a tile about 0.3-0.5 s after the last click. Both directions, wrap-around and filters verified (12 clicks forward land 12 tiles ahead; 5 back land 5 behind).
- qa.js clean; no console errors.

## Round: Calmer spin (2026-10-29)
- Removed the opacity fades that made the roll blink; faces now hide through backface culling only. Top speed 6 tiles/s (was ~25), gentler acceleration. Sampled 150 frames of a 3-click spam: no frame without a visible tile, no container height jumps over 14 px.
- qa.js clean; no console errors.

## Round: Blink fix, bigger fixed spin buttons (2026-10-29)
- Root causes of the blink: tiles had a bouncy 0.35 s CSS transform transition that lagged the per-frame rotation, and hidden tiles still carried the scroll-reveal class (opacity 0 plus a 0.7 s pop-in) the first time they were shown. Fixed with transition none while spinning and no reveal class on carousel tiles. Verified frame by frame.
- Spin buttons are 60 px, in a pill that sticks above the bottom nav while the tile is on screen, so tall tiles cannot push them out of view (checked with an 1100 px tall tile).
- qa.js clean; no console errors.

## Round: Fun spin arrows (2026-10-29)
- Spin buttons carry big chunky SVG arrows (40 px, 8 px stroke) that nudge in their direction, grow on hover and squash when pressed; reduced motion keeps them still. Spin behaviour re-verified.
- qa.js clean; no console errors.

## Round: Candy spin buttons (2026-10-29)
- Arrow animation removed. The spin circles are glossy candy balls: radial gel gradient, fine dot texture, white gloss spot and arc, inner shading. Colour follows the world accent.
- qa.js clean; no console errors.

## Round: Smarter balloons, fee/calm colours, what-to-look-for (2026-10-29)
- A balloon only appears when text wraps to 2+ lines at the current width; one-liners stay visible. Headers (intros, section blurbs), footers (disclaimers, "Look at" lines) and the P/E box never get balloons. Token World balloons are blue.
- Bubble pit has Fun / Fee / Calm colouring: green (cheap or calm) through yellow to red, relative to all funds, grey where there is no data; each bubble shows its number. Size still follows volume.
- US-listed fees for 71 funds from Yahoo Finance fund profiles (fetched 2026-10-29, cross-checked against the 10 issuer-reported fees); volatility from data/facts.json. Europe-listed funds have no fee data and show grey.
- P/E explained in plain words in the fund's four questions and on the Basics page. "What to check on those sites" list added under the fund links. Fluctuation "look at" line rewritten as "waves, like seasons".
- qa.js clean; no console errors.

## Round: Plain four Fs (2026-10-29)
- No balloons inside the four-Fs boxes, lists (including "On those sites, check") or the P/E box.
- All 16 fund-type profiles and the generic fee, flow and look-at lines rewritten in plain words: "bumps" instead of swings, "fewer people trade it" instead of "thinner", the buy price and sell price gap explained once, yield and P/E explained where used. Basics page four boxes simplified; Flow defined.
- qa.js clean; no console errors.

## Region presets (where are you?)
- First visit shows a "Where are you?" picker (16 choices); choice saved in localStorage `td-region`; header chip reopens it.
- Funds not usually sold in the chosen region are hidden in bubble piles; "Show N more" reveals them greyed with a 🚫 mark; "ask" mark = check your broker.
- Each ball carries a small flag for the fund's home country (from ISIN prefix; US for US-listed); selected fund shows "Made in X" and a region status line.
- Added XACT OMXS30 (SE0000693293, Swedish) as an example of a Sweden-domiciled fund. Sources disagree on plain vs ESG index naming; verify on the provider site.
- Checked headless at 390/1280: no console errors, no overflow, qa.js clean.

## Wider fund list, domicile wording, new bottom menu
- Wording is "Domiciled in X" (not "made in"): iShares funds are run by BlackRock but domiciled in Ireland. Domicile = ISIN prefix, except `DOMFIX` (ETPs: WisdomTree Bitcoin/Ether are Jersey, VanEck Bitcoin ETN is Liechtenstein); checked against justETF "domiciled in" text 2026-10-29.
- Added ~100 funds: single-country piles (Canada, Mexico, Brazil, Korea, Taiwan, Switzerland, Italy, more), regional piles, sector/theme piles, metals, S&P 500 sector UCITS, European-listed ETCs/ETPs for metals and crypto. US-listed names/fees from Yahoo fund profiles, UCITS/ETC/ETP names/ISINs/fees from justETF (both 2026-10-29). New funds have no volatility data yet (grey in Calm mode); tiers are estimates.
- Commodities page trimmed to gold, silver, platinum & palladium, oil. Natural gas, copper and farm funds all exist, but they hold futures and can drift from the price; their piles are removed from the menu (data kept in THEMES).
- Bottom menu: token coin (far left), News, Investing (pops World / Sectors / Commodities bubbles; in Token World Assets / Networks / Issuance), Dashboard, Basics, Fee calc, Game (placeholder toast).
- Headless 390/1280: no console errors, nav clicks scroll to the right sections, qa.js clean.

## One page at a time, fun Investing bubbles, own Basics page
- Real world shows one page at a time (`body[data-view]`, `showView`, called from `scrollToSection`), framed by a black vignette (`#vig`, iris animation) on every page except the dashboard.
- Investing bubbles: bouncy pop with stagger, idle bob, wiggling icons, sparkle bursts on open and on pick, shrink-out on close.
- Basics is its own page (`#basics`): the 4 Fs in one short line each, a button to the fee calculator, and a folded "Why invest at all?". The fee calculator page (`#fees`) now holds only the calculator.
- Headless 390/1280: every nav path shows only its page; no console errors; qa.js clean.

## Steady Investing bubbles, one Investing page
- Investing bubbles pop in once and then stay put (no bobbing, no vertical movement; hover and click only scale).
- World, Sectors and Commodities now share one page, stacked in that order. The bubble you pick scrolls to its part.
- Headless 390/1280: bubble positions identical 0.9 s and 2.4 s after opening; all three sections visible; no console errors.

## Start-here note, longer Basics, one learning page, edge vignette
- Fee sticker removed. Dashboard top has a short "Investing is not complicated" note (5 one-line points) linking to Basics.
- Basics page: "Investing in plain words" (6 short points, SPIVA link as the source for "most active funds trail their index over long periods"), then the 4 Fs, then the fee calculator on the same page (Basics and Fee calc buttons scroll to their part).
- Vignette is now directional: it darkens only above and below the tile in focus, on the two multi-tile views (Investing = World/Sectors/Commodities; Basics + Fee calc). No full-screen vignette any more.
- Wording kept to checkable claims: the "casino" and "science says ignore the news" ideas were not used as stated; the note says single stocks, crypto and trends swing harder and funds spread risk.
- Headless 390/1280: no console errors, no overflow, qa.js clean.

## Inflation slider and stock-picking note
- Fee calc page: new "Inflation eats money" card under the calculator (slider 0–10%, default 2% marked as an example). It uses the money and years above and shows cash in today's prices, the fund after fees in today's prices, and real growth per year. Checked by hand: 10,000 at 2% for 20 years buys 6,730 in today's money.
- Basics: new "Why not pick single stocks?" card. Sources: Bessembinder (2018), J. Financial Economics, "Do stocks outperform Treasury bills?" (only ~4% of US stocks account for the net gains over T-bills, 1926–2016) and S&P SPIVA scorecards. Not used as stated: "close to 0 risk after decades". The text says the range of results has historically narrowed with longer holding, and that it is never risk-free.
- Dashboard note's last point now says picking single stocks is very hard.
- Headless 390/1280: no console errors, no overflow, qa.js clean.

## VOO vs 2% savings chart
- Dashboard note and Basics each have a bar chart: VOO from its first trading day (9 Sep 2010) to 31 Dec 2025 is +717% with dividends reinvested (+519% price only); a 2% savings account over the same 15.3 years is +35%. Source: Yahoo Finance daily data fetched 2026-10-29. See `VS` in index.html and docs/UPDATING.md.
- Headless 390/1280: no console errors, no overflow, qa.js clean.

## Corner flames on spinning tiles
- While a carousel spins, a small flame (three layered flames plus two sparks) sits on each of the four tile corners. Heat follows the spin speed: it grows as the tile accelerates when you keep clicking, leans against the direction of travel, and dies down as it slows. The layer is removed when the tile locks in. Hidden with reduced motion (the spin is already off then).
- Headless: heat reached 1.0 at full spin, layer and `.spinning` class removed after settling, no console errors; qa.js clean.

## Flames circle the whole tile
- The corner flames became a ring of fire: 14 to 34 flames (by tile size) evenly spaced around the whole tile edge, each pointing outward, and the ring travels around the tile in the direction of the spin. Size and brightness follow the spin speed; the ring is removed when the tile locks in.
- Headless: heat reaches 1.0, ring gone after settling, no console errors; qa.js clean.

## Lightning instead of flames
- The ring of fire is now electric lightning: a jagged bolt (blue glow, bright core, white centre) runs in a closed loop around the whole tile and re-strikes every 45 ms. As the spin speeds up the bolt jitters wider, gets thicker and brighter, and up to 9 forked bolts shoot outward from the edge. Removed when the tile locks in; hidden with reduced motion.
- Headless: heat 1.0 at full spin, layer gone after settling, no console errors; qa.js clean.

## Thicker lightning, one bubble view, one-way gate, dough physics
- Lightning: glow 16 to 34 px, bolt 5 to 10 px, white core and forks brighter; faintly visible even at low speed.
- Bubble pit: the Fun / Fee / Calm switch is gone. Every ball always shows its details: flag, icon, ticker, short name, fee and 3-year swing (as many as fit its size). Size is still volume (TIER). Colours are the fixed candy colours.
- One-way gate: a ball that has fallen fully in can no longer leave through the top (ceiling clamp once inside; a throw straight up stays in). Checked: after throwing a ball up at 6000 px/s no ball is above the top edge.
- Dough physics: balls hit with almost no bounce, stick when touching (separating speed is damped, tangential slip is dragged along), and may overlap a little under pressure. Pressed balls flatten along the contact direction (strain tensor per ball, quick to flatten and slow to recover, no springy overshoot); floor and wall hits flatten too.
- Headless 390/1280: no console errors, all balls inside, qa.js clean.

## Dough balls, falling from above, sliding
- Balls are now irregular dough blobs: each ball's outline is a closed curve of 18 points (`blobPath`, applied as `clip-path`). Contacts (other balls, floor, walls, gate) push the outline in at the contact point and bulge it out to the sides; points move in quickly and recover slowly, plus a small constant wobble, so every ball stays lumpy and different. The element box is 1.34x the physics circle to leave room for the bulge; one drop-shadow is applied to the whole field.
- Physics: friction between balls and on the floor is much lower (they slide and roll off each other); balls still stick a little when pulled apart and hit with almost no bounce.
- The pit now spans the full screen height. Balls fall in from above the screen, behind the title bar; a dashed line at 150 px marks the one-way gate and nothing can climb back above it (a ball thrown up at 7000 px/s stayed below it).
- Headless 390/1280: no NaN positions, no console errors, qa.js clean.

## Token World revamp, Saturn buttons, Coinpull
- Token World is now six short views like the real world: Home (planets + early-days note), Basics (what is tokenization, six short points, "what to watch" fold), Wallets (keys, custody, hot/cold, seed phrase, address, fees, scams, "ETFs need no wallet"), and an Explore group stacked in order: Options (what exists today + examples + market fold), Networks (explore the system, details, brokers fold), Issuance. Bottom menu: coin, News, Explore (Options / Networks / Issuance bubbles), Home, Basics, Wallets (replaces Fee calc, not relevant here), Game. News from Token World returns to the real news page.
- The M balloon is a small Saturn in Token World. Popping it reveals the text, flashes, and throws about 30 pieces of debris and ring shards outward slowly; they are then pulled back into the spot (2.5 s) and a dimmed Saturn is left as the "close" button (click to re-inflate). Real world keeps the red balloon with confetti.
- Coinpull (Game button in Token World; real world still shows a placeholder): runner on candles, hold = jetpack. 80% of candles are green and each charges the jetpack a little (more as the climb goes on); walls climb slowly unless boosting; boosting costs fuel (a full tank lasts about 2 s). After 80 to 130 candles a rugpull cliff appears, sized so that landing softly needs 20 to 60% fuel (formula `fuelNeed`/`dropFor`; a 15% margin is built in). Holding while falling brakes only above 510 px/s, so braking too early wastes fuel. Landing faster than about 590 px/s ends the game (one life). Soft landing gives +250. Best score is kept in localStorage. Simulated: perfect timing without boosting survives; burning the fuel before the cliff dies.
- Headless 390/1280: no console errors, qa.js clean.

## Coinpull rework (greed vs fuel)
- Candles are uneven and volatile: green candles climb more and more per step (trend 3 px plus 0.42 px per candle, with random spikes and 12% double-height wall candles), red ones fall; wicks above and below differ in length.
- The run speeds up over time (170 to 560 px/s) and the background grid and speed streaks move faster with it.
- Controls: a tap or click is a jet burst (cheap: 5% fuel, about 46 px hop, max about 11 per second); holding gives continuous thrust but burns 1.15 fuel per second, so it is much more expensive. Holding while falling only brakes above 510 px/s.
- Score grows exponentially: points = (distance + 0.4 x height gained while thrusting) x 1.03^candles climbed, shown as a multiplier next to the score. The faster you climb, the more candles you pass before the rug, so greed pays, but fuel burned climbing is not there for the fall.
- The rugpull has no warning and no marker on the fuel bar: a 4000 to 9000 px drop that comes after 26 to 42 s of climbing; terminal speed 1700 px/s; landing faster than about 594 px/s is death. Best play lets speed build and pumps taps at the end; pumping the whole way burns far more fuel. Soft landing after a big fall: +500.
- Character: front-facing, one big black eye with no white, a small tongue sticking out forward, robe, big twin jetpack tanks with large flames, glow, smoke and sparks.
- Simulated: careful and moderately greedy policies with late taps survive and score millions; a policy that taps constantly runs dry and dies at the rug. Headless: no console errors, qa.js clean.

## Coinpull: fall damage, steeper candles, candles decided late
- Fall damage now has three bands by impact speed: under 800 px/s nothing, 800 to 1150 px/s "OUCH" (lose 25% fuel, stumble at 45% speed for 0.7 s, screen shake), above 1150 px/s you die. Before, anything over about 594 px/s killed, which meant a valley deeper than about 126 px was deadly (speed after a drop h is sqrt(2 x 1400 x h)). Terminal speed is now 2300 px/s so the rugpull still needs a few late taps.
- Climbing gets harder: trend per green candle 5 + 0.8 px per candle climbed, 14% double-size wall candles, and 7% unpredictable valleys (80 to 320 px dips as a long red candle). Crawling without the jetpack is slower (70 px/s) so steep sections need it.
- Green candles recharge less (0.4% growing to 1.4% per candle) so fuel is a real budget. Simulated at the rug: careful play arrives with about 48% fuel, greedy play with about 15%, and an all-in policy with 0% and dies; no-jetpack play barely scores.
- Candles are decided only 5 candles before the player arrives. Until then they show as flickering dashed outlines in changing colours and heights, so the next shape, colour, valley or the cliff cannot be seen coming.
- `tap(true)` bypasses the cooldown for tests.
- Headless: no console errors, qa.js clean.
- Game over now reads "LIQUIDATED 💀 — You are now in a lifetime of debt. This is not investing. This is speculation... oh right, gambling!" plus the score. Checked by forcing a fall in headless.

## Coinpull: valley penalty, jumpable rugpull, stronger jetpack
- Landing in a valley (a fall of 60 to 1200 px) now costs score: −depth/9 % (at most −40%), shown as "VALLEY −x% SCORE".
- The rugpull is now a gap: a pit of 4000 to 9000 px with a plateau on the far side at the old height and a floor far below, both lasting 30 candles. A candle has two surfaces (`top` and `low`); the player is on the lower one once it is more than 600 px under the old peak. Flying across ends with "MADE IT ACROSS! +25% SCORE"; falling in means braking as before ("SOFT LANDING +500"), or death.
- Gap width = (random 0.1 to 1.0) x 6 x current speed in px (`RUGK`), so the fuel needed is spread evenly: with a full tank crossing is (almost) certain, at 50% it works about half the time. A perfect scripted tapper crossed about 33% with 10% fuel, 50% with 25–40%, 87–90% with 55–70% and 100% from 85%; a human will do worse. Taps cost up to 4x more when high above the ground (e.g. over the pit), so hovering across is not free.
- Jetpack stronger: tap 520 px/s (was 360, about 97 px hop), hold thrust 1500 (was 900), max rise 650, terminal fall speed 2600.
- Headless: no console errors, qa.js clean.

## Coinpull: cash-out credit card, gold bounce, leverage levels
- The far side of the rugpull gap is a giant credit card (26 candles long, magnetic stripe, chip, big 16-bit pixel letters "CASH OUT!"). Landing on it from the air bounces the player (-1700 px/s), turns the character gold for 3 s (invulnerable: no fall damage, no valley loss, no liquidation), adds +25% score, banks the score (best score is saved immediately) and starts the next level: background palette changes (5 palettes, cross-fade 1.6 s) and leverage goes up by one.
- Leverage L: points x L; valley loss L times bigger (capped at 40% x L, max 90%) and each valley landing has a (L-1) x depth/640 chance of outright liquidation (e.g. L=2, 320 px valley = 50%).
- Falling into the pit instead keeps the level and leverage as before (brake to survive).
- Headless: forced scenario crossed the gap, bounced, went gold (gold 3 s, LEV 2x, background changed), card renders with the letters, no console errors, qa.js clean.

## Coinpull: more fuel, more valleys, silent red blink
- Fuel is more generous: green candles recharge 1% growing to 3% per candle (was 0.4% to 1.4%), taps cost 3.5% (was 5%), holding burns 0.8 per second (was 1.15), start fuel 60%.
- Valleys are more common (17% of climbing candles, 40 to 320 px deep).
- Touching anything going down now costs score: any landing after a fall of 20 px or more takes depth/9 % (times the leverage), and the whole screen blinks red slightly. No text is shown for these penalties (the OUCH and VALLEY messages are gone; the hard-landing fuel loss also just blinks). Gold invulnerability still blocks them.
- Headless: a 120 px drop cost about 11% of the score with the blink and no text; qa.js clean.

## Coinpull: snappier jetpack, faster refill, easier gaps, surprise rugpull
- Snappier: tap cooldown 50 ms (was 85), hold thrust starts after 80 ms (was 180), hold acceleration 2000 (was 1500).
- Faster refill: green candles give 2% growing to 5% (was 1% to 3%), plus a slow passive refill (1.5% per second) while standing on the ground without pressing.
- Gaps are easier to close: gap width factor 3.5 (was 6) and the extra cost of hovering high above the ground is at most +120% (was +300%). Scripted tapper: crossed 37% at 10% fuel, 83% at 25%, 100% from 40%.
- Stronger uptrend: trend 6 px plus 1.0 px per candle (was 5 + 0.8).
- The rugpull candle is now the normal red candle colour (solid body, dark cap, wick), not a see-through outline, and it is decided only 3 candles before you reach it (was 5), so it shows up close and by surprise.
- Headless: rug decided 3 candles ahead in all runs that reached it; qa.js clean.

## Coinpull: dollar score, level speed-up, zero-dollar liquidation, END EARLY
- The score is drawn as `$` plus the number in a 16-bit pixel font (own digits, `$`, `,` and `.` added to the pixel table next to "CASH OUT!"), yellow with a black shadow.
- Each cash-out and surviving the rugpull speeds the game up: level 2 runs 1.2x faster, level 3 1.3x, and so on (1 + 0.1 x level). Points are still multiplied by the level.
- From level 2 up, touching down loses level x depth/600 of the score; if that reaches 100% the score is $0 and you are liquidated (e.g. level 2 and a 300 px valley). Level 1 keeps the old rule (depth/900, at most 40%). Fixed a bug where valleys deeper than about 230 px cost fuel but no score.
- Cash-out is now a choice: landing on the card stops the game, banks the score (+25%, best score saved) and shows "CASHED OUT: keep speculating >:)" or END EARLY! Ending early shows "YOU WALKED AWAY" with the score ("the only winning move"). Continuing bounces, goes gold for 3 s and starts the next level. Offered at every cash-out.
- Headless: the choice card, both buttons, gold bounce into level 2, end early, level-2 liquidation at $0 all worked; qa.js clean.

## Coinpull: forward thrust, longer and snappier fuel, fewer rug deaths
- Pressing now tilts the character forward (up to about 15 degrees, flames trail behind) and adds up to +50% forward speed while thrusting (taps and hold), so crossing the gap is realistic.
- Fuel lasts longer: a tap costs 2.5% (was 3.5%), holding burns 0.55 per second (was 0.8). Snappier: tap lift 640 px/s (was 520), hold thrust starts after 30 ms (was 80) with acceleration 2600 (was 2000), max rise 760.
- Fewer rug deaths: terminal fall speed 2200 (was 2600), hard-landing penalty from 1000 px/s (was 800), death from 1500 px/s (was 1150), and the camera shows more ground below while falling. Gap width factor retuned to 10 for the faster forward speed.
- Scripted checks: a tapper crossed 30% at 10% fuel and every time from 25%; when it fell in, it survived the pit every time (0 deaths); the careful, greedy and all-in policies all survived the first rug.
- Headless: no console errors, qa.js clean.

## Coinpull: only a cash out counts, gold vs hollow buttons, second card, half rugpulls
- Best score is only saved by END EARLY (a real cash out). Dying (fall damage or liquidation) scores nothing: the game over text says "You lost $X. Only a cash out counts." Continuing after a cash-out no longer saves anything.
- "KEEP SPECULATING >:)" is a gold shiny button with a moving glint; "END EARLY!" is hollow, white, normal weight.
- A second cash-out card now exists on the pit floor of every full rugpull: raised 480 px above the floor, 30 candles long, starting 6 candles past the gap start. Reaching it needs jetpack fuel (walls taller than 260 px can only be climbed with the jetpack). Landing on it from the air gives the same choice. The old far-side card is kept.
- Half rugpulls (35% of rugpulls): no gap and no card, just a 1500 to 3200 px drop with a flat landing; a soft landing earns +500.
- Zone after the gap is now 44 candles long. `HALFP` and `RUGK` can be set from tests.
- Headless: choice card with gold/hollow buttons, END EARLY, level-2 liquidation, scripted bots reached the pit-floor card in 14 of 24 forced pit falls (crude bots), half rugpulls survived 16 of 16; qa.js clean.

## Coinpull: parachute replaces the jetpack
- Jetpack tanks and flames removed from `player()`; a yellow/purple canvas parachute is drawn behind the kitten. It unfolds from a packed bundle to a full canopy in ~0.25 s while boosting (`s.u>0`) and folds away on release; no sway under `prefers-reduced-motion`, open/closed snaps.
- HUD/help text says "Parachute"; gameplay and fuel bar unchanged.
- Headless Chromium (900×700 and 390×800): `pc` eased 0→1 within ~0.3 s on hold, back to 0 after release, screenshots show canopy behind the kitten, no console errors.

## Smiley label under the coin
- Bottom-nav smiley now shows a label underneath: "Tokenized investments" in the real world, "Real world investments" in Token World (headless Chromium, 1000px and 390px, no errors).

## Coinpull: cut-out dancing cat
- `player()` now draws `assets/mascots/catdance.webp` (101 frames, 8 per row, 10 fps / 14 while boosting) via its own `window._catSheet`; `dancer-dance.webp` is untouched for other uses. Bottom edge anchored just under the feet (dy = -S·0.97, S=150); parachute shoulder anchor raised to y=-92 only, canopy unchanged.
- Headless Chromium (900×700, 390×800): cat animates, parachute opens on hold and folds on release, no console errors.

## Coinpull soundtrack
- `assets/audio/gaming-loop.wav`: supplied 192 kHz FLAC resampled to 44.1 kHz/16-bit WAV (4.4 MB, WAV because the artifact host does not serve FLAC, 24.78 s) with a 12 ms fade-in so the wrap from the faded tail to the start has no click. Played via WebAudio `AudioBufferSourceNode.loop=true` (sample-exact, no `<audio loop>` gap), started from the Game tap, stopped on close. 🔊/🔇 button next to ✕, remembered in `cp-mute`.
- Headless Chromium over http: file decodes (24.78 s, 44.1 kHz, stereo), mute toggles, no console errors. (Not fetchable from file://.)

## Soundtrack speeds up with the level
- Song `playbackRate` = 1× on level 1, then 1.2× on level 2, 1.3× on level 3 and so on (same factor as the run speed); resets to 1× on a new run. Tape-style: pitch rises with speed. Verified in headless Chromium over http.

## Coinpull: smooth gliding line, % scoring, parachute bonus, chart patterns
- **Glide:** `ground(x)` is now an invisible smooth line (smoothstep between neighbouring candle tops); feet sit exactly on it (max offset 0.000 px in a 28 s hands-off run). Walls no longer stop the run: steeper than climb speed (`CLIMB`=1000 px/s) just slows the scroll so the cat climbs at its normal speed; only a step over 520 px (pit walls) blocks. A drop steeper than `DESC` (1100 px/s) or a gap makes the cat leave the line and fall (landing damage rules unchanged). Walking onto the raised pit-floor card now also triggers the cash out.
- **Scoring as chart %:** rising height = + %, falling = − %, `lv · Δy / 1500` (so a 150 px gap up ≈ +10%, ×level for leverage); landing penalty uses the same scale (`lv·(1−e^(−depth/1500))`, ≥100% still liquidates). The distance term remains. A big pop-up (+25%, −9%…) slaps on screen for moves ≥ 4% in one go (≥ 12% also shakes the screen).
- **Parachute:** open canopy = +10% on all gains; HUD shows "CHUTE +10%"; added to the help card.
- **Patterns:** up phase = biased random walk, plus ~10% chance per candle to play a pattern: bull flag, ascending triangle, double bottom, head and shoulders (bearish), cup and handle, V reversal, stairs.
- Headless Chromium: hands-off 28 s run never stuck (avg ~230 px/s) with slaps both ways; full rugpull crossing identical to before (30/30 from 25% fuel); game7/rug/choice scripts pass; no console errors, desktop + phone.

## Coinpull: ping-pong cat, auto-float over walls, slower scoring, bubbly %
- Cat animation plays forward, then reversed, then forward (frame = triangle wave over 2·101−2 steps) and its frame rate also scales ×1.2 / ×1.3 … per level (phase accumulated, no jumps when the rate changes).
- Any candle/wall more than 300 px above the feet within the next 5 candles makes the cat float up automatically (1800 px/s) until it is level with the top, so scroll speed never changes (wall test: 900 px wall, scroll 205→225 px/s steadily, no slowdown or stop). The old hard stop at big walls is gone. Moderate steps are still climbed along the smooth line at the normal climbing speed.
- Score growth much slower: height % now scaled by 1/5000 px (was 1/1500) and the candle multiplier is 1.015^k (was 1.03^k). Hands-off 28 s run: ~$2.5k (was ~$27k). Slap threshold lowered to 2% (shake at 8%) to match.
- % pop-ups use a bubbly rounded font (Baloo 2 from Google Fonts, falling back to rounded system fonts) with white outline, gradient fill and drop shadow.
- Headless Chromium over http: full-rug crossing still 30/30 from 25% fuel, game7 policies unchanged, no console errors.

## Coinpull: feet always on the candles, 10% valley cap, chute on hold only, liquidation tile, pause
- **Feet on the candles:** the auto-float is gone. The line follows each candle's top exactly and only eases over a narrow band (30% of a candle) at the borders. When the line rises (wall or very high candle) the cat climbs it at a steady 900 px/s while the scroll keeps its pace (900 px wall test: scroll 199–220 px/s, 0 frames floating above the line). Landing on a wall side also just climbs, with no damage.
- **Valleys:** score follows height as % (1/10000 px, x leverage) but the drawdown from the last high is capped at 10% (x leverage) so no valley costs more than ~10%; winning it back only pays above the old high (no free ratchet). Candle multiplier 1.01^k. First rug now arrives at about $8k (was $330k before the % changes).
- **Parachute only while holding:** the canopy opens after ~0.2 s of holding with fuel (and only then the +10%); a press is just a jump.
- **Cat loop:** frames 94–100 of the sheet are a ghosted crossfade, so the cat uses frames 0–92 played forward/reverse (no fade, no chop).
- **Liquidated:** title LIQUIDATED, text "You lost everything including your house. But you got some vibes left to cope with.", button "(Start speculating again?)". The cat dances at 2x and orbits the tile, slowly accelerating; the tile has an animated rainbow glow (static under reduced motion).
- **Pause:** ⏸ button (and P key / tab hidden) shows a PAUSED tile with Resume/Quit; game, timers and music freeze (AudioContext suspended). Esc resumes when paused.
- Headless Chromium desktop + phone: pause freezes and resumes, liquidation tile + orbiting cat render, no console errors; game7 / rug (30/30 crossing from 25% fuel) / choice scripts pass.

## Coinpull: candle step limit and more varied candles
- No candle may differ from the previous one by more than 300 px (about 2 cat heights) up or down in the normal up phase, so the cat no longer has to fly up; only rugpull/half rugpull gap down. A 0.1% rarity can gap up 320–460 px (measured over 15,960 candles: max step down 300, gaps up >300 on 0.21%).
- Candle bodies now range from tiny dojis (10 px) to long ones (up to 260 px), tied loosely to the size of the move, with 0–36 px wicks and 22% of wicks 3x longer.
- Headless: hands-off run, game7, rug (30/30 from 25% fuel) and choice scripts pass, no console errors.

## Coinpull: score is a portfolio, rugpull = knock-out gap with a floating cash-out card
- **Score = portfolio that follows the chart.** Starts at $1,000. No more points ticking up with time. Every pixel climbed is +%, every pixel down is -%, both scaled by leverage `L = 1 + 0.1·level` (level 1 = 1.1×, level 2 = 1.2× …) over 8000 px. Falling more than 300 px in one go is a very strong -% (1000 px scale). The old 10% drawdown cap and the candle multiplier are gone. Open parachute still gives +10% on gains. HUD shows the leverage ("1.1× LEV").
- **Rugpull is a knock-out.** Ground vanishes under a huge red candle. A floating credit card hangs 260–520 px under the old high after a gap (gap width as before, so it needs fuel to reach) and is always there; there is no hill and no pit any more. Touching it still pauses with KEEP SPECULATING / END EARLY. The market restarts at the card's height. Fall below the knock-out line (1800/L px under the old high, a red dashed "KNOCK-OUT" line appears when you are falling) and you are liquidated. While falling the score collapses to -90% at the line (smooth exp curve, reversible if you fly back up); higher level = closer knock-out.
- **Mini rugpull** (35%): a sudden drop of 500–1000 px (was 1500–3200) onto ground, landing damage by impact speed as before; the fall itself costs a strong -%.
- Headless Chromium: hands-off 28 s run reaches ~$2k from $1,000; a tapper crosses the rug 30/30 from 25% fuel (16/30 at 10%; the rest are knocked out); score collapse verified (849 -> 277 after 912 px under the high); no console errors. The old scripted bots (game7) now die at the first rug because they do not fly the gap, as intended.

## Coinpull: design review + final audit pass
**Compared with** Tiny Wings (gliding on hills, one-touch), Canabalt (relentless pace, instant retry), Jetpack Joyride (tap/hold jet, fun feedback), Aviator-style crash games (cash out before the crash, live multiplier) and stock apps (Robinhood-style change chips). What we kept: one-touch control, constant pace, a single big risk moment (the rugpull) with a cash-out choice. What was added from that comparison:
- **Stock-app change chips:** % pop-ups are now a green/orange pill with ▲/▼ and white bold numerals in the system UI font (SF/Segoe/Roboto), one decimal under 10%; no more decorative font (Google Fonts link removed).
- **Live portfolio readout:** HUD shows total return since the start ("▲ 12.4% · 1.1× LEV"), and the $ score tints green/red with the short-term trend (crash-game style live feedback).
- **Dead cat bounce:** after the cash-out card the market restarts with 7 candles of relief rally then 4 of bull trap, announced with "DEAD CAT BOUNCE".
- **Fuel economy rebalanced:** uphill gains on the ground charge the tank (+35% of the % gained), green candles give 1–3%, passive charge on the ground is 1.5%/s and 5%/s when under 30% (rubber band so a bad stretch is recoverable), flying gains do not recharge (no infinite-climb loop). The fuel bar shows the number of jumps left. Rug crossing with a perfect tapper: ~33% at 10% fuel, ~100% from 25%.
- **Sound & feel:** synthesised SFX (jump, gain, loss, cash-out, level-up, knock-out) obeying the mute button; haptics on big moves; no screen shake or vibration with reduced motion; first-run coach hint ("TAP to jump · HOLD for the parachute").
- **Flying over the card:** if you clear the card without touching it, the rug is simply behind you (nothing banked, no level up).
- **Terrain slope cap** (trend ≤ 70 px/candle) so long runs do not explode the score.
- **Audit:** 60 randomised runs of up to 200 s with five different input styles: no exceptions, no NaN/negative score, no fuel out of range, no stuck run (min distance 1,100 px); deaths 21 knock-outs, 27 falls. Removed dead pit/second-card code. Pause, liquidation tile, choice card and glide tests re-run clean on desktop and phone width.
- Ideas left for later: ghost of your best run, daily seed, near-miss bonus for skimming the knock-out line, share card.

## Coinpull: stronger uptrend, jumpable gaps, fairer knock-out
- **Uptrend:** mostly green candles (86%), bigger rises (x1.5), rarer/shallower valleys (8%, 30–220 px), smaller red candles, score scale 6000 px. Terrain rises ~32 px/candle; the first up phase now ends around $2.2k (median) hands-off and ~$3k for a player who jumps the gaps (best runs $7–10k).
- **Gaps to jump:** in the up phase (after candle 6, ~7% per candle, at least 9 apart) a 3–4 candle pit 300 px deep appears; a tap clears it, walking in costs ~13% (fall beyond 200 px is the strong -%) and a red blink, then the cat climbs out.
- **Knock-out is fairer:** knock-out line is now 4800/L px under the old high (was 1800/L), silently at least 55% fuel when the rug arrives (rubber band), card 32 candles wide, gap factor 8 (was 10), braking a fall burns 45% less fuel. Bot that holds the parachute when the fall starts survives ~85%, one that does nothing still survives ~45% (lands on the card); 10% fuel tapper crosses 73% of the time, 100% from 25%.
- Fuzz (60 randomised runs) clean again: no NaN/negative, no stuck run; pause/choice/glide checks pass.

## Coinpull: gentler rugpull, no fall-damage death
- **Death only at $0.** Landing hard no longer kills (stumble, fuel loss and a red blink remain, plus the % cost of the fall). Liquidation happens only when the score reaches zero: in the rugpull void the score falls smoothly with depth `rugBase·(1−depth/ZERO)^1.4` and reaches $0 at the red dashed "ZERO" line, 3600/L px under the old high (L = leverage). Flying back up restores it.
- **Rugpull easier to cross:** gap factor 2.5 (was 8 at first, then 3): widest gap now ≈ 2.5·speed/CW candles, the card hangs only 200–400 px under the old high, holding in the void burns 40% less fuel (and a falling brake 55% less). Simulated players at 300/450/560 px/s: tapping every 0.6 s from the edge survives 40/40; holding the parachute from the edge 35–38/40; holding only after 0.5 s of falling 32–39/40; doing nothing 28–33/40 (they land on the card).
- Fuzz (60 randomised runs) clean; pause, choice, glide scripts pass.

## Coinpull: flames instead of the parachute, deadlier gaps
- **Flames:** the parachute is gone. A tap lights small flames at the feet instantly (the jump itself is unchanged and immediate); holding makes them grow longer, wider and hotter, reaching full power after ~1.4 s, and they die out in ~0.2 s after release. Reduced motion: no flicker. The +10% bonus now reads "FLAMES +10%" and applies once you have held for 0.2 s. All texts say flames/fuel; the help card now lists "Jump the gaps".
- **Gaps (not rugpulls):** pits are more frequent (10% per candle, 7+ candles apart) and 3–5 candles wide. Falling into one costs 40% × leverage of your money once per pit (red blink + shake + −% chip); a repeat offender reaches $0 and is liquidated. Simulated: a player who jumps ends the first up phase at about $1.6k (median), one who never jumps at about $320.
- Fuzz, choice, pause and glide scripts re-run clean (desktop + phone width), no console errors.

## Coinpull: flame shape and colour sequence
- Flames are drawn behind the cat and start inside its paws with a rounded top and a fireball at each nozzle, so nothing is cut off at the feet. Sequence every time: ignition explosion (bright fireball + spikes, first 0.32 s) → weak small blue flame → grows longer/wider and shifts blue → yellow-white → orange/red over ~1.4 s of holding. A tap shows the explosion and a short blue flame; flames fade ~0.18 s after release. Reduced motion: no spikes or flicker. Verified by frame captures at 60/200/500/900/1400 ms, desktop and phone; fuzz, choice and pause scripts clean.

## Coinpull: balancing audit, cash-out compass, rename, leverage that bites
- **Game is now called DEAD CAT BOUNCE.** The title on the start card pulses green↔red and bounces; the other cards (cash out, liquidated…) keep their own titles. Reduced motion: static green.
- **Bigger gaps:** 5–7 candles at low speed up to 13 at full speed (a single tap is no longer always enough). Simulated: one tap at the edge falls in 31% of pits at 200 px/s, ~15% at 300–560; a tap plus a second tap when short: ~0%; no jump: 77–98%.
- **Leverage scaling:** a mistake (falling into a gap) costs `25% + 20%·level` of your money: 45% at level 1, 65% at 2, 85% at 3, everything from level 4 (one mistake and you are liquidated; verified 10/10 at levels 4 and 5). The level-up banner shows the current price ("LEVERAGE 1.3× · A MISTAKE NOW COSTS 65%"). Gains are still scaled by the leverage too, and the ZERO line gets closer (3600/L).
- **Cash-out compass:** once the ground has vanished, a bobbing gold arrow sits over the card when it is on screen; when it is off screen a gold 💳 pointer on the screen edge points toward it with the distance ("CASH OUT · 320 m"). The card is drawn at its full width even before all its candles exist.
- **Flames** follow the paws of the current dance frame (anchor table read from the sprite sheet at load, falls back to the middle when the canvas is not readable) and are ~30% wider with a bigger fireball.
- **Rule: the cat is never under the line.** Verified over 154k frames of five random input styles: 0 frames below the invisible line. A steep climb now slows the scroll instead of letting the cat sink into the candle; touching a wall from the air snaps onto it.
- Rug survival (human.js): holding from the edge 37–40/40, tapping 40/40. Fuzz, choice, pause and glide scripts clean.

## Dead Cat Bounce: zoomed-out chart and patterns that mostly fail
- **Zoomed out:** the world is drawn at 0.38–0.62× (width-dependent: ~0.62 on desktop, ~0.38 on phones) around the cat, which now sits in the middle of the screen (the cat sprite is drawn at about 105 px on screen whatever the zoom). The left half shows the price history (so patterns can be recognised), the right half the unknown future as dashed ghost candles. Physics, the line, flames, KO line, card and compass were adapted (compass, orbit and % chips are drawn in screen space). Verified at 1000×700 and 390×800: 0 frames with the cat under the line over 135k frames, fuzz/choice/pause scripts clean, no console errors.
- **Patterns are a weak predictor:** the up phase still plays bull flag, ascending triangle, double bottom, head and shoulders (bearish), cup and handle, V and stairs, now as set-up + textbook outcome. The outcome only follows the textbook 25% of the time; 30% nothing happens and 45% the opposite happens. The help card says so ("they only work about 1 time in 4").
