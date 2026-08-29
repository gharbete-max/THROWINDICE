// Overlay stacking for the group (family) and index (theme/country) detail
// screens — mirrors the prototype's own `fam`/`detail` state exactly: a
// theme can be opened from inside an open group (both stay stacked), tabs
// close everything. Deliberately not URL-routed (see README notes in
// scripts/build-data) — kept as simple, predictable local state.
import { createContext, useCallback, useContext, useState, type ReactNode } from "react";

interface OverlayCtx {
  famKey: string | null;
  detailKey: string | null;
  openFamily: (key: string) => void;
  openTheme: (key: string) => void;
  closeFamily: () => void;
  closeTheme: () => void;
  closeAll: () => void;
}

const Ctx = createContext<OverlayCtx | null>(null);

export function OverlayProvider({ children }: { children: ReactNode }) {
  const [famKey, setFamKey] = useState<string | null>(null);
  const [detailKey, setDetailKey] = useState<string | null>(null);

  const openFamily = useCallback((key: string) => {
    setFamKey(key);
    setDetailKey(null);
  }, []);
  const openTheme = useCallback((key: string) => setDetailKey(key), []);
  const closeFamily = useCallback(() => setFamKey(null), []);
  const closeTheme = useCallback(() => setDetailKey(null), []);
  const closeAll = useCallback(() => {
    setFamKey(null);
    setDetailKey(null);
  }, []);

  return (
    <Ctx.Provider value={{ famKey, detailKey, openFamily, openTheme, closeFamily, closeTheme, closeAll }}>
      {children}
    </Ctx.Provider>
  );
}

export function useOverlay() {
  const v = useContext(Ctx);
  if (!v) throw new Error("useOverlay must be used within OverlayProvider");
  return v;
}
