import { BrowserRouter, Routes, Route } from "react-router-dom";
import { OverlayProvider, useOverlay } from "./lib/overlay";
import TabBar from "./components/TabBar";
import Today from "./screens/Today";
import Markets from "./screens/Markets";
import Compare from "./screens/Compare";
import Method from "./screens/Method";
import GroupDetail from "./screens/GroupDetail";
import IndexDetail from "./screens/IndexDetail";

function Shell() {
  const { famKey, detailKey } = useOverlay();
  return (
    <div
      style={{
        position: "relative",
        height: "100dvh",
        maxWidth: 560,
        margin: "0 auto",
        overflow: "hidden",
        background: "linear-gradient(180deg,#1c1f33 0%,#161826 40%,#141622 100%)",
        fontFamily: "var(--font-body)",
        color: "var(--color-text)",
      }}
    >
      <Routes>
        <Route path="/" element={<Today />} />
        <Route path="/markets" element={<Markets />} />
        <Route path="/compare" element={<Compare />} />
        <Route path="/method" element={<Method />} />
      </Routes>
      {famKey && <GroupDetail key={famKey} famKey={famKey} />}
      {detailKey && <IndexDetail key={detailKey} detailKey={detailKey} />}
      <TabBar />
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <OverlayProvider>
        <Shell />
      </OverlayProvider>
    </BrowserRouter>
  );
}
