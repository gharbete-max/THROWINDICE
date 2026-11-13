# Putting throwindice on your website as its own page

throwindice is one static folder: no build step, no server, no cookies. It works at any URL depth.

## Steps

1. `SITE_URL=https://yoursite.com/throwindice/ scripts/package.sh` writes `dist/throwindice/`.
   (`SITE_URL` only rewrites the share-card address, `og:url` and `og:image`.)
2. Upload that folder to `yoursite.com/throwindice/` (any static host, or your site's `public/` folder).
3. Link to it: `<a href="/throwindice/">Investing, simply</a>`.

## Options

- **Inside your site's chrome:** `<iframe src="/throwindice/?embed" style="width:100%;height:100vh;border:0" title="throwindice">`.
  `?embed` hides the throwindice wordmark and keeps its menu. The game opens full screen inside the frame.
- **Deep link to the game:** `/throwindice/#play`.
- **Look:** it follows throwpaper's design system (paper `#fafaf8`, ink `#0e0e10`, gold `#cea85c`, bronze `#8f6b3a`,
  platinum greys, flat cards, glass only on the header, menu and dialogs, Inter 16/1.55, light and dark). The CSS is the
  `tpStyle` block at the end of `<head>` in `index.html`; its values are copied from throwpaper's `DESIGN.md`.
- **Fonts:** Inter is first in the stack but not bundled (same as throwpaper): it uses Inter if the visitor has it, else the system font.
- **Data:** `data/facts.json` and `data/holdings.json` are refreshed monthly by `.github/workflows/monthly-data.yml`. On your own host, re-run the
  package script after each refresh, or run `scripts/build-data/index.mjs` yourself.

## Checklist before going live

- [ ] Packaged with your `SITE_URL`.
- [ ] Opened on a phone (320 and 390 px) and desktop, light and dark.
- [ ] `Not advice` is visible on the home page, funds, tokens and game start (it is, by default).
- [ ] If your site sets a Content-Security-Policy: the page needs inline script/style, `data:` images, and `fetch` of its own `data/*.json`.
