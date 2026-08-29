// The shape both the mock dataset (src/data/mock.ts) and the real monthly
// data pipeline (scripts/build-data) produce. Screens only ever read this
// shape — swapping mock for real data is a one-line change in src/data/index.ts.

export type Kind = "theme" | "country";

/** Raw input for one instrument: a theme (1–3 ETFs, equal-weighted) or a
 * country index. Everything else (score, weather, chart geometry, deltas)
 * is derived from this at load time by src/lib/build.ts. */
export interface RawInstrument {
  key: string;
  emoji: string;
  name: string;
  /** Short description of what it tracks. */
  proxy: string;
  /** 0–100 composite score, latest month. */
  temp: number;
  /** Change in score vs. last month. */
  delta: number;
  /** Seed for the deterministic mock history generator. Only used when
   * `hist` isn't supplied — the real pipeline provides `hist` directly
   * (24 actual monthly scores) and omits this. */
  seed?: number;
  /** The five factor scores (0–100) behind this month's temp, in FACTORS order. */
  f: [number, number, number, number, number];
  /** One-line take for this month. */
  line: string;
  /** ETF tickers, "·"-joined (empty string for countries — they use the index itself). */
  etfs: string;
  /** 24 real monthly composite scores, oldest→newest, latest === temp.
   * Present only from the real data pipeline; the mock dataset fabricates
   * this from `seed` instead (see src/lib/build.ts). */
  hist?: number[];
  /** Real two-step-ahead Holt forecast, when the pipeline could fit one
   * (needs ≥6 months of history). Powers the scenario probabilities in
   * src/lib/weather.ts's scenarios() when present; falls back to the
   * heuristic otherwise. */
  forecast?: { p1: number; p2: number; resid: number };
}

export interface RawTheme extends RawInstrument {
  famKey: string;
}

export interface RawFamily {
  key: string;
  emoji: string;
  name: string;
  /** Front-page headline when this group is a top mover, e.g. "Energy had a strong month". */
  head: string;
  /** One-line explainer under the headline. */
  intro: string;
  /** Longer paragraph shown on the group detail screen. */
  body: string;
  themes: RawTheme[];
}

export interface RawCountry extends RawInstrument {}

export interface MacroRegion {
  name: string;
  emoji: string;
  /** Country keys averaged into this region tile. */
  keys: string[];
}

export interface LearnCard {
  key: string;
  emoji: string;
  q: string;
  a: string;
  b: string;
}

export interface SourceRoot {
  families: RawFamily[];
  countries: RawCountry[];
  macro: MacroRegion[];
  /** Top-5 holdings, by instrument key, as [name, weightPct] pairs. */
  holdings: Record<string, [string, number][]>;
  /** Annual fee, by theme key, as a fraction of a percent (e.g. 0.48 = 0.48%). */
  fees: Record<string, number>;
  learn: LearnCard[];
  /** ISO month this dataset represents, e.g. "2026-08". */
  asOf: string;
  /** Human label for the next report, e.g. "1 September". */
  nextReport: string;
}
