"""The @techinsixty mascot: an original flat-vector character inspired by the presenter art (curly black hair, nose
bandage, moustache + goatee, oversized navy tee with a red label, black kitten on his shoulder). Writes character.svg
with the kit's SVG ids (CHARACTER.md) plus kitten rigs. Run: python3 make.py"""
import math, os

OUT = "#141414"
SKIN, SKIN_SH, SKIN_HI = "#e9b48c", "#d09670", "#f4c9a5"
HAIR, HAIR_SH, HAIR_HI = "#1a1b21", "#0d0e12", "#3a3f52"
TEE, TEE_SH, TEE_HI = "#232a40", "#181d2e", "#2f3854"
RED, BAND, BAND_PAD = "#e5372d", "#efd3a8", "#f8e7c9"
CAT, CAT_SH, CAT_HI, PINK, AMBER = "#18181d", "#0c0c10", "#34343f", "#f08fa0", "#f3b33d"
W = 5   # outline width

def rng(seed):
    s = seed
    def r():
        nonlocal s
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        return s / 0x7FFFFFFF
    return r

def P(pts): return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"

# ------------------------------------------------------------------ hair: curly mop built from round clumps
def curls(cx, cy, rx, ry, n, rmin, rmax, seed, keep=lambda x, y: True, a0=0, a1=360):
    r = rng(seed); out = []
    for i in range(n):
        a = math.radians(a0 + (a1 - a0) * (i + r() * 0.7) / n)
        x, y = cx + rx * math.cos(a) * (0.82 + 0.18 * r()), cy + ry * math.sin(a) * (0.82 + 0.18 * r())
        if keep(x, y): out.append((x, y, rmin + r() * (rmax - rmin)))
    return out

def wisp_contour(cx, cy, rx, ry, n, amp, seed, a0=-200, a1=20, swirl=0.38):
    """A messy wavy silhouette: n wisps, each a curved point swept sideways (reads as wavy locks, not curls)."""
    r = rng(seed); pts = []; d = ""
    angs = [math.radians(a0 + (a1 - a0) * i / n) for i in range(n + 1)]
    for i in range(n):
        t0, t1 = angs[i], angs[i + 1]; tm = t0 + (t1 - t0) * (0.5 + swirl * (1 if math.cos((t0 + t1) / 2) > 0 else -1) * 0.6)
        A = amp * (0.55 + 0.7 * r())
        p0 = (cx + rx * math.cos(t0), cy + ry * math.sin(t0))
        tip = (cx + (rx + A) * math.cos(tm), cy + (ry + A) * math.sin(tm))
        p1 = (cx + rx * math.cos(t1), cy + ry * math.sin(t1))
        c1 = (cx + (rx + A * 0.55) * math.cos(t0 + (t1 - t0) * 0.15), cy + (ry + A * 0.55) * math.sin(t0 + (t1 - t0) * 0.15))
        c2 = (cx + (rx + A * 0.2) * math.cos(t1 - (t1 - t0) * 0.1), cy + (ry + A * 0.2) * math.sin(t1 - (t1 - t0) * 0.1))
        if i == 0: d += f"M{p0[0]:.1f},{p0[1]:.1f} "
        d += f"Q{c1[0]:.1f},{c1[1]:.1f} {tip[0]:.1f},{tip[1]:.1f} Q{c2[0]:.1f},{c2[1]:.1f} {p1[0]:.1f},{p1[1]:.1f} "
    return d

def smooth(pts, closed=True, k=0.5):
    """Catmull-Rom through points -> cubic beziers (soft, wavy outlines)."""
    n = len(pts); d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f} "
    rng_ = range(n) if closed else range(n - 1)
    for i in rng_:
        p0, p1, p2, p3 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        if not closed: p0, p3 = pts[max(i - 1, 0)], pts[min(i + 2, n - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 3, p1[1] + (p2[1] - p0[1]) * k / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * k / 3, p2[1] - (p3[1] - p1[1]) * k / 3)
        d += f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} "
    return d + ("Z" if closed else "")

def hair_back():
    # short, neat hair hugging the skull, a little volume on top, short sideburns
    pts = [(-142, 10), (-148, -60), (-140, -128), (-108, -186), (-52, -216), (10, -224), (72, -214), (122, -184),
           (148, -130), (152, -60), (144, 10), (132, 12), (132, -40), (0, -60), (-132, -40), (-132, 12)]
    d = smooth(pts, True, 0.8)
    hi = "".join(f'<path d="M{x},{y} q{dx},-14 {dx * 2.4},-2" stroke="{HAIR_HI}" stroke-width="6" fill="none" stroke-linecap="round" opacity="0.8"/>'
                 for x, y, dx in ((-90, -186, 14), (-20, -208, 16), (52, -200, 16)))
    return f'<path d="{d}" fill="{HAIR}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>' + hi

