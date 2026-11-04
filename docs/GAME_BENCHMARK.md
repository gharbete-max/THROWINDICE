# Live Cat Bounce vs the big runners (judgement, 2026-11-04)

Evidence is thin: the searches ([Chrome Dino notes](https://dinogame.gg/blog/why-chrome-dino-is-addictive/), [TouchArcade on Canabalt](https://toucharcade.com/2012/05/24/semi-secret-teases-new-canabalt-update-ideas), [MacStories on Alto's Odyssey](https://www.macstories.net/?p=53258)) returned mostly commentary and no retention or session-length data, and nothing on Geometry Dash. The comparison below is my reading of those loops plus general knowledge, not measured data.

| Loop trait | Dino / Canabalt / Subway Surfers / Alto | Ours before | Ours now |
|---|---|---|---|
| One input | one button (jump); Alto hold; Subway swipes | tap + hold + double jump | same (the double jump is the depth) |
| Death is final and readable | instant, you see why | 3 hearts + fall damage (muddy) | one hit ends the run: gap or wall; a touch of an edge slides you up |
| Restart speed | seconds, a big reason players retry (Dino notes) | card after 0.6 s, button | card after 0.3 s, tap anywhere or Space restarts |
| Score | distance first, coins second | coins only, easy to inflate | distance shown beside coins; chain x1-x3 (was x5); coin values 1/2/5/15; fewer coins |
| Difficulty | speed ramps, obstacles get denser, never unfair | unreachable cliffs, drops into walls | speed +7% per checkpoint to 1.7x; every fall is followed by a landing and run-up zone sized from fall time x speed (this removed unwinnable spots) |
| Own-best pressure | Alto/Dino show high score; Geometry Dash shows progress | none | dashed BEST line in the world at your record distance |
| Skill reward | near-misses, flow | PERFECT / chain | PERFECT (jump right at an edge), chain, guide coins over every gap |
| Goals beyond one run | Jetpack Joyride missions | none | 3 daily goals |

## Where it is weaker than the leaders
- No cosmetic/progression meta (skins, upgrades). The cat is fixed on purpose (theme), so progression would need to be bound to the chart theme (e.g. new tickers/backgrounds) - not built.
- Difficulty is tuned against bots, not people. The human-like bot (reaction jitter up to 170 ms, simple rules) dies at a median level 3 / about 21 s / 195 m; a perfect-timing search bot lasts longer. Real players will differ, so these numbers are a starting point.
- Runs average well under the 30-60 s a casual runner usually aims for; if testers die too soon, lower the speed ramp or lengthen the opening easy stretch (140 candles now).
