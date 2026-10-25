"""The @techinsixty bag head: an original anonymous dev with a paper-bag head (marker X eyes, zigzag grin, creases,
torn bottom edge) in a dark grey-green sweatshirt. Flat outlines, two-bone arm rig, marker brows, lip sync.
Run: python3 make.py -> character.svg + character.json"""
import math, os

OUT = "#121212"
SKIN, SKIN_SH, SKIN_HI = "#f1d0ac", "#dcb48e", "#f8e0c4"
HAIR, HAIR_HI = "#161616", "#2e2e33"
JK, JK_SH, JK_HI, STITCH = "#3d4440", "#2c3230", "#535b56", "#2c3230"     # sweatshirt
BAG, BAG_SH, BAG_HI, BAG_DK = "#c9a578", "#b08d62", "#dcbd92", "#9c7a51"
MARK = "#1c1a17"
RED = "#e5372d"
W = 6

def rng(seed):
    s = seed
    def r():
        nonlocal s
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        return s / 0x7FFFFFFF
    return r

def P(pts): return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"
def caps(x1, y1, x2, y2, w):
    return f'<path d="M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}" stroke-width="{w}" stroke-linecap="round"/>'

def hand(kind, flip=False):
    """Cartoon hand in wrist space (wrist at 0,0, fingers toward -y). Shapes are drawn twice: outlined, then filled
    without outline on top, so all parts merge into one clean silhouette."""
    fw = 15                                   # finger thickness
    palm = '<path d="M-27,-4 Q-31,-34 -24,-56 L24,-56 Q31,-34 27,-4 Q20,10 0,12 Q-20,10 -27,-4 Z"/>'
    fingers = []
    if kind in ("palm", "wave"):
        for i, (x, ln, ang) in enumerate(((-18, 42, -9), (-6, 52, -3), (7, 50, 3), (19, 40, 10))):
            a = math.radians(ang - 90); fingers.append(caps(x, -50, x + ln * math.cos(a), -50 + ln * math.sin(a), fw))
        fingers.append(caps(-24, -22, -46, -46, fw + 1))             # thumb out to the side
    elif kind == "point":
        fingers.append(caps(-14, -50, -14, -104, fw))                # index up
        for x in (-1, 11, 21): fingers.append(caps(x, -52, x, -60, fw))   # curled knuckles
        fingers.append(caps(-20, -24, 2, -36, fw + 1))               # thumb folded across
    elif kind == "thumb":
        fingers.append(caps(-22, -30, -30, -82, fw + 2))             # thumb up
        for y in (-48, -34, -20): fingers.append(caps(-14, y, 22, y, fw))  # curled fingers to the side
    shapes = "".join(fingers)
    outline = f'<g fill="none" stroke="{OUT}">{shapes.replace("stroke-width=", "data-w=")}</g>'
    # outlined pass: thicker strokes in ink, then skin strokes on top
    ink = "".join(f.replace(f'stroke-width="{w}"', f'stroke-width="{w + 2 * 4}"') for f, w in [(f, int(f.split('stroke-width="')[1].split('"')[0])) for f in fingers])
    ink = ink.replace('stroke-width="23"', 'stroke-width="25"').replace('stroke-width="24"', 'stroke-width="26"').replace('stroke-width="25"', 'stroke-width="26"')
    g = (f'<g stroke="{OUT}" fill="none">{ink}</g>'
         f'<g fill="{SKIN}" stroke="{OUT}" stroke-width="4" stroke-linejoin="round">{palm}</g>'
         f'<g stroke="{SKIN}" fill="none">{shapes}</g>'
         f'<g fill="{SKIN}" stroke="none">{palm.replace("Z\"/>", "Z\" transform=\"scale(0.86) translate(0 -3)\"/>")}</g>')
    if kind in ("palm", "wave"):
        g += f'<path d="M-14,-24 q14,8 26,-2" stroke="{SKIN_SH}" stroke-width="3" fill="none" stroke-linecap="round"/>'
    return f'<g transform="scale({-HS if flip else HS} {HS})">{g}</g>'

