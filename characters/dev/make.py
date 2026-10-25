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
HEAD = (600, 380)
EL, ER = (382, 742), (818, 742)

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

# ------------------------------------------------------------------ head (local coords, face centre 0,0)
def cap():
    """Black baseball cap seen from the front: structured crown, curved bill projecting toward the viewer."""
    crown = "M-138,-92 C-146,-188 -80,-244 0,-246 C80,-244 146,-188 138,-92 Q0,-110 -138,-92 Z"
    seams = (f'<path d="M0,-244 Q-56,-206 -74,-100 M0,-244 Q56,-206 74,-100" stroke="{CAP_SH}" stroke-width="3" fill="none"/>'
             f'<path d="M-112,-160 Q-64,-222 -8,-234" stroke="{CAP_HI}" stroke-width="9" fill="none" stroke-linecap="round" opacity="0.8"/>'
             f'<path d="M-60,-104 Q-66,-170 -40,-226 M60,-104 Q66,-170 40,-226" stroke="{STITCH}" stroke-width="1.6" stroke-dasharray="4 5" fill="none" opacity="0.7"/>')
    button = f'<ellipse cx="0" cy="-245" rx="13" ry="6" fill="{CAP}" stroke="{OUT}" stroke-width="2.5"/>'
    logo = f'<path d="M-30,-176 l-16,14 l16,14 M30,-176 l16,14 l-16,14 M10,-182 l-20,40" stroke="#2c2c32" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    bill = "M-152,-98 C-100,-114 100,-114 152,-98 C164,-80 142,-58 100,-50 C60,-44 -60,-44 -100,-50 C-142,-58 -164,-80 -152,-98 Z"
    under = "M-146,-74 C-110,-60 110,-60 146,-74 C128,-56 70,-46 0,-45 C-70,-46 -128,-56 -146,-74 Z"
    return (f'<path d="{crown}" fill="{CAP}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>{seams}{button}{logo}'
            f'<path d="{bill}" fill="{CAP_HI}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>'
            f'<path d="M-132,-90 C-80,-104 80,-104 132,-90" stroke="{STITCH}" stroke-width="2" stroke-dasharray="6 6" fill="none"/>'
            f'<path d="M-120,-80 C-70,-92 70,-92 120,-80" stroke="{STITCH}" stroke-width="2" stroke-dasharray="6 6" fill="none" opacity="0.7"/>'
            f'<path d="{under}" fill="{CAP_SH}"/>')

def sunglasses():
    lens = lambda cx: (f"M{cx - 44},{-20} Q{cx},{-26} {cx + 44},{-20} Q{cx + 46},{8} {cx + 34},{26} Q{cx},{40} {cx - 34},{26} Q{cx - 46},{8} {cx - 44},{-20} Z")
    L, R = lens(-54), lens(54)
    sheen = "".join(f'<path d="M{cx - 30},{-12} L{cx - 10},{-14} L{cx - 34},{24} L{cx - 44},{14} Z" fill="#ffffff" opacity="0.13"/>'
                    f'<path d="M{cx + 6},{-14} L{cx + 14},{-14} L{cx - 10},{30} L{cx - 18},{30} Z" fill="#ffffff" opacity="0.08"/>' for cx in (-54, 54))
    return (f'<path d="M-98,-14 L-124,-8 M98,-14 L124,-8" stroke="{OUT}" stroke-width="7" stroke-linecap="round"/>'
            f'<path d="{L}" fill="#0d0e11" stroke="{OUT}" stroke-width="5" stroke-linejoin="round"/>'
            f'<path d="{R}" fill="#0d0e11" stroke="{OUT}" stroke-width="5" stroke-linejoin="round"/>'
            f'<path d="M-98,-20 Q-54,-30 -10,-20 M10,-20 Q54,-30 98,-20" stroke="#0a0a0c" stroke-width="10" fill="none" stroke-linecap="round"/>'
            f'<path d="M-10,-14 Q0,-20 10,-14" stroke="{OUT}" stroke-width="6" fill="none" stroke-linecap="round"/>' + sheen)

