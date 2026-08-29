import { store } from "../data";
import { useOverlay } from "../lib/overlay";
import ScreenScroll from "../components/ScreenScroll";
import MeterBar from "../components/MeterBar";

export default function GroupDetail({ famKey }: { famKey: string }) {
  const { closeFamily, openTheme } = useOverlay();
  const fam = store.famByKey[famKey];
  if (!fam) return null;

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        background: "linear-gradient(180deg,#20243a,#161826 45%)",
        zIndex: 25,
        animation: "mwSlide .22s ease both",
      }}
    >
      <ScreenScroll>
        <div onClick={closeFamily} style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 13, color: "#e8b55c", cursor: "pointer", padding: "6px 2px", marginBottom: 6 }}>
          <span style={{ fontSize: 15 }}>←</span>
          <span>Back</span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <span style={{ fontSize: 44, lineHeight: 1, flex: "none" }}>{fam.emoji}</span>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontFamily: "var(--font-heading)", fontWeight: 500, fontSize: 23, letterSpacing: "-.02em", lineHeight: 1.15 }}>{fam.name}</div>
            <div style={{ fontSize: 11.5, color: "var(--color-neutral-500)", marginTop: 2 }}>{fam.count}</div>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "baseline", gap: 10, marginTop: 12 }}>
          <span style={{ fontFamily: "var(--font-heading)", fontSize: 50, lineHeight: 1, letterSpacing: "-.035em", color: fam.color }}>{fam.temp}</span>
          <span style={{ fontSize: 15, color: fam.deltaColor }}>{fam.delta}</span>
          <span style={{ fontSize: 15, color: "var(--color-neutral-300)", marginLeft: "auto" }}>
            {fam.condition} {fam.wxEmoji}
          </span>
        </div>
        <MeterBar markerX={fam.markerX} />

        <p style={{ margin: "14px 0 0", fontSize: 14, lineHeight: 1.6, color: "var(--color-neutral-200)" }}>{fam.body}</p>

        <div style={{ marginTop: 14, padding: "12px 13px", borderRadius: 12, background: "rgba(232,181,92,.08)", boxShadow: "inset 0 0 0 1px rgba(232,181,92,.3)" }}>
          <div style={{ fontSize: 12.5, lineHeight: 1.55, color: "#f0d9a8" }}>
            🔎 The average hides the split: <strong>{fam.best.name.toLowerCase()}</strong> is at {fam.best.temp}, <strong>{fam.worst.name.toLowerCase()}</strong> at {fam.worst.temp}.
          </div>
        </div>

        <div style={{ marginTop: 8, display: "flex", alignItems: "baseline", gap: 9, padding: "11px 13px", borderRadius: 12, background: "#1e2130", boxShadow: "inset 0 0 0 1px rgba(233,233,237,.07)" }}>
          <span style={{ fontSize: 15, flex: "none" }}>💸</span>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 12.5, color: "var(--color-neutral-300)" }}>
              Typical fee in this group · <span style={{ color: "#f0d9a8" }}>{fam.feeLabel}</span>
            </div>
            <div style={{ fontSize: 11, color: "var(--color-neutral-600)", marginTop: 2 }}>Roughly {fam.feeCost}. What each fund charges is on its own page.</div>
          </div>
        </div>

        <div style={{ fontSize: 10, letterSpacing: ".12em", textTransform: "uppercase", color: "var(--color-neutral-500)", margin: "20px 2px 8px" }}>Inside this group · warmest first</div>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {fam.themes.map((t) => (
            <div
              key={t.key}
              onClick={() => openTheme(t.key)}
              style={{ display: "flex", alignItems: "center", gap: 11, padding: "12px 13px", borderRadius: 13, background: t.bg, boxShadow: `inset 0 0 0 1px ${t.edge}`, cursor: "pointer" }}
            >
              <span style={{ fontSize: 22, flex: "none" }}>{t.emoji}</span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 14, fontFamily: "var(--font-heading)", fontWeight: 500 }}>
                  {t.name} {t.mark}
                </div>
                <div style={{ fontSize: 11, color: "var(--color-neutral-500)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                  {t.proxy} · {t.etfs}
                </div>
              </div>
              <svg width="46" height="22" viewBox="0 0 56 26" fill="none" style={{ flex: "none" }}>
                <path d={t.spark} stroke={t.color} strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              <div style={{ flex: "none", textAlign: "right", minWidth: 44 }}>
                <div style={{ fontFamily: "var(--font-heading)", fontSize: 19, lineHeight: 1.1, color: t.color }}>{t.temp}</div>
                <div style={{ fontSize: 10.5, color: t.deltaColor }}>{t.delta}</div>
              </div>
            </div>
          ))}
        </div>
        <p style={{ margin: "16px 2px 0", fontSize: 10.5, lineHeight: 1.55, color: "var(--color-neutral-600)" }}>Group score is the equal-weight average of the themes above. Illustrative data, not advice.</p>
      </ScreenScroll>
    </div>
  );
}
