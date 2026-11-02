// reel-kit sketchbook page: config.json (written by compose.py) -> scenes of Looseleaf cards, captions and a buddy.
// Everything is a pure function of time: window.__seek(t) sets React state t and seeks one GSAP timeline.
import { useState } from "react"
import { createRoot } from "react-dom/client"
import { flushSync } from "react-dom"
import "./theme.css"
import { InkProvider } from "@/lib/ink/react"
import { Card } from "@/components/ui/card"
import { IndexCard } from "@/components/ui/index-card"
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
import { Slider } from "@/components/ui/slider"
import { Stamp } from "@/components/ui/stamp"
import { Doodle } from "@/components/ui/doodle"
import { Circled } from "@/components/ui/circled"
import { Button } from "@/components/ui/button"
import { Icon } from "@/components/ui/icon"
import { StickyNote } from "@/components/ui/sticky-note"
import { Mascot } from "@/components/ui/mascot"
import { Polaroid, PolaroidCaption } from "@/components/ui/polaroid"
import { Cat } from "./cat"

const gsap = (window as any).gsap
type Cfg = any
const after = (t: number, at?: number) => at === undefined || t >= at

function Dood({ d, id }: { d: any; id: string }) {
  if (!d) return null
  return <div id={id} data-qa="doodle" style={{ position: "absolute", left: d.x ?? 60, top: d.y ?? 580 }}><Doodle name={d.name} size={d.size ?? 90} /></div>
}

