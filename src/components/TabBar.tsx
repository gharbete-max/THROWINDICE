import { useLocation, useNavigate } from "react-router-dom";
import { useOverlay } from "../lib/overlay";

const GOLD = "#e8b55c";
const DIM = "grayscale(.75) opacity(.55)";

const TABS = [
  { path: "/", emoji: "🌤️", label: "Today" },
  { path: "/markets", emoji: "🌍", label: "Markets" },
  { path: "/compare", emoji: "⚖️", label: "Compare" },
  { path: "/method", emoji: "📖", label: "Method" },
];

export default function TabBar() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const { closeAll } = useOverlay();

  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 40,
        padding: "9px 10px calc(env(safe-area-inset-bottom) + 12px)",
        background: "linear-gradient(180deg,rgba(22,24,38,.55),rgba(22,24,38,.95) 45%)",
        backdropFilter: "blur(18px)",
        WebkitBackdropFilter: "blur(18px)",
        borderTop: "1px solid rgba(233,233,237,.08)",
        display: "flex",
      }}
    >
      {TABS.map((t) => {
        const active = pathname === t.path;
        return (
          <button
            key={t.path}
            onClick={() => {
              closeAll();
              navigate(t.path);
            }}
            style={{
              flex: 1,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 3,
              cursor: "pointer",
              color: active ? GOLD : "var(--color-neutral-600)",
            }}
          >
            <span style={{ fontSize: 19, filter: active ? "none" : DIM }}>{t.emoji}</span>
            <span style={{ fontSize: 10 }}>{t.label}</span>
          </button>
        );
      })}
    </div>
  );
}