def mouths():
    lip = "#9a5048"
    m = {
        "closed": f'<path d="M-22,84 Q2,90 24,82" stroke="{lip}" stroke-width="4.5" fill="none" stroke-linecap="round"/>',
        "o": (f'<path d="M-22,80 Q2,76 26,80 Q22,104 2,106 Q-18,104 -22,80 Z" fill="#4e1c1e" stroke="{OUT}" stroke-width="3" stroke-linejoin="round"/>'
              f'<path d="M-18,82 Q2,79 22,82 L20,88 Q2,86 -16,88 Z" fill="#f6f2ea"/><path d="M-10,99 Q2,92 14,99 Q2,105 -10,99 Z" fill="#d6626a"/>'),
        "smile": f'<path d="M-24,84 Q4,96 30,78" stroke="{lip}" stroke-width="5" fill="none" stroke-linecap="round"/><path d="M30,78 l6,-5" stroke="{lip}" stroke-width="4" stroke-linecap="round"/>',
    }
    return "".join(f'<g id="m-{k}" class="mth" opacity="{1 if k == "smile" else 0}">{v}</g>' for k, v in m.items())

def head():
    # sharp, squared jaw
    face = "M-118,-70 L-120,4 C-118,44 -104,76 -80,100 L-30,130 Q0,140 30,130 L80,100 C104,76 118,44 120,4 L118,-70 C110,-140 62,-172 0,-172 C-62,-172 -110,-140 -118,-70 Z"
    jaw_sh = "M82,102 C106,80 120,48 122,8 L122,-30 L112,10 C108,52 94,80 66,104 L40,124 L36,130 Z"
    beard = ("M-122,-8 C-120,48 -106,80 -82,102 L-36,130 Q0,142 36,130 L82,102 C106,80 120,48 122,-8 L108,-4 "
             "C106,40 94,66 70,86 Q46,104 26,106 Q0,98 -26,106 Q-46,104 -70,86 C-94,66 -106,40 -108,-4 Z")
    moust = "M-34,72 Q-14,60 0,66 Q14,60 34,72 Q16,68 0,72 Q-16,68 -34,72 Z"
    return f'''
  <g><ellipse cx="-121" cy="4" rx="17" ry="26" fill="{SKIN}" stroke="{OUT}" stroke-width="{W}"/><ellipse cx="121" cy="4" rx="17" ry="26" fill="{SKIN}" stroke="{OUT}" stroke-width="{W}"/>
     <path d="M-124,-6 q-7,10 0,20 M124,-6 q7,10 0,20" stroke="{SKIN_SH}" stroke-width="3" fill="none" stroke-linecap="round"/>
     <circle cx="126" cy="24" r="5.5" fill="#09090b"/><circle cx="124.5" cy="22.5" r="1.6" fill="#77777f"/></g>
  <path d="{face}" fill="{SKIN}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="{jaw_sh}" fill="{SKIN_SH}" opacity="0.6"/>
  <clipPath id="beardclip"><path d="{beard}"/></clipPath>
  <path d="{beard}" fill="#3b2a22" opacity="0.32"/>
  <path d="M-40,104 Q0,96 40,104 L30,130 Q0,140 -30,130 Z" fill="#2c1f1a" opacity="0.35"/>
  <path d="M-60,-62 C-30,-48 30,-48 60,-62 L118,-62 L118,-40 C60,-28 -60,-28 -118,-40 L-118,-62 Z" fill="{SKIN_SH}" opacity="0.55"/>
  <path d="M-36,128 Q0,140 36,128 L30,114 Q0,124 -30,114 Z" fill="{HAIR}" opacity="0.32"/>
  <path d="{moust}" fill="#2c1f1a" opacity="0.5"/>
  <path d="M-118,-66 L-120,-2 L-108,0 L-106,-66 Z M118,-66 L120,-2 L108,0 L106,-66 Z" fill="{HAIR}" opacity="0.85"/>
  <path d="M-96,-38 Q-60,-50 -20,-40 L-22,-30 Q-60,-38 -94,-28 Z M96,-38 Q60,-50 20,-40 L22,-30 Q60,-38 94,-28 Z" fill="{HAIR}"/>
  <g id="eyes-open"></g><g id="eyes-shut" opacity="0"></g>
  <path d="M6,8 L-6,48 Q2,56 16,50" stroke="#a8694a" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M8,10 L18,46" stroke="{SKIN_SH}" stroke-width="6" stroke-linecap="round" opacity="0.6"/>
  {sunglasses()}
  {mouths()}
  {cap()}'''