function CardView({ c, i, t, cfg }: { c: any; i: number; t: number; cfg: Cfg }) {
  const id = `s${i}`; const top = c.top
  const dark = cfg.look === "dark"
  switch (c.type) {
    case "hook": return <>
      <div id={`${id}-card`} data-qa="card" style={{ position: "absolute", left: 38, top: top ?? 110, width: 464 }}>
        <Card stock={c.stock ?? "graph"} rules={c.stock === "paper" ? "none" : "graph"} className="px-7 py-6">
          {(c.rows || []).map((r: any, j: number) => {
            const st: any = r.kind === "big" ? { fontSize: r.size ?? 60, lineHeight: 1.0, fontWeight: 700 }
              : r.kind === "mark" ? { fontSize: r.size ?? 50, lineHeight: 1.15, fontWeight: 700, whiteSpace: "nowrap", marginTop: 4 }
              : { fontSize: r.size ?? 26, marginTop: 6 }
            return <div key={j} id={`${id}-r${j}`} className={"big" + (r.kind === "dim" || !r.kind ? " dim" : "")} style={st}>
              {r.kind === "mark" ? <span className="mark">{r.text}</span> : r.text}</div>
          })}
        </Card></div>
      <Dood d={c.doodle} id={`${id}-dd`} /></>
    case "split": {
      const keys = c.keys || []; let tab = c.tabs?.[0], v = 0
      for (let k = 0; k < keys.length; k++) {
        const a = keys[k], b = keys[k + 1]
        if (t >= a.at) { if (a.tab !== undefined) tab = typeof a.tab === "number" ? c.tabs[a.tab] : a.tab; v = a.value ?? v
          if (b && t < b.at && b.value !== undefined) v = (a.value ?? v) + (b.value - (a.value ?? v)) * Math.min(1, (t - a.at) / Math.min(1, b.at - a.at)) }
      }
      return <>
        <div id={`${id}-card`} data-qa="card" style={{ position: "absolute", left: 32, top: top ?? 170, width: 476 }}>
          <Card stock="paper" className="px-7 py-7" tape="top">
            <div className="big dim" style={{ fontSize: 22 }}>{c.title}</div>
            <ToggleGroup type="single" value={tab} variant="outline" className="mt-1">
              {(c.tabs || []).map((x: string) => <ToggleGroupItem key={x} value={x} style={{ fontSize: 22, padding: "0 22px", height: 46 }}>{x}</ToggleGroupItem>)}
            </ToggleGroup>
            <div style={{ marginTop: 18 }}><Slider value={[v]} max={100} aria-label={c.title || "slider"} /></div>
            <div className="big" style={{ display: "flex", justifyContent: "space-between", fontSize: 22, marginTop: 4 }}>
              <span>{c.labels?.[0]}</span><span>{c.labels?.[1]}</span></div>
          </Card></div>
        <Dood d={c.doodle} id={`${id}-dd`} /></>
    }
    case "stat": return <>
      <div id={`${id}-card`} data-qa="card" style={{ position: "absolute", left: 50, top: top ?? 160, width: 440 }}>
        <IndexCard hole className="px-8 py-8">
          <div className="big dim" style={{ fontSize: 24 }}>{c.label}</div>
          <div className="big" style={{ fontSize: c.size ?? 100, fontWeight: 700, lineHeight: 1, margin: "22px 0 18px 14px" }}>
            {c.circle === false ? <span id={`${id}-num`}>{c.value}</span>
              : <Circled tone={dark ? "red" : "red"} weight="brush"><span id={`${id}-num`}>{c.value}</span></Circled>}</div>
          <div className="big" style={{ fontSize: 24 }}>{c.sub}</div>
        </IndexCard></div>
      {c.stamp ? <div id={`${id}-stamp`} data-qa="stamp" style={{ position: "absolute", left: c.stamp.x ?? 40, top: c.stamp.y ?? 470 }}><Stamp text={c.stamp.text} tilt={-10} size={150} /></div> : null}
      <Dood d={c.doodle} id={`${id}-dd`} /></>
    case "shot": return <>
      <div id={`${id}-card`} data-qa="card" style={{ position: "absolute", left: 30, top: top ?? 200, width: 480 }}>
        <Card stock="paper" className="px-5 py-5" tape="top">
          <img src={c.src} style={{ width: "100%", borderRadius: 6, display: "block", maxHeight: c.height ?? 300, objectFit: "cover", objectPosition: "top" }} />
          {c.chips?.length ? <div className="big" style={{ fontSize: 24, marginTop: 6, display: "flex", gap: 14, justifyContent: "center", flexWrap: "wrap" }}>
            {c.chips.map((ch: any, j: number) => <span key={j} id={`${id}-ch${j}`} className={ch.mark ? "mark" : ch.dim ? "dim" : ""}>{ch.text}</span>)}</div> : null}
        </Card></div>
      <Dood d={c.doodle} id={`${id}-dd`} /></>
    case "checklist": return <>
      <div id={`${id}-card`} data-qa="card" style={{ position: "absolute", left: 40, top: top ?? 170, width: 460 }}>
        <Card stock="paper" className="px-7 py-6" tape="top">
          <div className="big dim" style={{ fontSize: 22 }}>{c.title}</div>
          {(c.items || []).map((it: any, j: number) => <div key={j} className="big" style={{ display: "flex", alignItems: "center", gap: 12, fontSize: 26, marginTop: 10 }}>
            <span style={{ width: 30, height: 30, display: "inline-flex", alignItems: "center", justifyContent: "center", border: "2px solid currentColor", borderRadius: 6 }}>
              <span id={`${id}-tk${j}`} style={{ opacity: after(t, it.at) ? 1 : 0, color: "var(--rk-accent)" }}><Icon name="check" size={22} /></span></span>
            <span>{it.text}</span></div>)}
        </Card></div>
      <Dood d={c.doodle} id={`${id}-dd`} /></>
    case "versus": return <>
      <div style={{ position: "absolute", left: 24, right: 24, top: top ?? 190, display: "flex", gap: 16 }}>
        {(["good", "bad"] as const).map(k => c[k] ? <div key={k} id={`${id}-${k}`} data-qa="card" style={{ flex: 1 }}>
          <IndexCard className="px-5 py-5">
            <div className="big" style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 26, fontWeight: 700, color: k === "bad" ? "var(--rk-accent)" : undefined }}>
              <Icon name={k === "good" ? "check" : "x"} size={24} />{c[k].title}</div>
            <div className="big" style={{ fontSize: 22, marginTop: 8 }}>{c[k].text}</div>
          </IndexCard></div> : null)}
      </div>
      <Dood d={c.doodle} id={`${id}-dd`} /></>
    case "note": return <>
      <div id={`${id}-card`} data-qa="card" style={{ position: "absolute", left: 70, top: top ?? 180, width: 400 }}>
        <StickyNote color={c.color ?? "yellow"} className="px-7 py-7">
          <div className="big" style={{ fontSize: c.size ?? 40, fontWeight: 700, lineHeight: 1.1, color: "#2a2420" }}>{c.text}</div>
          {c.sub ? <div className="big" style={{ fontSize: 22, marginTop: 10, color: "#4a433c" }}>{c.sub}</div> : null}
        </StickyNote></div>
      <Dood d={c.doodle} id={`${id}-dd`} /></>
    case "follow": {
      const yt = c.platform === "youtube"; const done = t >= c.tap_at
      return <>
        <div id={`${id}-card`} data-qa="card" style={{ position: "absolute", left: 135, top: top ?? 160, width: 270 }}>
          <Polaroid className="w-full" tape="top">
            <div style={{ aspectRatio: "1", overflow: "hidden" }}>{c.avatar ? <img src={c.avatar} style={{ width: "100%", height: "100%", objectFit: "cover" }} /> : null}</div>
            <PolaroidCaption>{c.handle}</PolaroidCaption>
          </Polaroid></div>
        <div id={`${id}-btn`} data-qa="button" style={{ position: "absolute", left: 0, right: 0, top: (top ?? 160) + 410, display: "flex", justifyContent: "center" }}>
          <Button size="lg" variant={done ? "outline" : "default"}
            style={{ fontSize: 26, height: 58, padding: "0 40px", ...(yt && !done ? { background: "#ff0033", color: "#fff" } : {}), ...(dark && !done ? { color: "#fff" } : {}) }}>
            {done ? (yt ? "✓ Subscribed" : "✓ Following") : (yt ? "Subscribe" : "Follow")}</Button></div></>
    }
  }
  return null
}

