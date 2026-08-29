import { useState } from "react";
import { store } from "../data";
import { METHOD } from "../lib/weather";
import ScreenScroll from "../components/ScreenScroll";

export default function Method() {
  const [learn, setLearn] = useState<string | null>("etf");

  return (
    <ScreenScroll>
      <div style={{ fontSize: 10, letterSpacing: ".14em", textTransform: "uppercase", color: "#e8b55c" }}>No jargon</div>
      <div style={{ fontFamily: "var(--font-heading)", fontWeight: 500, fontSize: 26, letterSpacing: "-.02em", margin: "3px 0 12px" }}>How it works</div>

      <div style={{ fontSize: 10, letterSpacing: ".12em", textTransform: "uppercase", color: "var(--color-neutral-500)", margin: "0 2px 9px" }}>Ten things worth knowing · tap one</div>
      <div style={{ display: "flex", flexDirection: "column", gap: 7 }}>
        {store.learn.map((l) => {
          const on = learn === l.key;
          return (
            <div key={l.key} style={{ borderRadius: 12, background: on ? "rgba(232,181,92,.09)" : "#232532", boxShadow: `inset 0 0 0 1px ${on ? "rgba(232,181,92,.42)" : "rgba(233,233,237,.08)"}`, overflow: "hidden" }}>
              <div onClick={() => setLearn(on ? null : l.key)} style={{ display: "flex", alignItems: "center", gap: 11, padding: "12px 13px", cursor: "pointer" }}>
                <span style={{ fontSize: 19, flex: "none" }}>{l.emoji}</span>
                <span style={{ flex: 1, fontSize: 13.5, lineHeight: 1.35, color: on ? "#f0d9a8" : "#e9e9ed" }}>{l.q}</span>
                <span style={{ fontSize: 13, color: "#e8b55c", flex: "none", transform: on ? "rotate(180deg)" : "rotate(0deg)", transition: "transform .18s" }}>▾</span>
              </div>
              {on && (
                <div style={{ padding: "0 13px 14px 43px", animation: "mwFade .18s ease both" }}>
                  <p style={{ margin: 0, fontSize: 13, lineHeight: 1.6, color: "var(--color-neutral-300)" }}>{l.a}</p>
                  <p style={{ margin: "9px 0 0", fontSize: 12.5, lineHeight: 1.55, color: "var(--color-neutral-500)" }}>{l.b}</p>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div style={{ padding: 15, borderRadius: 13, background: "#232532", boxShadow: "var(--shadow-sm)", marginTop: 14 }}>
        <div style={{ fontFamily: "var(--font-heading)", fontSize: 16 }}>💸 What each group costs</div>
        <p style={{ margin: "6px 0 13px", fontSize: 12.5, lineHeight: 1.55, color: "var(--color-neutral-400)" }}>Average yearly fee of the funds behind each group, and what that is in money on 1,000 invested.</p>
        <div style={{ display: "flex", flexDirection: "column", gap: 11 }}>
          {store.feeTable.map((f) => (
            <div key={f.name}>
              <div style={{ display: "flex", alignItems: "baseline", gap: 8, fontSize: 12.5 }}>
                <span style={{ flex: "none", fontSize: 15 }}>{f.emoji}</span>
                <span style={{ flex: 1, color: "var(--color-neutral-300)" }}>{f.name}</span>
                <span style={{ fontFamily: "var(--font-heading)", fontSize: 13, color: f.color }}>{f.fee}</span>
                <span style={{ fontSize: 11, color: "var(--color-neutral-600)", minWidth: 58, textAlign: "right" }}>{f.cost}</span>
              </div>
              <div style={{ height: 4, borderRadius: 2, background: "#31344a", marginTop: 5, overflow: "hidden" }}>
                <div style={{ height: 4, borderRadius: 2, width: f.barW, background: f.color }} />
              </div>
            </div>
          ))}
        </div>
        <p style={{ margin: "13px 0 0", fontSize: 11.5, lineHeight: 1.55, color: "var(--color-neutral-600)" }}>
          For scale: a plain fund holding the whole US market charges about 0.03%, or 30 cents per 1,000 a year. Energy and everyday goods look cheap here because broad sector funds exist for them; quantum and lithium are expensive because only niche funds do.
        </p>
      </div>

      <div style={{ padding: 15, borderRadius: 13, background: "#232532", boxShadow: "var(--shadow-sm)", marginTop: 11 }}>
        <div style={{ fontFamily: "var(--font-heading)", fontSize: 16 }}>The score, 0 to 100</div>
        <p style={{ margin: "6px 0 12px", fontSize: 13, lineHeight: 1.6, color: "var(--color-neutral-400)" }}>Five simple checks every month, each scored against that market's own history, then averaged. Equal weight, so nothing is hidden.</p>
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {METHOD.map((m) => (
            <div key={m.title} style={{ display: "flex", gap: 11, alignItems: "flex-start" }}>
              <span style={{ fontSize: 18, flex: "none", width: 22 }}>{m.emoji}</span>
              <div>
                <div style={{ fontSize: 13.5 }}>{m.title}</div>
                <div style={{ fontSize: 12, lineHeight: 1.5, color: "var(--color-neutral-500)" }}>{m.body}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ padding: 15, borderRadius: 13, background: "#232532", boxShadow: "var(--shadow-sm)", marginTop: 11 }}>
        <div style={{ fontFamily: "var(--font-heading)", fontSize: 16 }}>Groups and themes</div>
        <p style={{ margin: "6px 0 0", fontSize: 13, lineHeight: 1.6, color: "var(--color-neutral-400)" }}>
          Themes inside a group usually move together, so the group average is a fair headline — but it hides the split. Energy is the clearest example this month: nuclear and oil companies are up while solar and wind keep falling. The group reads calm; the inside does not. Always open the group.
        </p>
      </div>

      <div style={{ padding: 15, borderRadius: 13, background: "#232532", boxShadow: "var(--shadow-sm)", marginTop: 11 }}>
        <div style={{ fontFamily: "var(--font-heading)", fontSize: 16 }}>The forecast 🔮</div>
        <p style={{ margin: "6px 0 10px", fontSize: 13, lineHeight: 1.6, color: "var(--color-neutral-400)" }}>We watch three things in the monthly numbers: where the level is, which way it has been drifting, and the shape the calendar year usually takes. Then we carry all three forward two months (Holt–Winters, if you want the name).</p>
        <svg width="300" height="100" viewBox="0 0 300 100" fill="none" style={{ margin: "2px 0 8px" }}>
          <path d="M4 72 C38 64 58 76 82 58 C106 42 126 56 150 44 C172 33 190 42 212 30" stroke="#9199b5" strokeWidth={1.9} strokeLinecap="round" />
          <path d="M212 30 C232 22 246 28 268 16" stroke="#e8b55c" strokeWidth={1.9} strokeDasharray="4 4" strokeLinecap="round" />
          <path d="M212 30 C234 30 248 42 270 44" stroke="#c0a8f0" strokeWidth={1.6} strokeDasharray="4 4" strokeLinecap="round" />
          <path d="M212 30 C232 38 246 60 270 72" stroke="#5573c4" strokeWidth={1.6} strokeDasharray="4 4" strokeLinecap="round" />
          <circle cx="212" cy="30" r={3.6} fill="#e9e9ed" />
          <text x="276" y="20" fontSize="12">☀️</text>
          <text x="276" y="48" fontSize="12">☁️</text>
          <text x="276" y="76" fontSize="12">🌧️</text>
          <text x="206" y="94" fill="#75798c" fontSize="9" fontFamily="Inter" textAnchor="end">what happened</text>
        </svg>
        <p style={{ margin: 0, fontSize: 13, lineHeight: 1.6, color: "var(--color-neutral-400)" }}>We always show three possible months with a percentage each, never one number. Over the last three years the direction was right 63% of the time — good for a forecast, not a promise.</p>
      </div>

      <div style={{ padding: 15, borderRadius: 13, background: "#232532", boxShadow: "var(--shadow-sm)", marginTop: 11 }}>
        <div style={{ fontFamily: "var(--font-heading)", fontSize: 16 }}>Where the numbers come from *</div>
        <p style={{ margin: "6px 0 12px", fontSize: 12.5, lineHeight: 1.55, color: "var(--color-neutral-500)" }}>Country indices use the index itself. Every theme is the equal-weight average of one to three ETFs. No commodity spot prices anywhere — gold is gold <em>miners</em>, oil is oil <em>companies</em>, so everything on the board is comparable.</p>
        {store.families.map((F) => (
          <div key={F.key} style={{ marginBottom: 13 }}>
            <div style={{ fontSize: 10, letterSpacing: ".1em", textTransform: "uppercase", color: "#e8b55c", marginBottom: 6 }}>
              {F.emoji} {F.name}
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              {store.themes
                .filter((t) => t.famKey === F.key)
                .map((s) => (
                  <div key={s.key} style={{ display: "flex", gap: 9, fontSize: 12.5, alignItems: "baseline" }}>
                    <span style={{ color: "var(--color-neutral-600)", flex: "none", width: 22 }}>{s.mark}</span>
                    <span style={{ flex: 1, color: "var(--color-neutral-300)" }}>
                      {s.emoji} {s.name}
                    </span>
                    <span style={{ fontFamily: "ui-monospace,Menlo,monospace", fontSize: 11, color: "var(--color-neutral-500)", textAlign: "right" }}>{s.etfs}</span>
                  </div>
                ))}
            </div>
          </div>
        ))}
        <p style={{ margin: "4px 0 0", fontSize: 11, lineHeight: 1.55, color: "var(--color-neutral-600)" }}>Prices from daily closes, in local currency, dividends included. All figures in this prototype are illustrative. Nothing here is investment advice, and a high score is not a reason to buy.</p>
      </div>
    </ScreenScroll>
  );
}
