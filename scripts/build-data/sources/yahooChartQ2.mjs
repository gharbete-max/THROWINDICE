// Layer 3 — the same Yahoo chart API, but the query2 host. Yahoo serves
// query1/query2 from different edges; in practice one is sometimes rate-
// limited or geo-blocked while the other isn't, so this earns its place
// as its own layer rather than a retry of layer 2.
import { fetchYahooChart } from "./yahooChartQ1.mjs";

export const name = "yahoo-chart-query2";

export async function fetchDaily(ticker) {
  return fetchYahooChart(ticker, "query2.finance.yahoo.com");
}
