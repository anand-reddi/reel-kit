"""Draws the @techinsixty presenter as a rigged vector puppet -> character.svg.
Reference: the user's character sheets (curly black hair, nose bandage, moustache + goatee, navy hoodie with a red
オタク label, black kitten with yellow eyes on his left shoulder). Keeps the kit's ids (CHARACTER.md) and adds
kitten rigs: #cat (bobs on stamps), #tail (swish), #cat-ear (twitch), #cat-eyes-open / #cat-eyes-shut (blink).
Run: python3 make.py"""
import math, os

HAIR, HAIR_HI, LINE = "#15161c", "#3d4356", "#0b0c11"
SKIN, SKIN_SH, SKIN_LINE = "#f0bd94", "#d99c74", "#7a4a33"
NAVY, NAVY_SH, NAVY_HI, CORD = "#20263a", "#151a29", "#2d3550", "#d8dbe2"
RED, BAND, BAND_PAD, BAND_LINE = "#e5372d", "#efd0a3", "#f8e6c6", "#8c6a46"
CAT, CAT_HI, PINK, EYE_Y = "#121318", "#2b2e3a", "#ea8e9c", "#f3c33a"

def lcg(seed):
    s = seed
    def r():
        nonlocal s
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        return s / 0x7FFFFFFF
    return r

# ------------------------------------------------------------------ hands and arms
def hand(x, y, kind, rot=0, flip=False):
    sx = -1 if flip else 1
    o = f'stroke="{SKIN_LINE}" stroke-width="3"'
    if kind == "point":
        f = f'<rect x="-10" y="-84" width="20" height="66" rx="10" fill="{SKIN}" {o}/><path d="M-34,-6 q-8,-26 8,-34" stroke="{SKIN_LINE}" stroke-width="3" fill="none"/>'
    elif kind == "palm":
        f = "".join(f'<rect x="{-30 + i * 15}" y="{-78 + abs(i - 1.5) * 10}" width="15" height="56" rx="7.5" fill="{SKIN}" {o}/>' for i in range(4))
        f += f'<rect x="26" y="-34" width="15" height="42" rx="7.5" fill="{SKIN}" {o} transform="rotate(38 33 -12)"/>'
    elif kind == "thumb":
        f = f'<rect x="-9" y="-80" width="19" height="56" rx="9.5" fill="{SKIN}" {o}/>'
    else:
        f = ""
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({sx} 1)">{f}<ellipse rx="42" ry="38" fill="{SKIN}" {o}/>'
            f'<path d="M-30,8 q30,22 60,0" stroke="{SKIN_SH}" stroke-width="4" fill="none"/></g>')

def arm(sh, el, hd, kind, rot=0, flip=False):
    p = f"M{sh[0]},{sh[1]} Q{el[0]},{el[1]} {hd[0]},{hd[1] + 34}"
    return (f'<path d="{p}" stroke="{LINE}" stroke-width="100" stroke-linecap="round" fill="none"/>'
            f'<path d="{p}" stroke="{NAVY}" stroke-width="88" stroke-linecap="round" fill="none"/>'
            f'<path d="{p}" stroke="{NAVY_HI}" stroke-width="10" stroke-linecap="round" fill="none" opacity="0.6" transform="translate(-14 -6)"/>'
            f'<circle cx="{hd[0]}" cy="{hd[1] + 40}" r="47" fill="{NAVY_SH}" stroke="{LINE}" stroke-width="5"/>'
            + hand(hd[0], hd[1], kind, rot, flip))

SL, SR = (405, 610), (795, 610)
POSES = {   # his right arm is on the viewer's left; the kitten sits on the viewer's right shoulder
    "up":    [arm(SL, (250, 600), (300, 330), "point", -8)],
    "palms": [arm(SL, (230, 740), (215, 560), "palm", -25), arm(SR, (1000, 800), (1040, 650), "palm", 30, True)],
    "card":  [arm(SL, (205, 560), (225, 320), "point", -32)],
    "thumb": [arm(SL, (300, 800), (450, 690), "thumb", -12)],
    "shrug": [arm(SL, (260, 760), (225, 540), "palm", -40), arm(SR, (1010, 800), (1050, 610), "palm", 42, True)],
    "wave":  [arm(SL, (235, 620), (285, 360), "palm", -14)],
}

