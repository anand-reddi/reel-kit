"""The @techinsixty dev: a young developer in a black cap, black sunglasses, light beard, black denim jacket over a
white tee, with the black kitten on his shoulder. Original flat-vector character (soft cartoon style).
Arms are real rigs (#armL / #armR rotate at the elbow, hand shapes swap mid-swing) driven by character.json "arms".
Run: python3 make.py -> character.svg"""
import math, os

OUT = "#221d1a"
SKIN, SKIN_SH, SKIN_HI = "#e4b08a", "#cc9470", "#f0c7a6"
HAIR, HAIR_HI = "#17161a", "#3c3a44"
JK, JK_SH, JK_HI, STITCH = "#202227", "#16171b", "#2f3138", "#4a4c55"     # black denim
TEE, TEE_SH = "#f3f1ec", "#d9d6cf"
CAP, CAP_SH, CAP_HI = "#141417", "#0b0b0d", "#26262b"
CAT, CAT_SH, CAT_HI, PINK, AMBER = "#18181d", "#0c0c10", "#34343f", "#f08fa0", "#f3b33d"
W = 3.5

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
    g = (f'<g stroke="{OUT}" fill="none">{ink}</g>'
         f'<g fill="{SKIN}" stroke="{OUT}" stroke-width="4" stroke-linejoin="round">{palm}</g>'
         f'<g stroke="{SKIN}" fill="none">{shapes}</g>'
         f'<g fill="{SKIN}" stroke="none">{palm.replace("Z\"/>", "Z\" transform=\"scale(0.86) translate(0 -3)\"/>")}</g>')
    if kind in ("palm", "wave"):
        g += f'<path d="M-14,-24 q14,8 26,-2" stroke="{SKIN_SH}" stroke-width="3" fill="none" stroke-linecap="round"/>'
    return f'<g transform="scale({-1.25 if flip else 1.25} 1.25)">{g}</g>'

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
HEAD = (600, 372)
SHL, SHR = (440, 612), (760, 612)          # shoulder joints
U, F = 118, 150                             # upper arm, forearm lengths

# ------------------------------------------------------------------ head (local coords, face centre 0,0)
def cap():
    """Black baseball cap seen from the front: structured crown, curved bill projecting toward the viewer."""
    crown = "M-134,-118 C-142,-212 -78,-266 0,-268 C78,-266 142,-212 134,-118 Q0,-136 -134,-118 Z"
    seams = (f'<path d="M0,-266 Q-54,-230 -72,-126 M0,-266 Q54,-230 72,-126" stroke="{CAP_SH}" stroke-width="3" fill="none"/>'
             f'<path d="M-108,-186 Q-62,-246 -8,-256" stroke="{CAP_HI}" stroke-width="9" fill="none" stroke-linecap="round" opacity="0.8"/>'
             f'<path d="M-58,-130 Q-64,-194 -38,-248 M58,-130 Q64,-194 38,-248" stroke="{STITCH}" stroke-width="1.6" stroke-dasharray="4 5" fill="none" opacity="0.7"/>')
    button = f'<ellipse cx="0" cy="-267" rx="13" ry="6" fill="{CAP}" stroke="{OUT}" stroke-width="2.5"/>'
    logo = f'<path d="M-30,-200 l-16,14 l16,14 M30,-200 l16,14 l-16,14 M10,-206 l-20,40" stroke="#2c2c32" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    bill = "M-148,-124 C-98,-140 98,-140 148,-124 C160,-106 140,-86 98,-80 C58,-74 -58,-74 -98,-80 C-140,-86 -160,-106 -148,-124 Z"
    under = "M-142,-102 C-106,-88 106,-88 142,-102 C124,-84 68,-74 0,-73 C-68,-74 -124,-84 -142,-102 Z"
    return (f'<path d="{crown}" fill="{CAP}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>{seams}{button}{logo}'
            f'<path d="{bill}" fill="{CAP_HI}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>'
            f'<path d="M-128,-116 C-78,-130 78,-130 128,-116" stroke="{STITCH}" stroke-width="2" stroke-dasharray="6 6" fill="none"/>'
            f'<path d="M-118,-106 C-68,-118 68,-118 118,-106" stroke="{STITCH}" stroke-width="2" stroke-dasharray="6 6" fill="none" opacity="0.7"/>'
            f'<path d="{under}" fill="{CAP_SH}"/>')

