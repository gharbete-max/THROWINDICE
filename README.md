# THROWINDICE

A dumbed-down, index-focused atlas of ETFs, commodities and tokenized assets.
Educational, not financial advice: no forecasts, no scores, no individual
stocks, only dated and sourced facts. Save what you like, then click through
to a broker.

Two worlds, one coin toggle: **Real World** (green) and **Token World** (blue).

## Run it

`index.html` is a single self-contained file. Open it, or serve the folder
with any static host (`python3 -m http.server`). No build step.

## Data

`scripts/build-data/` refreshes `data/facts.json` monthly via GitHub Actions
(see its README). Plan and audit: `docs/AUDIT_AND_PLAN.md`.
