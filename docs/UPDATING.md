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

## Region rules (REG in index.html)
`REG` maps each region to how US-listed funds and UCITS funds can usually be bought (2 yes, 1 ask broker, 0 mostly not). Re-check yearly against regulator and broker pages (EU/UK key-information-document rule, UCITS marketing rules, China capital controls). Domicile comes from the ISIN prefix; add `DOMFIX` entries for funds without an ISIN and a `FLAGS` drawing for any new country.

## UCITS, ETC and ETP data
Name, ISIN, domicile and fee come from `https://www.justetf.com/en/etf-profile.html?isin=<ISIN>` (title, "domiciled in …" text, total expense ratio). Put the fee in `FEEX`, the size guess in `TIER`, and add a `DOMFIX` entry when the ISIN prefix is not the domicile (ETPs).

## VOO vs savings chart (`VS` in index.html)
Period: VOO's first trading day (2010-09-09) to the last trading day of 2025 (2025-12-31), a fixed, complete period. Numbers: Yahoo Finance daily chart (`query1.finance.yahoo.com/v8/finance/chart/VOO?period1=…&period2=…&interval=1d`). `voo` = adjusted-close growth in % (dividends reinvested) = 716.8, `price` = close-only growth = 519.0, `sav` = (1.02^15.31 − 1) × 100 = 35.4. Move the end date forward only when you want a newer year.