# ------------------------------------------------------------------ head
def teardrop(L, w):
    """A curl lobe pointing along +x with a hooked tip."""
    return (f"M0,{-w / 2:.1f} C{L * 0.45:.1f},{-w / 2:.1f} {L * 0.85:.1f},{-w * 0.35:.1f} {L:.1f},{-w * 0.55:.1f} "
            f"C{L * 0.92:.1f},{-w * 0.05:.1f} {L * 0.6:.1f},{w / 2:.1f} 0,{w / 2:.1f} Z")

def hair_lobes(seed, n, cx, cy, rx, ry, a0, a1, Lr, wr, swirl, keep):
    r = lcg(seed); out = []
    for i in range(n):
        a = math.radians(a0 + (a1 - a0) * (i + r() * 0.6) / n)
        x, y = cx + rx * math.cos(a), cy + ry * math.sin(a)
        if not keep(x, y): continue
        ang = math.degrees(a) + swirl + (r() - 0.5) * 30
        L, w = Lr[0] + r() * (Lr[1] - Lr[0]), wr[0] + r() * (wr[1] - wr[0])
        out.append(f'<path d="{teardrop(L, w)}" transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f})" fill="{HAIR}" stroke="{LINE}" stroke-width="2.5"/>')
    return "".join(out)

def eye(cx, cy, s, cid):
    # s = -1 viewer-left eye, +1 viewer-right; the inner corner is toward the nose, the outer corner sits higher
    i, o = cx - s * 42, cx + s * 48
    sc = f"M{i},{cy + 4} Q{cx},{cy - 24} {o},{cy - 10} Q{cx + s * 6},{cy + 20} {i},{cy + 4} Z"
    ix = cx - 5
    return (f'<clipPath id="{cid}"><path d="{sc}"/></clipPath>'
            f'<path d="{sc}" fill="#fbf8f2"/>'
            f'<g clip-path="url(#{cid})"><circle cx="{ix}" cy="{cy - 1}" r="19" fill="#7a3f16"/><circle cx="{ix}" cy="{cy + 1}" r="13" fill="#c98035"/>'
            f'<circle cx="{ix}" cy="{cy}" r="8" fill="#1a0f0a"/><circle cx="{ix + 6}" cy="{cy - 7}" r="5" fill="#fff"/>'
            f'<path d="M{i - 10},{cy - 30} L{o + 10},{cy - 30} L{o + 10},{cy - 6} Q{cx},{cy - 14} {i - 10},{cy + 2} Z" fill="{SKIN_SH}" opacity="0.4"/></g>'
            f'<path d="M{i - s * 2},{cy + 6} Q{cx},{cy - 28} {o},{cy - 12} L{o + s * 12},{cy - 20}" stroke="{LINE}" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M{i + s * 8},{cy + 10} Q{cx + s * 6},{cy + 18} {o - s * 6},{cy + 2}" stroke="{SKIN_LINE}" stroke-width="2.5" fill="none" opacity="0.8"/>')

def brow(cx, cy, s):
    i, o, m = cx - s * 44, cx + s * 60, cx + s * 8
    return f'<path d="M{i},{cy + 14} Q{m},{cy - 10} {o},{cy - 14} L{o - s * 4},{cy - 6} Q{m},{cy + 2} {i},{cy + 26} Z" fill="{HAIR}" stroke="{LINE}" stroke-width="2"/>'

def eyes_shut():
    return "".join(f'<path d="M{cx - 46 * s},{-2} Q{cx},{14} {cx + 46 * s},{-6}" stroke="{LINE}" stroke-width="7" fill="none" stroke-linecap="round"/>' for cx, s in ((-62, -1), (62, 1)))

def mouth(kind):
    if kind == "o":
        return f'<path d="M-22,114 Q0,108 24,112 Q20,138 0,140 Q-20,138 -22,114 Z" fill="#4a1d1d" stroke="{LINE}" stroke-width="3"/><ellipse cx="2" cy="132" rx="11" ry="5" fill="#c4545a"/>'
    if kind == "smile":
        return f'<path d="M-26,114 Q6,132 34,108" stroke="#4a1d1d" stroke-width="5.5" fill="none" stroke-linecap="round"/>'
    return f'<path d="M-24,118 Q2,124 28,114" stroke="#4a1d1d" stroke-width="5" fill="none" stroke-linecap="round"/>'

