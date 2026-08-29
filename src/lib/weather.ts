// Shared scoring / formatting logic. Ported from the Claude Design
// prototype's inline script (project/Market Weather v3.dc.html), typed and
// framework-free so it can be imported by both the React app and the Node
// data-pipeline script (scripts/build-data/*) that will eventually replace
// the mock dataset with real numbers computed the same way.

export const UP = "#5fc09a";
export const DOWN = "#e2726b";
export const FLAT = "#8d94ad";
export const GOLD = "#e8b55c";

export interface WeatherBand {
  min: number;
  name: string;
  emoji: string;
  color: string;
  fill: string;
}

// A 0–100 score maps to one of six weather conditions, storm to clear.
export const WX: WeatherBand[] = [
  { min: 80, name: "Clear", emoji: "☀️", color: "#e8b55c", fill: "rgba(232,181,92,.28)" },
  { min: 65, name: "Sunny spells", emoji: "🌤️", color: "#c0a8f0", fill: "rgba(192,168,240,.26)" },
  { min: 50, name: "Cloudy", emoji: "☁️", color: "#9199b5", fill: "rgba(145,153,181,.22)" },
  { min: 35, name: "Drizzle", emoji: "🌦️", color: "#7f9bd8", fill: "rgba(127,155,216,.22)" },
  { min: 20, name: "Rain", emoji: "🌧️", color: "#5573c4", fill: "rgba(85,115,196,.24)" },
  { min: 0, name: "Storm", emoji: "⛈️", color: "#6a6fc0", fill: "rgba(106,111,192,.24)" },
];

export function wx(temp: number): WeatherBand {
  return WX.find((w) => temp >= w.min) ?? WX[WX.length - 1];
}

export const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export const dLabel = (d: number) => (d === 0 ? "–" : (d > 0 ? "▲" : "▼") + Math.abs(d));
export const dColor = (d: number) => (d > 0 ? UP : d < 0 ? DOWN : FLAT);

/** Tint a weather/status color into a low-alpha card background, blended
 * toward the app's surface color — same recipe the prototype used via
 * CSS color-mix, computed here so it also works outside a browser (Node). */
export function tint(hex: string, alphaPct: number, base = "#232532"): string {
  return `color-mix(in srgb, ${hex} ${alphaPct}%, ${base})`;
}

export interface Factor {
  emoji: string;
  label: string;
  fmt: (score: number) => string;
  plain: (score: number) => string;
}

// The five simple checks every score is built from.
export const FACTORS: Factor[] = [
  {
    emoji: "📈",
    label: "Going up?",
    fmt: (s) => (s >= 50 ? "+" : "") + ((s - 50) / 12).toFixed(1) + "% a month",
    plain: (s) => (s >= 70 ? "Rising steadily." : s >= 50 ? "Drifting up, slowly." : s >= 35 ? "Slipping a little." : "Falling."),
  },
  {
    emoji: "🎢",
    label: "Bumpy?",
    fmt: (s) => (30 - s * 0.22).toFixed(1) + "% swings",
    plain: (s) => (s >= 70 ? "Very calm — small daily moves." : s >= 50 ? "Normal for this market." : s >= 35 ? "Choppy. Expect surprises." : "Wild. Prices jump around."),
  },
  {
    emoji: "👥",
    label: "Broad?",
    fmt: (s) => Math.round(20 + s * 0.62) + "% of companies up",
    plain: (s) => (s >= 65 ? "Most companies are rising, not just a few names." : s >= 45 ? "About half are joining in." : "Only a handful are holding it up."),
  },
  {
    emoji: "🏔️",
    label: "Near its high?",
    fmt: (s) => "-" + ((100 - s) * 0.28).toFixed(1) + "% off the top",
    plain: (s) => (s >= 80 ? "Basically at its record. Careful — that can be a peak." : s >= 55 ? "Close to the top." : s >= 35 ? "A dip, nothing unusual." : "Well below its high."),
  },
  {
    emoji: "🔊",
    label: "Busy?",
    fmt: (s) => (s >= 50 ? "+" : "") + Math.round((s - 50) * 0.4) + "% trading",
    plain: (s) => (s >= 65 ? "Lots of people trading it — real conviction." : s >= 45 ? "Ordinary activity." : "Quiet. Few people bothering."),
  },
];

export const METHOD = [
  { emoji: "📈", title: "Is it going up?", body: "Price change over one and three months." },
  { emoji: "🎢", title: "Is it bumpy?", body: "How much prices jump around day to day. Calm scores higher." },
  { emoji: "👥", title: "Is it broad?", body: "How many companies are rising, not just the biggest few." },
  { emoji: "🏔️", title: "Is it near its high?", body: "How far below its best price of the year it sits." },
  { emoji: "🔊", title: "Is it busy?", body: "Whether trading volume backs the move up." },
];

