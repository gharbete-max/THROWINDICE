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
