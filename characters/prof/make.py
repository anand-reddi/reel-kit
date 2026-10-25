"""The @techinsixty professor: an original older, deadpan tech professor (grey swept-back hair, short grey beard,
half-moon reading glasses, mustard cardigan over a white shirt and red bow tie). Two-bone arm rig, brows, blinks.
Run: python3 make.py -> character.svg + character.json"""
import math, os

OUT = "#2a211c"
SKIN, SKIN_SH, SKIN_HI = "#ecbf9c", "#d4a17e", "#f6d3b8"
HAIR, HAIR_SH, HAIR_HI = "#bdb9b2", "#938e86", "#e0ddd7"
JK, JK_SH, JK_HI, STITCH = "#c9933a", "#a9782a", "#dcaa55", "#8f6420"     # mustard cardigan
TEE, TEE_SH = "#f4f2ee", "#d8d5ce"
RED = "#e5372d"
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
def hair():
    back = ("M-128,-40 C-150,-120 -128,-214 -60,-246 C-10,-268 60,-262 104,-232 C146,-200 154,-120 130,-40 "
            "L118,-30 C122,-90 112,-150 80,-176 C40,-150 -40,-150 -84,-174 C-112,-150 -122,-96 -116,-30 Z")
    swoop = ("M-104,-150 C-96,-214 -30,-246 34,-242 C92,-238 132,-204 128,-150 C110,-176 76,-196 30,-198 "
             "C-14,-200 -60,-186 -104,-150 Z")
    strands = "".join(f'<path d="M{x},{y} C{x + 30},{y - 30} {x + 70},{y - 34} {x + 106},{y - 18}" stroke="{HAIR_SH}" stroke-width="3" fill="none" stroke-linecap="round"/>'
                      for x, y in ((-90, -178), (-80, -206), (-50, -226)))
    hi = f'<path d="M-60,-222 C-20,-244 40,-244 84,-224" stroke="{HAIR_HI}" stroke-width="8" fill="none" stroke-linecap="round" opacity="0.8"/>'
    return (f'<path d="{back}" fill="{HAIR}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>'
            f'<path d="{swoop}" fill="{HAIR}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>{strands}{hi}')

def eyes():
    def eye(cx):
        return (f'<path d="M{cx - 22},-2 Q{cx},-18 {cx + 22},-2 Q{cx},8 {cx - 22},-2 Z" fill="#fbf8f2" stroke="{OUT}" stroke-width="2.5"/>'
                f'<circle cx="{cx + 2}" cy="-4" r="8" fill="#4a3426"/><circle cx="{cx + 2}" cy="-4" r="4" fill="#140d08"/><circle cx="{cx + 5}" cy="-7" r="2.4" fill="#fff"/>'
                f'<path d="M{cx - 24},-4 Q{cx},-22 {cx + 24},-4" stroke="{OUT}" stroke-width="4.5" fill="none" stroke-linecap="round"/>'
                f'<path d="M{cx - 18},-16 Q{cx},-26 {cx + 18},-16" stroke="{SKIN_SH}" stroke-width="2.5" fill="none" stroke-linecap="round"/>')
    shut = "".join(f'<path d="M{cx - 22},-2 Q{cx},6 {cx + 22},-2" stroke="{OUT}" stroke-width="4.5" fill="none" stroke-linecap="round"/>' for cx in (-48, 48))
    crows = "".join(f'<path d="M{s * 76},-8 l{s * 12},-6 M{s * 76},0 l{s * 13},0 M{s * 76},8 l{s * 12},6" stroke="{SKIN_SH}" stroke-width="2.5" stroke-linecap="round"/>' for s in (-1, 1))
    return f'<g id="eyes-open">{eye(-48)}{eye(48)}</g><g id="eyes-shut" opacity="0">{shut}</g>{crows}'

