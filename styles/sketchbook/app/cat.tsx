// An original black cat, drawn in the Looseleaf sticker manner: white die-cut border, flat fills, clean outline.
// Expressions only (no talking): idle, happy, shocked, smug, love. Parts are ids-free classes so GSAP can move them.
export type CatFace = "idle" | "happy" | "shocked" | "smug" | "love"
const Y = "#f3c64a", INK = "#141414", LINE = "#2c2c2c", PINK = "#f19aa6", RED = "#e5372d"

function Eyes({ face, look }: { face: CatFace; look: number }) {
  const lx = look * 4
  if (face === "happy") return <g fill="none" stroke={Y} strokeWidth={6} strokeLinecap="round">
    <path d="M62 96 Q75 80 88 96" /><path d="M112 96 Q125 80 138 96" /></g>
  if (face === "love") return <g fill={RED}>
    {[75, 125].map(x => <path key={x} d={`M${x} 104 C${x - 22} 90 ${x - 12} 74 ${x} 86 C${x + 12} 74 ${x + 22} 90 ${x} 104 Z`} />)}</g>
  if (face === "smug") return <g>
    {[75, 125].map(x => <g key={x}><path d={`M${x - 15} 92 A15 12 0 0 0 ${x + 15} 92 Z`} fill={Y} />
      <ellipse cx={x + 3 + lx} cy={96} rx={4.5} ry={6} fill={INK} />
      <path d={`M${x - 17} 91 L${x + 17} 91`} stroke={LINE} strokeWidth={4} strokeLinecap="round" /></g>)}</g>
  const big = face === "shocked"
  return <g className="cat-eyes">
    {[75, 125].map(x => <g key={x}><ellipse cx={x} cy={92} rx={big ? 19 : 14} ry={big ? 20 : 16} fill={Y} />
      <ellipse cx={x + lx} cy={93} rx={big ? 4 : 5.5} ry={big ? 5 : 12} fill={INK} />
      <circle cx={x - 5 + lx} cy={86} r={big ? 4 : 3.2} fill="#fff" /></g>)}</g>
}

export function Cat({ face = "idle", look = 0, size = 220, blink = 1 }: { face?: CatFace; look?: number; size?: number; blink?: number }) {
  const mouth = face === "shocked" ? <ellipse cx={100} cy={124} rx={7} ry={9} fill="#3a1d22" />
    : face === "smug" ? <path d="M86 118 Q100 128 116 114" fill="none" stroke="#8a8a8a" strokeWidth={3.5} strokeLinecap="round" />
    : <path d="M88 116 Q94 124 100 116 Q106 124 112 116" fill="none" stroke="#8a8a8a" strokeWidth={3.5} strokeLinecap="round" />
  const shape = (s: any) => <g {...s}>
    <path className="cat-tail" d="M150 196 C 196 186 198 132 172 112" fill="none" strokeLinecap="round" strokeWidth={s.tw} stroke={s.tc} />
    <ellipse cx={100} cy={164} rx={58} ry={52} />
    <g className="cat-ear-l"><path d="M46 70 L50 12 L92 44 Z" strokeLinejoin="round" /></g>
    <g className="cat-ear-r"><path d="M154 70 L150 12 L108 44 Z" strokeLinejoin="round" /></g>
    <ellipse cx={100} cy={90} rx={64} ry={54} />
    <ellipse cx={80} cy={212} rx={17} ry={10} /><ellipse cx={120} cy={212} rx={17} ry={10} />
  </g>
  return (
    <svg viewBox="-14 -6 228 240" width={size} height={size * 240 / 228} style={{ overflow: "visible", filter: "drop-shadow(0 6px 8px rgba(0,0,0,.55))" }}>
      {shape({ fill: "#fff", stroke: "#fff", strokeWidth: 16, tw: 34, tc: "#fff" })}
      {shape({ fill: INK, stroke: LINE, strokeWidth: 3, tw: 18, tc: INK })}
      <path d="M57 58 L58 26 L82 44 Z" fill={PINK} opacity={0.85} /><path d="M143 58 L142 26 L118 44 Z" fill={PINK} opacity={0.85} />
      <g className="cat-face">
        <g transform={`translate(0 ${92 * (1 - blink)}) scale(1 ${blink})`}><Eyes face={face} look={look} /></g>
        {face === "happy" || face === "love" ? <g fill={PINK} opacity={0.55}><ellipse cx={58} cy={110} rx={11} ry={6} /><ellipse cx={142} cy={110} rx={11} ry={6} /></g> : null}
        <path d="M94 106 L106 106 L100 113 Z" fill={PINK} />
        {mouth}
        <g stroke="#6d6d6d" strokeWidth={2.2} strokeLinecap="round">
          <path d="M44 104 L18 98" /><path d="M44 112 L16 114" /><path d="M156 104 L182 98" /><path d="M156 112 L184 114" /></g>
      </g>
      <path d="M86 150 Q100 160 114 150" fill="none" stroke={LINE} strokeWidth={3} strokeLinecap="round" opacity={0.7} />
    </svg>)
}