def curly_silhouette(seed, cx, cy, rx, ry, n, amp, ymax, pw=1.4, lean=0.6):
    r = lcg(seed); peaks = [(i + r() * 0.5) / n * 2 * math.pi for i in range(n)]; amps = [amp * (0.6 + 0.6 * r()) for _ in range(n)]
    pts = []
    for k in range(480):
        t = k / 480 * 2 * math.pi; b = 0
        for p, A in zip(peaks, amps):
            d = math.atan2(math.sin(t - p), math.cos(t - p)) * n / 2
            if abs(d) < math.pi / 2: b = max(b, A * math.cos(d) ** pw)
        x = cx + (rx + b) * math.cos(t) - math.sin(t) * b * lean; y = cy + (ry + b) * math.sin(t) + math.cos(t) * b * lean
        pts.append((x, min(y, ymax)))
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z", list(zip(peaks, amps))

def head():
    r = lcg(77)
    stubble = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.5" fill="{HAIR}" opacity="0.25"/>'
                      for x, y in ((math.sin(t) * 140 * (0.84 + 0.16 * r()), 46 + (1 - math.cos(t)) * 62 + r() * 16)
                                   for t in (math.radians(-80 + i * 4) for i in range(41))) if abs(x) > 40 or y > 150)
    face = "M-156,-60 C-158,30 -136,92 -92,134 L-30,168 C-10,178 14,178 34,168 L96,132 C138,92 158,30 156,-60 C154,-150 94,-196 0,-196 C-94,-196 -154,-150 -156,-60 Z"
    sil, peaks = curly_silhouette(11, 0, -92, 222, 198, 17, 52, 120)
    locks = ""
    for p, A in peaks:
        if math.sin(p) > 0.3 or (int(p * 10) % 2): continue
        x0, y0 = 0 + 110 * math.cos(p), -92 + 110 * math.sin(p)
        x1, y1 = 0 + (222 + A * 0.7) * math.cos(p) - math.sin(p) * A * 0.5, -92 + (198 + A * 0.7) * math.sin(p) + math.cos(p) * A * 0.5
        mx, my = (x0 + x1) / 2 - math.sin(p) * 30, (y0 + y1) / 2 + math.cos(p) * 30
        locks += f'<path d="M{x0:.1f},{y0:.1f} Q{mx:.1f},{my:.1f} {x1:.1f},{min(y1, 70):.1f}" stroke="{LINE}" stroke-width="3" fill="none" opacity="0.9"/>'
        locks += f'<path d="M{x0 * 1.05:.1f},{y0 * 1.05 - 6:.1f} Q{mx:.1f},{my - 10:.1f} {(x0 + x1) / 2:.1f},{(y0 + y1) / 2 - 6:.1f}" stroke="{HAIR_HI}" stroke-width="4" fill="none" stroke-linecap="round" opacity="0.7"/>'
    back = f'<path d="{sil}" fill="{HAIR}" stroke="{LINE}" stroke-width="4" stroke-linejoin="round"/>{locks}'
    # bangs: irregular wavy locks curling outward from the parting; only the lower edge is outlined
    locks_x = [(-182, -132, -58), (-132, -78, -78), (-78, -30, -70), (-30, 22, -84), (22, 70, -66), (70, 124, -74), (124, 182, -50)]
    edge = "M-190,-120 "
    for xa, xb, tipy in locks_x:
        mid = (xa + xb) / 2; lean = -22 if mid < -10 else 22; tipx = mid + lean
        edge += f"C{xa + 4},{tipy * 0.55 - 40:.0f} {tipx - lean * 0.9:.0f},{tipy + 6:.0f} {tipx:.0f},{tipy:.0f} C{tipx - lean * 0.2:.0f},{tipy - 22:.0f} {xb - 6},{-112 + (r() - 0.5) * 16:.0f} {xb},{-120 + (r() - 0.5) * 12:.0f} "
    fringe = (f'<clipPath id="hairclip"><path d="{sil}"/></clipPath><path d="{edge} L200,-260 L-200,-260 Z" fill="{HAIR}" clip-path="url(#hairclip)"/>'
              f'<path d="{edge}" stroke="{LINE}" stroke-width="3.5" fill="none" stroke-linejoin="round"/>')
    fringe += "".join(f'<path d="M{x},-160 q{12 if x > 0 else -12},34 {26 if x > 0 else -26},62" stroke="{HAIR_HI}" stroke-width="4" fill="none" stroke-linecap="round" opacity="0.65"/>' for x in (-120, -50, 40, 112))
    sides = ""
    hi = ""
    band = (f'<g transform="translate(4 52) rotate(-16)"><rect x="-56" y="-15" width="112" height="30" rx="13" fill="{BAND}" stroke="{BAND_LINE}" stroke-width="3"/>'
            f'<rect x="-17" y="-11" width="34" height="22" rx="4" fill="{BAND_PAD}" stroke="{BAND_LINE}" stroke-width="1.5"/>'
            + "".join(f'<circle cx="{x}" cy="{y}" r="1.8" fill="{BAND_LINE}"/>' for x in (-44, -34, -26, 26, 34, 44) for y in (-5, 5)) + "</g>")
    return f'''
  <rect x="-62" y="120" width="124" height="130" fill="{SKIN_SH}"/>
  {back}
  <ellipse cx="-152" cy="18" rx="26" ry="38" fill="{SKIN}" stroke="{SKIN_LINE}" stroke-width="3"/><ellipse cx="152" cy="18" rx="26" ry="38" fill="{SKIN}" stroke="{SKIN_LINE}" stroke-width="3"/>
  <path d="{face}" fill="{SKIN}" stroke="{SKIN_LINE}" stroke-width="3.5"/>
  <path d="M76,140 C128,100 154,40 156,-40 L156,30 C144,96 112,140 56,166 Z" fill="{SKIN_SH}" opacity="0.6"/>
  {stubble}
  {brow(-64, -44, -1)}{brow(64, -44, 1)}
  <g id="eyes-open">{eye(-64, 8, -1, "eyl")}{eye(64, 8, 1, "eyr")}</g>
  <g id="eyes-shut" opacity="0">{eyes_shut()}</g>
  <path d="M6,26 L-6,76 Q4,84 18,78" stroke="{SKIN_LINE}" stroke-width="3.5" fill="none" stroke-linecap="round"/>
  {band}
  <path d="M-56,106 Q-30,86 0,92 Q30,86 58,104 Q32,100 0,106 Q-30,100 -56,106 Z" fill="{HAIR}"/>
  <path d="M-56,106 L-50,132 M58,104 L52,130" stroke="{HAIR}" stroke-width="5" opacity="0.7"/>
  <path d="M-28,140 Q0,132 28,140 L20,166 Q0,180 -20,166 Z" fill="{HAIR}"/>
  {"".join(f'<g id="m-{k}" class="mth" opacity="{1 if k == "smile" else 0}">{mouth(k)}</g>' for k in ("closed", "o", "smile"))}
  {sides}{fringe}{hi}'''