def sunglasses():
    lens = lambda cx: (f"M{cx - 42},{-18} Q{cx},{-24} {cx + 42},{-18} Q{cx + 44},{8} {cx + 32},{24} Q{cx},{36} {cx - 32},{24} Q{cx - 44},{8} {cx - 42},{-18} Z")
    sheen = "".join(f'<path d="M{cx - 28},{-10} L{cx - 10},{-12} L{cx - 32},{22} L{cx - 42},{12} Z" fill="#ffffff" opacity="0.14"/>'
                    f'<path d="M{cx + 6},{-12} L{cx + 13},{-12} L{cx - 9},{28} L{cx - 16},{28} Z" fill="#ffffff" opacity="0.08"/>' for cx in (-52, 52))
    return (f'<path d="M-94,-12 L-116,-6 M94,-12 L116,-6" stroke="{OUT}" stroke-width="7" stroke-linecap="round"/>'
            + "".join(f'<path d="{lens(cx)}" fill="#0d0e11" stroke="{OUT}" stroke-width="5" stroke-linejoin="round"/>' for cx in (-52, 52))
            + f'<path d="M-94,-18 Q-52,-28 -10,-18 M10,-18 Q52,-28 94,-18" stroke="#0a0a0c" stroke-width="10" fill="none" stroke-linecap="round"/>'
              f'<path d="M-10,-12 Q0,-18 10,-12" stroke="{OUT}" stroke-width="6" fill="none" stroke-linecap="round"/>' + sheen)

def mouths():
    lip = "#9a5048"; y = 98
    m = {
        "closed": f'<path d="M-22,{y} Q2,{y + 6} 24,{y - 2}" stroke="{lip}" stroke-width="4.5" fill="none" stroke-linecap="round"/>',
        "o": (f'<path d="M-22,{y - 4} Q2,{y - 8} 26,{y - 4} Q22,{y + 20} 2,{y + 22} Q-18,{y + 20} -22,{y - 4} Z" fill="#4e1c1e" stroke="{OUT}" stroke-width="3" stroke-linejoin="round"/>'
              f'<path d="M-18,{y - 2} Q2,{y - 5} 22,{y - 2} L20,{y + 4} Q2,{y + 2} -16,{y + 4} Z" fill="#f6f2ea"/><path d="M-10,{y + 15} Q2,{y + 8} 14,{y + 15} Q2,{y + 21} -10,{y + 15} Z" fill="#d6626a"/>'),
        "smile": f'<path d="M-24,{y} Q4,{y + 12} 30,{y - 6}" stroke="{lip}" stroke-width="5" fill="none" stroke-linecap="round"/><path d="M30,{y - 6} l6,-5" stroke="{lip}" stroke-width="4" stroke-linecap="round"/>',
    }
    return "".join(f'<g id="m-{k}" class="mth" opacity="{1 if k == "smile" else 0}">{v}</g>' for k, v in m.items())

def head():
    # tall face, sharp angular jaw (straight planes to a defined chin)
    face = "M-114,-96 L-116,22 L-90,108 L-32,150 Q0,158 32,150 L90,108 L116,22 L114,-96 C106,-176 60,-206 0,-206 C-60,-206 -106,-176 -114,-96 Z"
    jaw_sh = "M90,108 L116,22 L114,-30 L104,24 L80,104 L30,142 L32,150 Z"
    cheek = "M-100,40 L-78,96 M100,40 L78,96"
    beard = ("M-116,10 L-90,108 L-32,150 Q0,158 32,150 L90,108 L116,10 L102,14 L80,92 Q52,116 26,118 Q0,110 -26,118 Q-52,116 -80,92 L-102,14 Z")
    moust = "M-34,86 Q-14,74 0,80 Q14,74 34,86 Q16,82 0,86 Q-16,82 -34,86 Z"
    brows = (f'<g id="brows"><g id="browL"><path d="M-96,-64 L-24,-60 L-22,-48 L-94,-50 Z" fill="{HAIR}" stroke="{OUT}" stroke-width="2" stroke-linejoin="round"/></g>'
             f'<g id="browR"><path d="M96,-64 L24,-60 L22,-48 L94,-50 Z" fill="{HAIR}" stroke="{OUT}" stroke-width="2" stroke-linejoin="round"/></g></g>')
    return f'''
  <g><ellipse cx="-117" cy="12" rx="16" ry="26" fill="{SKIN}" stroke="{OUT}" stroke-width="{W}"/><ellipse cx="117" cy="12" rx="16" ry="26" fill="{SKIN}" stroke="{OUT}" stroke-width="{W}"/>
     <path d="M-120,2 q-7,10 0,20 M120,2 q7,10 0,20" stroke="{SKIN_SH}" stroke-width="3" fill="none" stroke-linecap="round"/>
     <circle cx="122" cy="32" r="5.5" fill="#09090b"/><circle cx="120.5" cy="30.5" r="1.6" fill="#77777f"/></g>
  <path d="{face}" fill="{SKIN}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="{jaw_sh}" fill="{SKIN_SH}" opacity="0.6"/>
  <path d="{cheek}" stroke="{SKIN_SH}" stroke-width="3" stroke-linecap="round" opacity="0.8"/>
  <path d="{beard}" fill="#3b2a22" opacity="0.3"/>
  <path d="M-38,124 Q0,116 38,124 L32,150 Q0,158 -32,150 Z" fill="#2c1f1a" opacity="0.32"/>
  <path d="M-114,-96 L-116,-24 C-60,-38 60,-38 116,-24 L114,-96 Z" fill="{SKIN_SH}" opacity="0.0"/>
  <path d="M-110,-88 C-50,-72 50,-72 110,-88 L112,-70 C50,-56 -50,-56 -112,-70 Z" fill="{SKIN_SH}" opacity="0.6"/>
  <path d="{moust}" fill="#2c1f1a" opacity="0.5"/>
  <path d="M-114,-86 L-116,14 L-104,16 L-102,-86 Z M114,-86 L116,14 L104,16 L102,-86 Z" fill="{HAIR}" opacity="0.85"/>
  {brows}
  <g id="eyes-open"></g><g id="eyes-shut" opacity="0"></g>
  <path d="M6,14 L-6,60 Q2,68 16,62" stroke="#a8694a" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M8,16 L18,58" stroke="{SKIN_SH}" stroke-width="6" stroke-linecap="round" opacity="0.6"/>
  {sunglasses()}
  {mouths()}
  {cap()}'''