def hair_front():
    # side-swept fringe (parting on his right), lower edge with a few soft wave tips; clipped to the head shape
    edge = [(-150, -96), (-118, -112), (-96, -96), (-66, -118), (-36, -104), (-4, -126), (30, -112), (64, -136),
            (98, -128), (128, -146), (152, -130)]
    pts = [(-160, -150)] + edge + [(160, -170), (110, -222), (10, -236), (-90, -222)]
    d = smooth(pts, True, 0.7)
    out = f'<path d="{d}" fill="{HAIR}" stroke="{OUT}" stroke-width="4.5" stroke-linejoin="round"/>'
    out += "".join(f'<path d="M{x},{y} q{18},14 {30},34" stroke="{HAIR_HI}" stroke-width="5" fill="none" stroke-linecap="round" opacity="0.75"/>'
                   for x, y in ((-120, -176), (-60, -190), (6, -196), (70, -186)))
    return out

# ------------------------------------------------------------------ face
def eye(cx, s):
    """s=-1 viewer-left, +1 viewer-right. Cool, half-lidded almond eye looking slightly to the side."""
    y = 0
    white = f"M{cx - 34 * s},{y + 2} Q{cx - 4 * s},{y - 20} {cx + 34 * s},{y - 6} Q{cx + 6 * s},{y + 16} {cx - 34 * s},{y + 2} Z"
    clip = f"ec{'L' if s < 0 else 'R'}"
    return (f'<clipPath id="{clip}"><path d="{white}"/></clipPath><path d="{white}" fill="#fbf7f0"/>'
            f'<g clip-path="url(#{clip})"><circle cx="{cx + 6}" cy="{y - 2}" r="14" fill="#7a3f17"/><circle cx="{cx + 6}" cy="{y}" r="9" fill="#c47d33"/>'
            f'<circle cx="{cx + 6}" cy="{y - 1}" r="5.5" fill="#160d08"/><circle cx="{cx + 10}" cy="{y - 6}" r="3.5" fill="#fff"/>'
            f'<rect x="{cx - 40}" y="{y - 30}" width="80" height="18" fill="{SKIN_SH}" opacity="0.55"/></g>'
            f'<path d="M{cx - 38 * s},{y + 3} Q{cx - 4 * s},{y - 22} {cx + 36 * s},{y - 8} l{8 * s},-6" stroke="{OUT}" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M{cx - 26 * s},{y + 10} Q{cx + 2 * s},{y + 16} {cx + 28 * s},{y + 4}" stroke="{SKIN_SH}" stroke-width="3" fill="none" stroke-linecap="round"/>')

def brows():
    return (f'<path d="M-108,-44 Q-70,-66 -18,-34 L-24,-20 Q-68,-48 -106,-30 Z" fill="{HAIR}" stroke="{OUT}" stroke-width="2.5" stroke-linejoin="round"/>'
            f'<path d="M108,-52 Q70,-70 18,-34 L24,-20 Q68,-52 106,-38 Z" fill="{HAIR}" stroke="{OUT}" stroke-width="2.5" stroke-linejoin="round"/>')

def mouths():
    m = {
        "closed": f'<path d="M-22,100 Q2,106 26,96" stroke="#5a2a24" stroke-width="5" fill="none" stroke-linecap="round"/>',
        "o": (f'<path d="M-20,96 Q2,90 24,94 Q22,118 2,121 Q-18,118 -20,96 Z" fill="#4a1c1c" stroke="{OUT}" stroke-width="3.5" stroke-linejoin="round"/>'
              f'<path d="M-12,111 Q2,104 16,111 Q2,121 -12,111 Z" fill="#c95b60"/><path d="M-14,97 L18,96 L16,101 L-12,102 Z" fill="#f4efe6"/>'),
        "smile": f'<path d="M-24,98 Q4,114 30,90" stroke="#5a2a24" stroke-width="5.5" fill="none" stroke-linecap="round"/><path d="M30,90 l6,-4" stroke="#5a2a24" stroke-width="4" stroke-linecap="round"/>',
    }
    return "".join(f'<g id="m-{k}" class="mth" opacity="{1 if k == "smile" else 0}">{v}</g>' for k, v in m.items())

