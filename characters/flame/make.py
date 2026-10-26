"""The @techinsixty flame head: an original faceless presenter with a soft gradient flame for a head (yellow to pink
to violet, a dark void face with a blue under-glow) in a dark hoodie. The flame tongues flicker, leap on accented
words, and an blue glow under the void is his mouth; two blue eyes glow inside it. Two-bone arm rig. Run: python3 make.py"""
import math, os

OUT = "#120c24"
SKIN, SKIN_SH, SKIN_HI = "#2c2354", "#4b3c86", "#3a2e6a"
HAIR, HAIR_HI = "#161616", "#2e2e33"
JK, JK_SH, JK_HI, STITCH = "#2a2150", "#1c1638", "#4b3c86", "#1c1638"
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
SHL, SHR = (476, 626), (724, 626)
U, F = 104, 110
HS = 1.2                                     # hand scale

def smooth(pts, closed=True, k=0.8):
    n = len(pts); d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f} "
    for i in range(n if closed else n - 1):
        p0, p1, p2, p3 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 6, p1[1] + (p2[1] - p0[1]) * k / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) * k / 6, p2[1] - (p3[1] - p1[1]) * k / 6)
        d += f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} "
    return d + ("Z" if closed else "")

# ------------------------------------------------------------------ head: soft gradient flame with a dark void face (global coords)
DEFS = '''<defs>
  <linearGradient id="fl" gradientUnits="userSpaceOnUse" x1="600" y1="490" x2="600" y2="60">
    <stop offset="0" stop-color="#4f7dff"/><stop offset="0.18" stop-color="#b064ff"/><stop offset="0.38" stop-color="#ff5f8f"/>
    <stop offset="0.6" stop-color="#ff8a3a"/><stop offset="0.85" stop-color="#ffc24a"/><stop offset="1" stop-color="#ffe08a"/></linearGradient>
  <radialGradient id="rim" gradientUnits="userSpaceOnUse" cx="590" cy="330" r="190">
    <stop offset="0.55" stop-color="#ff6aa8" stop-opacity="0"/><stop offset="1" stop-color="#ff6aa8" stop-opacity="0.75"/></radialGradient>
  <radialGradient id="void" cx="0.5" cy="0.46" r="0.5">
    <stop offset="0" stop-color="#030208"/><stop offset="0.45" stop-color="#070410"/><stop offset="0.64" stop-color="#1c0a2a"/>
    <stop offset="0.78" stop-color="#5a1446" stop-opacity="0.75"/><stop offset="0.9" stop-color="#c03a5a" stop-opacity="0.3"/><stop offset="1" stop-color="#ff7a50" stop-opacity="0"/></radialGradient>
  <linearGradient id="hood" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2f2556"/><stop offset="1" stop-color="#120d26"/></linearGradient>
  <filter id="b2" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2"/></filter>
  <filter id="b8" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="8"/></filter>
  <filter id="b18" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="18"/></filter>
</defs>'''

BLOB = "M454,392 C436,312 458,236 520,210 C566,192 606,206 646,196 C716,188 762,248 762,326 C764,410 712,480 612,490 C524,494 470,456 454,392 Z"
TONGUES = {   # each tongue is rooted deep inside the head blob and sways around its own base, so it never lifts off
    "tongueM": ("M530,330 C522,200 584,128 612,48 C650,116 708,170 680,330 Z", "605 330", 4, 1.3),
    "tongueL": ("M472,360 C450,262 462,190 496,140 C520,200 556,240 560,340 Z", "515 350", 5, 1.1),
    "tongueR": ("M640,340 C676,230 714,180 748,162 C760,214 766,270 750,340 Z", "700 345", 4, 1.5),
}

def flame_paths():
    return [BLOB] + [d for d, *_ in TONGUES.values()]