def fur(cx, cy, rx, ry, n, jag, seed):
    r = rng(seed); pts = []
    for i in range(n * 2):
        a = i / (n * 2) * 2 * math.pi; k = 1 + (jag * (0.5 + 0.5 * r()) if i % 2 else 0)
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    return P(pts)

def kitten(kx=800, ky=484):
    eye = lambda x, y, r: (f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r * 1.08}" fill="{AMBER}" stroke="{OUT}" stroke-width="3"/>'
                           f'<ellipse cx="{x + 1}" cy="{y + 2}" rx="{r * 0.55}" ry="{r * 0.78}" fill="#120f0a"/>'
                           f'<circle cx="{x + r * 0.35}" cy="{y - r * 0.4}" r="{r * 0.32}" fill="#fff"/><circle cx="{x - r * 0.3}" cy="{y + r * 0.45}" r="{r * 0.14}" fill="#fff"/>')
    return f'''<g id="cat">
  <g id="tail"><path d="M{kx + 70},{ky + 105} C{kx + 140},{ky + 100} {kx + 160},{ky + 30} {kx + 128},{ky - 18} C{kx + 120},{ky - 30} {kx + 102},{ky - 26} {kx + 108},{ky - 10}
     C{kx + 130},{ky + 30} {kx + 116},{ky + 72} {kx + 62},{ky + 82} Z" fill="{CAT}" stroke="{OUT}" stroke-width="4" stroke-linejoin="round"/>
     <path d="M{kx + 128},{ky + 6} q12,30 -4,58" stroke="{CAT_HI}" stroke-width="5" fill="none" stroke-linecap="round"/></g>
  <path d="{fur(kx + 10, ky + 92, 86, 52, 22, 0.1, 4)}" fill="{CAT}" stroke="{OUT}" stroke-width="4" stroke-linejoin="round"/>
  <path d="M{kx - 58},{ky + 128} q-12,-28 8,-40 q24,-6 26,22 q0,24 -34,18 Z M{kx - 4},{ky + 134} q-10,-28 10,-38 q24,-4 24,22 q-2,24 -34,16 Z" fill="{CAT}" stroke="{OUT}" stroke-width="4" stroke-linejoin="round"/>
  <path d="M{kx - 46},{ky + 124} l2,-8 M{kx - 34},{ky + 126} l1,-8 M{kx + 8},{ky + 130} l2,-8 M{kx + 20},{ky + 130} l1,-8" stroke="{CAT_HI}" stroke-width="3" stroke-linecap="round"/>
  <path d="M{kx - 74},{ky - 30} L{kx - 82},{ky - 104} L{kx - 26},{ky - 58} Z" fill="{CAT}" stroke="{OUT}" stroke-width="4" stroke-linejoin="round"/>
  <path d="M{kx - 70},{ky - 40} L{kx - 74},{ky - 88} L{kx - 38},{ky - 60} Z" fill="{PINK}"/>
  <g id="cat-ear"><path d="M{kx + 26},{ky - 58} L{kx + 82},{ky - 102} L{kx + 72},{ky - 26} Z" fill="{CAT}" stroke="{OUT}" stroke-width="4" stroke-linejoin="round"/>
     <path d="M{kx + 36},{ky - 58} L{kx + 72},{ky - 86} L{kx + 64},{ky - 36} Z" fill="{PINK}"/></g>
  <path d="{fur(kx, ky, 82, 70, 24, 0.12, 8)}" fill="{CAT}" stroke="{OUT}" stroke-width="4" stroke-linejoin="round"/>
  <path d="M{kx - 50},{ky - 44} q46,-22 96,-2" stroke="{CAT_HI}" stroke-width="5" fill="none" stroke-linecap="round" opacity="0.8"/>
  <g id="cat-eyes-open">{eye(kx - 32, ky + 4, 21)}{eye(kx + 32, ky + 4, 21)}</g>
  <g id="cat-eyes-shut" opacity="0"><path d="M{kx - 52},{ky + 6} q20,14 40,0 M{kx + 12},{ky + 6} q20,14 40,0" stroke="{AMBER}" stroke-width="5" fill="none" stroke-linecap="round"/></g>
  <path d="M{kx - 7},{ky + 30} l14,0 l-7,8 Z" fill="{PINK}"/>
  <path d="M{kx - 14},{ky + 42} q7,8 14,0 q7,8 14,0" stroke="#5a4848" stroke-width="3" fill="none" stroke-linecap="round"/>
  <path d="M{kx - 4},{ky + 46} q4,16 10,0 Z" fill="{PINK}" stroke="{OUT}" stroke-width="2"/>
  <path d="M{kx - 60},{ky + 26} l-40,-6 M{kx - 60},{ky + 36} l-38,6 M{kx + 60},{ky + 26} l40,-6 M{kx + 60},{ky + 36} l38,6" stroke="#8c8f9c" stroke-width="2.5" stroke-linecap="round"/>
</g>'''

