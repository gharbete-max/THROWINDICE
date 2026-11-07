# THROWINDICE: notes for Claude Code

Single-page site (`index.html`, no build step). It has the investing pages, Token World mode, and a canvas runner game ("Live Ball Bounce"). All game code is inside one closure in `index.html` (state `R`, `step(dt)`, `player()`, the draw loop).

## Where things are decided

- **`docs/MARKET.md`**: the market pivot. Decisions, the ordered task list (M1–M7) and the asset inventory. **Start here for game work.**
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
# Playwright: open /_test.html, remove .modalShade, setPage('parallel'), click .navbtn[data-page="game"], click #gcGo.
# window.__R is the live state. Keys E/S/A/D = long/short/cash/all-in. Swipes: mouse down, move 40px+, up.
# Useful: __R.nextCp = __R.sx + 400 (bring the bull), _cp.trick('cork'), _cp.flickDir(dx,dy).
```

**Delete `_test.html` afterwards; never commit it.** Check for `pageerror` and 4xx responses.

## Rendering 3D assets (Blender as a Python module)

- **Generator:** `scripts/icons/objects.py <name,name,...> <outdir> <res> <samples> 1`, run with bpy (Python 3.13 + `bpy`). Each name renders to `<outdir>/<name>/000.png`.
- **Environment switches:**

| Variable | Values |
|---|---|
| `RUNNER_SKIN` | `gold` (default), `glass` (shield), `blue` (magnet), `green` (2x), `rainbow` (combo) |
| `RUNNER_PROP` | `case` (cash run), `shades` (all-in strut) |
| `RUNNER_FACE` | `love`, `love-noeyes` |

- **Runner frame list (35):** walk 8, jog 8, run 8, tko 3, rise 4, fall 4 → `runner-{gait}-{i}`.
- **Runner sheet packing:**
  - Crop box `(x0, 27, x1, 209)`, frames side by side, cell height 182.
  - The game draws at height 217, so the pixel scale is `217/182`.
  - The body centre sits at render x = 118, so a sheet with a different `x0` needs its offset in code (see `PROP_X0`).
- **Render cost:** 256 px, 32–48 samples. About 1–2 min per 35-frame skin on 2 cores; glass skins are slower.
- **Skin → file suffix:** gold → none, glass → `-glass`, blue → `-magnet`, green → `-x2`, rainbow → `-rainbow`.
- Check every frame's alpha bounding box stays inside the 256 px render. Shrink the pose, never move the camera.
- **Contact-sheet first:** render one skin at 8 samples and look at it before the full run.
- Export `.webp`, quality about 86, `method=6`.