/** Deterministic pseudo-random 24-month history ending at `end`, seeded so
 * the mock dataset is stable across renders/builds. The real pipeline
 * replaces this with actual monthly closes. */
export function series(seed: number, end: number, n: number): number[] {
  let s = seed >>> 0;
  const r = () => {
    s = (s * 1103515245 + 12345) & 0x7fffffff;
    return s / 0x7fffffff;
  };
  const out: number[] = [];
  let v = end + (r() - 0.5) * 26;
  for (let i = 0; i < n; i++) {
    out.push(v);
    v = v + (r() - 0.5) * 15 + (end - v) * 0.11;
  }
  const vals = out.map((x) => Math.max(9, Math.min(93, Math.round(x))));
  vals[n - 1] = end;
  return vals;
}

export interface Scenario {
  emoji: string;
  label: string;
  prob: number;
  delta: number;
  body: string;
}

export interface RealForecast {
  p1: number;
  p2: number;
  resid: number;
}

/** Two-step-ahead outlook, expressed as three branching scenarios rather
 * than one number — the Holt–Winters-flavoured forecast the Method screen
 * describes in plain words. `factors[1]` = bumpiness, `factors[3]` = near-high.
 *
 * When `forecast` is supplied (the real pipeline's Holt's-method fit —
 * see scripts/build-data/lib/holtwinters.mjs), the middle scenario centres
 * on its actual two-step point forecast and the band width comes from its
 * residual spread, rather than the temp/factor heuristic below (which is
 * what the mock dataset — with no real trend to fit — falls back to). */
export function scenarios(temp: number, factors: number[], forecast?: RealForecast): Scenario[] {
  const bumpy = factors[1] < 45;
  const hot = factors[3] >= 80;
  const up = Math.max(12, Math.min(56, 34 + (temp - 55) * 0.35 - (bumpy ? 6 : 0)));
  const dn = Math.max(11, Math.min(46, 22 - (temp - 55) * 0.32 + (bumpy ? 10 : 0)));
  const mid = 100 - Math.round(up) - Math.round(dn);
  const upDelta = bumpy ? 11 : 7;

  if (forecast) {
    // Centre the "more of the same" scenario on the real 2-step forecast;
    // widen/narrow the up/down bands with the fit's own residual spread
    // (a noisier history → less confident, wider probability split).
    const spread = Math.max(6, Math.min(40, forecast.resid * 2));
    const upP = Math.round(Math.max(10, Math.min(60, 38 - (forecast.p2 - temp) * -0.6 - spread * 0.3)));
    const dnP = Math.round(Math.max(10, Math.min(55, 22 + (temp - forecast.p2) * 0.4 + spread * 0.25)));
    const midP = Math.max(5, 100 - upP - dnP);
    return [
      {
        emoji: "☀️",
        label: "It gets better",
        prob: upP,
        delta: Math.round(forecast.p2 - temp + spread * 0.5),
        body: "Calm holds and more companies join in — the score would read " + wx(Math.min(96, forecast.p2 + spread * 0.5)).name.toLowerCase() + ".",
      },
      {
        emoji: "☁️",
        label: "More of the same",
        prob: midP,
        delta: Math.round(forecast.p2 - temp),
        body: `The fitted trend points to about ${forecast.p2} two months out (it read ${forecast.p1} for next month) — the most likely path if nothing changes.`,
      },
      {
        emoji: "⛈️",
        label: "It turns",
        prob: dnP,
        delta: Math.round(forecast.p2 - temp - spread * 0.5),
        body:
          spread > 20
            ? "A sharp drop. This one's history is noisy enough that the fitted trend has wide error bars in both directions."
            : hot
              ? "Sitting at its high is the risk — a pullback would knock the score down hard."
              : "Weak prices spread and the score slides into worse weather.",
      },
    ];
  }

  return [
    {
      emoji: "☀️",
      label: "It gets better",
      prob: Math.round(up),
      delta: upDelta,
      body: "Calm holds and more companies join in — the score would read " + wx(Math.min(96, temp + upDelta)).name.toLowerCase() + ".",
    },
    {
      emoji: "☁️",
      label: "More of the same",
      prob: mid,
      delta: temp > 60 ? -3 : 1,
      body: "The most likely path: no real change, the score stays around " + Math.round(temp + (temp > 60 ? -3 : 1)) + ".",
    },
    {
      emoji: "⛈️",
      label: "It turns",
      prob: Math.round(dn),
      delta: bumpy ? -24 : -16,
      body: bumpy
        ? "A sharp drop. This one moves fast in both directions, so the fall would be quick."
        : hot
          ? "Sitting at its high is the risk — a pullback would knock the score down hard."
          : "Weak prices spread and the score slides into worse weather.",
    },
  ];
}
