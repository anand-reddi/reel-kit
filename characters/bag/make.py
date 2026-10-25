"""The @techinsixty bag head: an original anonymous dev wearing a crumpled paper bag (marker X eyes, crooked zigzag
grin, torn bottom edge sitting on the collar) and an oversized dark sweatshirt. Two-bone arm rig, lip sync.
Run: python3 make.py -> character.svg + character.json"""
import math, os

OUT = "#121212"
SKIN, SKIN_SH, SKIN_HI = "#f5dccb", "#e2bba6", "#fbeadf"
HAIR, HAIR_HI = "#161616", "#2e2e33"
JK, JK_SH, JK_HI, STITCH = "#383e3a", "#2a2f2c", "#5c625d", "#2a2f2c"     # sweatshirt
JK_LT = "#4a504c"
BAG, BAG_SH, BAG_HI, BAG_DK = "#c6a374", "#ad8a5c", "#d5b78a", "#94744b"
MARK, CREASE, LIP = "#1b1915", "#3b2d1d", "#e9aaa0"
RED = "#e5372d"
W = 5

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
HEAD = (600, 336)
SHL, SHR = (424, 640), (776, 640)
U, F = 112, 118
HS = 1.2                                     # hand scale

def smooth(pts, closed=True, k=0.8):
    n = len(pts); d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f} "
    for i in range(n if closed else n - 1):
        p0, p1, p2, p3 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 6, p1[1] + (p2[1] - p0[1]) * k / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) * k / 6, p2[1] - (p3[1] - p1[1]) * k / 6)
        d += f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} "
    return d + ("Z" if closed else "")

# ------------------------------------------------------------------ head: crumpled paper bag (local coords, centre 0,0)
# The bag sits low: its torn bottom edge stops just above the collar, so only a sliver of chin and neck shows.
def bag_pts():
    top = [(-170, -198), (-120, -186), (-50, -190), (16, -192), (30, -168), (46, -196), (110, -200), (170, -206)]
    right = [(174, -150), (178, -40), (182, 70), (186, 168)]
    n, teeth = 17, []
    for i in range(1, n):
        x = 186 - i * 370 / n
        teeth.append((x, 168 + (15 if i % 2 else 0) + (5 if i % 4 == 1 else 0) - (3 if i % 5 == 2 else 0)))
    left = [(-184, 166), (-178, 40), (-174, -80), (-178, -150)]
    return top + right + teeth + left

def zig(amp, rise, drop=0, hook=16, n=10):
    # crooked marker zigzag: rises toward the right end and hooks up into a smirk
    x0, x1, pts = -118, 116, []
    for i in range(n + 1):
        t = i / n; x = x0 + (x1 - x0) * t; yb = 100 + drop - rise * t ** 2.2
        pts.append((x, yb + (amp if i % 2 else -amp)))
    ex, ey = pts[-1]; pts.append((ex + 10, ey - hook * 0.55)); pts.append((ex + 16, ey - hook))
    return "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in pts)

def brush(p1, p2, w1, w2):
    (x1, y1), (x2, y2) = p1, p2; dx, dy = x2 - x1, y2 - y1; L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L
    q = [(x1 + nx * w1 / 2, y1 + ny * w1 / 2), (x2 + nx * w2 / 2, y2 + ny * w2 / 2), (x2 - nx * w2 / 2, y2 - ny * w2 / 2), (x1 - nx * w1 / 2, y1 - ny * w1 / 2)]
    return f'<path d="{P(q)}" fill="{MARK}" stroke="{MARK}" stroke-width="3" stroke-linejoin="round"/>'

def X(cx, cy, w=86, h=100):
    return (brush((cx - w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), 22, 18) +
            brush((cx + w / 2 - 4, cy - h / 2 + 2), (cx - w / 2 + 2, cy + h / 2), 21, 19))

