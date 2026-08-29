/** The horizontal storm→clear gradient bar with a marker, used on the
 * group and index detail overlays (below the big score). */
export default function MeterBar({ markerX }: { markerX: string }) {
  return (
    <>
      <div
        style={{
          height: 9,
          borderRadius: 5,
          marginTop: 12,
          background: "linear-gradient(to right,#4a4fa2,#5573c4 28%,#9199b5 52%,#c0a8f0 76%,#e8b55c)",
          position: "relative",
        }}
      >
        <div
          style={{
            position: "absolute",
            top: -4,
            left: markerX,
            width: 4,
            height: 17,
            borderRadius: 2,
            background: "#e9e9ed",
            boxShadow: "0 0 0 2px #161826",
          }}
        />
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 14, marginTop: 4 }}>
        <span>⛈️</span>
        <span>☀️</span>
      </div>
    </>
  );
}