def head():
    bloom = "".join(f'<path d="{d}" fill="url(#fl)"/>' for d in flame_paths())
    tongues = "".join(f'<g id="{k}"><path d="{d}" fill="url(#fl)" filter="url(#b2)"/></g>' for k, (d, *_) in TONGUES.items())
    def eye(cx, cy):
        return (f'<ellipse cx="{cx}" cy="{cy}" rx="20" ry="24" fill="#3d6dff" opacity="0.6" filter="url(#b8)"/>'
                f'<ellipse cx="{cx}" cy="{cy}" rx="9" ry="12" fill="#8fb2ff" filter="url(#b2)"/>'
                f'<ellipse cx="{cx}" cy="{cy - 1}" rx="4" ry="5.5" fill="#eef4ff"/>')
    eyes = (f'<g id="eyes-open">{eye(536, 326)}{eye(602, 322)}</g>'
            '<g id="eyes-shut" opacity="0"><path d="M520,330 Q536,338 552,330 M586,326 Q602,334 618,326" stroke="#8fb2ff" stroke-width="6" fill="none" '
            'stroke-linecap="round" filter="url(#b2)"/></g>')
    glow = lambda rx, ry, op, crx, cry, cop, cy=456: (f'<ellipse cx="588" cy="{cy}" rx="{rx}" ry="{ry}" fill="#3d6dff" opacity="{op}" filter="url(#b8)"/>'
                                                      f'<ellipse cx="588" cy="{cy + 3}" rx="{crx}" ry="{cry}" fill="#b8d0ff" opacity="{cop}" filter="url(#b2)"/>')
    m = {
        "closed": glow(70, 16, 0.8, 34, 6, 0.5),
        "o": glow(88, 27, 1, 48, 11, 0.9, cy=452),
        "smile": ('<path d="M526,438 Q588,480 650,438" stroke="#3d6dff" stroke-width="24" fill="none" stroke-linecap="round" opacity="0.9" filter="url(#b8)"/>'
                  '<path d="M548,446 Q588,470 628,446" stroke="#c8daff" stroke-width="6" fill="none" stroke-linecap="round" opacity="0.85" filter="url(#b2)"/>'),
    }
    mouths = "".join(f'<g id="m-{k}" class="mth" opacity="{1 if k == "smile" else 0}">{v}</g>' for k, v in m.items())
    return f'''<g id="head">
  <g opacity="0.55" filter="url(#b18)">{bloom}</g>
  <g id="flames">{tongues}</g>
  <path d="{BLOB}" fill="url(#fl)" filter="url(#b2)"/>
  <path d="{BLOB}" fill="url(#rim)" filter="url(#b2)"/>
  <path d="M716,236 C740,280 746,334 732,388" stroke="#fff3d6" stroke-width="14" fill="none" stroke-linecap="round" opacity="0.6" filter="url(#b8)"/><path d="M600,96 C590,130 570,160 556,200" stroke="#fff6dc" stroke-width="10" fill="none" stroke-linecap="round" opacity="0.5" filter="url(#b8)"/><path d="M480,300 C470,350 478,400 500,436" stroke="#ff4f9a" stroke-width="16" fill="none" stroke-linecap="round" opacity="0.5" filter="url(#b8)"/>
  <ellipse cx="570" cy="356" rx="128" ry="142" fill="url(#void)" filter="url(#b8)"/>
  <ellipse cx="566" cy="346" rx="70" ry="94" fill="#050309" opacity="0.9" filter="url(#b18)"/>
  {eyes}
  {mouths}
</g>'''

# ------------------------------------------------------------------ two-bone arm: hoodie sleeves, shadowy hands
def tube(x0, x1, w0, w1): return f"M{x0},{-w0} L{x1},{-w1} L{x1},{w1} L{x0},{w0} Z"