def readers():
    """Half-moon reading glasses sitting low on the nose (he looks over them)."""
    lens = lambda cx: f"M{cx - 36},10 L{cx + 36},10 Q{cx + 34},40 {cx},42 Q{cx - 34},40 {cx - 36},10 Z"
    return (f'<path d="M-84,12 L-112,4 M84,12 L112,4" stroke="#6b4a2e" stroke-width="4" stroke-linecap="round"/>'
            + "".join(f'<path d="{lens(cx)}" fill="#dfeff4" fill-opacity="0.35" stroke="#6b4a2e" stroke-width="4" stroke-linejoin="round"/>'
                      f'<path d="M{cx - 22},18 L{cx - 8},18" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity="0.8"/>' for cx in (-50, 50))
            + f'<path d="M-14,14 Q0,6 14,14" stroke="#6b4a2e" stroke-width="4" fill="none"/>')

def mouths():
    lip = "#9b5a50"; y = 100
    m = {
        "closed": f'<path d="M-20,{y} Q0,{y + 3} 22,{y - 1}" stroke="{lip}" stroke-width="4.5" fill="none" stroke-linecap="round"/>',
        "o": (f'<path d="M-20,{y - 4} Q0,{y - 8} 22,{y - 4} Q18,{y + 18} 0,{y + 20} Q-16,{y + 18} -20,{y - 4} Z" fill="#4e1c1e" stroke="{OUT}" stroke-width="3" stroke-linejoin="round"/>'
              f'<path d="M-16,{y - 2} Q0,{y - 5} 18,{y - 2} L16,{y + 3} Q0,{y + 1} -14,{y + 3} Z" fill="#f6f2ea"/><path d="M-9,{y + 13} Q1,{y + 7} 11,{y + 13} Q1,{y + 18} -9,{y + 13} Z" fill="#d6626a"/>'),
        "smile": f'<path d="M-22,{y - 2} Q2,{y + 8} 26,{y - 8}" stroke="{lip}" stroke-width="5" fill="none" stroke-linecap="round"/>',
    }
    return "".join(f'<g id="m-{k}" class="mth" opacity="{1 if k == "smile" else 0}">{v}</g>' for k, v in m.items())

def head():
    face = "M-112,-80 L-114,20 C-112,64 -96,100 -66,128 C-42,148 -20,156 0,156 C20,156 42,148 66,128 C96,100 112,64 114,20 L112,-80 C106,-160 60,-196 0,-196 C-60,-196 -106,-160 -112,-80 Z"
    beard = ("M-114,8 C-112,64 -96,100 -66,128 C-42,148 -20,158 0,158 C20,158 42,148 66,128 C96,100 112,64 114,8 L98,14 "
             "C96,52 78,74 52,84 Q30,76 0,78 Q-30,76 -52,84 C-78,74 -96,52 -98,14 Z")
    moust = "M-40,92 C-26,78 -10,78 0,84 C10,78 26,78 40,92 C26,88 12,90 0,94 C-12,90 -26,88 -40,92 Z"
    brows = (f'<g id="brows"><g id="browL"><path d="M-80,-46 Q-50,-62 -18,-48 L-20,-38 Q-50,-50 -78,-36 Z" fill="{HAIR}" stroke="{OUT}" stroke-width="2.5" stroke-linejoin="round"/></g>'
             f'<g id="browR"><path d="M80,-46 Q50,-62 18,-48 L20,-38 Q50,-50 78,-36 Z" fill="{HAIR}" stroke="{OUT}" stroke-width="2.5" stroke-linejoin="round"/></g></g>')
    lines = f'<path d="M-50,-110 Q0,-118 50,-110 M-40,-92 Q0,-98 40,-92" stroke="{SKIN_SH}" stroke-width="3" fill="none" stroke-linecap="round"/>'
    return f'''
  <g><ellipse cx="-113" cy="10" rx="17" ry="27" fill="{SKIN}" stroke="{OUT}" stroke-width="{W}"/><ellipse cx="113" cy="10" rx="17" ry="27" fill="{SKIN}" stroke="{OUT}" stroke-width="{W}"/>
     <path d="M-116,0 q-7,10 0,20 M116,0 q7,10 0,20" stroke="{SKIN_SH}" stroke-width="3" fill="none" stroke-linecap="round"/></g>
  <path d="{face}" fill="{SKIN}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="M66,128 C96,100 112,64 114,20 L112,-40 L104,20 C102,60 86,94 58,120 Z" fill="{SKIN_SH}" opacity="0.6"/>
  {lines}
  <path d="{beard}" fill="{HAIR}" stroke="{OUT}" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M-60,120 Q0,150 60,120" stroke="{HAIR_SH}" stroke-width="4" fill="none" stroke-linecap="round"/>
  {mouths()}
  <path d="{moust}" fill="{HAIR}" stroke="{OUT}" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M4,4 Q-14,50 -6,62 Q8,72 22,62" stroke="#ad6f4f" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M8,8 L22,56" stroke="{SKIN_SH}" stroke-width="7" stroke-linecap="round" opacity="0.5"/>
  {eyes()}
  {brows}
  {readers()}
  {hair()}'''

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
            + "".join(f'<path d="M{F - 30 + i * 6},-27 L{F - 30 + i * 6},27" stroke="{STITCH}" stroke-width="2"/>' for i in range(5))
            + '</g></g>'
            f'</g></g>')

