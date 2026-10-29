# Updating THROWINDICE (quarterly)

The site lists funds and tokens and explains them. It does not show prices or performance, so it only needs a review about once a quarter (Jan, Apr, Jul, Oct).

Everything lives in `index.html`.

## Checklist
1. **Fees**: for the 10 funds with a fee (`etfFacts` in the script), re-check the expense ratio on the provider page and update `fee` and the "Fee checked" date in `selectETF`.
2. **New funds**: add an entry to `NEW` (ticker, category, issuer, name, kind, one-line plain sentence, plain "what is inside", icon, optional ISIN). No fee unless it is sourced. Use an ISIN only if you are sure of it; otherwise the page links to a justETF search.
3. **Links**: click through the justETF, etf.com and Holdings links for a few funds. Fix or drop dead ones.
4. **Tokens**: re-read the official pages linked on the Token cards; update or remove cards whose product changed.
5. **Calculator defaults**: re-check the long-run growth range and the average index ETF fee (ICI report) and update the "Starting values" note and `resetCalc`.
6. **Label**: update "Reviewed quarterly · Oct 2026" on the ETF page.
7. Run the checks in `docs/QA.md`, open a PR, merge.

## Brokers
`BROKERS` in the script holds placeholder broker names and plain homepages. Replace with real affiliate URLs when available and keep the "sponsored" rel and the disclosure.

## Hidden bubble size tiers
`TIER` in `index.html` gives each fund a size tier from 1 (small) to 4 (large). It only sets how big its bubble is in the pit; users never see it. Tiers come from average daily dollar volume (3-month average shares × latest monthly close, from `data/facts.json`): 4 ≥ $1B, 3 ≥ $200M, 2 ≥ $40M, 1 below. Funds with no data in `facts.json` (UCITS funds and some newer ones) have rough estimates. When you add a fund, add it to `TIER`; refresh the numbers each quarter (run the data workflow by hand, then recompute).

## Fee and volatility maps (FEEX, VOLX in index.html)
Each quarter refresh `FEEX` (percent per year, US-listed ETFs) from Yahoo Finance fund profiles (quoteSummary `fundProfile.feesExpensesInvestment`, needs a crumb from `query1.finance.yahoo.com/v1/test/getcrumb` after loading `fc.yahoo.com` cookies) and `VOLX` from `data/facts.json` `volatility3y`. Funds with an issuer-reported fee in `etfFacts` keep that value. Update the source/date line above `FEEX` and the disclaimer text.
