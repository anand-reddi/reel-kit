"""The @techinsixty chibi: an original big-head cartoon dev (messy black hair with a cowlick, sleepy half-lidded eyes,
over-ear headphones with red rings, black tee). Thick flat outlines, two-bone arm rig, brows, blinks, lip sync.
Run: python3 make.py -> character.svg + character.json"""
import math, os

OUT = "#121212"
SKIN, SKIN_SH, SKIN_HI = "#f1d0ac", "#dcb48e", "#f8e0c4"
HAIR, HAIR_HI = "#161616", "#2e2e33"
JK, JK_SH, JK_HI, STITCH = "#1a1a1c", "#111113", "#2a2a2e", "#2a2a2e"     # black tee
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
HEAD = (600, 360)
SHL, SHR = (482, 600), (718, 600)
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

# ------------------------------------------------------------------ head (local coords, face centre 0,0)
def hair_back():
    # big soft messy mop: rounded clumps with a few curled flicks at the sides and a cowlick on top
    pts = [(-150, 60), (-188, 72), (-206, 40), (-180, 20), (-212, -20), (-196, -62), (-222, -96), (-196, -132),
           (-178, -184), (-130, -220), (-80, -244), (-30, -252), (6, -286), (34, -298), (40, -270), (24, -252),
           (80, -250), (138, -226), (186, -186), (214, -140), (232, -100), (210, -84), (226, -40), (200, -10),
           (214, 34), (190, 52), (160, 40), (150, -40), (-150, -40)]
    curls = (f'<path d="M-208,-26 q-22,-6 -18,-26" stroke="{OUT}" stroke-width="5" fill="none" stroke-linecap="round"/>'
             f'<path d="M222,-38 q22,-4 20,-26" stroke="{OUT}" stroke-width="5" fill="none" stroke-linecap="round"/>')
    return f'<path d="{smooth(pts, True, 1.0)}" fill="{HAIR}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>' + curls

def fringe():
    # wavy locks falling over the forehead, each tip curling to the viewer's right
    cap = f'<path d="M-186,-104 C-176,-214 -80,-254 10,-254 C100,-252 180,-208 190,-104 Q100,-130 0,-128 Q-100,-130 -186,-104 Z" fill="{HAIR}"/>'
    locks = [(-168, -140, -146, -54), (-118, -150, -92, -66), (-66, -156, -38, -56), (-14, -158, 14, -40),
             (38, -156, 66, -62), (90, -150, 116, -74), (140, -140, 164, -56)]
    out = ""
    for x0, y0, tx, ty in locks:
        w = 64
        d = (f"M{x0 - w * 0.4},{y0} C{x0 - w * 0.6},{(y0 + ty) / 2} {tx - 26},{ty + 4} {tx},{ty} "
             f"C{tx + 10},{ty - 4} {tx + 8},{ty - 18} {tx - 4},{ty - 18} "
             f"C{tx - 2},{ty - 30} {x0 + w * 0.9},{(y0 + ty) / 2 - 10} {x0 + w * 0.8},{y0} Z")
        out += f'<path d="{d}" fill="{HAIR}" stroke="{OUT}" stroke-width="{W - 1}" stroke-linejoin="round"/>'
    hl = "".join(f'<path d="M{x},{y} q{dx},{dy} {dx * 2},{dy * 2.4}" stroke="{HAIR_HI}" stroke-width="7" fill="none" stroke-linecap="round"/>'
                 for x, y, dx, dy in ((-110, -214, 12, 18), (-30, -230, 14, 20), (60, -222, 14, 20), (132, -196, 12, 18)))
    return out + cap + hl

