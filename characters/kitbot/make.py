"""The @techinsixty kitbot: an original cute black cat robot (glossy black shell, cat ears with glowing inner ears,
dark screen face with LED pill eyes and an LED cat mouth, collar light, chest heart, swinging robot tail).
Two-bone arm rig, LED lip sync, blinks, ear twitch, tail sway, heartbeat. Run: python3 make.py"""
import math, os

OUT = "#0b0b0e"
SKIN, SKIN_SH, SKIN_HI = "#383a45", "#4a4c5a", "#3d3f4a"
HAIR, HAIR_HI = "#161616", "#2e2e33"
JK, JK_SH, JK_HI, STITCH = "#1f2026", "#15161a", "#3d3f4a", "#15161a"
BOT, BOT_SH, BOT_HI, JOINT = "#22232a", "#16171c", "#4a4c5a", "#33353f"
GLASS, LED, BLUSH, TAG = "#0c0e12", "#ff9a3c", "#ff6f91", "#ffc857"
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
HEAD = (600, 340)
SHL, SHR = (474, 610), (726, 610)
U, F = 92, 104
HS = 1.05                                     # hand scale

def smooth(pts, closed=True, k=0.8):
    n = len(pts); d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f} "
    for i in range(n if closed else n - 1):
        p0, p1, p2, p3 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 6, p1[1] + (p2[1] - p0[1]) * k / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) * k / 6, p2[1] - (p3[1] - p1[1]) * k / 6)
        d += f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} "
    return d + ("Z" if closed else "")

# ------------------------------------------------------------------ head: glossy black cat-bot (local coords, centre 0,0)
def led_glow(d, w):   # soft LED bloom: wide faint stroke under the crisp one
    return f'<path d="{d}" stroke="{LED}" stroke-width="{w + 12}" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.18"/>'

def head():
    shell = "M-190,-20 C-190,-120 -120,-150 0,-150 C120,-150 190,-120 190,-20 C190,90 140,140 0,140 C-140,140 -190,90 -190,-20 Z"
    ear = lambda s: (f'<path d="M{s * 176},-70 L{s * 168},-262 L{s * 54},-142 Z" fill="{BOT}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>'
                     f'<path d="M{s * 150},-104 L{s * 150},-206 L{s * 86},-142 Z" fill="{LED}" opacity="0.85"/>'
                     f'<path d="M{s * 160},-118 L{s * 158},-176" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity="0.5"/>')
    whisk = "".join(f'<path d="M{s * 184},{y} L{s * 262},{y + dy}" stroke="{OUT}" stroke-width="5" stroke-linecap="round"/>'
                    for s in (-1, 1) for y, dy in ((14, -16), (40, 6)))
    visor = "M-150,-30 C-150,-96 -96,-104 0,-104 C96,-104 150,-96 150,-30 C150,56 112,100 0,100 C-112,100 -150,56 -150,-30 Z"
    def eye(cx):
        return (f'<rect x="{cx - 30}" y="-58" width="60" height="84" rx="30" fill="{LED}" opacity="0.2"/>'
                f'<rect x="{cx - 23}" y="-50" width="46" height="70" rx="23" fill="{LED}"/>'
                f'<circle cx="{cx + 7}" cy="-30" r="9" fill="#fff" opacity="0.95"/><circle cx="{cx - 9}" cy="6" r="4" fill="#fff" opacity="0.7"/>')
    shut = "".join(led_glow(f"M{cx - 24},-8 Q{cx},6 {cx + 24},-8", 9) +
                   f'<path d="M{cx - 24},-8 Q{cx},6 {cx + 24},-8" stroke="{LED}" stroke-width="9" fill="none" stroke-linecap="round"/>' for cx in (-60, 60))
    eyes = f'<g id="xeyes"><g id="eyes-open">{eye(-60)}{eye(60)}</g><g id="eyes-shut" opacity="0">{shut}</g></g>'
    w = "M-26,52 Q-13,66 0,52 Q13,66 26,52"
    m = {
        "closed": led_glow(w, 7) + f'<path d="{w}" stroke="{LED}" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
        "o": (led_glow(w, 7) + f'<path d="{w}" stroke="{LED}" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
              f'<path d="M-12,62 Q0,58 12,62 Q12,82 0,84 Q-12,82 -12,62 Z" fill="{LED}" opacity="0.9"/>'),
        "smile": (led_glow("M-34,50 Q-17,72 0,54 Q17,72 34,50", 7) +
                  f'<path d="M-34,50 Q-17,72 0,54 Q17,72 34,50" stroke="{LED}" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
                  f'<path d="M-8,64 Q0,80 8,64 Z" fill="{BLUSH}"/>'),
    }
    mouths = "".join(f'<g id="m-{k}" class="mth" opacity="{1 if k == "smile" else 0}">{v}</g>' for k, v in m.items())
    cheeks = "".join(f'<ellipse cx="{s * 104}" cy="44" rx="20" ry="11" fill="{BLUSH}" opacity="0.55"/>' for s in (-1, 1))
    return f'''
  {ear(-1)}
  <g id="earR">{ear(1)}</g>
  {whisk}
  <path d="{shell}" fill="{BOT}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="M-150,-96 C-110,-136 -40,-140 30,-136" stroke="{BOT_HI}" stroke-width="12" fill="none" stroke-linecap="round" opacity="0.9"/>
  <path d="M150,60 C130,110 80,128 30,132" stroke="{BOT_SH}" stroke-width="10" fill="none" stroke-linecap="round"/>
  <path d="{visor}" fill="{GLASS}" stroke="{OUT}" stroke-width="4"/>
  <path d="M-128,-56 C-120,-84 -80,-92 -40,-92" stroke="#fff" stroke-width="7" fill="none" stroke-linecap="round" opacity="0.18"/>
  {cheeks}
  {eyes}
  {mouths}
  <circle cx="0" cy="-128" r="7" fill="{LED}"/><circle cx="0" cy="-128" r="13" fill="{LED}" opacity="0.25"/>
  <circle cx="-168" cy="-6" r="7" fill="{BOT_HI}" stroke="{OUT}" stroke-width="3"/><circle cx="168" cy="-6" r="7" fill="{BOT_HI}" stroke="{OUT}" stroke-width="3"/>'''