def head():
    outline = P(bag_pts())
    chin = (f'<path d="M-74,130 L74,130 L70,176 Q0,236 -70,176 Z" fill="{SKIN}" stroke="{OUT}" stroke-width="{W - 1}" stroke-linejoin="round"/>'
            f'<path d="M-70,130 L70,130 L68,176 Q0,206 -68,176 Z" fill="{LIP}"/>'
            f'<path d="M-30,186 Q0,196 30,186" stroke="{SKIN_SH}" stroke-width="4" fill="none" stroke-linecap="round"/>')
    facets = "".join(f'<path d="{P(p)}" fill="{c}" opacity="{o}"/>' for p, c, o in (
        ([(-200, -230), (200, -230), (200, -170), (60, -160), (-80, -150), (-200, -146)], BAG_HI, 0.9),        # folded rim
        ([(-200, -146), (-80, -150), (-36, -70), (-200, 10)], BAG_HI, 0.45),                                    # left light patch
        ([(126, -168), (200, -170), (200, 210), (150, 210), (118, 60)], BAG_SH, 0.9),                          # right side in shade
        ([(52, 110), (200, 30), (200, 210), (30, 210)], BAG_DK, 0.55),                                          # lower right
        ([(-24, 20), (44, -18), (96, 56), (20, 104)], BAG_SH, 0.45),                                           # centre crease
        ([(-200, 80), (-110, 112), (-70, 210), (-200, 210)], BAG_SH, 0.6),                                     # lower left
        ([(-120, -60), (-60, -80), (-80, 20)], BAG_HI, 0.35),
    ))
    creases = (f'<path d="M-184,-40 L-132,-56 L-96,-92 M-60,-150 L-18,-104 L60,-124 M118,40 L110,128 M-142,96 L-122,160 '
               f'M66,-60 L150,-112 M-20,140 L2,176 M30,-168 L22,-140" stroke="{CREASE}" stroke-width="2.6" fill="none" stroke-linejoin="round" stroke-linecap="round"/>'
               f'<path d="M-150,-170 L120,-180" stroke="{BAG_DK}" stroke-width="3" fill="none" opacity="0.7"/>'
               f'<path d="M-110,-128 L-40,-118 M-150,-100 L-120,-96" stroke="#e6cc9f" stroke-width="7" fill="none" stroke-linecap="round" opacity="0.8"/>')
    flap = f'<path d="M16,-192 L30,-168 L46,-196 Z" fill="{BAG_DK}" stroke="{OUT}" stroke-width="2.5" stroke-linejoin="round"/>'
    E1, E2 = (-64, -6), (70, -10)
    squash = lambda c: f'transform="translate({c[0]} {c[1]}) scale(1 0.28) translate({-c[0]} {-c[1]})"'
    eyes = (f'<g id="xeyes"><g id="eyes-open">{X(*E1)}{X(*E2)}</g>'
            f'<g id="eyes-shut" opacity="0"><g {squash(E1)}>{X(*E1)}</g><g {squash(E2)}>{X(*E2)}</g></g></g>')
    m = {
        "closed": f'<path d="{zig(11, 18, hook=14)}" stroke="{MARK}" stroke-width="11" fill="none" stroke-linejoin="miter" stroke-miterlimit="6" stroke-linecap="round"/>',
        "o": f'<path d="{zig(20, 20, drop=6, hook=18)}" stroke="{MARK}" stroke-width="12" fill="none" stroke-linejoin="miter" stroke-miterlimit="6" stroke-linecap="round"/>',
        "smile": f'<path d="{zig(13, 26, hook=20)}" stroke="{MARK}" stroke-width="11" fill="none" stroke-linejoin="miter" stroke-miterlimit="6" stroke-linecap="round"/>',
    }
    mouths = "".join(f'<g id="m-{k}" class="mth" opacity="{1 if k == "smile" else 0}">{v}</g>' for k, v in m.items())
    return f'''
  {chin}
  <clipPath id="bagclip"><path d="{outline}"/></clipPath>
  <path d="{outline}" fill="{BAG}"/>
  <g clip-path="url(#bagclip)">{facets}{creases}</g>
  {flap}
  <path d="{outline}" fill="none" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  {eyes}
  {mouths}'''

# ------------------------------------------------------------------ two-bone arm: oversized sweatshirt sleeves, cuffs, bare hands
def tube(x0, x1, w0, w1): return f"M{x0},{-w0} L{x1},{-w1} L{x1},{w1} L{x0},{w0} Z"

