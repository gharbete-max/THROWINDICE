# THROWINDICE: notes for Claude Code

Single-page site (`index.html`, no build step). It has the investing pages, Token World mode, and a canvas runner game ("Live Ball Bounce"). All game code is inside one closure in `index.html` (state `R`, `step(dt)`, `player()`, the draw loop).

## Where things are decided

- **`docs/HANDOFF.md`**: the ordered work queue. **Start every session here.**

- **`docs/MARKET.md`**: the market pivot. Decisions, the ordered task list (M1–M7) and the asset inventory. **Start here for game work.**
- **`docs/BALANCE.md`**: how all systems integrate into one portfolio, measured baseline, targets, and balancing tasks B1–B8. Check every gameplay-number change with `node scripts/balance/sim.js` (needs playwright).
- **`docs/ANIMATION.md`**: animation rules (blend, loops, priorities), flick tricks, trick chains, and the recipe for adding a trick.
- `docs/QA.md`, `docs/UPDATING.md`: site QA and content updates.

## Rules

- **Commits:** author `gharbete-max <gh.arbete@gmail.com>`. Push to `main` (rebase on `origin/main` first; another session may push concurrently).
- **Deploy:** GitHub Pages must be enabled once by the owner (Settings → Pages → Source: GitHub Actions). Until then the Deploy workflow fails at configure-pages.
- **Edit surgically.** `index.html` is large and minified-ish. Use exact string replacements, and assert each one matches exactly once.
  - Never run regex clean-ups over the whole file: CSS regexes must stay inside the `<style>` block.
- **Motion lives in rendered 3D frames**, never canvas fakery (no scale-X flips or cross-fades between poses). Small additive effects (glow, wobble, particles, the arrow spring) are fine.
- **Reduced motion:** check `RMQ.matches` for every new effect.
- **Spirit** (`MARKET.md` §0): the market never ends a run, no real tickers or advice, one finger, phone first.

## Testing the game (headless)

```
python3 -c "h=open('index.html').read();open('_test.html','w').write(h.replace('function step(dt){if(R.dead)return;','function step(dt){window.__R=R;if(R.dead)return;'))"
python3 -m http.server 8765 &
# Playwright: open /_test.html, remove .modalShade, setPage('parallel'), call navGame(document.querySelector(".navbtn[data-page=game]")) (the bottom bar is hidden in the Apple-style UI, so a click times out), click #gcGo.
# window.__R is the live state. Keys E/S/A/D = long/short/cash/all-in. Swipes: mouse down, move 40px+, up.
# Useful: __R.nextCp = __R.sx + 400 (bring the bull), _cp.trick('cork'), _cp.flickDir(dx,dy), __R.shield=true / __R.magT=5 / __R.x2T=5 (auras).
```

**Delete `_test.html` afterwards; never commit it.** Check for `pageerror` and 4xx responses.

## Rendering 3D assets (Blender as a Python module)

- **Generator:** `scripts/icons/objects.py <name,name,...> <outdir> <res> <samples> 1`, run with bpy (Python 3.13 + `bpy`). Each name renders to `<outdir>/<name>/000.png`.
- **Environment switches:**

