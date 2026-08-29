// Turns a SourceRoot (mock today, real pipeline output later) into the
// fully-scored Store the screens render from. Pure function, no React —
// call once (see src/data/index.ts) and pass the result down.
import type { SourceRoot, RawInstrument, Kind } from "../data/types";
import type { BuiltInstrument, BuiltFamily, Store, GlobalSummary, MacroTile } from "../data/built";
import { wx, series, dLabel, dColor, tint, UP, DOWN, GOLD } from "./weather";

function fallbackSeed(key: string): number {
  let h = 0;
  for (let i = 0; i < key.length; i++) h = (h * 31 + key.charCodeAt(i)) >>> 0;
  return h || 1;
}

function buildInstrument(raw: RawInstrument, kind: Kind, extra: Partial<BuiltInstrument> = {}): BuiltInstrument {
  const w = wx(raw.temp);
  const hist = raw.hist ?? series(raw.seed ?? fallbackSeed(raw.key), raw.temp, 24);
  const recent = hist.slice(12);
  const lo = Math.min(...recent);
  const hi = Math.max(...recent);
  const spark = recent
    .map((v, i, a) => {
      const x = 2 + (i * 50) / (a.length - 1);
      const y = 3 + 20 - ((v - lo) / Math.max(1, hi - lo)) * 20;
      return (i ? "L" : "M") + x.toFixed(1) + "," + y.toFixed(1);
    })
    .join(" ");
  const ret = (raw.f[0] - 50) / 3.2;
  const vol = 30 - raw.f[1] * 0.22;
  const high = -((100 - raw.f[3]) * 0.28);
  return {
    key: raw.key,
    kind,
    emoji: raw.emoji,
    name: raw.name,
    proxy: raw.proxy,
    etfs: raw.etfs,
    temp: raw.temp,
    rawDelta: raw.delta,
    delta: dLabel(raw.delta),
    deltaColor: dColor(raw.delta),
    condition: w.name,
    wxEmoji: w.emoji,
    color: w.color,
    fillTop: w.fill,
    bg: tint(w.color, 11),
    edge: tint(w.color, 34),
    markerX: `calc(${raw.temp}% - 2px)`,
    f: raw.f,
    line: raw.line,
    hist,
    spark,
    ret,
    vol,
    high,
    retLabel: (ret > 0 ? "+" : "") + ret.toFixed(1) + "%",
    retColor: ret >= 0 ? UP : DOWN,
    volLabel: vol.toFixed(1) + "%",
    highLabel: high.toFixed(1) + "%",
    nearHigh: high > -2.5,
    forecast: raw.forecast,
    ...extra,
  };
}

export function buildStore(source: SourceRoot): Store {
  let n = 0;
  const themes: BuiltInstrument[] = [];
  const byKey: Record<string, BuiltInstrument> = {};

  const families: BuiltFamily[] = source.families.map((F) => {
    const list = F.themes.map((t) => {
      n += 1;
      const mark = "*" + n;
      const built = buildInstrument(t, "theme", {
        famKey: F.key,
        famName: F.name,
        mark,
      });
      themes.push(built);
      byKey[built.key] = built;
      return built;
    });
    const temp = Math.round(list.reduce((a, x) => a + x.temp, 0) / list.length);
    const delta = Math.round(list.reduce((a, x) => a + x.rawDelta, 0) / list.length);
    const w = wx(temp);
    const sorted = list.slice().sort((a, b) => b.temp - a.temp);
    const best = sorted[0];
    const worst = sorted[sorted.length - 1];
    const avgFee = list.reduce((a, x) => a + (source.fees[x.key] || 0), 0) / list.length;
    return {
      key: F.key,
      emoji: F.emoji,
      name: F.name,
      head: F.head,
      intro: F.intro,
      body: F.body,
      temp,
      rawDelta: delta,
      delta: dLabel(delta),
      deltaColor: dColor(delta),
      condition: w.name,
      wxEmoji: w.emoji,
      color: w.color,
      bg: tint(w.color, 10),
      edge: tint(w.color, 34),
      markerX: `calc(${temp}% - 2px)`,
      count: list.length + " themes",
      spread: `${best.emoji} ${best.temp} → ${worst.temp} ${worst.emoji}`,
      best,
      worst,
      themes: sorted,
      avgFee,
      feeLabel: avgFee.toFixed(2) + "% a year",
      feeCost: Math.round(avgFee * 10) + " per 1,000 invested, every year",
    };
  });
  const famByKey: Record<string, BuiltFamily> = {};
  families.forEach((f) => (famByKey[f.key] = f));

  const countries = source.countries.map((c) => {
    const built = buildInstrument(c, "country");
    byKey[built.key] = built;
    return built;
  });

  const globalTemp = Math.round(families.reduce((a, f) => a + f.temp, 0) / families.length);
  const gw = wx(globalTemp);
  const gAngle = Math.PI - (globalTemp / 100) * Math.PI;
  const global: GlobalSummary = {
    temp: globalTemp,
    condition: gw.name,
    emoji: gw.emoji,
    color: gw.color,
    line: "A middling month with strong corners. Energy and technology carried it, health care and the everyday economy sat still, and nothing here is calm all the way through.",
    arcDash: ((globalTemp / 100) * 392).toFixed(0) + " 400",
    needle: {
      x1: (155 + 86 * Math.cos(gAngle)).toFixed(1),
      y1: (156 - 86 * Math.sin(gAngle)).toFixed(1),
      x2: (155 + 112 * Math.cos(gAngle)).toFixed(1),
      y2: (156 - 112 * Math.sin(gAngle)).toFixed(1),
    },
  };

  const headlines = families
    .slice()
    .sort((a, b) => Math.abs(b.rawDelta) - Math.abs(a.rawDelta))
    .slice(0, 3);

  const macro: MacroTile[] = source.macro.map((m) => {
    const list = m.keys.map((k) => byKey[k]);
    const t = Math.round(list.reduce((a, x) => a + x.temp, 0) / list.length);
    const dl = Math.round(list.reduce((a, x) => a + x.rawDelta, 0) / list.length);
    const w = wx(t);
    return {
      name: m.name,
      emoji: m.emoji,
      temp: t,
      condition: w.name,
      color: w.color,
      delta: dLabel(dl),
      deltaColor: dColor(dl),
      bg: tint(w.color, 10),
      edge: tint(w.color, 34),
    };
  });

  const movers = themes
    .concat(countries)
    .slice()
    .sort((a, b) => Math.abs(b.rawDelta) - Math.abs(a.rawDelta))
    .slice(0, 6);

  const feeTable = families
    .slice()
    .sort((a, b) => a.avgFee - b.avgFee)
    .map((f) => ({
      emoji: f.emoji,
      name: f.name,
      fee: f.avgFee.toFixed(2) + "%",
      cost: Math.round(f.avgFee * 10) + " / 1,000",
      barW: Math.min(100, (f.avgFee / 0.65) * 100).toFixed(0) + "%",
      color: f.avgFee < 0.3 ? UP : f.avgFee < 0.5 ? "#c0a8f0" : GOLD,
    }));

  return {
    asOf: source.asOf,
    nextReport: source.nextReport,
    themeCount: themes.length,
    families,
    countries,
    themes,
    byKey,
    famByKey,
    global,
    headlines,
    macro,
    movers,
    feeTable,
    holdings: source.holdings,
    fees: source.fees,
    learn: source.learn,
  };
}