# ------------------------------------------------------------------ arm rig: drawn along +x from the elbow (0,0); the kit rotates it
def arm(side):
    flip = side == "R"; L = 150
    tube = f"M0,-40 L{L - 34},-30 L{L - 34},30 L0,40 Z"
    cuff = f"M{L - 36},-27 L{L - 6},-24 L{L - 6},24 L{L - 36},27 Z"
    hands = {"L": {"point": 0, "palm": -10, "thumb": -35}, "R": {"palm": 10, "point": 0}}[side]
    hg = "".join(f'<g id="arm{side}-{k}" opacity="0"><g transform="translate({L} 0) rotate({90 + hr})">{hand(k, flip)}</g></g>' for k, hr in hands.items())
    return (f'<g id="arm{side}"><g transform="translate({(EL if side == "L" else ER)[0]} {(EL if side == "L" else ER)[1]})">'
            f'{hg}'
            f'<path d="{tube}" fill="{JK}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>'
            f'<path d="M6,-22 L{L - 40},-16" stroke="{JK_HI}" stroke-width="8" stroke-linecap="round" opacity="0.8"/>'
            f'<path d="M4,30 L{L - 40},22" stroke="{STITCH}" stroke-width="2" stroke-dasharray="6 6"/>'
            f'<path d="{cuff}" fill="{JK_SH}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>'
            f'<circle cx="{L - 21}" cy="16" r="4" fill="#7a7a82"/>'
            f'<circle cx="0" cy="0" r="40" fill="{JK}"/></g></g>')

# ------------------------------------------------------------------ body: black denim jacket open over a white tee
def body():
    jacket = "M352,600 C414,566 490,550 540,548 L660,548 C710,550 786,566 848,600 C888,626 896,700 888,790 L796,804 L792,1010 L408,1010 L404,804 L312,790 C304,700 312,626 352,600 Z"
    return f'''
  <path d="M560,470 L556,566 Q600,584 644,566 L640,470 Z" fill="{SKIN_SH}" stroke="{OUT}" stroke-width="{W}"/>
  <path d="M560,520 Q600,540 640,520 L640,470 L560,470 Z" fill="#b98262" opacity="0.6"/>
  <path d="{jacket}" fill="{JK}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="M532,560 L668,560 L650,1010 L550,1010 Z" fill="{TEE}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="M546,560 Q600,606 654,560" stroke="{TEE_SH}" stroke-width="9" fill="none"/>
  <path d="M546,560 Q600,606 654,560" stroke="{OUT}" stroke-width="2.5" fill="none"/>
  <path d="M600,640 Q588,760 596,1010" stroke="{TEE_SH}" stroke-width="10" fill="none" opacity="0.7"/>
  <path d="M532,560 L548,1010 L568,1010 L556,610 Z M668,560 L652,1010 L632,1010 L644,610 Z" fill="{JK_SH}"/>
  <path d="M522,548 Q600,530 678,548 L672,566 Q600,548 528,566 Z" fill="{JK_SH}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="M528,560 L478,574 L520,664 L556,612 Z" fill="{JK}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="M672,560 L722,574 L680,664 L644,612 Z" fill="{JK}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="M486,580 L522,654 M714,580 L678,654" stroke="{STITCH}" stroke-width="2" stroke-dasharray="5 5"/>
  <path d="M556,612 L568,1010 M644,612 L632,1010" stroke="{OUT}" stroke-width="{W}"/>
  <path d="M570,620 L580,1010 M630,620 L620,1010" stroke="{STITCH}" stroke-width="2" stroke-dasharray="6 6"/>
  {"".join(f'<circle cx="{x}" cy="{y}" r="6" fill="#6f6f77" stroke="{OUT}" stroke-width="2"/>' for x, y in ((561, 700), (564, 790), (566, 880)))}
  <path d="M372,640 Q450,624 532,636 M828,640 Q750,624 668,636" stroke="{STITCH}" stroke-width="2" stroke-dasharray="6 6" fill="none"/>
  <path d="M428,662 L516,662 L512,700 L472,712 L432,700 Z" fill="{JK}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="M772,662 L684,662 L688,700 L728,712 L768,700 Z" fill="{JK}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <circle cx="472" cy="698" r="5" fill="#6f6f77"/><circle cx="728" cy="698" r="5" fill="#6f6f77"/>
  <path d="M790,640 C830,700 860,750 870,800 L796,804 L792,1010 L740,1010 C760,900 768,760 790,640 Z" fill="{JK_SH}" opacity="0.8"/>
  <path d="M404,804 C398,740 398,690 414,640 M796,804 C802,740 802,690 786,640" stroke="{JK_SH}" stroke-width="5" fill="none"/>'''

def svg():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1000" width="1200" height="1000">
<g id="pres-body">
  {body()}
  <g id="head" transform="translate({HEAD[0]} {HEAD[1]})">{head()}</g>
  {kitten()}
  {arm("L")}{arm("R")}
</g></svg>'''

here = os.path.dirname(os.path.abspath(__file__))
open(os.path.join(here, "character.svg"), "w").write(svg())
print("wrote character.svg")