# ------------------------------------------------------------------ layout (svg coords)
HEAD = (600, 320)
SHL, SHR = (478, 610), (722, 610)
U, F = 96, 112
HS = 1.2                                     # hand scale

def smooth(pts, closed=True, k=0.8):
    n = len(pts); d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f} "
    for i in range(n if closed else n - 1):
        p0, p1, p2, p3 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 6, p1[1] + (p2[1] - p0[1]) * k / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) * k / 6, p2[1] - (p3[1] - p1[1]) * k / 6)
        d += f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} "
    return d + ("Z" if closed else "")

# ------------------------------------------------------------------ head: paper bag (local coords, centre 0,0)
def bag_shape():
    # slightly flared bag, torn zigzag bottom
    n = 14; teeth = []
    for i in range(n + 1):
        x = 172 - i * 344 / n
        teeth.append((x, 158 + (16 if i % 2 else 0) + (i % 3) * 2))
    return P([(-150, -250), (150, -262), (172, 150)] + teeth[1:-1] + [(-172, 156)])

def zig(y0, amp, curve=0.0, x0=-104, x1=110, n=8):
    pts = []
    for i in range(n + 1):
        t = i / n; x = x0 + (x1 - x0) * t
        pts.append(f"{x:.0f},{y0 + (amp if i % 2 else -amp) - curve * (1 - (2 * t - 1) ** 2):.0f}")
    return "M" + " L".join(pts)