# ------------------------------------------------------------------ two-bone arm: black metal segments, glowing joint, LED cuff, mitt hands
def tube(x0, x1, w0, w1): return f"M{x0},{-w0} L{x1},{-w1} L{x1},{w1} L{x0},{w0} Z"

def arm(side, rest_u, rest_f):
    flip = side == "R"; sx, sy = SHL if side == "L" else SHR
    up_t, fo_t = tube(0, U, 24, 22), tube(0, F - 8, 22, 20)
    cuff = tube(F - 24, F - 6, 26, 26)
    ink = lambda d, w=2 * W: f'<path d="{d}" fill="{OUT}" stroke="{OUT}" stroke-width="{w}" stroke-linejoin="round"/>'
    hands = {"L": {"point": 0, "palm": -8, "thumb": -25}, "R": {"palm": 8, "point": 0}}[side]
    hg = "".join(f'<g id="arm{side}-{k}" opacity="0"><g transform="translate({F} 0) rotate({90 + hr})">{hand(k, flip)}</g></g>' for k, hr in hands.items())
    fore = f'transform="rotate({rest_f} {U} 0)"'
    return (f'<g id="arm{side}" transform="rotate({rest_u} {sx} {sy})"><g transform="translate({sx} {sy})">'
            f'{ink(up_t)}<g class="fore" {fore}><g transform="translate({U} 0)">{ink(fo_t)}</g></g>'
            f'<path d="{up_t}" fill="{BOT}"/><path d="M6,-12 L{U - 10},-11" stroke="{BOT_HI}" stroke-width="6" stroke-linecap="round"/>'
            f'<circle r="34" fill="{BOT}" stroke="{OUT}" stroke-width="{W}"/><circle cx="-6" cy="-8" r="10" fill="{BOT_HI}"/>'
            f'<g class="fore" {fore}><g transform="translate({U} 0)">{hg}<path d="{fo_t}" fill="{BOT}"/>'
            f'<path d="M6,-10 L{F - 30},-9" stroke="{BOT_HI}" stroke-width="5" stroke-linecap="round"/>'
            f'<path d="{cuff}" fill="{LED}" stroke="{OUT}" stroke-width="4" stroke-linejoin="round"/>'
            f'<circle r="27" fill="{JOINT}" stroke="{OUT}" stroke-width="{W}"/><circle r="9" fill="{LED}"/></g></g>'
            f'</g></g>')