def headphones(front):
    if not front:   # far cup, peeking out behind the face on the viewer's right
        return (f'<ellipse cx="166" cy="34" rx="42" ry="58" fill="#1d1d20" stroke="{OUT}" stroke-width="{W}"/>'
                f'<ellipse cx="174" cy="34" rx="26" ry="40" fill="none" stroke="{RED}" stroke-width="9"/>')
    band = f'<path d="M-170,-10 C-190,-150 -110,-250 -10,-262" stroke="{OUT}" stroke-width="34" fill="none" stroke-linecap="round"/><path d="M-170,-10 C-190,-150 -110,-250 -10,-262" stroke="#26262b" stroke-width="22" fill="none" stroke-linecap="round"/>'
    slider = f'<rect x="-196" y="-120" width="30" height="40" rx="6" fill="#55555c" stroke="{OUT}" stroke-width="4" transform="rotate(-14 -181 -100)"/>'
    cup = (f'<ellipse cx="-172" cy="36" rx="52" ry="68" fill="#1d1d20" stroke="{OUT}" stroke-width="{W}"/>'
           f'<ellipse cx="-180" cy="36" rx="36" ry="50" fill="#141416" stroke="{RED}" stroke-width="11"/>'
           f'<path d="M-150,-14 C-136,6 -134,64 -150,86" stroke="#2c2c31" stroke-width="10" fill="none" stroke-linecap="round"/>')
    return band + slider + cup

def eyes():
    def eye(cx):
        sc = f"M{cx - 40},0 L{cx + 40},0 Q{cx + 32},28 {cx},30 Q{cx - 32},28 {cx - 40},0 Z"
        return (f'<clipPath id="e{cx}"><path d="{sc}"/></clipPath><path d="{sc}" fill="#ffffff"/>'
                f'<g clip-path="url(#e{cx})"><circle cx="{cx + 4}" cy="6" r="21" fill="#6a3a14"/><circle cx="{cx + 4}" cy="8" r="11" fill="#2a1408"/>'
                f'<circle cx="{cx + 12}" cy="6" r="4" fill="#fff" opacity="0.9"/></g>'
                f'<path d="M{cx - 46},-2 L{cx + 44},-2" stroke="{OUT}" stroke-width="10" stroke-linecap="round"/>'
                f'<path d="{sc}" fill="none" stroke="{OUT}" stroke-width="3"/>')
    shut = "".join(f'<path d="M{cx - 44},6 Q{cx},20 {cx + 42},6" stroke="{OUT}" stroke-width="9" fill="none" stroke-linecap="round"/>' for cx in (-64, 64))
    return f'<g id="eyes-open">{eye(-64)}{eye(64)}</g><g id="eyes-shut" opacity="0">{shut}</g>'

def mouths():
    y = 112
    m = {
        "closed": f'<path d="M-12,{y} Q2,{y + 4} 14,{y}" stroke="{OUT}" stroke-width="5" fill="none" stroke-linecap="round"/>',
        "o": f'<path d="M-16,{y - 4} Q0,{y - 6} 16,{y - 4} Q14,{y + 14} 0,{y + 16} Q-14,{y + 14} -16,{y - 4} Z" fill="#5a1f22" stroke="{OUT}" stroke-width="4" stroke-linejoin="round"/><path d="M-8,{y + 10} Q0,{y + 5} 8,{y + 10} Q0,{y + 14} -8,{y + 10} Z" fill="#d6626a"/>',
        "smile": f'<path d="M-18,{y - 2} Q2,{y + 10} 22,{y - 6}" stroke="{OUT}" stroke-width="5" fill="none" stroke-linecap="round"/>',
    }
    return "".join(f'<g id="m-{k}" class="mth" opacity="{1 if k == "smile" else 0}">{v}</g>' for k, v in m.items())