def head():
    chin = (f'<path d="M-70,140 Q-62,214 0,222 Q62,214 70,140 Z" fill="{SKIN}" stroke="{OUT}" stroke-width="{W - 1}"/>'
            f'<path d="M-68,150 Q0,196 68,150 L70,140 L-70,140 Z" fill="{SKIN_SH}"/>'
            f'<path d="M-22,194 Q0,203 22,194" stroke="#c07a72" stroke-width="5" fill="none" stroke-linecap="round" opacity="0.7"/>')
    rim = (f'<path d="M-150,-250 L150,-262 L156,-196 L-154,-186 Z" fill="{BAG_HI}" stroke="{OUT}" stroke-width="{W - 1}" stroke-linejoin="round"/>'
           f'<path d="M-6,-255 L14,-214 L30,-257" fill="{BAG_SH}" stroke="{OUT}" stroke-width="3" stroke-linejoin="round"/>')
    shade = (f'<path d="M100,-194 L156,-196 L172,150 L120,162 Z" fill="{BAG_SH}" opacity="0.75"/>'
             f'<path d="M-154,-186 L-120,-188 L-132,156 L-172,156 Z" fill="{BAG_HI}" opacity="0.5"/>'
             f'<path d="M-40,-160 L-10,-110 L120,-150 M-150,10 L-90,40 L-118,150 M70,20 L152,96 M40,-190 L54,-140 M-20,110 L10,170" '
             f'stroke="{BAG_DK}" stroke-width="3" fill="none" opacity="0.75" stroke-linejoin="round"/>'
             f'<path d="M-60,-150 L-14,-100 M110,30 L80,120" stroke="{BAG_HI}" stroke-width="4" fill="none" opacity="0.8"/>')
    def X(cx, cy, s=38):
        return (f'<path d="M{cx - s},{cy - s} L{cx + s * 0.9},{cy + s * 1.05} M{cx + s * 0.95},{cy - s * 0.95} L{cx - s * 0.9},{cy + s}" '
                f'stroke="{MARK}" stroke-width="17" stroke-linecap="round"/>')
    eyes = (f'<g id="eyes-open">{X(-66, -40)}{X(70, -44)}</g>'
            f'<g id="eyes-shut" opacity="0"><path d="M-108,-38 L-26,-40 M30,-42 L112,-44" stroke="{MARK}" stroke-width="15" stroke-linecap="round"/></g>')
    brows = (f'<g id="brows"><g id="browL"><path d="M-106,-110 L-30,-102" stroke="{MARK}" stroke-width="11" stroke-linecap="round"/></g>'
             f'<g id="browR"><path d="M32,-106 L108,-116" stroke="{MARK}" stroke-width="11" stroke-linecap="round"/></g></g>')
    y = 70
    m = {
        "closed": f'<path d="{zig(y, 12)}" stroke="{MARK}" stroke-width="11" fill="none" stroke-linejoin="round" stroke-linecap="round"/>',
        "o": (f'<path d="{zig(y - 12, 9, 0, -84, 90, 6)} L90,{y + 16} Q0,{y + 46} -84,{y + 16} Z" fill="{MARK}" stroke="{MARK}" stroke-width="10" stroke-linejoin="round"/>'
              f'<path d="M-40,{y + 20} Q0,{y + 34} 40,{y + 20}" stroke="#7a2b2b" stroke-width="10" fill="none" stroke-linecap="round"/>'),
        "smile": f'<path d="{zig(y, 12, 22)}" stroke="{MARK}" stroke-width="11" fill="none" stroke-linejoin="round" stroke-linecap="round"/>',
    }
    mouths = "".join(f'<g id="m-{k}" class="mth" opacity="{1 if k == "smile" else 0}">{v}</g>' for k, v in m.items())
    return f'''
  {chin}
  <path d="{bag_shape()}" fill="{BAG}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  {shade}
  {rim}
  {eyes}
  {mouths}
  {brows}'''

# ------------------------------------------------------------------ two-bone arm: full sweatshirt sleeves, cuffs, bare hands
def tube(x0, x1, w0, w1): return f"M{x0},{-w0} L{x1},{-w1} L{x1},{w1} L{x0},{w0} Z"

def arm(side, rest_u, rest_f):
    flip = side == "R"; sx, sy = SHL if side == "L" else SHR
    up_t, fo_t = tube(-10, U + 4, 44, 36), tube(0, F - 8, 36, 30)
    cuff = tube(F - 28, F - 4, 33, 31)
    ink = lambda d, w=2 * W: f'<path d="{d}" fill="{OUT}" stroke="{OUT}" stroke-width="{w}" stroke-linejoin="round"/>'
    hands = {"L": {"point": 0, "palm": -8, "thumb": -25}, "R": {"palm": 8, "point": 0}}[side]
    hg = "".join(f'<g id="arm{side}-{k}" opacity="0"><g transform="translate({F} 0) rotate({90 + hr})">{hand(k, flip)}</g></g>' for k, hr in hands.items())
    fore = f'transform="rotate({rest_f} {U} 0)"'
    return (f'<g id="arm{side}" transform="rotate({rest_u} {sx} {sy})"><g transform="translate({sx} {sy})">'
            f'{ink(up_t)}<g class="fore" {fore}><g transform="translate({U} 0)">{ink(fo_t)}<circle r="{38 + W}" fill="{OUT}"/></g></g>'
            f'<path d="{up_t}" fill="{JK}"/><circle r="44" fill="{JK}"/>'
            f'<path d="M6,-30 L{U * 0.8:.0f},-26" stroke="{JK_HI}" stroke-width="8" stroke-linecap="round"/>'
            f'<g class="fore" {fore}><g transform="translate({U} 0)">{hg}<path d="{fo_t}" fill="{JK}"/><circle r="38" fill="{JK}"/>'
            f'<path d="{cuff}" fill="{JK_SH}" stroke="{OUT}" stroke-width="4" stroke-linejoin="round"/>'
            f'<path d="M8,16 L{F - 36},14" stroke="{JK_SH}" stroke-width="7" stroke-linecap="round"/></g></g>'
            f'</g></g>')

