import { useState } from "react";
import { store } from "../data";
import { useOverlay } from "../lib/overlay";
import ScreenScroll from "../components/ScreenScroll";
import MeterBar from "../components/MeterBar";
import { FACTORS, MONTHS, UP, DOWN, GOLD, wx, scenarios } from "../lib/weather";

const PX = 28, PR = 318, TOP = 14, BOT = 152;
const y = (v: number) => BOT - (v / 100) * (BOT - TOP);

export default function IndexDetail({ detailKey }: { detailKey: string }) {
  const { closeTheme, openTheme } = useOverlay();
  const [hoverIdx, setHoverIdx] = useState<number | null>(null);
  const [scenario, setScenario] = useState(1);
  const [holdOpen, setHoldOpen] = useState(false);

  const dr = store.byKey[detailKey];
  if (!dr) return null;

  const len = dr.hist.length;
  const total = len + 2;
  const px = (i: number) => PX + (i * (PR - PX)) / (total - 1);
  const pts = dr.hist.map((v, i) => ({
    i,
    v,
    x: px(i),
    yy: y(v),
    month: MONTHS[(7 - (len - 1 - i) + 24) % 12],
    year: i < len - 8 ? 25 : 26,
  }));
  const line2 = pts.map((p, i) => (i ? "L" : "M") + p.x.toFixed(1) + "," + p.yy.toFixed(1)).join(" ");
  const last = pts[len - 1];
  const area = line2 + " L" + last.x.toFixed(1) + "," + BOT + " L" + pts[0].x.toFixed(1) + "," + BOT + " Z";
  const step = (PR - PX) / (total - 1);
  const sc = scenarios(dr.temp, dr.f, dr.forecast);

  const branches = sc.map((s, i) => {
    const on = i === scenario;
    const mid = Math.max(9, Math.min(96, dr.temp + s.delta * 0.55));
    const end = Math.max(9, Math.min(96, dr.temp + s.delta));
    return {
      path: `M${last.x.toFixed(1)},${last.yy.toFixed(1)} L${px(len).toFixed(1)},${y(mid).toFixed(1)} L${px(len + 1).toFixed(1)},${y(end).toFixed(1)}`,
      color: on ? GOLD : "#8d94ad",
      w: on ? 2.2 : 1.2,
      op: on ? 1 : 0.35,
      left: (px(len + 1) + 4).toFixed(1) + "px",
      top: y(end).toFixed(1) + "px",
      fs: on ? 15 : 11,
      emoji: s.emoji,
    };
  });

  const hov = hoverIdx !== null ? pts[hoverIdx] : null;
  const hoverLabel = hov ? `${hov.month} '${hov.year} · ${hov.v} ${wx(hov.v).emoji}` : "tap the chart";

  const factors = FACTORS.map((f, i) => {
    const s = dr.f[i];
    return { ...f, value: f.fmt(s), plain: f.plain(s), barW: s + "%", color: s >= 70 ? UP : s >= 45 ? "#c0a8f0" : DOWN };
  });

  const fam = dr.famKey ? store.famByKey[dr.famKey] : null;
  const siblings = fam ? fam.themes.filter((t) => t.key !== dr.key) : [];
  const fee = dr.kind === "theme" ? store.fees[dr.key] ?? 0 : undefined;

  const holdings = (store.holdings[dr.key] || []).map(([name, pct]) => ({
    name,
    pct: pct.toFixed(1) + "%",
    barW: Math.min(100, pct * 4.2).toFixed(1) + "%",
  }));

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        background: "linear-gradient(180deg,#1f2338,#161826 45%)",
        zIndex: 30,
        animation: "mwSlide .22s ease both",
      }}
    >
      <ScreenScroll>
        <div onClick={closeTheme} style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 13, color: "#e8b55c", cursor: "pointer", padding: "6px 2px", marginBottom: 6 }}>
          <span style={{ fontSize: 15 }}>←</span>
          <span>Back</span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <span style={{ fontSize: 46, lineHeight: 1, flex: "none" }}>{dr.emoji}</span>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontFamily: "var(--font-heading)", fontWeight: 500, fontSize: 23, letterSpacing: "-.02em", lineHeight: 1.15 }}>
              {dr.name} {dr.mark}
            </div>
            <div style={{ fontSize: 11.5, color: "var(--color-neutral-500)", marginTop: 2 }}>
              {dr.kind === "theme" ? `${dr.famName} · ${dr.etfs}` : `${dr.proxy} · the index itself`}
            </div>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "baseline", gap: 10, marginTop: 12 }}>
          <span style={{ fontFamily: "var(--font-heading)", fontSize: 54, lineHeight: 1, letterSpacing: "-.035em", color: dr.color }}>{dr.temp}</span>
          <span style={{ fontSize: 15, color: dr.deltaColor }}>{dr.delta}</span>
          <span style={{ fontSize: 15, color: "var(--color-neutral-300)", marginLeft: "auto" }}>
            {dr.condition} {dr.wxEmoji}
          </span>
        </div>
        <MeterBar markerX={dr.markerX} />

        <p style={{ margin: "14px 0 0", fontSize: 14, lineHeight: 1.6, color: "var(--color-neutral-200)" }}>{dr.line}</p>

        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", margin: "20px 2px 8px" }}>
          <div style={{ fontSize: 10, letterSpacing: ".12em", textTransform: "uppercase", color: "var(--color-neutral-500)" }}>Last 2 years</div>
          <div style={{ fontSize: 11, color: "var(--color-neutral-500)" }}>{hoverLabel}</div>
        </div>

        <div style={{ borderRadius: 12, background: "#1b1e2d", boxShadow: "var(--shadow-sm)", padding: "10px 8px 4px" }}>
          <div style={{ position: "relative", width: 330, height: 190 }}>
            <svg width="330" height="190" viewBox="0 0 330 190" fill="none" style={{ display: "block" }}>
              <defs>
                <linearGradient id="mwFill3" x1="0" y1="0" x2="0" y2="1">
                  <stop stopColor={dr.fillTop} />
                  <stop offset="1" stopColor="rgba(0,0,0,0)" />
                </linearGradient>
              </defs>
              <line x1="28" y1="117.5" x2="320" y2="117.5" stroke="rgba(233,233,237,.06)" />
              <line x1="28" y1="83" x2="320" y2="83" stroke="rgba(233,233,237,.06)" />
              <line x1="28" y1="48.5" x2="320" y2="48.5" stroke="rgba(233,233,237,.06)" />
              <path d={area} fill="url(#mwFill3)" />
              <path d={line2} stroke={dr.color} strokeWidth={2.2} strokeLinecap="round" strokeLinejoin="round" fill="none" />
              <line x1={last.x.toFixed(1)} y1="12" x2={last.x.toFixed(1)} y2="152" stroke="rgba(233,233,237,.16)" strokeDasharray="3 4" />
              {branches.map((b, i) => (
                <path key={i} d={b.path} stroke={b.color} strokeWidth={b.w} strokeDasharray="4 4" strokeLinecap="round" fill="none" opacity={b.op} />
              ))}
              {hov && (
                <g>
                  <line x1={hov.x.toFixed(1)} y1="12" x2={hov.x.toFixed(1)} y2="152" stroke="rgba(232,181,92,.6)" />
                  <circle cx={hov.x.toFixed(1)} cy={hov.yy.toFixed(1)} r={4.5} fill="#161826" stroke="#e8b55c" strokeWidth={2} />
                </g>
              )}
              {pts.map((p) => (
                <rect
                  key={p.i}
                  x={(p.x - step / 2).toFixed(1)}
                  y="12"
                  width={step.toFixed(1)}
                  height="140"
                  fill="transparent"
                  onMouseEnter={() => setHoverIdx(p.i)}
                  onClick={() => setHoverIdx(p.i)}
                  style={{ cursor: "crosshair" }}
                />
              ))}
            </svg>
            <div style={{ position: "absolute", left: 0, top: y(25) - 7.5, width: 24, textAlign: "right", fontSize: 9, color: "#6c7089" }}>25</div>
            <div style={{ position: "absolute", left: 0, top: y(50) - 7.5, width: 24, textAlign: "right", fontSize: 9, color: "#6c7089" }}>50</div>
            <div style={{ position: "absolute", left: 0, top: y(75) - 7.5, width: 24, textAlign: "right", fontSize: 9, color: "#6c7089" }}>75</div>
            <div style={{ position: "absolute", left: 28, top: 160, width: 292, display: "flex", justifyContent: "space-between", fontSize: 9, color: "#6c7089", pointerEvents: "none" }}>
              <span>Sep</span>
              <span>Mar</span>
              <span>Sep</span>
              <span>Mar</span>
              <span>Aug</span>
            </div>
            {branches.map((b, i) => (
              <div key={i} style={{ position: "absolute", left: b.left, top: b.top, transform: "translate(-50%,-50%)", fontSize: b.fs, lineHeight: 1, opacity: b.op, pointerEvents: "none" }}>
                {b.emoji}
              </div>
            ))}
          </div>
        </div>

        <div style={{ fontSize: 10, letterSpacing: ".12em", textTransform: "uppercase", color: "var(--color-neutral-500)", margin: "20px 2px 8px" }}>Next two months · tap one</div>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {sc.map((s, i) => {
            const on = i === scenario;
            return (
              <div
                key={s.label}
                onClick={() => setScenario(i)}
                style={{ padding: "13px 14px", borderRadius: 13, background: on ? "rgba(232,181,92,.12)" : "#232532", boxShadow: `inset 0 0 0 1px ${on ? "rgba(232,181,92,.5)" : "rgba(233,233,237,.08)"}`, cursor: "pointer" }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <span style={{ fontSize: 21, flex: "none" }}>{s.emoji}</span>
                  <span style={{ flex: 1, fontSize: 14.5, fontFamily: "var(--font-heading)" }}>{s.label}</span>
                  <span style={{ fontFamily: "var(--font-heading)", fontSize: 19, color: on ? GOLD : "#9199b5" }}>{s.prob}%</span>
                </div>
                <p style={{ margin: "8px 0 0 31px", fontSize: 12.5, lineHeight: 1.55, color: "var(--color-neutral-400)" }}>{s.body}</p>
              </div>
            );
          })}
        </div>

        <div style={{ fontSize: 10, letterSpacing: ".12em", textTransform: "uppercase", color: "var(--color-neutral-500)", margin: "20px 2px 8px" }}>The five checks</div>
        <div style={{ display: "flex", flexDirection: "column", gap: 11 }}>
          {factors.map((f) => (
            <div key={f.label}>
              <div style={{ display: "flex", alignItems: "baseline", gap: 8, fontSize: 13 }}>
                <span style={{ flex: "none", fontSize: 15 }}>{f.emoji}</span>
                <span style={{ flex: 1 }}>{f.label}</span>
                <span style={{ color: "var(--color-neutral-400)", fontSize: 12.5 }}>{f.value}</span>
              </div>
              <div style={{ height: 6, borderRadius: 3, background: "#31344a", marginTop: 5, overflow: "hidden" }}>
                <div style={{ height: 6, borderRadius: 3, width: f.barW, background: f.color }} />
              </div>
              <div style={{ fontSize: 11.5, color: "var(--color-neutral-600)", marginTop: 4 }}>{f.plain}</div>
            </div>
          ))}
        </div>

        {dr.kind === "theme" && (
          <div style={{ marginTop: 20, padding: 13, borderRadius: 12, background: "#1e2130", boxShadow: "inset 0 0 0 1px rgba(233,233,237,.07)" }}>
            <div style={{ fontSize: 10, letterSpacing: ".12em", textTransform: "uppercase", color: "var(--color-neutral-500)" }}>{dr.mark} Built from these funds</div>
            <div style={{ fontFamily: "ui-monospace,Menlo,monospace", fontSize: 14, color: "#f0d9a8", marginTop: 7, letterSpacing: ".02em" }}>{dr.etfs}</div>
            <div style={{ fontSize: 12, lineHeight: 1.55, color: "var(--color-neutral-400)", marginTop: 7 }}>
              Those letters are just nicknames the exchange gives each fund — type one into a broker and you get the whole basket.{" "}
              {dr.etfs.indexOf("·") < 0 ? "Only one fund tracks this cleanly, so the theme is that fund." : "We average them so no single provider’s list decides the score."}
            </div>
            <div style={{ height: 1, background: "rgba(233,233,237,.08)", margin: "12px 0" }} />
            <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
              <span style={{ fontSize: 15, flex: "none" }}>💸</span>
              <span style={{ flex: 1, fontSize: 12.5, color: "var(--color-neutral-300)" }}>Yearly fee</span>
              <span style={{ fontFamily: "var(--font-heading)", fontSize: 15, color: "#f0d9a8" }}>{fee!.toFixed(2)}% a year</span>
            </div>
            <div style={{ fontSize: 11.5, lineHeight: 1.55, color: "var(--color-neutral-600)", marginTop: 6 }}>
              About {Math.round(fee! * 10)} a year for every 1,000 you hold, taken out of the price daily — you never see a bill.
            </div>
            <div style={{ fontSize: 12, color: "var(--color-neutral-400)", marginTop: 6 }}>
              {fee! < 0.15 ? "✅ As cheap as investing gets." : fee! < 0.4 ? "👍 Normal for a fund this specific." : fee! < 0.6 ? "🤔 Pricey. Common for themes, but it compounds." : "⚠️ Expensive. Over ten years the fee alone eats a noticeable slice."}
            </div>
            <div style={{ fontSize: 11, color: "var(--color-neutral-600)", marginTop: 9 }}>
              {dr.etfs.indexOf("·") < 0 ? "Only one ETF tracks this cleanly, so the theme is that fund." : "Equal-weight average, daily closes, dividends included."}
            </div>
          </div>
        )}

        <div style={{ marginTop: 11, borderRadius: 12, background: "#1e2130", boxShadow: "inset 0 0 0 1px rgba(233,233,237,.07)", overflow: "hidden" }}>
          <div onClick={() => setHoldOpen((v) => !v)} style={{ display: "flex", alignItems: "center", gap: 10, padding: 13, cursor: "pointer" }}>
            <span style={{ fontSize: 17, flex: "none" }}>🏢</span>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 13.5 }}>Top 5 holdings</div>
              <div style={{ fontSize: 11, color: "var(--color-neutral-600)" }}>
                {dr.kind === "theme" ? `The biggest companies inside ${dr.etfs.replace(/ · /g, " + ")}` : `The biggest companies in the ${dr.proxy}`}
              </div>
            </div>
            <span style={{ fontSize: 13, color: "#e8b55c", flex: "none", transform: holdOpen ? "rotate(180deg)" : "rotate(0deg)", transition: "transform .18s" }}>▾</span>
          </div>
          {holdOpen && (
            <div style={{ padding: "0 13px 13px", animation: "mwFade .18s ease both" }}>
              <div style={{ display: "flex", flexDirection: "column", gap: 9 }}>
                {holdings.map((h) => (
                  <div key={h.name}>
                    <div style={{ display: "flex", alignItems: "baseline", gap: 8, fontSize: 12.5 }}>
                      <span style={{ flex: 1, color: "var(--color-neutral-300)" }}>{h.name}</span>
                      <span style={{ color: "var(--color-neutral-500)", fontSize: 11.5 }}>{h.pct}</span>
                    </div>
                    <div style={{ height: 4, borderRadius: 2, background: "#31344a", marginTop: 4, overflow: "hidden" }}>
                      <div style={{ height: 4, borderRadius: 2, width: h.barW, background: dr.color }} />
                    </div>
                  </div>
                ))}
              </div>
              <div style={{ fontSize: 11, lineHeight: 1.5, color: "var(--color-neutral-600)", marginTop: 11 }}>
                {dr.kind === "theme"
                  ? "Percentages are the share of the blended theme, as of 1 August. A theme with one huge holding moves with that one company — check this before you read the score as a whole market."
                  : "Share of the index as of 1 August."}
              </div>
            </div>
          )}
        </div>

        {siblings.length > 0 && (
          <div>
            <div style={{ fontSize: 10, letterSpacing: ".12em", textTransform: "uppercase", color: "var(--color-neutral-500)", margin: "20px 2px 8px" }}>Others in {dr.famName}</div>
            <div style={{ display: "flex", gap: 7, overflowX: "auto", paddingBottom: 4 }}>
              {siblings.map((s) => (
                <div
                  key={s.key}
                  onClick={() => openTheme(s.key)}
                  style={{ flex: "none", width: 108, padding: 11, borderRadius: 12, background: s.bg, boxShadow: `inset 0 0 0 1px ${s.edge}`, cursor: "pointer" }}
                >
                  <div style={{ fontSize: 19 }}>{s.emoji}</div>
                  <div style={{ fontSize: 11.5, lineHeight: 1.3, color: "var(--color-neutral-300)", marginTop: 5, height: 30, overflow: "hidden" }}>{s.name}</div>
                  <div style={{ fontFamily: "var(--font-heading)", fontSize: 17, color: s.color, marginTop: 3 }}>{s.temp}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        <p style={{ margin: "18px 2px 0", fontSize: 10.5, lineHeight: 1.55, color: "var(--color-neutral-600)" }}>Illustrative data. A high score is not a signal to buy — sometimes it means you are late.</p>
      </ScreenScroll>
    </div>
  );
}
