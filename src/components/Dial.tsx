import type { GlobalSummary } from "../data/built";

/** The front-page composite gauge — a 180° arc with a short outer-band
 * needle (radius 86→112, no hub) so it can never cross the centred readout. */
export default function Dial({ g, line }: { g: GlobalSummary; line: string }) {
  return (
    <div
      style={{
        marginTop: 14,
        padding: "16px 14px 12px",
        borderRadius: 16,
        background: "linear-gradient(180deg,#282c47,#212433)",
        boxShadow: "var(--shadow-sm)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
      }}
    >
      <div style={{ position: "relative", width: 310, height: 194 }}>
        <svg width="310" height="182" viewBox="0 0 310 182" fill="none" style={{ display: "block" }}>
          <defs>
            <linearGradient id="mwArc3" x1="30" y1="0" x2="280" y2="0" gradientUnits="userSpaceOnUse">
              <stop stopColor="#4a4fa2" />
              <stop offset=".28" stopColor="#5573c4" />
              <stop offset=".52" stopColor="#9199b5" />
              <stop offset=".76" stopColor="#c0a8f0" />
              <stop offset="1" stopColor="#e8b55c" />
            </linearGradient>
          </defs>
          <path d="M30 156a125 125 0 0 1 250 0" stroke="#31344a" strokeWidth={13} strokeLinecap="round" />
          <path d="M30 156a125 125 0 0 1 250 0" stroke="url(#mwArc3)" strokeWidth={13} strokeLinecap="round" strokeDasharray={g.arcDash} />
          <line x1={g.needle.x1} y1={g.needle.y1} x2={g.needle.x2} y2={g.needle.y2} stroke="#e9e9ed" strokeWidth={3} strokeLinecap="round" />
        </svg>
        <div style={{ position: "absolute", left: 16, top: 170, fontSize: 16, lineHeight: 1 }}>⛈️</div>
        <div style={{ position: "absolute", right: 16, top: 170, fontSize: 16, lineHeight: 1 }}>☀️</div>
        <div style={{ position: "absolute", left: 0, top: 96, width: 310, display: "flex", alignItems: "center", justifyContent: "center", gap: 9 }}>
          <span style={{ fontSize: 27, lineHeight: 1 }}>{g.emoji}</span>
          <span style={{ fontFamily: "var(--font-heading)", fontWeight: 500, fontSize: 44, lineHeight: 1, letterSpacing: "-.03em" }}>{g.temp}</span>
        </div>
        <div style={{ position: "absolute", left: 0, top: 146, width: 310, textAlign: "center", fontSize: 12.5, letterSpacing: ".04em", color: g.color }}>{g.condition}</div>
      </div>
      <p style={{ margin: "2px 4px 0", fontSize: 13.5, lineHeight: 1.6, color: "var(--color-neutral-300)", textAlign: "center", textWrap: "pretty" as any }}>{line}</p>
    </div>
  );
}
