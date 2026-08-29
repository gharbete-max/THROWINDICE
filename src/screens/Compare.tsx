import { useMemo, useState } from "react";
import { store } from "../data";
import { useOverlay } from "../lib/overlay";
import ScreenScroll from "../components/ScreenScroll";

const GOLD = "#e8b55c";
const X_MIN = -9, X_MAX = 13, Y_MIN = 10, Y_MAX = 27;
const sX = (v: number) => 46 + ((v - X_MIN) / (X_MAX - X_MIN)) * 268;
const sY = (v: number) => 30 + ((v - Y_MIN) / (Y_MAX - Y_MIN)) * 210;

export default function Compare() {
  const { openTheme } = useOverlay();
  const [cmpFam, setCmpFam] = useState<string>("All");
  const [sector, setSector] = useState<string>("gld");

  const cmpList = cmpFam === "All" ? store.themes : store.famByKey[cmpFam].themes;
  const sel = store.byKey[sector] ?? store.themes[0];
  const zeroX = sX(0).toFixed(1);
  const gridY = [14, 18, 22, 26].map((v) => sY(v).toFixed(1));

  const famFilters = useMemo(
    () => [{ key: "All", label: `All ${store.themes.length}` }, ...store.families.map((f) => ({ key: f.key, label: `${f.emoji} ${f.name.split(" ")[0]}` }))],
    []
  );

  const scatterRows = cmpList.slice().sort((a, b) => b.ret - a.ret);

  return (
    <ScreenScroll>
      <div style={{ fontSize: 10, letterSpacing: ".14em", textTransform: "uppercase", color: "#e8b55c" }}>Themes · last 3 months</div>
      <div style={{ fontFamily: "var(--font-heading)", fontWeight: 500, fontSize: 26, letterSpacing: "-.02em", margin: "3px 0 4px" }}>Reward vs. bumpiness</div>
      <p style={{ fontSize: 12.5, lineHeight: 1.55, color: "var(--color-neutral-400)", margin: "0 0 10px" }}>Right = made more money. Up = calmer ride. Top right is the sweet spot. Tap an emoji.</p>

      <div style={{ display: "flex", gap: 6, overflowX: "auto", paddingBottom: 4, marginBottom: 8 }}>
        {famFilters.map((f) => {
          const active = cmpFam === f.key;
          return (
            <div
              key={f.key}
              onClick={() => setCmpFam(f.key)}
              style={{
                padding: "6px 12px",
                borderRadius: 20,
                fontSize: 12,
                whiteSpace: "nowrap",
                cursor: "pointer",
                background: active ? "rgba(232,181,92,.16)" : "#232532",
                color: active ? GOLD : "#b2b6ca",
                boxShadow: `inset 0 0 0 1px ${active ? "rgba(232,181,92,.5)" : "rgba(233,233,237,.08)"}`,
              }}
            >
              {f.label}
            </div>
          );
        })}
      </div>

      <div style={{ borderRadius: 14, background: "#1b1e2d", boxShadow: "var(--shadow-sm)", padding: "10px 8px 4px" }}>
        <div style={{ position: "relative", width: 330, height: 302 }}>
          <svg width="330" height="302" viewBox="0 0 330 302" fill="none" style={{ display: "block" }}>
            {gridY.map((y) => (
              <line key={y} x1="42" y1={y} x2="318" y2={y} stroke="rgba(233,233,237,.06)" />
            ))}
            <line x1={zeroX} y1="18" x2={zeroX} y2="250" stroke="rgba(232,181,92,.3)" strokeDasharray="3 4" />
            {cmpList.map((s) => {
              const on = s.key === sector;
              return on ? <circle key={s.key} cx={sX(s.ret).toFixed(1)} cy={sY(s.vol).toFixed(1)} r={19} fill="rgba(232,181,92,.20)" /> : null;
            })}
          </svg>
          <div style={{ position: "absolute", left: 46, top: 18, fontSize: 9.5, letterSpacing: ".08em", color: "#5fc09a" }}>CALM RIDE</div>
          <div style={{ position: "absolute", left: 46, top: 240, fontSize: 9.5, letterSpacing: ".08em", color: "#e2726b" }}>WILD RIDE</div>
          <div style={{ position: "absolute", left: 0, top: 264, width: 330, textAlign: "center", fontSize: 9.5, letterSpacing: ".08em", color: "#8d94ad" }}>LOST MONEY ← → MADE MONEY</div>
          <div style={{ position: "absolute", left: 0, top: 285, width: 330, textAlign: "center", fontSize: 8.5, color: "#595d6c" }}>glow = the one you picked</div>
          {cmpList.map((s) => {
            const on = s.key === sector;
            return (
              <div
                key={s.key}
                onClick={() => setSector(s.key)}
                style={{
                  position: "absolute",
                  left: sX(s.ret).toFixed(1) + "px",
                  top: sY(s.vol).toFixed(1) + "px",
                  transform: "translate(-50%,-50%)",
                  fontSize: on ? 26 : 18,
                  lineHeight: 1,
                  opacity: on ? 1 : 0.7,
                  cursor: "pointer",
                }}
              >
                {s.emoji}
              </div>
            );
          })}
        </div>
      </div>

      <div style={{ marginTop: 12, padding: 14, borderRadius: 13, background: sel.bg, boxShadow: `inset 0 0 0 1px ${sel.edge}` }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{ fontSize: 26 }}>{sel.emoji}</span>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontFamily: "var(--font-heading)", fontSize: 16.5 }}>
              {sel.name} {sel.mark}
            </div>
            <div style={{ fontSize: 11, color: "var(--color-neutral-500)" }}>{sel.famName} · {sel.etfs}</div>
          </div>
          <span style={{ fontFamily: "var(--font-heading)", fontSize: 24, color: sel.color }}>{sel.temp}</span>
        </div>
        <div style={{ display: "flex", gap: 14, marginTop: 13 }}>
          <div>
            <div style={{ fontSize: 9.5, letterSpacing: ".1em", textTransform: "uppercase", color: "var(--color-neutral-600)" }}>3 months</div>
            <div style={{ fontFamily: "var(--font-heading)", fontSize: 18, color: sel.retColor }}>{sel.retLabel}</div>
          </div>
          <div>
            <div style={{ fontSize: 9.5, letterSpacing: ".1em", textTransform: "uppercase", color: "var(--color-neutral-600)" }}>Bumpiness</div>
            <div style={{ fontFamily: "var(--font-heading)", fontSize: 18 }}>{sel.volLabel}</div>
          </div>
          <div>
            <div style={{ fontSize: 9.5, letterSpacing: ".1em", textTransform: "uppercase", color: "var(--color-neutral-600)" }}>Off its high</div>
            <div style={{ fontFamily: "var(--font-heading)", fontSize: 18 }}>{sel.highLabel}</div>
          </div>
        </div>
        <p style={{ margin: "11px 0 0", fontSize: 13, lineHeight: 1.55, color: "var(--color-neutral-300)" }}>{sel.line}</p>
        <div onClick={() => openTheme(sel.key)} style={{ marginTop: 12, fontSize: 12.5, color: "#e8b55c", cursor: "pointer" }}>
          Open full report →
        </div>
      </div>

      {sel.nearHigh && (
        <div style={{ display: "flex", gap: 9, marginTop: 10, padding: 12, borderRadius: 12, background: "rgba(232,181,92,.10)", boxShadow: "inset 0 0 0 1px rgba(232,181,92,.4)" }}>
          <span style={{ fontSize: 17, flex: "none" }}>⚠️</span>
          <p style={{ margin: 0, fontSize: 12, lineHeight: 1.55, color: "#f0d9a8" }}>
            This one is sitting right at its highest price of the year. Doing best lately is <strong>not</strong> the same as being the best thing to buy — you may be buying a peak. Not advice.
          </p>
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", marginTop: 14 }}>
        {scatterRows.map((s) => (
          <div
            key={s.key}
            onClick={() => setSector(s.key)}
            style={{ display: "flex", alignItems: "center", gap: 10, padding: "9px 4px", cursor: "pointer", borderBottom: "1px solid rgba(233,233,237,.07)" }}
          >
            <span style={{ fontSize: 16, flex: "none" }}>{s.emoji}</span>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 13, color: s.key === sector ? "#e9e9ed" : "#cfd3e5" }}>
                {s.name} {s.mark}
              </div>
              <div style={{ fontSize: 10, color: "var(--color-neutral-600)" }}>{s.famName}</div>
            </div>
            <span style={{ fontSize: 12.5, color: s.retColor, minWidth: 52, textAlign: "right" }}>{s.retLabel}</span>
            <span style={{ fontSize: 11, color: "var(--color-neutral-600)", minWidth: 40, textAlign: "right" }}>{s.volLabel}</span>
          </div>
        ))}
      </div>
      <p style={{ margin: "12px 4px 0", fontSize: 10.5, lineHeight: 1.6, color: "var(--color-neutral-600)" }}>Each theme is the equal-weight average of the ETFs marked by its number. Full list on the Method tab.</p>
    </ScreenScroll>
  );
}
