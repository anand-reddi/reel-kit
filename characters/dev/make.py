"""The @techinsixty dev: a teen developer in a hoodie (soft-shaded cartoon, after the reference reel style), with the black kitten. Was: the mascot: an original flat-vector character inspired by the presenter art (curly black hair, nose
bandage, moustache + goatee, oversized navy tee with a red label, black kitten on his shoulder). Writes character.svg
with the kit's SVG ids (CHARACTER.md) plus kitten rigs. Run: python3 make.py"""
import math, os

OUT = "#2b2420"
SKIN, SKIN_SH, SKIN_HI = "#eabd98", "#d6a07c", "#f6d2b4"
HAIR, HAIR_SH, HAIR_HI = "#1d1c22", "#121116", "#45434f"
TEE, TEE_SH, TEE_HI = "#4b4f59", "#3b3e47", "#5c616d"      # charcoal hoodie
RED, BAND, BAND_PAD = "#e5372d", "#efd3a8", "#f8e7c9"
CAT, CAT_SH, CAT_HI, PINK, AMBER = "#18181d", "#0c0c10", "#34343f", "#f08fa0", "#f3b33d"
W = 3.5   # outline width

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
           (148, -130), (152, -60), (144, 10), (118, 12), (110, -40), (0, -60), (-110, -40), (-118, 12)]
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
    """Big friendly teen eye: white, brown iris, two catchlights, a soft upper lash line."""
    y = 4
    white = f"M{cx - 30},{y} Q{cx},{y - 30} {cx + 30},{y} Q{cx},{y + 24} {cx - 30},{y} Z"
    clip = f"ec{'L' if s < 0 else 'R'}"
    return (f'<clipPath id="{clip}"><path d="{white}"/></clipPath><path d="{white}" fill="#fdfaf5"/>'
            f'<g clip-path="url(#{clip})"><circle cx="{cx + 3}" cy="{y - 1}" r="15" fill="#5b3418"/><circle cx="{cx + 3}" cy="{y + 1}" r="10" fill="#8a5427"/>'
            f'<circle cx="{cx + 3}" cy="{y}" r="6.5" fill="#140c07"/><circle cx="{cx + 8}" cy="{y - 6}" r="4" fill="#fff"/><circle cx="{cx - 2}" cy="{y + 6}" r="1.8" fill="#fff"/>'
            f'<path d="M{cx - 34},{y - 34} H{cx + 34} V{y - 14} Q{cx},{y - 26} {cx - 34},{y - 14} Z" fill="{SKIN_SH}" opacity="0.35"/></g>'
            f'<path d="M{cx - 32},{y + 1} Q{cx},{y - 31} {cx + 32},{y + 1}" stroke="{OUT}" stroke-width="5" fill="none" stroke-linecap="round"/>'
            f'<path d="M{cx + 30 * s},{y - 2} l{8 * s},-5" stroke="{OUT}" stroke-width="4" stroke-linecap="round"/>')

def brows():
    return (f'<path d="M-94,-46 Q-62,-62 -28,-50" stroke="{HAIR}" stroke-width="10" fill="none" stroke-linecap="round"/>'
            f'<path d="M94,-46 Q62,-62 28,-50" stroke="{HAIR}" stroke-width="10" fill="none" stroke-linecap="round"/>')

def mouths():
    lip = "#a5524b"
    m = {
        "closed": f'<path d="M-20,86 Q2,96 24,86" stroke="{lip}" stroke-width="5" fill="none" stroke-linecap="round"/>',
        "o": (f'<path d="M-26,80 Q2,76 30,80 Q26,110 2,112 Q-22,110 -26,80 Z" fill="#5a1f22" stroke="{OUT}" stroke-width="3" stroke-linejoin="round"/>'
              f'<path d="M-22,82 Q2,79 26,82 L24,89 Q2,87 -20,89 Z" fill="#fbf7f1"/>'
              f'<path d="M-12,104 Q2,95 16,104 Q2,112 -12,104 Z" fill="#e2646b"/>'),
        "smile": (f'<path d="M-30,80 Q2,84 34,78 Q28,104 2,106 Q-24,104 -30,80 Z" fill="#5a1f22" stroke="{OUT}" stroke-width="3" stroke-linejoin="round"/>'
                  f'<path d="M-26,81 Q2,85 30,79 L28,87 Q2,92 -24,88 Z" fill="#fbf7f1"/><path d="M-10,100 Q4,93 16,99 Q4,106 -10,100 Z" fill="#e2646b"/>'),
    }
    return "".join(f'<g id="m-{k}" class="mth" opacity="{1 if k == "smile" else 0}">{v}</g>' for k, v in m.items())

