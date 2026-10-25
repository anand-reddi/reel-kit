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
    # voluminous wavy mop: overlapping elongated clumps swept around the head (not round curls, not spikes)
    r = rng(5); cl = []
    for i in range(17):
        t = math.radians(-200 + 220 * i / 16 + (r() - 0.5) * 6)
        R = 150 + r() * 18
        cx, cy = R * math.cos(t), -118 + R * 0.92 * math.sin(t)
        cl.append((cx, cy, 70 + r() * 22, 40 + r() * 14, math.degrees(t) + 90 + (20 if math.cos(t) > 0 else -20)))
    cl += [(-170, -10, 46, 70, -12), (170, -10, 46, 70, 12), (-150, 40, 34, 52, -20), (150, 40, 34, 52, 20), (0, -130, 170, 130, 0)]
    o = "".join(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{a + W:.1f}" ry="{b + W:.1f}" transform="rotate({ang:.1f} {x:.1f} {y:.1f})" fill="{OUT}"/>' for x, y, a, b, ang in cl)
    f = "".join(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{a:.1f}" ry="{b:.1f}" transform="rotate({ang:.1f} {x:.1f} {y:.1f})" fill="{HAIR}"/>' for x, y, a, b, ang in cl)
    hi = "".join(f'<path d="M{x - 26 * math.cos(math.radians(ang)):.1f},{y - 26 * math.sin(math.radians(ang)):.1f} q{20 * math.sin(math.radians(ang)):.1f},{-20 * math.cos(math.radians(ang)):.1f} {52 * math.cos(math.radians(ang)):.1f},{52 * math.sin(math.radians(ang)):.1f}" stroke="{HAIR_HI}" stroke-width="6" fill="none" stroke-linecap="round" opacity="0.75"/>'
                 for x, y, a, b, ang in cl[:17:2])
    return o + f + hi

def hair_front():
    # big wavy locks falling over the forehead (like the art), each sweeping outward with a curled tip
    cap = f'<path d="M-196,-130 Q-170,-206 0,-222 Q170,-206 196,-130 L196,-150 L-196,-150 Z" fill="{HAIR}"/>'
    locks = [((-200, -120), (-118, -172), (-176, -62), -1), ((-150, -164), (-46, -190), (-112, -84), -1),
             ((-80, -188), (24, -194), (-40, -76), -1), ((-10, -194), (96, -184), (40, -82), 1),
             ((62, -188), (160, -160), (110, -78), 1), ((124, -170), (200, -118), (178, -58), 1)]
    out = cap
    for (x0, y0), (x1, y1), (tx, ty), d in locks:
        path = (f"M{x0},{y0} C{x0 + d * 4},{y0 + 50} {tx + d * 22},{ty - 40} {tx},{ty} "
                f"C{tx - d * 4},{ty - 10} {tx - d * 16},{ty - 16} {tx - d * 30},{ty - 22} "
                f"C{(tx + x1) / 2},{(ty + y1) / 2 + 10} {x1 - d * 2},{y1 + 40} {x1},{y1} Z")
        out += f'<path d="{path}" fill="{HAIR}" stroke="{OUT}" stroke-width="4.5" stroke-linejoin="round"/>'
        mx = (x0 + x1) / 2
        out += f'<path d="M{mx:.0f},{min(y0, y1) + 14} C{mx + d * 4:.0f},{(y0 + ty) / 2:.0f} {tx + d * 10},{ty - 50} {tx + d * 6},{ty - 22}" stroke="{HAIR_HI}" stroke-width="5" fill="none" stroke-linecap="round" opacity="0.7"/>'
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
    band = (f'<g transform="translate(6 40) rotate(-12)"><rect x="-44" y="-12" width="88" height="24" rx="11" fill="{BAND}" stroke="{OUT}" stroke-width="3"/>'
            f'<rect x="-13" y="-8" width="26" height="16" rx="3" fill="{BAND_PAD}" stroke="#9b7652" stroke-width="1.5"/>'
            + "".join(f'<circle cx="{x}" cy="{y}" r="1.6" fill="#9b7652"/>' for x in (-34, -26, 26, 34) for y in (-4, 4)) + "</g>")
    return f'''
  <path d="M-40,120 L-44,215 L44,215 L40,120 Z" fill="{SKIN_SH}" stroke="{OUT}" stroke-width="{W}"/>
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
def hand(kind, flip=False):
    o = f'stroke="{OUT}" stroke-width="4" stroke-linejoin="round"'
    f = lambda x, y, w, h, rot=0: f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{w / 2}" fill="{SKIN}" {o} transform="rotate({rot} {x + w / 2} {y + h})"/>'
    palm = f'<path d="M-30,-6 Q-34,-40 -20,-46 L22,-46 Q34,-40 30,-6 Q26,26 0,30 Q-26,26 -30,-6 Z" fill="{SKIN}" {o}/>'
    if kind == "point":
        g = f(-8, -112, 18, 70) + palm + f"<path d='M-24,-40 q4,-10 14,-6 M-24,-24 q6,-8 16,-4 M-22,-8 q8,-8 18,-2' stroke='{SKIN_SH}' stroke-width='4' fill='none'/>" + f(16, -52, 16, 42, 35)
    elif kind == "palm":
        g = "".join(f(-30 + i * 15, -96 + abs(i - 1.5) * 9, 15, 60) for i in range(4)) + palm + f(22, -46, 16, 42, 48)
    elif kind == "thumb":
        g = f(-8, -96, 18, 58, -8) + palm + f"<path d='M-24,-30 h40 M-24,-14 h40 M-22,2 h36' stroke='{SKIN_SH}' stroke-width='4'/>"
    else:
        g = palm
    return f'<g transform="scale({-1.38 if flip else 1.38} 1.38)">{g}</g>'

def forearm(elbow, angle, kind, length=150, flip=False, hrot=0):
    ex, ey = elbow; a = math.radians(angle); hx, hy = ex + length * math.cos(a), ey + length * math.sin(a)
    rot = angle + 90 + hrot
    nx, ny = -math.sin(a), math.cos(a)
    q = lambda w0, w1: f"M{ex + nx * w0:.1f},{ey + ny * w0:.1f} L{hx + nx * w1:.1f},{hy + ny * w1:.1f} L{hx - nx * w1:.1f},{hy - ny * w1:.1f} L{ex - nx * w0:.1f},{ey - ny * w0:.1f} Z"
    return (f'<path d="{q(34 + W, 24 + W)}" fill="{OUT}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/><circle cx="{ex}" cy="{ey}" r="{34 + W}" fill="{OUT}"/>'
            f'<path d="{q(34, 24)}" fill="{SKIN}"/><circle cx="{ex}" cy="{ey}" r="34" fill="{SKIN}"/>'
            f'<path d="M{ex + 14 * math.cos(a + 1.57):.1f},{ey + 14 * math.sin(a + 1.57):.1f} L{hx + 14 * math.cos(a + 1.57):.1f},{hy + 14 * math.sin(a + 1.57):.1f}" stroke="{SKIN_SH}" stroke-width="14" stroke-linecap="round" opacity="0.7"/>'
            f'<g transform="translate({hx:.1f} {hy:.1f}) rotate({rot:.1f})">{hand(kind, flip)}</g>')

EL, ER = (318, 812), (882, 812)      # elbows at the sleeve hems
POSES = {
    "up":    [forearm(EL, -95, "point", 170)],
    "card":  [forearm(EL, -122, "point", 170, hrot=-10)],
    "palms": [forearm(EL, -150, "palm", 150, hrot=-20), forearm(ER, -30, "palm", 150, True, 20)],
    "thumb": [forearm(EL, -40, "thumb", 150, hrot=-50)],
    "shrug": [forearm(EL, -165, "palm", 140, hrot=-40), forearm(ER, -15, "palm", 140, True, 40)],
    "wave":  [forearm(EL, -105, "palm", 170, hrot=5)],
}
HANG = {"L": f'<path d="M{EL[0] - 34},{EL[1]} L{EL[0] - 28},1010 L{EL[0] + 20},1010 L{EL[0] + 34},{EL[1]} Z" fill="{SKIN}" stroke="{OUT}" stroke-width="{W}"/>',
        "R": f'<path d="M{ER[0] + 34},{ER[1]} L{ER[0] + 28},1010 L{ER[0] - 20},1010 L{ER[0] - 34},{ER[1]} Z" fill="{SKIN}" stroke="{OUT}" stroke-width="{W}"/>'}
def pose_group(name, parts):
    uses_l = name in ("up", "card", "palms", "thumb", "shrug", "wave"); uses_r = name in ("palms", "shrug")
    hang = ("" if uses_l else HANG["L"]) + ("" if uses_r else HANG["R"])
    return f'<g id="pose-{name}" class="pose" opacity="0">{hang}{"".join(parts)}</g>'

# ------------------------------------------------------------------ body: oversized drop-shoulder tee
def body():
    tee = "M300,590 C360,560 450,548 520,546 L680,546 C750,548 840,560 900,590 C960,620 975,700 960,812 L840,830 L838,1010 L362,1010 L360,830 L240,812 C225,700 240,620 300,590 Z"
    return f'''
  <path d="{tee}" fill="{TEE}" stroke="{OUT}" stroke-width="{W}" stroke-linejoin="round"/>
  <path d="M840,830 L838,1010 L760,1010 C790,900 800,760 860,640 C900,700 950,760 960,812 Z" fill="{TEE_SH}" opacity="0.9"/>
  <path d="M240,812 L360,830 M840,830 L960,812" stroke="{OUT}" stroke-width="{W}"/>
  <path d="M250,790 L360,808 M850,808 L955,790" stroke="{TEE_HI}" stroke-width="5" opacity="0.8"/>
  <path d="M360,830 C352,760 352,700 368,640 M840,830 C848,760 848,700 832,640" stroke="{TEE_SH}" stroke-width="6" fill="none"/>
  <path d="M470,700 L560,780 L520,690 M650,740 L700,820" stroke="{TEE_SH}" stroke-width="7" fill="none" stroke-linecap="round"/>
  <path d="M512,548 Q600,630 688,548" fill="{SKIN_SH}" stroke="{OUT}" stroke-width="{W}"/>
  <path d="M500,546 Q600,650 700,546" stroke="{TEE_SH}" stroke-width="16" fill="none"/>
  <path d="M500,546 Q600,650 700,546" stroke="{OUT}" stroke-width="{W}" fill="none"/>
  <path d="M556,600 l-6,26 M644,600 l6,26" stroke="{SKIN_SH}" stroke-width="3" opacity="0.8"/>
  <g transform="translate(712 650)"><rect x="-17" y="0" width="34" height="96" fill="none" stroke="#ece8e0" stroke-width="3"/>
    <text x="0" y="28" text-anchor="middle" font-size="24" font-weight="700" fill="{RED}" font-family="sans-serif">オ</text>
    <text x="0" y="58" text-anchor="middle" font-size="24" font-weight="700" fill="{RED}" font-family="sans-serif">タ</text>
    <text x="0" y="88" text-anchor="middle" font-size="24" font-weight="700" fill="{RED}" font-family="sans-serif">ク</text></g>'''

# ------------------------------------------------------------------ kitten on his left shoulder (viewer right)
def fur(cx, cy, rx, ry, n, jag, seed):
    r = rng(seed); pts = []
    for i in range(n * 2):
        a = i / (n * 2) * 2 * math.pi; k = 1 + (jag * (0.5 + 0.5 * r()) if i % 2 else 0)
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    return P(pts)

def kitten():
    kx, ky = 872, 470
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