# ------------------------------------------------------------------ two-bone arm: shoulder -> elbow -> wrist, drawn along +x
def tube(x0, x1, w0, w1): return f"M{x0},{-w0} L{x1},{-w1} L{x1},{w1} L{x0},{w0} Z"

def arm(side, rest_u, rest_f):
    flip = side == "R"; sx, sy = SHL if side == "L" else SHR
    up_t, fo_t, cuff = tube(0, U, 46, 38), tube(0, F - 32, 38, 31), tube(F - 34, F - 6, 30, 28)
    ink = lambda d: f'<path d="{d}" fill="{OUT}" stroke="{OUT}" stroke-width="{2 * W}" stroke-linejoin="round"/>'
    hands = {"L": {"point": 0, "palm": -8, "thumb": -25}, "R": {"palm": 8, "point": 0}}[side]
    hg = "".join(f'<g id="arm{side}-{k}" opacity="0"><g transform="translate({F} 0) rotate({90 + hr})">{hand(k, flip)}</g></g>' for k, hr in hands.items())
    fore = f'transform="rotate({rest_f} {U} 0)"'
    return (f'<g id="arm{side}" transform="rotate({rest_u} {sx} {sy})"><g transform="translate({sx} {sy})">'
            # silhouette pass (ink), then fill pass: upper arm and forearm merge into one clean shape
            f'{ink(up_t)}<circle r="{46 + W}" fill="{OUT}"/>'
            f'<g class="fore" {fore}><g transform="translate({U} 0)">{ink(fo_t)}{ink(cuff)}<circle r="{38 + W}" fill="{OUT}"/></g></g>'
            f'<path d="{up_t}" fill="{JK}"/><circle r="46" fill="{JK}"/>'
            f'<path d="M4,-30 L{U - 6},-24" stroke="{JK_HI}" stroke-width="8" stroke-linecap="round" opacity="0.8"/>'
            f'<path d="M6,34 L{U - 8},30" stroke="{STITCH}" stroke-width="2" stroke-dasharray="6 6"/>'
            f'<g class="fore" {fore}><g transform="translate({U} 0)">{hg}'
            f'<path d="{fo_t}" fill="{JK}"/><circle r="38" fill="{JK}"/>'
            f'<path d="M6,-22 L{F - 40},-17" stroke="{JK_HI}" stroke-width="7" stroke-linecap="round" opacity="0.8"/>'
            f'<path d="{cuff}" fill="{JK_SH}"/><path d="M{F - 34},-30 L{F - 34},30" stroke="{OUT}" stroke-width="2.5"/>'
            f'<circle cx="{F - 20}" cy="16" r="4" fill="#7a7a82"/></g></g>'
            f'</g></g>')