# ------------------------------------------------------------------ torso: rounded black shell, LED collar + tag, chest screen with a heart, robot tail
def body():
    torso = "M506,520 Q600,494 694,520 C736,536 752,590 756,660 L766,1010 L434,1010 L444,660 C448,590 464,536 506,520 Z"
    tail = "M720,880 C800,880 846,826 842,756 C838,706 860,676 890,680"
    heart = "M600,700 C580,684 566,672 566,658 C566,646 576,638 586,638 C593,638 598,642 600,648 C602,642 607,638 614,638 C624,638 634,646 634,658 C634,672 620,684 600,700 Z"
    return f'''
  <g id="tail">
    <path d="{tail}" stroke="{OUT}" stroke-width="{34 + 2 * W}" fill="none" stroke-linecap="round"/>
    <path d="{tail}" stroke="{BOT}" stroke-width="34" fill="none" stroke-linecap="round"/>
    <path d="{tail}" stroke="{BOT_HI}" stroke-width="34" fill="none" stroke-dasharray="4 30" opacity="0.9"/>
    <circle cx="894" cy="680" r="20" fill="{LED}" stroke="{OUT}" stroke-width="{W}"/><circle cx="888" cy="674" r="6" fill="#fff" opacity="0.8"/>
  </g>
  <rect x="566" y="470" width="68" height="60" fill="{JOINT}" stroke="{OUT}" stroke-width="{W}"/>
  <path d="{torso}" fill="{BOT}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="M470,600 C462,700 458,820 456,1010" stroke="{BOT_HI}" stroke-width="12" fill="none" stroke-linecap="round" opacity="0.8"/>
  <path d="M730,640 C736,760 740,880 742,1010" stroke="{BOT_SH}" stroke-width="14" fill="none"/>
  <path d="M500,530 Q600,566 700,530" stroke="{OUT}" stroke-width="{18 + 2 * W}" fill="none" stroke-linecap="round"/>
  <path d="M500,530 Q600,566 700,530" stroke="{LED}" stroke-width="18" fill="none" stroke-linecap="round"/>
  <circle cx="600" cy="572" r="18" fill="{TAG}" stroke="{OUT}" stroke-width="{W}"/><path d="M592,572 L608,572" stroke="{OUT}" stroke-width="4" stroke-linecap="round"/>
  <rect x="540" y="614" width="120" height="104" rx="22" fill="{GLASS}" stroke="{OUT}" stroke-width="4"/>
  <path d="{heart}" fill="{LED}" opacity="0.85"/>
  <g id="heart-glow" opacity="0"><path d="{heart}" fill="#fff" opacity="0.55"/><path d="{heart}" fill="none" stroke="{LED}" stroke-width="16" opacity="0.3"/></g>
  <circle cx="490" cy="900" r="6" fill="{BOT_HI}"/><circle cx="710" cy="900" r="6" fill="{BOT_SH}"/>'''

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
    "head_origin": "600 500", "avatar_view": "360 50 480 480",
    "poses": list(POSES_L),
    "arms": [{"id": "armL", "shoulder": list(SHL), "upper": U, "hands": ["point", "palm", "thumb"], "poses": POSES_L},
             {"id": "armR", "shoulder": list(SHR), "upper": U, "hands": ["palm", "point"], "poses": POSES_R}],
    "brows": {"sel": "#xeyes", "raise": -8},
    "idle": [{"sel": "#tail", "rot": 7, "period": 1.8, "origin": "740 880"}],
    "twitch": [{"sel": "#earR", "rot": 10, "every": 2.7, "offset": 1.1, "origin": "120 -100"}],
    "blink2": [{"shut": "#heart-glow", "every": 1.0, "offset": 0.4}],
}, open(os.path.join(here, "character.json"), "w"), indent=1)
print("wrote character.svg + character.json")
