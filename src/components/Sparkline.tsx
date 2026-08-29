export default function Sparkline({ path, color }: { path: string; color: string }) {
  return (
    <svg width="46" height="22" viewBox="0 0 56 26" fill="none" style={{ flex: "none" }}>
      <path d={path} stroke={color} strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
