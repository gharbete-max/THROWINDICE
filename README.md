# Isobar — market weather

A mobile-styled PWA that turns ETF and country-index prices into a
monthly "weather report" for global markets — six sector groups, 29
themes, 11 country indices, a Holt-forecast two-month outlook, and a
plain-language Method screen. Implements the design mocked up in Claude
Design as "Regional indices weather app" (Market Weather v3).

## Run it

```
npm install
npm run dev
```

Ships today on the **mock dataset** (`src/data/mock.ts`) — deterministic,
shaped like real data, no network calls. That's deliberate: this is a
static frontend with zero backend, so it works the same in dev, in CI,
and deployed, whether or not the data pipeline has ever run.

## The data

`scripts/build-data/` is a free, no-API-key-required (optionally
key-enhanced) pipeline that fetches real ETF/index prices from a ranked
chain of 13 fallback sources, computes the app's scores/forecast from
them, and writes `src/data/generated.json`. Runs monthly via
`.github/workflows/monthly-data.yml` (free on GitHub Actions).

**Read `scripts/build-data/README.md`** for the full picture — the
source list, the honestly-documented approximations, and the one-line
switch in `src/data/index.ts` that moves the app from the mock dataset
to real generated data once you're happy with a run's output.

## Structure

```
src/
  data/           types, the mock dataset, buildStore() entry point
  lib/            weather scoring/formatting, chart-ready build logic, overlay nav state
  components/     shared UI (tab bar, dial, sparkline, meter bar, scroll shell)
  screens/        Today, Markets, Compare, Method, GroupDetail, IndexDetail
scripts/
  build-data/     the free data pipeline (see its own README)
  gen-icons.mjs   one-off PWA icon generator (needs `playwright`, not a persistent dep)
```

## Deploying (free)

This is a static build (`npm run build` → `dist/`) — any static host
works. Cloudflare Pages, Vercel, and Netlify all have free tiers with no
credit card required and auto-deploy from GitHub:

**Cloudflare Pages** (recommended — most generous free tier, no build
minute limits):
1. Push this repo to GitHub.
2. [dash.cloudflare.com](https://dash.cloudflare.com) → Workers & Pages →
   Create → Pages → connect the repo.
3. Build command `npm run build`, output directory `dist`.
4. Every push to `main` auto-deploys; the monthly data-refresh commit
   (from the GitHub Action) triggers a redeploy the same way.

**Vercel** / **Netlify**: same shape — import the repo, build command
`npm run build`, output `dist`. Both auto-detect Vite with no other
config needed.

No environment variables are required for the site itself. The optional
`FMP_API_KEY` / `TWELVEDATA_API_KEY` / `ALPHAVANTAGE_API_KEY` secrets
belong on the **GitHub Actions** side (repo Settings → Secrets), not the
static host — the deployed site never calls any API at runtime.
