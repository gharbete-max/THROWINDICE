import { store } from "../data";
import { useOverlay } from "../lib/overlay";
import ScreenScroll, { Kicker } from "../components/ScreenScroll";
import Dial from "../components/Dial";

export default function Today() {
  const { openFamily, openTheme } = useOverlay();

  return (
    <ScreenScroll>
      <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between" }}>
        <div>
          <div style={{ fontSize: 10, letterSpacing: ".14em", textTransform: "uppercase", color: "#e8b55c" }}>Monthly report</div>
          <div style={{ fontFamily: "var(--font-heading)", fontWeight: 500, fontSize: 26, letterSpacing: "-.02em", lineHeight: 1.1, marginTop: 3 }}>
            {monthLabel(store.asOf)}
          </div>
        </div>
        <div style={{ fontSize: 11, color: "var(--color-neutral-500)", textAlign: "right", lineHeight: 1.35 }}>
          next report
          <br />
          {store.nextReport}
        </div>
      </div>

      <Dial g={store.global} line={store.global.line} />

      <Kicker>The month in plain words</Kicker>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {store.headlines.map((f) => (
          <div
            key={f.key}
            onClick={() => openFamily(f.key)}
            style={{ display: "flex", gap: 12, alignItems: "flex-start", padding: "12px 13px", borderRadius: 13, background: f.bg, boxShadow: `inset 0 0 0 1px ${f.edge}`, cursor: "pointer" }}
          >
            <span style={{ fontSize: 23, lineHeight: 1.1, flex: "none" }}>{f.emoji}</span>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 14.5, fontFamily: "var(--font-heading)", fontWeight: 500 }}>{f.head}</div>
              <div style={{ fontSize: 12.5, lineHeight: 1.5, color: "var(--color-neutral-400)", marginTop: 2 }}>{f.intro}</div>
            </div>
            <span style={{ fontSize: 15, color: "var(--color-neutral-600)", flex: "none", paddingTop: 2 }}>›</span>
          </div>
        ))}
      </div>

      <Kicker>The six groups · tap to open</Kicker>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
        {store.families.map((f) => (
          <div
            key={f.key}
            onClick={() => openFamily(f.key)}
            style={{ padding: "12px 13px", borderRadius: 13, background: f.bg, boxShadow: `inset 0 0 0 1px ${f.edge}`, cursor: "pointer" }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
              <span style={{ fontSize: 18 }}>{f.emoji}</span>
              <span style={{ fontSize: 12.5, color: "var(--color-neutral-300)", flex: 1, lineHeight: 1.25 }}>{f.name}</span>
            </div>
            <div style={{ display: "flex", alignItems: "baseline", gap: 6, marginTop: 7 }}>
              <span style={{ fontFamily: "var(--font-heading)", fontSize: 25, letterSpacing: "-.02em", color: f.color }}>{f.temp}</span>
              <span style={{ fontSize: 11, color: f.deltaColor }}>{f.delta}</span>
              <span style={{ fontSize: 15, marginLeft: "auto" }}>{f.wxEmoji}</span>
            </div>
            <div style={{ fontSize: 11, color: "var(--color-neutral-500)", marginTop: 1 }}>{f.spread}</div>
          </div>
        ))}
      </div>

      <Kicker>Around the world</Kicker>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
        {store.macro.map((m) => (
          <div key={m.name} style={{ padding: "12px 13px", borderRadius: 13, background: m.bg, boxShadow: `inset 0 0 0 1px ${m.edge}` }}>
            <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
              <span style={{ fontSize: 17 }}>{m.emoji}</span>
              <span style={{ fontSize: 12.5, color: "var(--color-neutral-300)", flex: 1 }}>{m.name}</span>
            </div>
            <div style={{ display: "flex", alignItems: "baseline", gap: 6, marginTop: 6 }}>
              <span style={{ fontFamily: "var(--font-heading)", fontSize: 25, letterSpacing: "-.02em", color: m.color }}>{m.temp}</span>
              <span style={{ fontSize: 11, color: m.deltaColor }}>{m.delta}</span>
            </div>
            <div style={{ fontSize: 11, color: "var(--color-neutral-500)", marginTop: 1 }}>{m.condition}</div>
          </div>
        ))}
      </div>

      <Kicker style={{ marginBottom: 6 }}>Biggest changes since last month</Kicker>
      <div style={{ display: "flex", flexDirection: "column" }}>
        {store.movers.map((m) => (
          <div
            key={m.key}
            onClick={() => openTheme(m.key)}
            style={{ display: "flex", alignItems: "center", gap: 10, padding: "9px 4px", cursor: "pointer", borderBottom: "1px solid rgba(233,233,237,.07)" }}
          >
            <span style={{ fontSize: 17, flex: "none" }}>{m.emoji}</span>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 13.5 }}>{m.name}</div>
              <div style={{ fontSize: 10.5, color: "var(--color-neutral-600)" }}>{m.famName ?? "Country index"}</div>
            </div>
            <span style={{ fontSize: 13, color: m.deltaColor, minWidth: 44, textAlign: "right" }}>{m.delta}</span>
            <span style={{ fontFamily: "var(--font-heading)", fontSize: 14, color: m.color, minWidth: 32, textAlign: "right" }}>{m.temp}</span>
          </div>
        ))}
      </div>

      <p style={{ margin: "16px 4px 0", fontSize: 10.5, lineHeight: 1.55, color: "var(--color-neutral-600)" }}>
        Every score mixes five simple checks — is it going up, is it bumpy, is it broad, is it near its high, is it busy — into one number from 0 to 100. Group scores are the average of their themes. Not advice.
      </p>
    </ScreenScroll>
  );
}

function monthLabel(asOf: string) {
  const [y, m] = asOf.split("-").map(Number);
  return new Date(Date.UTC(y, m - 1, 1)).toLocaleDateString("en-US", { month: "long", year: "numeric", timeZone: "UTC" });
}
