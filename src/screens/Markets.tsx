import { useMemo, useState } from "react";
import { store } from "../data";
import { useOverlay } from "../lib/overlay";
import ScreenScroll, { Kicker } from "../components/ScreenScroll";
import Sparkline from "../components/Sparkline";

const GOLD = "#e8b55c";
type Filter = "All" | "Themes" | "Countries";

export default function Markets() {
  const { openFamily, openTheme } = useOverlay();
  const [q, setQ] = useState("");
  const [filter, setFilter] = useState<Filter>("All");

  const query = q.trim().toLowerCase();
  const browseGroups = !query && filter === "All";

  const results = useMemo(() => {
    const pool = filter === "Countries" ? store.countries : filter === "Themes" ? store.themes : store.themes.concat(store.countries);
    let list = pool;
    if (query) {
      list = pool.filter((x) => `${x.name} ${x.proxy} ${x.etfs} ${x.famName ?? ""}`.toLowerCase().includes(query));
    }
    return list.slice().sort((a, b) => b.temp - a.temp);
  }, [query, filter]);

  return (
    <ScreenScroll>
      <div style={{ fontSize: 10, letterSpacing: ".14em", textTransform: "uppercase", color: "#e8b55c" }}>{store.themeCount} themes · {store.countries.length} countries</div>
      <div style={{ fontFamily: "var(--font-heading)", fontWeight: 500, fontSize: 26, letterSpacing: "-.02em", margin: "3px 0 12px" }}>Markets</div>

      <div style={{ position: "relative" }}>
        <span style={{ position: "absolute", left: 11, top: "50%", transform: "translateY(-50%)", fontSize: 14, opacity: 0.6 }}>🔍</span>
        <input
          className="mwq"
          type="text"
          placeholder='Search "quantum", "miners", "Germany"…'
          value={q}
          onChange={(e) => setQ(e.target.value)}
          style={{
            width: "100%",
            paddingLeft: 34,
            minHeight: 42,
            borderRadius: 12,
            fontSize: 14,
            background: "var(--color-surface)",
            border: "1px solid var(--color-divider)",
            color: "var(--color-text)",
          }}
        />
      </div>

      <div style={{ display: "flex", gap: 7, marginTop: 10 }}>
        {(["All", "Themes", "Countries"] as Filter[]).map((f) => {
          const active = filter === f;
          return (
            <div
              key={f}
              onClick={() => setFilter(f)}
              style={{
                padding: "6px 13px",
                borderRadius: 20,
                fontSize: 12,
                cursor: "pointer",
                background: active ? "rgba(232,181,92,.16)" : "#232532",
                color: active ? GOLD : "#b2b6ca",
                boxShadow: `inset 0 0 0 1px ${active ? "rgba(232,181,92,.5)" : "rgba(233,233,237,.08)"}`,
              }}
            >
              {f}
            </div>
          );
        })}
      </div>

      {browseGroups ? (
        <div style={{ marginTop: 16, display: "flex", flexDirection: "column", gap: 9 }}>
          {store.families.map((f) => (
            <div
              key={f.key}
              onClick={() => openFamily(f.key)}
              style={{ padding: "13px 14px", borderRadius: 13, background: f.bg, boxShadow: `inset 0 0 0 1px ${f.edge}`, cursor: "pointer" }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span style={{ fontSize: 22, flex: "none" }}>{f.emoji}</span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 15, fontFamily: "var(--font-heading)", fontWeight: 500 }}>{f.name}</div>
                  <div style={{ fontSize: 11, color: "var(--color-neutral-500)" }}>{f.count}</div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontFamily: "var(--font-heading)", fontSize: 21, color: f.color, lineHeight: 1.1 }}>{f.temp}</div>
                  <div style={{ fontSize: 10.5, color: f.deltaColor }}>{f.delta}</div>
                </div>
                <span style={{ fontSize: 19, flex: "none" }}>{f.wxEmoji}</span>
              </div>
              <div style={{ display: "flex", gap: 5, marginTop: 11 }}>
                {f.themes.map((t) => (
                  <div key={t.key} style={{ flex: 1, height: 5, borderRadius: 3, background: t.color }} />
                ))}
              </div>
              <div style={{ fontSize: 11, color: "var(--color-neutral-500)", marginTop: 7 }}>{f.spread}</div>
            </div>
          ))}
          <Kicker style={{ margin: "12px 2px 2px" }}>Country indices</Kicker>
          {store.countries.map((r) => (
            <div
              key={r.key}
              onClick={() => openTheme(r.key)}
              style={{ display: "flex", alignItems: "center", gap: 11, padding: "10px 4px", cursor: "pointer", borderBottom: "1px solid rgba(233,233,237,.07)" }}
            >
              <span style={{ fontSize: 19, flex: "none" }}>{r.emoji}</span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 13.5 }}>{r.name}</div>
                <div style={{ fontSize: 10.5, color: "var(--color-neutral-600)" }}>{r.proxy}</div>
              </div>
              <Sparkline path={r.spark} color={r.color} />
              <span style={{ fontFamily: "var(--font-heading)", fontSize: 16, color: r.color, minWidth: 32, textAlign: "right" }}>{r.temp}</span>
            </div>
          ))}
        </div>
      ) : (
        <div>
          <div style={{ fontSize: 11, color: "var(--color-neutral-600)", margin: "14px 2px 6px" }}>
            {results.length} {results.length === 1 ? "match" : "matches"} · warmest first
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 7 }}>
            {results.map((r) => (
              <div
                key={r.key}
                onClick={() => openTheme(r.key)}
                style={{ display: "flex", alignItems: "center", gap: 11, padding: "11px 12px", borderRadius: 12, background: "#232532", boxShadow: `inset 0 0 0 1px ${r.edge}`, cursor: "pointer" }}
              >
                <span style={{ fontSize: 21, flex: "none" }}>{r.emoji}</span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 14, fontFamily: "var(--font-heading)", fontWeight: 500 }}>
                    {r.name}
                    {r.mark ? <span style={{ color: "var(--color-neutral-600)", fontWeight: 400 }}> {r.mark}</span> : null}
                  </div>
                  <div style={{ fontSize: 11, color: "var(--color-neutral-500)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {r.kind === "theme" ? `${r.famName} · ${r.etfs}` : `${r.proxy} · the index itself`}
                  </div>
                </div>
                <Sparkline path={r.spark} color={r.color} />
                <div style={{ flex: "none", textAlign: "right", minWidth: 44 }}>
                  <div style={{ fontFamily: "var(--font-heading)", fontSize: 19, lineHeight: 1.1, color: r.color }}>{r.temp}</div>
                  <div style={{ fontSize: 10.5, color: r.deltaColor }}>{r.delta}</div>
                </div>
              </div>
            ))}
          </div>
          {results.length === 0 && (
            <div style={{ padding: "28px 6px", textAlign: "center", color: "var(--color-neutral-500)", fontSize: 13 }}>
              🤷 Nothing matches that. Try "nuclear", "gold", "ai" or a country.
            </div>
          )}
        </div>
      )}
    </ScreenScroll>
  );
}