def arm(side, rest_u, rest_f):
    flip = side == "R"; sx, sy = SHL if side == "L" else SHR
    up_t, fo_t = tube(0, U + 4, 40, 37), tube(0, F - 6, 38, 32)
    cuff = tube(F - 30, F - 4, 35, 33)
    ink = lambda d, w=2 * W: f'<path d="{d}" fill="{OUT}" stroke="{OUT}" stroke-width="{w}" stroke-linejoin="round"/>'
    hands = {"L": {"point": 0, "palm": -8, "thumb": -25}, "R": {"palm": 8, "point": 0}}[side]
    hg = "".join(f'<g id="arm{side}-{k}" opacity="0"><g transform="translate({F} 0) rotate({90 + hr})">{hand(k, flip)}</g></g>' for k, hr in hands.items())
    fore = f'transform="rotate({rest_f} {U} 0)"'
    return (f'<g id="arm{side}" transform="rotate({rest_u} {sx} {sy})"><g transform="translate({sx} {sy})">'
            f'{ink(up_t)}<g class="fore" {fore}><g transform="translate({U} 0)">{ink(fo_t)}<circle r="{38 + W}" fill="{OUT}"/></g></g>'
            f'<path d="{up_t}" fill="{JK}"/><circle r="48" fill="{JK}"/>'
            f'<path d="M14,-28 L{U * 0.8:.0f},-26" stroke="{JK_HI}" stroke-width="7" stroke-linecap="round"/>'
            f'<g class="fore" {fore}><g transform="translate({U} 0)">{hg}<path d="{fo_t}" fill="{JK}"/><circle r="38" fill="{JK}"/>'
            f'<path d="{cuff}" fill="{JK_SH}" stroke="{OUT}" stroke-width="4" stroke-linejoin="round"/>'
            f'<path d="M10,16 L{F - 38},14" stroke="{JK_SH}" stroke-width="7" stroke-linecap="round"/></g></g>'
            f'</g></g>')

# ------------------------------------------------------------------ torso: oversized sweatshirt, drooping shoulders, high crew collar
def body():
    sw = "M522,534 Q600,522 678,534 C750,542 822,572 836,652 L846,1010 L354,1010 L364,652 C378,572 450,542 522,534 Z"
    return f'''
  <clipPath id="swclip"><path d="{sw}"/></clipPath>
  <path d="{sw}" fill="{JK}"/>
  <g clip-path="url(#swclip)">
    <path d="M400,1010 L840,640 L840,1010 Z" fill="{JK_LT}"/>
    <path d="M560,1010 L840,770 L840,1010 Z" fill="{JK_HI}" opacity="0.7"/>
      </g>
  <path d="{sw}" fill="none" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="M540,470 L540,580 Q600,604 660,580 L660,470 Z" fill="{SKIN}" stroke="{OUT}" stroke-width="{W}"/>
  <path d="M540,470 L660,470 L660,540 Q600,560 540,540 Z" fill="{SKIN_SH}" opacity="0.7"/>
  <path d="M520,548 Q600,628 680,548" stroke="{JK_SH}" stroke-width="24" fill="none" stroke-linecap="round"/>
  <path d="M520,536 Q600,616 680,536" stroke="{OUT}" stroke-width="3.5" fill="none"/>
  <path d="M514,560 Q600,644 686,560" stroke="{OUT}" stroke-width="3.5" fill="none"/>
  <path d="M536,600 C520,640 506,690 500,760 M700,606 C716,660 724,700 726,760 M650,700 L612,790" stroke="{OUT}" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.75"/>'''

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
    "head_origin": "600 540", "avatar_view": "370 110 460 460",
    "poses": list(POSES_L),
    "arms": [{"id": "armL", "shoulder": list(SHL), "upper": U, "hands": ["point", "palm", "thumb"], "poses": POSES_L},
             {"id": "armR", "shoulder": list(SHR), "upper": U, "hands": ["palm", "point"], "poses": POSES_R}],
    "brows": {"sel": "#xeyes", "raise": -8},
}, open(os.path.join(here, "character.json"), "w"), indent=1)
print("wrote character.svg + character.json")
