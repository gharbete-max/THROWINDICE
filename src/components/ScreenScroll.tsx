import type { CSSProperties, ReactNode } from "react";

/** The scrollable body every tab screen and overlay sits in — fills the
 * shell, clears the safe-area notch at top and the tab bar at bottom. */
export default function ScreenScroll({
  children,
  style,
}: {
  children: ReactNode;
  style?: CSSProperties;
}) {
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        overflowY: "auto",
        padding: "calc(env(safe-area-inset-top) + 22px) 18px calc(env(safe-area-inset-bottom) + 108px)",
        ...style,
      }}
    >
      {children}
    </div>
  );
}

export function Kicker({ children, style }: { children: ReactNode; style?: CSSProperties }) {
  return (
    <div
      style={{
        fontSize: 10,
        letterSpacing: ".12em",
        textTransform: "uppercase",
        color: "var(--color-neutral-500)",
        margin: "20px 2px 9px",
        ...style,
      }}
    >
      {children}
    </div>
  );
}