def head():
    face = "M-132,-70 C-136,20 -124,76 -84,116 L-30,154 C-12,164 12,164 30,154 L84,116 C124,76 136,20 132,-70 C128,-140 72,-178 0,-178 C-72,-178 -128,-140 -132,-70 Z"
    jaw_sh = "M78,112 C120,72 134,10 130,-70 L130,10 C120,74 96,108 52,138 Z"
    stub = rng(9); dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.6" fill="{HAIR}" opacity="0.28"/>'
                                     for x, y in ((math.sin(t) * 112 * (0.86 + 0.14 * stub()), 60 + (1 - math.cos(t)) * 66 + stub() * 14)
                                                  for t in (math.radians(-78 + i * 4) for i in range(40))) if abs(x) > 40 or y > 130)
    band = ''
    return f'''
  <path d="M-34,120 L-38,215 L38,215 L34,120 Z" fill="{SKIN_SH}" stroke="{OUT}" stroke-width="{W}"/>
  {hair_back()}
  <g><ellipse cx="-131" cy="10" rx="20" ry="30" fill="{SKIN}" stroke="{OUT}" stroke-width="{W}"/><ellipse cx="131" cy="10" rx="20" ry="30" fill="{SKIN}" stroke="{OUT}" stroke-width="{W}"/>
     <circle cx="-138" cy="34" r="6" fill="none" stroke="#c9ccd4" stroke-width="3"/><circle cx="138" cy="34" r="6" fill="none" stroke="#c9ccd4" stroke-width="3"/></g>
  <path d="{face}" fill="{SKIN}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="{jaw_sh}" fill="{SKIN_SH}" opacity="0.7"/>
  {dots}
  {brows()}
  <g id="eyes-open" transform="translate(0 0)">{eye(-58, -1)}{eye(58, 1)}</g>
  <g id="eyes-shut" opacity="0"><path d="M-96,0 Q-58,14 -22,-2" stroke="{OUT}" stroke-width="7" fill="none" stroke-linecap="round"/><path d="M22,-4 Q58,12 96,-6" stroke="{OUT}" stroke-width="7" fill="none" stroke-linecap="round"/></g>
  <path d="M8,8 L-4,58 Q4,64 18,60" stroke="#a8694a" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  {band}
  <path d="M-52,88 Q-26,70 2,78 Q30,70 56,86 Q34,84 2,92 Q-28,84 -52,88 Z" fill="{HAIR}" stroke="{OUT}" stroke-width="2.5" stroke-linejoin="round"/>
  {mouths()}
  <path d="M-16,126 Q2,118 20,126 L14,150 Q2,160 -10,150 Z" fill="{HAIR}" stroke="{OUT}" stroke-width="2.5" stroke-linejoin="round"/>
  {hair_front()}'''

# ------------------------------------------------------------------ arms and hands (forearms leave the sleeve hem at the elbow)
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

def forearm(elbow, angle, kind, length=150, flip=False, hrot=0):
    ex, ey = elbow; a = math.radians(angle); hx, hy = ex + length * math.cos(a), ey + length * math.sin(a)
    nx, ny = -math.sin(a), math.cos(a)
    q = lambda w0, w1: f"M{ex + nx * w0:.1f},{ey + ny * w0:.1f} L{hx + nx * w1:.1f},{hy + ny * w1:.1f} L{hx - nx * w1:.1f},{hy - ny * w1:.1f} L{ex - nx * w0:.1f},{ey - ny * w0:.1f} Z"
    rot = angle + 90 + hrot
    return (f'<path d="{q(29, 20)}" fill="{SKIN}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>'
            f'<path d="M{ex + nx * 12:.1f},{ey + ny * 12:.1f} L{hx + nx * 9:.1f},{hy + ny * 9:.1f}" stroke="{SKIN_SH}" stroke-width="9" stroke-linecap="round" opacity="0.6"/>'
            f'<g transform="translate({hx:.1f} {hy:.1f}) rotate({rot:.1f})">{hand(kind, flip)}</g>'
            f'<path d="M{ex + nx * 31:.1f},{ey + ny * 31:.1f} L{ex - nx * 31:.1f},{ey - ny * 31:.1f}" stroke="{TEE}" stroke-width="10"/>')