# ------------------------------------------------------------------ torso: loose sweatshirt with a crew neck
def body():
    sw = "M528,530 C484,540 452,570 446,612 L432,1010 L768,1010 L754,612 C748,570 716,540 672,530 Z"
    return f'''
  <path d="M568,470 L566,552 Q600,566 634,552 L632,470 Z" fill="{SKIN}" stroke="{OUT}" stroke-width="{W}"/>
  <path d="M568,488 Q600,520 632,488 L632,470 L568,470 Z" fill="{SKIN_SH}" opacity="0.8"/>
  <path d="{sw}" fill="{JK}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="M640,1010 L768,700 L768,1010 Z" fill="{JK_SH}" opacity="0.6"/>
  <path d="M548,536 Q600,586 652,536" fill="{SKIN}" stroke="{OUT}" stroke-width="{W}"/>
  <path d="M538,532 Q600,604 662,532" stroke="{JK_SH}" stroke-width="12" fill="none"/>
  <path d="M538,532 Q600,604 662,532" stroke="{OUT}" stroke-width="3" fill="none"/>
  <path d="M520,700 L560,640 M680,760 L640,860" stroke="{OUT}" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.6"/>'''

# ------------------------------------------------------------------ poses
POSES_L = {
    "rest":  dict(u=100, f=-6, hand="palm"),
    "up":    dict(u=160, f=110, hand="point"),
    "card":  dict(u=156, f=94, hand="point"),
    "palms": dict(u=138, f=100, hand="palm"),
    "shrug": dict(u=128, f=86, hand="palm"),
    "thumb": dict(u=128, f=156, hand="thumb"),
    "wave":  dict(u=162, f=106, hand="palm", wave=True),
}
POSES_R = {"rest": dict(u=80, f=6, hand="palm"), "palms": dict(u=42, f=-100, hand="palm"), "shrug": dict(u=52, f=-86, hand="palm"),
           "up": dict(u=20, f=-110, hand="point")}

def svg():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1000" width="1200" height="1000">
<g id="pres-body">
  {body()}
  <g id="head" transform="translate({HEAD[0]} {HEAD[1]})">{head()}</g>
  {arm("L", POSES_L["rest"]["u"], POSES_L["rest"]["f"])}{arm("R", POSES_R["rest"]["u"], POSES_R["rest"]["f"])}
</g></svg>'''

here = os.path.dirname(os.path.abspath(__file__))
open(os.path.join(here, "character.svg"), "w").write(svg())
import json
json.dump({
    "type": "svg", "file": "character.svg", "x": -60, "y": 1130, "width": 1200,
    "head_origin": f"{HEAD[0]} {HEAD[1] + 150}", "avatar_view": "360 60 480 480",
    "poses": list(POSES_L),
    "arms": [{"id": "armL", "shoulder": list(SHL), "upper": U, "hands": ["point", "palm", "thumb"], "poses": POSES_L},
             {"id": "armR", "shoulder": list(SHR), "upper": U, "hands": ["palm", "point"], "poses": POSES_R}],
    "brows": {"sel": "#brows", "raise": -10, "end": "#browL"},
}, open(os.path.join(here, "character.json"), "w"), indent=1)
print("wrote character.svg + character.json")