def head():
    face = "M-128,-64 C-132,20 -118,70 -82,104 C-54,128 -26,136 0,136 C26,136 54,128 82,104 C118,70 132,20 128,-64 C124,-138 70,-176 0,-176 C-70,-176 -124,-138 -128,-64 Z"
    cheek_sh = "M70,110 C112,74 126,22 124,-50 L128,-20 C128,40 112,82 82,104 C70,114 56,122 42,128 Z"
    return f'''
  {hair_back()}
  <g><ellipse cx="-127" cy="12" rx="19" ry="28" fill="{SKIN}" stroke="{OUT}" stroke-width="{W}"/><ellipse cx="127" cy="12" rx="19" ry="28" fill="{SKIN}" stroke="{OUT}" stroke-width="{W}"/>
     <path d="M-130,2 q-8,10 0,20 M130,2 q8,10 0,20" stroke="{SKIN_SH}" stroke-width="3" fill="none" stroke-linecap="round"/>
     <circle cx="133" cy="34" r="6.5" fill="#0c0c0e"/><circle cx="131" cy="32" r="2" fill="#6a6a74"/></g>
  <path d="{face}" fill="{SKIN}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="{cheek_sh}" fill="{SKIN_SH}" opacity="0.55"/>
  <ellipse cx="-78" cy="52" rx="20" ry="11" fill="#e8907a" opacity="0.35"/><ellipse cx="78" cy="52" rx="20" ry="11" fill="#e8907a" opacity="0.35"/>
  {brows()}
  <g id="eyes-open">{eye(-58, -1)}{eye(58, 1)}</g>
  <g id="eyes-shut" opacity="0"><path d="M-88,4 Q-58,20 -28,4" stroke="{OUT}" stroke-width="5" fill="none" stroke-linecap="round"/><path d="M28,4 Q58,20 88,4" stroke="{OUT}" stroke-width="5" fill="none" stroke-linecap="round"/></g>
  <path d="M4,22 Q-6,50 -2,56 Q6,62 16,56" stroke="#b47a5a" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  {mouths()}
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
    nx, ny = -math.sin(a), math.cos(a); ux, uy = math.cos(a), math.sin(a)
    q = lambda p0, p1, w0, w1: f"M{p0[0] + nx * w0:.1f},{p0[1] + ny * w0:.1f} L{p1[0] + nx * w1:.1f},{p1[1] + ny * w1:.1f} L{p1[0] - nx * w1:.1f},{p1[1] - ny * w1:.1f} L{p0[0] - nx * w0:.1f},{p0[1] - ny * w0:.1f} Z"
    cuff0 = (hx - ux * 34, hy - uy * 34); cuff1 = (hx - ux * 6, hy - uy * 6)
    rot = angle + 90 + hrot
    ribs = "".join(f'<path d="M{cuff0[0] + ux * t + nx * 22:.1f},{cuff0[1] + uy * t + ny * 22:.1f} L{cuff0[0] + ux * t - nx * 22:.1f},{cuff0[1] + uy * t - ny * 22:.1f}" stroke="{TEE_SH}" stroke-width="2"/>' for t in (8, 16, 24))
    return (f'<g transform="translate({hx:.1f} {hy:.1f}) rotate({rot:.1f})">{hand(kind, flip)}</g>'
            f'<path d="{q((ex, ey), cuff0, 40, 30)}" fill="{TEE}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>'
            f'<path d="M{ex + nx * 18:.1f},{ey + ny * 18:.1f} L{cuff0[0] + nx * 14:.1f},{cuff0[1] + ny * 14:.1f}" stroke="{TEE_HI}" stroke-width="8" stroke-linecap="round" opacity="0.7"/>'
            f'<path d="{q(cuff0, cuff1, 26, 24)}" fill="{TEE}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>{ribs}'
            f'<circle cx="{ex}" cy="{ey}" r="40" fill="{TEE}"/>')

EL, ER = (392, 760), (808, 760)      # elbows at the sleeve hems
POSES = {
    "up":    [forearm(EL, -92, "point", 150)],
    "card":  [forearm(EL, -118, "point", 150, hrot=-8)],
    "palms": [forearm(EL, -148, "palm", 135, hrot=-10), forearm(ER, -32, "palm", 135, True, 10)],
    "thumb": [forearm(EL, -55, "thumb", 135, hrot=-35)],
    "shrug": [forearm(EL, -160, "palm", 130, hrot=-25), forearm(ER, -20, "palm", 130, True, 25)],
    "wave":  [forearm(EL, -100, "palm", 150, hrot=6)],
}
HANG = {"L": f'<path d="M{EL[0] - 40},{EL[1] - 10} L{EL[0] - 34},1010 L{EL[0] + 24},1010 L{EL[0] + 40},{EL[1] - 10} Z" fill="{TEE}" stroke="{OUT}" stroke-width="{W}"/>',
        "R": f'<path d="M{ER[0] + 40},{ER[1] - 10} L{ER[0] + 34},1010 L{ER[0] - 24},1010 L{ER[0] - 40},{ER[1] - 10} Z" fill="{TEE}" stroke="{OUT}" stroke-width="{W}"/>'}
def pose_group(name, parts):
    uses_l = name in ("up", "card", "palms", "thumb", "shrug", "wave"); uses_r = name in ("palms", "shrug")
    hang = ("" if uses_l else HANG["L"]) + ("" if uses_r else HANG["R"])
    return f'<g id="pose-{name}" class="pose" opacity="0">{hang}{"".join(parts)}</g>'

# ------------------------------------------------------------------ body: oversized drop-shoulder tee
def body():
    tee = "M380,600 C430,572 490,560 540,558 L660,558 C710,560 770,572 820,600 C860,626 868,700 860,800 L776,812 L772,1010 L428,1010 L424,812 L340,800 C332,700 340,626 380,600 Z"
    hood = "M492,560 C470,520 520,500 600,500 C680,500 730,520 708,560 C690,620 650,642 600,642 C550,642 510,620 492,560 Z"
    return f'''
  <path d="{tee}" fill="{TEE}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="M776,812 L772,1010 L716,1010 C738,900 746,770 790,650 C830,700 856,750 860,800 Z" fill="{TEE_SH}" opacity="0.9"/>
  <path d="M424,812 C418,750 418,700 432,650 M776,812 C782,750 782,700 768,650" stroke="{TEE_SH}" stroke-width="5" fill="none"/>
  <path d="{hood}" fill="{TEE_SH}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="M566,470 L562,600 Q600,618 638,600 L634,470 Z" fill="{SKIN_SH}" stroke="{OUT}" stroke-width="{W}"/>
  <path d="M520,566 C540,604 570,618 600,618 C630,618 660,604 680,566" stroke="{OUT}" stroke-width="{W}" fill="none"/>
  <path d="M572,612 C566,660 568,700 574,736 M628,612 C634,660 632,700 626,736" stroke="#d9d6cf" stroke-width="6" fill="none" stroke-linecap="round"/>
  <rect x="566" y="732" width="14" height="22" rx="4" fill="#9a9aa2"/><rect x="620" y="732" width="14" height="22" rx="4" fill="#9a9aa2"/>
  <path d="M470,880 Q470,860 490,856 L710,856 Q730,860 730,880 L742,1010 L458,1010 Z" fill="{TEE_SH}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="M470,880 Q520,900 600,898 Q680,900 730,880" stroke="{OUT}" stroke-width="2.5" fill="none" opacity="0.6"/>
  <rect x="672" y="676" width="34" height="12" rx="3" fill="{RED}"/>'''

# ------------------------------------------------------------------ kitten on his left shoulder (viewer right)
def fur(cx, cy, rx, ry, n, jag, seed):
    r = rng(seed); pts = []
    for i in range(n * 2):
        a = i / (n * 2) * 2 * math.pi; k = 1 + (jag * (0.5 + 0.5 * r()) if i % 2 else 0)
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    return P(pts)

def kitten():
    kx, ky = 840, 470
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