function App({ cfg }: { cfg: Cfg }) {
  const [t, setT] = useState(0)
  ;(window as any).__setT = (v: number) => flushSync(() => setT(v))
  let ev = { pose: "idle", face: "idle", look: 0 } as any
  for (const e of cfg.events) if (t >= e.t) ev = e
  const blink = cfg.blinks.some((b: number) => t >= b && t < b + 0.14) ? 0.12 : 1
  const B = cfg.buddy
  // buddy in/out is a pure function of time: in over 0.35 s when a scene that shows it starts, out over 0.3 s before one that hides it
  let bv = 0
  cfg.scenes.forEach((sc: any, i: number) => {
    if (!cfg.show[i]) return
    const prev = i > 0 && cfg.show[i - 1], next = i < cfg.scenes.length - 1 && cfg.show[i + 1]
    const a = i === 0 ? 0.35 : sc.start - 0.15, z = sc.end - 0.25
    if (t >= (prev ? sc.start - 1 : a) && t <= (next ? sc.end + 1 : z + 0.3)) {
      const pin = prev ? 1 : Math.min(1, Math.max(0, (t - a) / 0.35)), pout = next ? 1 : Math.min(1, Math.max(0, 1 - (t - z) / 0.3))
      bv = Math.max(bv, Math.min(1 - Math.pow(1 - pin, 3), pout))
    }
  })
  return (
    <InkProvider tier="hi" motion="reduced">
      <div id="stage">
        {cfg.scenes.map((s: any, i: number) => <div key={i} className="sc" id={`s${i}`} style={{ opacity: i === 0 ? 1 : 0 }}>
          <CardView c={s.card} i={i} t={t} cfg={cfg} /></div>)}
        <div id="buddy" style={{ position: "absolute", left: B.x, top: B.y, transformOrigin: "50% 100%" }}>
          <div data-qa="buddy" style={{ opacity: bv, transform: `translateY(${(1 - bv) * 220}px)` }}>
          {cfg.theme.buddy === "cat" ? <Cat face={ev.face} look={ev.look} size={B.size} blink={blink} />
            : <Mascot pose={ev.pose} size={B.size * 1.12} />}</div></div>
        {cfg.lines.map((l: any, i: number) => <div key={i} className="cap" id={`c${i}`} style={{ opacity: 0, top: cfg.scenes[l.scene ?? 0]?.capY ?? 745 }}>
          {l.words.map((w: any, j: number) => <span key={j} className={"w" + (w.hi ? " hi" : "")} id={`c${i}w${j}`}>{w.w}</span>)}</div>)}
      </div>
    </InkProvider>)
}