| Variable | Values |
|---|---|
| `RUNNER_SKIN` | `gold` (default; cash/all in), `lgreen`/`ggreen` (long 1x/2x), `lred`/`gred` (short 1x/2x). Power-ups are canvas auras, not skins. |
| `RUNNER_PROP` | `case` (cash run). ALL IN is `o_skate` (skateboard), its own generator. |
| `RUNNER_FACE` | `love`, `love-noeyes` |
| `GLASS_STYLE` | `1` (default): the glass family. Every skin is a glass ball (gold = amber "honey glass" with gold limbs) with a glowing gold $ coin floating inside (`coin_heart`, the runner's signature; it rocks with the stride and squashes in the goo). Ticks are clear glass candles with a glowing core; power-ups are glass. `0` = the old opaque plastic. |

- **Runner frame list (105):** walk 24, jog 24, run 24 (`GAIT_N`), tko 9 (blended through 3 key poses), rise 12, fall 12 (`AIR`) → `runner-{gait}-{i}`. Sheets are 2 rows of 53 (`RC` in `index.html`; one row would pass WebP's 16383 px limit for the cash sheet). The game steps gaits by distance (30-75 fps), rise at 36 fps, fall at 45 fps. The love sheets keep their old 8 frames (rise 0-3, fall 0-3 of a 4-frame cycle = new rise/fall frames 0, 3, 6, 9); their hat anchors map to `HEADS.run[81+3i]` / `[93+3i]`.
- **Menu dancer:** 54 frames (`DANCE_N`), a 0.9 s loop at 60 fps, slid by `transform` on `.gcDancer::before` (no repaint).
- **Other sheets:** tricks 24 frames each, skate 168, bull/bear 96 (see `docs/ANIMATION.md`, "Frame rate and frame counts"). Sheets decode off the main thread (`bmMake`); canvas colours come from the theme palette `pal()`.
- **Runner sheet packing:**
  - Crop box `(x0, 27, x1, 209)`, frames side by side, cell height 182.
  - The game draws at height 217, so the pixel scale is `217/182`.
  - The body centre sits at render x = 118, so a sheet with a different `x0` needs its offset in code (see `PROP_X0`).
- **Render cost:** 256 px, 32–48 samples (glass needs ≥36 or it looks grainy). About 3 min per 35-frame glass skin on 2 cores; the whole runner set (5 skins × run, love, tricks, plus cash, dance, 2 skate skins) is ~1,100 frames, about 1.5–2 h.
- **Skin → file suffix:** gold → none, lgreen → `-lgreen`, ggreen → `-ggreen`, lred → `-lred`, gred → `-gred`.
- **Hats / head anchors:** every render with a ball named `rb` writes `head.json` (the top pole and a point above it, in render px). The packer turns these into `HEADS` in `index.html`. A new pose sheet needs its anchors added there, or hats won't sit on it.
- Check every frame's alpha bounding box stays inside the 256 px render. Shrink the pose, never move the camera.
- **Contact-sheet first:** render one skin at 8 samples and look at it before the full run.
- Export `.webp`, quality about 86, `method=6`.

## 60 fps rules

- **CSS:** animate only `transform` and `opacity` (keyframes and anything that loops). No looping `left`/`box-shadow`/`filter`/`background-position`; move a sheen with `translateX`, a glow with an opacity-animated pseudo-element, a sprite strip with a stepped `translateX` on its own layer.
- **Game canvas resolution is adaptive:** it starts at the screen density (max 2x) and drops 0.5x (or straight to 1x) when the frame-time average stays above ~18.2 ms (under ~55 fps) over 1.5 s (`dprCur`, `ftA` in `loop`). It never steps back up.
- **Scroll listeners** must not force layout when their effect is hidden (the vignette returns early in the Apple UI).
- **Page weight:** preload an image only if the element that uses it is rendered (`getClientRects().length`); the Apple UI hides the bottom nav, invest popup and token coin, whose spin sheets are ~1.8 MB. First visit is ~0.85 MB (index.html + data JSON + small icons); the hero sheet loads after `load`. Shared JSON fetches go through one promise (`window.__hold`).

## Brand

- **Name:** written `throwindice` (lowercase) with `indice` in gold: throw + indice (index). Wordmark is Inter ExtraBold (800), tracking -0.045em, outlined to SVG paths so it looks the same on every device.
- **Mark:** the price-tag bracket with its hole and a gold die (two pips) tipping into it. Token World swaps the die and `indice` to blue-violet (`.brandWord .g` fill `#bwt`).
- **Shared gradients** live once in a hidden-but-rendered `<svg>` at the top of `<body>`; inline copies (header, loading screen, menu) reference them. Don't put gradient `<defs>` inside elements that can be `display:none`.
- **Rebuild:** `python3 scripts/brand/build.py <inter-800.ttf> <logo3d.png>` writes `assets/brand/` (mark/logo light+dark SVGs, `favicon.svg` that follows dark mode, app icons from the 3D render) and prints the inline snippets. Inter: npm `@fontsource/inter` → `files/inter-latin-800-normal.woff2`, saved as TTF with fontTools.
- **3D mark:** `logo3d` in `objects.py` (smoked-glass tag, honey-glass gold die), 1024 px, 96 samples → `apple-touch-icon.png`, `icon-192/512.png`, `icon-maskable-512.png` (60% fill for the safe zone).
- **Share image:** `assets/brand/og.jpg` (1200 × 630: lockup, headline, hero poster). `og:image` uses the GitHub Pages URL `https://gharbete-max.github.io/throwindice/`; change it if the site moves.
- `manifest.webmanifest` at the root (install name, icons, colours).

## Site hero and icons

- **Home hero:** `o_hero(i)` in `objects.py` (`hero-0..23`, 720 px, 40 samples, about 1 min a frame) is a glass candle chart, the gold glass runner and the diamond bull, turned -20° to +20°. Packed to `assets/hero/hero.webp` (6 × 4 grid, cropped to the union box) and `hero-poster.webp` (frame 12, first paint). The script at the end of `index.html` scrubs the frame with scroll on a canvas; reduced motion shows the poster frame.
- **3D icons in the Apple UI:** inline emoji in running text stay hidden (`body.apple .e3d{display:none}`); icons are shown only in their slots: topic/pile rows (36 px, replacing the coloured dot), World/Sectors/Commodities rows (52 px, left of the title) and the home-page note bullets (30 px).
- **Game particles** are cached glass beads (`bead(colour)`); running dust (`puff`, `d:1`) stays a soft dot.
