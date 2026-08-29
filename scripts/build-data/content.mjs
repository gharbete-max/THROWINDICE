// The editorial half of the dataset — names, emoji, ETF tickers, and the
// human-written headline/body copy. Deliberately not computed: a monthly
// script has no business inventing "why" prose. Numbers (temp, delta, the
// five factors, history, forecast) are what index.mjs fills in from real
// prices; this file supplies everything else, mirroring src/data/mock.ts's
// structure (kept as a separate file, not imported, so the demo app never
// depends on network access — see README.md "why two copies").
//
// Country indices are proxied by each country's most liquid single-country
// ETF (see README.md "why ETF proxies for indices") rather than the raw
// index ticker, which most free sources don't carry reliably.

export const FAMILIES = [
  { key: "tech", emoji: "🚀", name: "Technology & future",
    head: "Technology kept climbing", intro: "Quantum and AI led, and they were the bumpiest things on the board.",
    body: "The group looks strong, but it is two different stories. The established, profitable giants rose calmly. Quantum and AI funds rose twice as fast with three times the swings — same group, completely different ride.",
    themes: [
      { key: "ai", emoji: "🤖", name: "AI & machine learning", proxy: "AI software and models", etfs: "ARTY · IGPT · CHAT" },
      { key: "qc", emoji: "⚛️", name: "Quantum computing", proxy: "Quantum hardware", etfs: "QTUM" },
      { key: "rb", emoji: "🦾", name: "Robotics & automation", proxy: "Factory robots, automation", etfs: "BOTZ · ROBO · IRBO" },
      { key: "sp", emoji: "🛰️", name: "Space & satellites", proxy: "Launch, satellites, imaging", etfs: "ARKX · UFO" },
      { key: "cy", emoji: "🔒", name: "Cybersecurity", proxy: "Security software", etfs: "CIBR · HACK · BUG" },
      { key: "sc", emoji: "🔌", name: "Semiconductors", proxy: "Chip makers and tools", etfs: "SMH · SOXX" },
      { key: "bt", emoji: "💻", name: "Established big tech", proxy: "Large profitable tech", etfs: "XLK · QQQ" },
    ] },
  { key: "fin", emoji: "🏦", name: "Finance & money",
    head: "Finance was pulled apart", intro: "Banks steady, crypto-linked companies down hard.",
    body: "Old finance and new finance went opposite ways. Banks and insurers were dull and fine. Crypto-linked companies gave back most of the summer, and they are the most violent thing in the app.",
    themes: [
      { key: "bk", emoji: "🏛️", name: "Banks & lenders", proxy: "Banks, regional lenders", etfs: "XLF · KBE" },
      { key: "ft", emoji: "💳", name: "Fintech & payments", proxy: "Payments, digital banking", etfs: "FINX · IPAY" },
      { key: "bc", emoji: "🪙", name: "Blockchain & stablecoins", proxy: "Exchanges, miners, issuers", etfs: "BLOK · BKCH" },
      { key: "ins", emoji: "🧾", name: "Insurance & asset managers", proxy: "Insurers, fund managers", etfs: "KIE · IAI" },
    ] },
  { key: "nrg", emoji: "🔋", name: "Energy",
    head: "Energy had a strong month", intro: "Nuclear and oil did the work; solar and wind are still falling.",
    body: "The strongest group headline of August — and the widest split inside it. Nuclear and oil companies did all the work. Solar and wind are in their fourth month of decline. Read the group score, then read the split.",
    themes: [
      { key: "nu", emoji: "☢️", name: "Nuclear & uranium", proxy: "Reactors, uranium miners", etfs: "URA · NLR" },
      { key: "oil", emoji: "🛢️", name: "Oil & gas companies", proxy: "Majors, drillers, services", etfs: "XLE · XOP" },
      { key: "sol", emoji: "☀️", name: "Solar", proxy: "Panel makers, installers", etfs: "TAN" },
      { key: "wnd", emoji: "🌬️", name: "Wind", proxy: "Turbine makers, developers", etfs: "FAN" },
      { key: "wat", emoji: "💧", name: "Water & hydro", proxy: "Utilities, treatment, pipes", etfs: "PHO · FIW" },
      { key: "grd", emoji: "🪫", name: "Grid & storage", proxy: "Cables, batteries, grid kit", etfs: "GRID · BATT" },
    ] },
  { key: "min", emoji: "⛏️", name: "Miners & materials",
    head: "Gold miners shone", intro: "Gold miners at a record; factory metals went nowhere.",
    body: "Gold diggers are at a record, and unlike most record-highs this one came with a calm ride. The metals used in factories — copper, steel, lithium — went nowhere or fell, which is what a slow industrial economy looks like.",
    themes: [
      { key: "gld", emoji: "🥇", name: "Gold miners", proxy: "Gold mining companies", etfs: "GDX · GDXJ" },
      { key: "cop", emoji: "🟠", name: "Copper & industrial metals", proxy: "Copper and metal miners", etfs: "COPX · PICK" },
      { key: "lit", emoji: "⚡", name: "Lithium & battery metals", proxy: "Lithium, rare earths", etfs: "LIT · REMX" },
      { key: "stl", emoji: "🧱", name: "Steel & building materials", proxy: "Steel, cement, chemicals", etfs: "SLX · XLB" },
    ] },
  { key: "hlt", emoji: "🧬", name: "Health & life sciences",
    head: "Health care stayed dull", intro: "Barely moved. Biotech is the soft part.",
    body: "Small moves, calm ride, no news. Big pharma and devices barely registered the month. Biotech is the weak spot: profitless companies that need cheap money, and money is not cheap.",
    themes: [
      { key: "bio", emoji: "🧪", name: "Biotech", proxy: "Drug developers", etfs: "XBI · IBB" },
      { key: "phm", emoji: "💊", name: "Big pharma", proxy: "Large drug makers", etfs: "XLV · PPH" },
      { key: "dev", emoji: "🩺", name: "Medical devices", proxy: "Equipment, diagnostics", etfs: "IHI" },
    ] },
  { key: "eco", emoji: "🏠", name: "Everyday economy",
    head: "The everyday economy is flat", intro: "Defence strong, shops and property weak.",
    body: "Defence is the one bright spot and has been all year. Shops and property are the weak end — both are where higher interest rates and careful shoppers show up first.",
    themes: [
      { key: "df", emoji: "🛡️", name: "Defence & aerospace", proxy: "Defence contractors", etfs: "ITA · EUAD" },
      { key: "ind", emoji: "🏗️", name: "Industrials & machinery", proxy: "Machinery, transport", etfs: "XLI · VIS" },
      { key: "ev", emoji: "🧴", name: "Everyday goods", proxy: "Food, drink, household", etfs: "XLP" },
      { key: "rtl", emoji: "🛍️", name: "Retail & consumer", proxy: "Shops, brands, leisure", etfs: "XRT · XLY" },
      { key: "re", emoji: "🏘️", name: "Real estate", proxy: "Property companies", etfs: "XLRE · VNQ" },
    ] },
];

