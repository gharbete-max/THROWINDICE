import type { Kind } from "./types";

/** A theme or country after scoring/formatting has been applied — what the
 * screens actually render. Chart-ready fields (spark, hist) are included;
 * anything that depends on interactive UI state (hover, selected scenario)
 * is computed on the fly in the component that owns that state. */
export interface BuiltInstrument {
  key: string;
  kind: Kind;
  emoji: string;
  name: string;
  proxy: string;
  etfs: string;
  temp: number;
  rawDelta: number;
  delta: string;
  deltaColor: string;
  condition: string;
  wxEmoji: string;
  color: string;
  fillTop: string;
  bg: string;
  edge: string;
  markerX: string;
  f: [number, number, number, number, number];
  line: string;
  /** 24 monthly scores, oldest→newest, latest === temp. */
  hist: number[];
  /** Sparkline path over the last 12 points, viewBox 0 0 56 26. */
  spark: string;
  ret: number;
  vol: number;
  high: number;
  retLabel: string;
  retColor: string;
  volLabel: string;
  highLabel: string;
  nearHigh: boolean;
  famKey?: string;
  famName?: string;
  mark?: string;
  /** Real Holt-forecast, when the data pipeline could fit one. See
   * src/lib/weather.ts's scenarios(). */
  forecast?: import("../lib/weather").RealForecast;
}

export interface BuiltFamily {
  key: string;
  emoji: string;
  name: string;
  head: string;
  intro: string;
  body: string;
  temp: number;
  rawDelta: number;
  delta: string;
  deltaColor: string;
  condition: string;
  wxEmoji: string;
  color: string;
  bg: string;
  edge: string;
  markerX: string;
  count: string;
  spread: string;
  best: BuiltInstrument;
  worst: BuiltInstrument;
  themes: BuiltInstrument[];
  avgFee: number;
  feeLabel: string;
  feeCost: string;
}

export interface GlobalSummary {
  temp: number;
  condition: string;
  emoji: string;
  color: string;
  line: string;
  arcDash: string;
  needle: { x1: string; y1: string; x2: string; y2: string };
}

export interface MacroTile {
  name: string;
  emoji: string;
  temp: number;
  condition: string;
  color: string;
  delta: string;
  deltaColor: string;
  bg: string;
  edge: string;
}

export interface Store {
  asOf: string;
  nextReport: string;
  themeCount: number;
  families: BuiltFamily[];
  countries: BuiltInstrument[];
  themes: BuiltInstrument[];
  byKey: Record<string, BuiltInstrument>;
  famByKey: Record<string, BuiltFamily>;
  global: GlobalSummary;
  headlines: BuiltFamily[];
  macro: MacroTile[];
  movers: BuiltInstrument[];
  feeTable: { emoji: string; name: string; fee: string; cost: string; barW: string; color: string }[];
  holdings: Record<string, [string, number][]>;
  fees: Record<string, number>;
  learn: import("./types").LearnCard[];
}