# ------------------------------------------------------------------ torso: mustard cardigan (arms are rigs) over a white shirt and red bow tie
def body():
    cardi = "M520,556 C470,566 436,588 424,624 L414,1010 L786,1010 L776,624 C764,588 730,566 680,556 Z"
    return f'''
  <path d="M566,500 L562,580 Q600,598 638,580 L634,500 Z" fill="{SKIN_SH}" stroke="{OUT}" stroke-width="{W}"/>
  <path d="{cardi}" fill="{JK}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="M532,560 L668,560 L612,760 L588,760 Z" fill="{TEE}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="M556,556 L600,600 L538,612 Z M644,556 L600,600 L662,612 Z" fill="{TEE}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="M600,600 L600,760" stroke="{TEE_SH}" stroke-width="3"/>
  <g transform="translate(600 604)"><path d="M0,0 L-34,-16 L-34,16 Z M0,0 L34,-16 L34,16 Z" fill="{RED}" stroke="{OUT}" stroke-width="3" stroke-linejoin="round"/>
     <rect x="-8" y="-9" width="16" height="18" rx="4" fill="{RED}" stroke="{OUT}" stroke-width="3"/></g>
  <path d="M532,560 L588,760 L566,1010 M668,560 L612,760 L634,1010" stroke="{OUT}" stroke-width="{W}" fill="none"/>
  <path d="M548,566 L598,758 L582,1010 M652,566 L602,758 L618,1010" stroke="{JK_SH}" stroke-width="10" fill="none" opacity="0.8"/>
  {"".join(f'<circle cx="{x}" cy="{y}" r="7" fill="#5a3b1a" stroke="{OUT}" stroke-width="2"/>' for x, y in ((612, 800), (614, 870), (616, 940)))}
  <path d="M736,660 C752,760 760,880 762,1010 L720,1010 C730,880 728,760 736,660 Z" fill="{JK_SH}" opacity="0.7"/>
  {"".join(f'<path d="M{x},640 L{x + 4},1010" stroke="{STITCH}" stroke-width="2" opacity="0.35"/>' for x in range(452, 760, 22) if not 520 < x < 690)}'''

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
           "up": dict(u=34, f=-118, hand="point")}

def svg():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1000" width="1200" height="1000">
<g id="pres-body">
  {body()}
  <g id="head" transform="translate({HEAD[0]} {HEAD[1]})">{head()}</g>
  {arm("L", POSES_L["rest"]["u"], POSES_L["rest"]["f"])}{arm("R", POSES_R["rest"]["u"], POSES_R["rest"]["f"])}
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
    "brows": {"sel": "#brows", "raise": -10, "end": "#browL"},
    "talk_nod": True,
}
import json
json.dump(cfg, open(os.path.join(here, "character.json"), "w"), indent=1)
print("wrote character.svg + character.json")