EL, ER = (398, 800), (802, 800)      # elbows at the sleeve hems
POSES = {
    "up":    [forearm(EL, -92, "point", 150)],
    "card":  [forearm(EL, -118, "point", 150, hrot=-8)],
    "palms": [forearm(EL, -148, "palm", 135, hrot=-10), forearm(ER, -32, "palm", 135, True, 10)],
    "thumb": [forearm(EL, -55, "thumb", 135, hrot=-35)],
    "shrug": [forearm(EL, -160, "palm", 130, hrot=-25), forearm(ER, -20, "palm", 130, True, 25)],
    "wave":  [forearm(EL, -100, "palm", 150, hrot=6)],
}
HANG = {"L": f'<path d="M{EL[0] - 29},{EL[1]} L{EL[0] - 24},1010 L{EL[0] + 18},1010 L{EL[0] + 29},{EL[1]} Z" fill="{SKIN}" stroke="{OUT}" stroke-width="{W}"/><path d="M{EL[0] - 31},{EL[1]} L{EL[0] + 31},{EL[1]}" stroke="{TEE}" stroke-width="10"/>',
        "R": f'<path d="M{ER[0] + 29},{ER[1]} L{ER[0] + 24},1010 L{ER[0] - 18},1010 L{ER[0] - 29},{ER[1]} Z" fill="{SKIN}" stroke="{OUT}" stroke-width="{W}"/><path d="M{ER[0] + 31},{ER[1]} L{ER[0] - 31},{ER[1]}" stroke="{TEE}" stroke-width="10"/>'}
def pose_group(name, parts):
    uses_l = name in ("up", "card", "palms", "thumb", "shrug", "wave"); uses_r = name in ("palms", "shrug")
    hang = ("" if uses_l else HANG["L"]) + ("" if uses_r else HANG["R"])
    return f'<g id="pose-{name}" class="pose" opacity="0">{hang}{"".join(parts)}</g>'

# ------------------------------------------------------------------ body: oversized drop-shoulder tee
def body():
    tee = "M370,600 C420,570 480,556 530,554 L670,554 C720,556 780,570 830,600 C872,628 880,700 870,792 L780,808 L776,1010 L424,1010 L420,808 L330,792 C320,700 328,628 370,600 Z"
    return f'''
  <path d="{tee}" fill="{TEE}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="M780,808 L776,1010 L712,1010 C736,900 744,770 790,650 C832,700 862,750 870,792 Z" fill="{TEE_SH}" opacity="0.9"/>
  <path d="M330,792 L420,808 M780,808 L870,792" stroke="{OUT}" stroke-width="{W}"/>
  <path d="M420,808 C414,750 414,700 428,650 M780,808 C786,750 786,700 772,650" stroke="{TEE_SH}" stroke-width="6" fill="none"/>
  <path d="M500,720 L560,790 M650,760 L690,830" stroke="{TEE_SH}" stroke-width="6" fill="none" stroke-linecap="round"/>
  <path d="M528,556 Q600,628 672,556" fill="{SKIN_SH}" stroke="{OUT}" stroke-width="{W}"/>
  <path d="M516,554 Q600,644 684,554" stroke="{TEE_SH}" stroke-width="14" fill="none"/>
  <path d="M516,554 Q600,644 684,554" stroke="{OUT}" stroke-width="{W}" fill="none"/>
  <g transform="translate(690 660)"><rect x="-15" y="0" width="30" height="86" fill="none" stroke="#ece8e0" stroke-width="3"/>
    <text x="0" y="25" text-anchor="middle" font-size="21" font-weight="700" fill="{RED}" font-family="sans-serif">オ</text>
    <text x="0" y="52" text-anchor="middle" font-size="21" font-weight="700" fill="{RED}" font-family="sans-serif">タ</text>
    <text x="0" y="79" text-anchor="middle" font-size="21" font-weight="700" fill="{RED}" font-family="sans-serif">ク</text></g>'''

# ------------------------------------------------------------------ kitten on his left shoulder (viewer right)
def fur(cx, cy, rx, ry, n, jag, seed):
    r = rng(seed); pts = []
    for i in range(n * 2):
        a = i / (n * 2) * 2 * math.pi; k = 1 + (jag * (0.5 + 0.5 * r()) if i % 2 else 0)
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    return P(pts)

def kitten():
    kx, ky = 838, 474
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

def svg():
    poses = "".join(pose_group(n, p) for n, p in POSES.items())
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1000" width="1200" height="1000">
<g id="pres-body">
  {body()}
  {poses}
  <g id="head" transform="translate(600 360)">{head()}</g>
  {kitten()}
</g></svg>'''

here = os.path.dirname(os.path.abspath(__file__))
open(os.path.join(here, "character.svg"), "w").write(svg())
print("wrote character.svg")