def arm(side, rest_u, rest_f):
    flip = side == "R"; sx, sy = SHL if side == "L" else SHR
    up_t, fo_t = tube(0, U + 4, 40, 34), tube(0, F - 6, 34, 28)
    hands = {"L": {"point": 0, "palm": -8, "thumb": -25}, "R": {"palm": 8, "point": 0}}[side]
    hg = "".join(f'<g id="arm{side}-{k}" opacity="0"><g transform="translate({F} 0) rotate({90 + hr})">{hand(k, flip)}</g></g>' for k, hr in hands.items())
    fore = f'transform="rotate({rest_f} {U} 0)"'
    return (f'<g id="arm{side}" transform="rotate({rest_u} {sx} {sy})"><g transform="translate({sx} {sy})">'
            f'<path d="{up_t}" fill="{JK}"/><circle r="42" fill="{JK}"/>'
            f'<path d="M14,-24 L{U * 0.8:.0f},-22" stroke="{JK_HI}" stroke-width="8" stroke-linecap="round" opacity="0.6" filter="url(#b2)"/>'
            f'<g class="fore" {fore}><g transform="translate({U} 0)">{hg}<circle r="36" fill="{JK}"/><path d="{fo_t}" fill="{JK}"/>'
            f'<path d="{tube(F - 26, F - 6, 30, 30)}" fill="{JK_SH}"/></g></g>'
            f'</g></g>')

# ------------------------------------------------------------------ torso: soft hoodie with the hood draped around the neck, warm rim light
def body():
    sw = "M524,546 C466,552 418,578 408,646 L396,1010 L804,1010 L792,646 C782,578 734,552 676,546 Z"
    return f'''
  <path d="M494,600 C480,530 530,494 600,494 C676,494 724,530 708,600 Z" fill="#2b2150"/>
  <path d="M568,450 C562,490 558,530 560,570 L640,570 C642,530 638,490 632,450 Z" fill="#1a1433" filter="url(#b2)"/>
  <path d="{sw}" fill="url(#hood)"/>
  <path d="M498,580 C510,540 548,536 572,560 L600,624 L628,560 C652,536 694,540 704,580 C712,620 680,652 630,660 L600,634 L570,660 C520,652 488,620 498,580 Z" fill="#2a2052"/>
  <path d="M572,560 L600,624 L628,560" stroke="#0c0819" stroke-width="8" fill="none" opacity="0.7" filter="url(#b2)"/>
  <path d="M500,600 C520,640 556,660 600,664 C644,660 682,640 702,600" stroke="#0c0819" stroke-width="5" fill="none" opacity="0.5" filter="url(#b2)"/>
  <path d="M416,640 C410,720 404,840 400,1010" stroke="#ff7aa0" stroke-width="12" fill="none" opacity="0.35" filter="url(#b8)"/>
  <path d="M790,650 C796,740 800,860 802,1010" stroke="#5b7cff" stroke-width="12" fill="none" opacity="0.35" filter="url(#b8)"/>
  <path d="M540,720 C532,780 530,840 532,920 M682,710 C692,780 696,850 694,950" stroke="#0c0819" stroke-width="6" fill="none" opacity="0.55" filter="url(#b2)"/>'''

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
{DEFS}<g id="pres-body">
  {body()}
  {head()}
  {arm("L", POSES_L["rest"]["u"], POSES_L["rest"]["f"])}{arm("R", POSES_R["rest"]["u"], POSES_R["rest"]["f"])}
</g></svg>'''

here = os.path.dirname(os.path.abspath(__file__))
open(os.path.join(here, "character.svg"), "w").write(svg())
import json
json.dump({
    "type": "svg", "file": "character.svg", "x": -60, "y": 1130, "width": 1200,
    "head_origin": "600 500", "avatar_view": "380 40 440 470",
    "poses": list(POSES_L),
    "arms": [{"id": "armL", "shoulder": list(SHL), "upper": U, "hands": ["point", "palm", "thumb"], "poses": POSES_L},
             {"id": "armR", "shoulder": list(SHR), "upper": U, "hands": ["palm", "point"], "poses": POSES_R}],
    "brows": {"sel": "#flames", "raise": -16},
    "idle": [{"sel": "#" + k, "rot": r, "period": p, "origin": o} for k, (d, o, r, p) in TONGUES.items()],
}, open(os.path.join(here, "character.json"), "w"), indent=1)
print("wrote character.svg + character.json")