# ------------------------------------------------------------------ kitten
def fur(cx, cy, rx, ry, n, jag, seed):
    r = lcg(seed); pts = []
    for i in range(n * 2):
        a = i / (n * 2) * 2 * math.pi; k = 1 + (jag * (0.6 + 0.4 * r()) if i % 2 else 0)
        pts.append(f"{cx + rx * k * math.cos(a):.1f},{cy + ry * k * math.sin(a):.1f}")
    return "M" + " L".join(pts) + " Z"

def kitten():
    eyes = "".join(f'<g transform="translate({x} 468)"><ellipse rx="17" ry="20" fill="{EYE_Y}" stroke="#a8740f" stroke-width="2.5"/>'
                   f'<ellipse rx="9" ry="14" fill="#141414"/><circle cx="5" cy="-7" r="5" fill="#fff"/><circle cx="-5" cy="6" r="2.5" fill="#fff"/></g>' for x in (818, 872))
    shut = "".join(f'<path d="M{x - 16},468 q16,10 32,0" stroke="{EYE_Y}" stroke-width="5" fill="none" stroke-linecap="round"/>' for x in (818, 872))
    return f'''<g id="cat"><g transform="translate(880 610) scale(1.22) translate(-880 -610)">
  <g id="tail"><path d="M930,600 C995,585 1030,520 1012,455 C1004,428 984,420 974,434 C992,462 992,520 922,566 Z" fill="{CAT}" stroke="{LINE}" stroke-width="3"/>
    <path d="M1006,470 q8,30 -8,60" stroke="{CAT_HI}" stroke-width="4" fill="none"/></g>
  <path d="{fur(888, 570, 88, 62, 22, 0.10, 5)}" fill="{CAT}" stroke="{LINE}" stroke-width="3"/>
  <path d="M842,616 q-12,-26 6,-40 q22,-6 26,22 q0,22 -32,18 Z M884,620 q-10,-26 8,-38 q22,-4 24,22 q-2,22 -32,16 Z" fill="{CAT}" stroke="{LINE}" stroke-width="3"/>
  <path d="M852,612 l2,-8 M862,614 l1,-8 M894,616 l2,-8 M904,616 l1,-8" stroke="{CAT_HI}" stroke-width="3"/>
  <path d="M800,420 L790,352 L838,398 Z" fill="{CAT}" stroke="{LINE}" stroke-width="3"/><path d="M804,410 L798,368 L828,398 Z" fill="{PINK}"/>
  <g id="cat-ear"><path d="M880,396 L912,346 L912,416 Z" fill="{CAT}" stroke="{LINE}" stroke-width="3"/><path d="M886,400 L906,364 L906,410 Z" fill="{PINK}"/></g>
  <path d="{fur(845, 466, 64, 56, 20, 0.12, 9)}" fill="{CAT}" stroke="{LINE}" stroke-width="3"/>
  <path d="M812,430 q30,-14 64,-2" stroke="{CAT_HI}" stroke-width="4" fill="none" opacity="0.7"/>
  <g id="cat-eyes-open">{eyes}</g><g id="cat-eyes-shut" opacity="0">{shut}</g>
  <path d="M839,492 l12,0 l-6,7 Z" fill="{PINK}"/><path d="M833,503 q6,7 12,0 q6,7 12,0" stroke="#4a3a3a" stroke-width="2.5" fill="none"/>
  <path d="M843,506 q2,12 8,0 Z" fill="{PINK}"/>
  <path d="M790,492 l-34,-6 M790,500 l-32,4 M902,488 l34,-8 M902,496 l34,2" stroke="#8a8f9e" stroke-width="2" opacity="0.8"/>
</g></g>'''

