// Every fund the site shows numbers for. Facts only — no prose, no fees
// (fees live next to their issuer source in the site's data block).
// Country "indices" are tracked through the most liquid single-country ETF
// because free feeds carry ETFs far more reliably than raw index tickers.
export const TICKERS = {
  broad: ["VT", "VOO", "SPY", "QQQ", "QQQM", "VGT"],
  bonds: ["BND", "AGG"],
  commodities: ["GLD", "IAU", "SLV", "USO", "UNG", "CPER", "DBA"],
  emerging: ["VWO", "IEMG"],
  countries: ["EWG", "EWQ", "EWU", "EWD", "VGK", "EWJ", "AAXJ", "MCHI", "INDA", "EWA"],
  sectors: ["XLK", "XLF", "XLE", "XLV", "XLI", "XLP", "XLY", "XLB", "XLRE"],
  themes: [
    "ARTY", "IGPT", "CHAT", "QTUM", "BOTZ", "ROBO", "IRBO", "ARKX", "UFO", "CIBR", "HACK", "BUG",
    "SMH", "SOXX", "KBE", "FINX", "IPAY", "BLOK", "BKCH", "KIE", "IAI", "URA", "NLR", "XOP", "TAN",
    "FAN", "PHO", "FIW", "GRID", "BATT", "GDX", "GDXJ", "COPX", "PICK", "LIT", "REMX", "SLX",
    "XBI", "IBB", "PPH", "IHI", "ITA", "EUAD", "VIS", "XRT", "VNQ",
  ],
};