# ------------------------------------------------------------------ torso: black denim jacket (no sleeves: the arms are rigs) over a white tee
def body():
    jacket = "M520,556 C470,566 436,588 424,624 L414,1010 L786,1010 L776,624 C764,588 730,566 680,556 Z"
    return f'''
  <path d="M564,500 L560,580 Q600,598 640,580 L636,500 Z" fill="{SKIN_SH}" stroke="{OUT}" stroke-width="{W}"/>
  <path d="M564,528 Q600,552 636,528 L636,500 L564,500 Z" fill="#b98262" opacity="0.6"/>
  <path d="{jacket}" fill="{JK}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="M538,574 L662,574 L648,1010 L552,1010 Z" fill="{TEE}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="M552,574 Q600,616 648,574" stroke="{TEE_SH}" stroke-width="9" fill="none"/>
  <path d="M552,574 Q600,616 648,574" stroke="{OUT}" stroke-width="2.5" fill="none"/>
  <path d="M600,650 Q590,780 596,1010" stroke="{TEE_SH}" stroke-width="10" fill="none" opacity="0.7"/>
  <path d="M526,560 Q600,544 674,560 L668,578 Q600,562 532,578 Z" fill="{JK_SH}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="M532,574 L492,588 L526,672 L558,622 Z" fill="{JK}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="M668,574 L708,588 L674,672 L642,622 Z" fill="{JK}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="M500,594 L528,662 M700,594 L672,662" stroke="{STITCH}" stroke-width="2" stroke-dasharray="5 5"/>
  <path d="M558,622 L566,1010 M642,622 L634,1010" stroke="{OUT}" stroke-width="{W}"/>
  <path d="M572,630 L580,1010 M628,630 L620,1010" stroke="{STITCH}" stroke-width="2" stroke-dasharray="6 6"/>
  {"".join(f'<circle cx="{x}" cy="{y}" r="6" fill="#6f6f77" stroke="{OUT}" stroke-width="2"/>' for x, y in ((562, 700), (564, 780), (566, 860)))}
  <path d="M446,676 L520,676 L516,708 L482,718 L448,708 Z" fill="{JK}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="M754,676 L680,676 L684,708 L718,718 L752,708 Z" fill="{JK}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <circle cx="482" cy="706" r="5" fill="#6f6f77"/><circle cx="718" cy="706" r="5" fill="#6f6f77"/>
  <path d="M736,660 C752,760 760,880 762,1010 L720,1010 C730,880 728,760 736,660 Z" fill="{JK_SH}" opacity="0.8"/>'''

# ------------------------------------------------------------------ poses (left arm angles; the right arm mirrors)
POSES_L = {   # u = upper-arm angle at the shoulder, f = elbow bend (both svg degrees; 90 = down, 180 = out to the left)
    "rest":  dict(u=100, f=-6, hand="palm"),
    "up":    dict(u=146, f=118, hand="point"),
    "card":  dict(u=152, f=92, hand="point"),
    "palms": dict(u=132, f=98, hand="palm"),
    "shrug": dict(u=124, f=84, hand="palm"),
    "thumb": dict(u=124, f=158, hand="thumb"),
    "wave":  dict(u=150, f=110, hand="palm", wave=True),
}
POSES_R = {"rest": dict(u=80, f=6, hand="palm"), "palms": dict(u=48, f=-98, hand="palm"), "shrug": dict(u=56, f=-84, hand="palm"),
           "up": dict(u=70, f=-14, hand="palm")}

def svg():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1000" width="1200" height="1000">
<g id="pres-body">
  {body()}
  <g id="head" transform="translate({HEAD[0]} {HEAD[1]})">{head()}</g>
  {arm("L", POSES_L["rest"]["u"], POSES_L["rest"]["f"])}{arm("R", POSES_R["rest"]["u"], POSES_R["rest"]["f"])}
  {kitten(816, 486)}
</g></svg>'''

here = os.path.dirname(os.path.abspath(__file__))
open(os.path.join(here, "character.svg"), "w").write(svg())
cfg = {
    "type": "svg", "file": "character.svg", "x": -60, "y": 1150, "width": 1200,
    "head_origin": f"{HEAD[0]} {HEAD[1] + 150}", "avatar_view": "400 90 400 400",
    "poses": list(POSES_L),
    "arms": [
        {"id": "armL", "shoulder": list(SHL), "upper": U, "hands": ["point", "palm", "thumb"], "poses": POSES_L},
        {"id": "armR", "shoulder": list(SHR), "upper": U, "hands": ["palm", "point"], "poses": POSES_R},
    ],
    "brows": {"sel": "#brows", "raise": -9, "end": "#browL"},
    "idle": [{"sel": "#tail", "rot": 10, "period": 1.8, "origin": "846 591"}],
    "twitch": [{"sel": "#cat-ear", "rot": 12, "every": 2.6, "offset": 0.9, "origin": "826 452"}],
    "blink2": [{"open": "#cat-eyes-open", "shut": "#cat-eyes-shut", "every": 3.3, "offset": 1.3}],
    "react": {"sel": "#cat", "y": -26, "rot": -5, "origin": "816 616"},
}
import json
json.dump(cfg, open(os.path.join(here, "character.json"), "w"), indent=1)
print("wrote character.svg + character.json")