function timeline(cfg: Cfg) {
  const tl = gsap.timeline({ paused: true }); const S = cfg.scenes
  const pop = (sel: string, at: number, from: any = { scale: 0.4, opacity: 0 }) => { if (document.querySelector(sel)) tl.fromTo(sel, from, { scale: 1, opacity: 1, rotation: 0, y: 0, x: 0, duration: 0.35, ease: "back.out(2)" }, at) }
  for (let i = 1; i < S.length; i++) {
    tl.to(`#s${i - 1}`, { x: -560, rotation: -4, duration: 0.3, ease: "power2.in" }, S[i].start - 0.2)
    tl.fromTo(`#s${i}`, { x: 560, rotation: 4, opacity: 1 }, { x: 0, rotation: 0, duration: 0.35, ease: "power3.out" }, S[i].start - 0.05)
  }
  S.forEach((s: any, i: number) => {
    const c = s.card, id = `#s${i}`
    if (i === 0) pop(`${id}-card`, 0.05, { y: 80, opacity: 0, rotation: 6 })
    if (c.doodle) pop(`${id}-dd`, c.doodle.at, { scale: 0, rotation: -30, opacity: 0 })
    if (c.type === "hook") (c.rows || []).forEach((r: any, j: number) => { if (r.at !== undefined) tl.fromTo(`${id}-r${j}`, { scale: 0.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "back.out(3)" }, r.at) })
    if (c.type === "stat") {
      tl.fromTo(`${id}-num`, { opacity: 0, scale: 0.5 }, { opacity: 1, scale: 1, duration: 0.3, ease: "back.out(3)" }, c.at)
      if (c.stamp) { pop(`${id}-stamp`, c.stamp.at, { scale: 2.4, opacity: 0, rotation: 10 }); tl.to(`${id}-stamp`, { x: 4, yoyo: true, repeat: 3, duration: 0.04 }, c.stamp.at + 0.3) }
    }
    if (c.type === "shot") (c.chips || []).forEach((ch: any, j: number) => tl.fromTo(`${id}-ch${j}`, { scale: 0.5, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "back.out(3)" }, ch.at))
    if (c.type === "versus") (["good", "bad"]).forEach(k => { if (c[k]) pop(`${id}-${k}`, c[k].at, { y: 60, opacity: 0, rotation: k === "good" ? -5 : 5 }) })
    if (c.type === "note") pop(`${id}-card`, c.at, { scale: 0.6, opacity: 0, rotation: -8 })
    if (c.type === "follow") tl.fromTo(`${id}-btn`, { scale: 1 }, { scale: 0.9, yoyo: true, repeat: 1, duration: 0.08 }, c.tap_at)
  })
  const reps = Math.max(1, Math.floor((cfg.dur - 0.7) / 0.55))
  tl.to("#buddy", { scaleY: 0.97, scaleX: 1.02, yoyo: true, repeat: reps - (reps % 2 ? 0 : 1), duration: 0.55, ease: "sine.inOut" }, 0.7)
  if (document.querySelector("#buddy .cat-tail")) tl.to("#buddy .cat-tail", { rotation: 8, svgOrigin: "150 196", yoyo: true, repeat: Math.floor((cfg.dur - 0.7) / 0.8), duration: 0.8, ease: "sine.inOut" }, 0.7)
  cfg.events.forEach((e: any) => { if (e.jump) tl.to("#buddy", { y: -34, yoyo: true, repeat: 1, duration: 0.16, ease: "power2.out" }, e.t) })
  cfg.lines.forEach((l: any, i: number) => {
    tl.set(`#c${i}`, { opacity: 1 }, l.start - 0.02)
    const next = cfg.lines[i + 1]; tl.set(`#c${i}`, { opacity: 0 }, next ? next.start - 0.03 : cfg.dur)
    l.words.forEach((w: any, j: number) => tl.fromTo(`#c${i}w${j}`, { opacity: 0, y: 10, filter: "blur(4px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.16 }, w.t))
  })
  tl.set({}, {}, cfg.dur)
  return tl
}

fetch("./config.json").then(r => r.json()).then((cfg: Cfg) => {
  document.documentElement.className = "look-" + cfg.look
  const r = document.documentElement.style
  r.setProperty("--rk-accent", cfg.theme.accent); r.setProperty("--rk-hi", cfg.theme.hi); r.setProperty("--rk-hi-text", cfg.theme.hi_text)
  // lines carry their scene index so captions can sit at a per-scene height
  cfg.lines.forEach((l: any) => { l.scene = cfg.scenes.findIndex((s: any) => l.start >= s.start - 0.01 && l.start < s.end) })
  cfg.blinks = []; for (let b = 1.4; b < cfg.dur - 0.5; b += 3.3) cfg.blinks.push(b)
  createRoot(document.getElementById("root")!).render(<App cfg={cfg} />)
  setTimeout(() => {
    const tl = timeline(cfg)
    ;(window as any).__seek = (t: number) => { (window as any).__setT(t); tl.seek(t, false) }
    ;(window as any).__ready = true
  }, 400)
})