def head():
    face = "M-150,-60 C-154,40 -120,122 -46,150 Q0,164 46,150 C120,122 154,40 150,-60 C146,-160 80,-206 0,-206 C-80,-206 -146,-160 -150,-60 Z"
    brows = (f'<g id="brows"><g id="browL"><path d="M-104,-30 Q-64,-46 -24,-34" stroke="{OUT}" stroke-width="13" fill="none" stroke-linecap="round"/></g>'
             f'<g id="browR"><path d="M104,-30 Q64,-46 24,-34" stroke="{OUT}" stroke-width="13" fill="none" stroke-linecap="round"/></g></g>')
    return f'''
  {hair_back()}
  {headphones(False)}
  <path d="{face}" fill="{SKIN}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="M46,150 C120,122 154,40 150,-60 L150,10 C140,80 110,124 60,146 Z" fill="{SKIN_SH}" opacity="0.5"/>
  {eyes()}
  <path d="M6,64 L0,80 L10,82" stroke="{SKIN_SH}" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  {mouths()}
  {brows}
  {fringe()}
  {headphones(True)}'''

# ------------------------------------------------------------------ two-bone arm: short black sleeve on the upper arm, bare forearm
def tube(x0, x1, w0, w1): return f"M{x0},{-w0} L{x1},{-w1} L{x1},{w1} L{x0},{w0} Z"

def arm(side, rest_u, rest_f):
    flip = side == "R"; sx, sy = SHL if side == "L" else SHR
    up_t, fo_t, sleeve = tube(0, U, 34, 28), tube(0, F - 4, 28, 22), tube(-6, U * 0.62, 42, 38)
    ink = lambda d, w=2 * W: f'<path d="{d}" fill="{OUT}" stroke="{OUT}" stroke-width="{w}" stroke-linejoin="round"/>'
    hands = {"L": {"point": 0, "palm": -8, "thumb": -25}, "R": {"palm": 8, "point": 0}}[side]
    hg = "".join(f'<g id="arm{side}-{k}" opacity="0"><g transform="translate({F} 0) rotate({90 + hr})">{hand(k, flip)}</g></g>' for k, hr in hands.items())
    fore = f'transform="rotate({rest_f} {U} 0)"'
    return (f'<g id="arm{side}" transform="rotate({rest_u} {sx} {sy})"><g transform="translate({sx} {sy})">'
            f'{ink(up_t)}<g class="fore" {fore}><g transform="translate({U} 0)">{ink(fo_t)}<circle r="{28 + W}" fill="{OUT}"/></g></g>'
            f'<path d="{up_t}" fill="{SKIN}"/>'
            f'<g class="fore" {fore}><g transform="translate({U} 0)">{hg}<path d="{fo_t}" fill="{SKIN}"/><circle r="28" fill="{SKIN}"/>'
            f'<path d="M4,12 L{F - 20},10" stroke="{SKIN_SH}" stroke-width="7" stroke-linecap="round" opacity="0.6"/></g></g>'
            f'<path d="{sleeve}" fill="{JK}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/><circle r="42" fill="{JK}"/>'
            f'<path d="M10,-26 L{U * 0.55:.0f},-24" stroke="{JK_HI}" stroke-width="7" stroke-linecap="round"/>'
            f'</g></g>')

# ------------------------------------------------------------------ torso: black tee
def body():
    tee = "M540,540 C500,548 470,566 462,600 L452,1010 L748,1010 L738,600 C730,566 700,548 660,540 Z"
    return f'''
  <path d="M568,480 L566,560 Q600,574 634,560 L632,480 Z" fill="{SKIN}" stroke="{OUT}" stroke-width="{W}"/>
  <path d="M568,500 Q600,526 632,500 L632,480 L568,480 Z" fill="{SKIN_SH}" opacity="0.8"/>
  <path d="{tee}" fill="{JK}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="M556,544 Q600,592 644,544" fill="{SKIN}" stroke="{OUT}" stroke-width="{W}"/>
  <path d="M548,540 Q600,604 652,540" stroke="{JK_HI}" stroke-width="7" fill="none"/>
  <path d="M700,600 C716,700 722,850 724,1010" stroke="{JK_HI}" stroke-width="8" fill="none" opacity="0.7"/>'''

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