// key, name, proxy = the description shown in the app; proxyTicker = the
// single-country ETF the pipeline actually fetches prices for.
export const COUNTRIES = [
  { key: "us", emoji: "🇺🇸", name: "United States", proxy: "S&P 500", proxyTicker: "SPY" },
  { key: "de", emoji: "🇩🇪", name: "Germany", proxy: "DAX 40", proxyTicker: "EWG" },
  { key: "fr", emoji: "🇫🇷", name: "France", proxy: "CAC 40", proxyTicker: "EWQ" },
  { key: "uk", emoji: "🇬🇧", name: "United Kingdom", proxy: "FTSE 100", proxyTicker: "EWU" },
  { key: "nd", emoji: "🇸🇪", name: "Nordics", proxy: "OMX Nordic 40", proxyTicker: "EWD" },
  { key: "eu", emoji: "🇪🇺", name: "Europe (all)", proxy: "STOXX Europe 600", proxyTicker: "VGK" },
  { key: "jp", emoji: "🇯🇵", name: "Japan", proxy: "Nikkei 225", proxyTicker: "EWJ" },
  { key: "ax", emoji: "🌏", name: "Asia ex-Japan", proxy: "MSCI Asia ex-Japan", proxyTicker: "AAXJ" },
  { key: "cn", emoji: "🇨🇳", name: "China", proxy: "CSI 300", proxyTicker: "MCHI" },
  { key: "in", emoji: "🇮🇳", name: "India", proxy: "Nifty 50", proxyTicker: "INDA" },
  { key: "au", emoji: "🇦🇺", name: "Australia", proxy: "ASX 200", proxyTicker: "EWA" },
];

export const MACRO = [
  { name: "United States", emoji: "🇺🇸", keys: ["us"] },
  { name: "Europe", emoji: "🇪🇺", keys: ["de", "fr", "uk", "nd", "eu"] },
  { name: "Asia", emoji: "🌏", keys: ["jp", "ax", "cn", "in"] },
  { name: "Australia", emoji: "🇦🇺", keys: ["au"] },
];

// Expense ratios aren't in any price feed — maintained by hand, same as
// the mock. Re-check yearly; funds rarely reprice mid-year.
export const FEES = {
  ai: 0.48, qc: 0.4, rb: 0.68, sp: 0.6, cy: 0.58, sc: 0.35, bt: 0.17,
  bk: 0.09, ft: 0.68, bc: 0.7, ins: 0.35,
  nu: 0.69, oil: 0.09, sol: 0.67, wnd: 0.56, wat: 0.55, grd: 0.58,
  gld: 0.51, cop: 0.65, lit: 0.75, stl: 0.56,
  bio: 0.35, phm: 0.12, dev: 0.39,
  df: 0.55, ind: 0.09, ev: 0.09, rtl: 0.35, re: 0.09,
};

// Same story as FEES — top-5 holdings need a constituents feed, which
// isn't reliably free per-fund. Maintained by hand for now; see README
// "upgrading holdings/breadth" for the free-but-more-work path (each
// issuer publishes a daily holdings CSV on the fund's own page).
export { HOLDINGS } from "./holdings.mjs";
export { LEARN } from "./learn.mjs";