# ------------------------------------------------------------------ body
def katakana():
    """オタク drawn as red strokes (no CJK font needed at render time), stacked vertically in the label."""
    s = f'stroke="{RED}" stroke-width="4.5" fill="none" stroke-linecap="round" stroke-linejoin="round"'
    o = f'<path d="M-12,-8 L14,-8 M4,-16 L4,12 Q4,16 -1,13 M3,-6 Q-4,6 -14,10 M10,-18 l4,4" {s}/>'
    ta = f'<path d="M-4,-16 Q-8,-8 -15,-2 M-6,-12 L12,-12 Q8,4 -10,16 M-4,-2 L8,4" {s}/>'
    ku = f'<path d="M-4,-16 Q-8,-8 -15,-2 M-6,-12 L12,-12 Q8,4 -10,16" {s}/>'
    return "".join(f'<g transform="translate(712 {y})">{g}</g>' for g, y in ((o, 668), (ta, 706), (ku, 744)))

def body():
    return f'''
  <path d="M235,1000 C245,790 290,650 425,592 C485,568 715,568 775,592 C910,650 955,790 965,1000 Z" fill="{NAVY}" stroke="{LINE}" stroke-width="6"/>
  <path d="M775,592 C910,650 955,790 965,1000 L860,1000 C850,820 820,680 775,592 Z" fill="{NAVY_SH}" opacity="0.8"/>
  <path d="M330,760 Q360,860 350,1000 M860,760 Q840,860 852,1000 M420,940 Q600,915 780,940" stroke="{NAVY_SH}" stroke-width="7" fill="none" stroke-linecap="round"/>
  <path d="M430,605 C440,520 760,520 770,605 C740,570 460,570 430,605 Z" fill="{NAVY_SH}" stroke="{LINE}" stroke-width="5"/>
  <path d="M470,590 Q600,660 730,590" stroke="{LINE}" stroke-width="5" fill="none"/>
  <path d="M548,610 Q542,680 552,740 M652,610 Q658,680 648,740" stroke="{CORD}" stroke-width="7" fill="none" stroke-linecap="round"/>
  <rect x="544" y="738" width="14" height="22" rx="4" fill="#9aa0ad"/><rect x="642" y="738" width="14" height="22" rx="4" fill="#9aa0ad"/>
  <rect x="690" y="642" width="44" height="124" fill="none" stroke="#ece8e0" stroke-width="3"/>
  {katakana()}'''

def presenter():
    poses = "".join(f'<g id="pose-{n}" class="pose" opacity="0">{"".join(parts)}</g>' for n, parts in POSES.items())
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1000" width="1200" height="1000">
<g id="pres-body">
  <rect x="535" y="450" width="130" height="150" fill="{SKIN_SH}"/>
  {body()}
  {poses}
  <g id="head" transform="translate(600 330)">{head()}</g>
  {kitten()}
</g></svg>'''

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "character.svg")
open(out, "w").write(presenter())
print("wrote", out)
