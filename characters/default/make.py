"""The @techinsixty presenter (default character): an original faceless figure with a black oval face (two blue glowing
eyes, a blue LED bot mouth that shows equaliser bars while talking), ears, a black fedora that lifts on accented words,
an open black overshirt over a white tee, and a silver chain with the 60-logo pendant that swings.
Arms are built like a cartoon explainer presenter: broad shoulders, thick sleeves from the shoulder seam, smooth elbow,
rolled cuffs near the wrist, a bare wrist and big hands with thin outlines. Two-bone arm rig.
Face shape presets from the classic face-shape chart: `python3 make.py <shape>` (oval default; round, heart, square,
oblong, diamond, triangle). Run: python3 make.py -> character.svg + character.json"""
import json, math, os, sys

# ------------------------------------------------------------------ palette
SHIRT, SHIRT_SH, SHIRT_HI, CUFF = "#232327", "#17171a", "#3b3b42", "#2e2e34"     # black overshirt
TEE, TEE_SH = "#f3f1ec", "#d8d4cb"                                              # white tee
LINE, LW = "#0c0c0e", 3
BTN = "#9a9aa2"
SKIN, SKIN_SH, SKIN_LN, HAND_OUT = "#3a3442", "#2a2531", "#5a5368", "#121016"  # shadow-figure neck and hands
BL = "#8fb2ff"
HAT, HAT_HI, BAND, FACE_C = "#18181c", "#303038", "#2a2a30", "#0a090e"

# ------------------------------------------------------------------ layout (svg coords)
SHL, SHR = (414, 640), (786, 640)     # shoulder joints at the outer top corners of the torso
U, F = 150, 140                        # upper arm, forearm (to the wrist)
HS = 1.4                               # hand scale

def tube(x0, x1, w0, w1): return f"M{x0},{-w0} L{x1},{-w1} L{x1},{w1} L{x0},{w0} Z"

# ------------------------------------------------------------------ hands (wrist at 0,0, fingers toward -y), thin outlines
def hand(kind, flip=False):
    fw = 15
    palm = "M-27,-4 Q-31,-34 -24,-56 L24,-56 Q31,-34 27,-4 Q20,10 0,12 Q-20,10 -27,-4 Z"
    f = []          # (x1, y1, x2, y2, width)
    if kind == "palm":
        for x, ln, ang in ((-18, 42, -9), (-6, 52, -3), (7, 50, 3), (19, 40, 10)):
            a = math.radians(ang - 90); f.append((x, -50, x + ln * math.cos(a), -50 + ln * math.sin(a), fw))
        f.append((-24, -22, -46, -46, fw + 1))
    elif kind == "point":
        f.append((-14, -50, -14, -106, fw))
        for x in (-1, 11, 21): f.append((x, -52, x, -62, fw))
        f.append((-20, -24, 2, -36, fw + 1))
    elif kind == "thumb":
        f.append((-22, -30, -30, -84, fw + 2))
        for y in (-48, -34, -20): f.append((-14, y, 22, y, fw))
    cap = lambda x1, y1, x2, y2, w, c: f'<path d="M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}" stroke="{c}" stroke-width="{w}" stroke-linecap="round"/>'
    g = "".join(cap(*a[:4], a[4] + 5, HAND_OUT) for a in f)
    g += f'<path d="{palm}" fill="{SKIN}" stroke="{HAND_OUT}" stroke-width="2.5" stroke-linejoin="round"/>'
    g += "".join(cap(*a[:4], a[4], SKIN) for a in f)
    g += f'<path d="{palm}" fill="{SKIN}" transform="scale(0.88) translate(0 -3)"/>'
    if kind == "palm":
        g += f'<path d="M-14,-24 q14,8 26,-2 M-6,-50 l0,-8 M7,-50 l0,-8" stroke="{SKIN_LN}" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
    elif kind == "point":
        g += f'<path d="M5,-52 l0,-8 M16,-52 l0,-8 M-16,-26 q10,-2 16,-8" stroke="{SKIN_LN}" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
    elif kind == "thumb":
        g += f'<path d="M-6,-41 l24,0 M-6,-27 l24,0" stroke="{SKIN_LN}" stroke-width="2.5" stroke-linecap="round"/>'
    return f'<g transform="scale({-HS if flip else HS} {HS})">{g}</g>'

# ------------------------------------------------------------------ head: soft gradient flame, triangle face, centred void (global coords)
DEFS = '''<defs>
  <linearGradient id="fl" gradientUnits="userSpaceOnUse" x1="600" y1="525" x2="600" y2="60">
    <stop offset="0" stop-color="#4f7dff"/><stop offset="0.16" stop-color="#b064ff"/><stop offset="0.36" stop-color="#ff5f8f"/>
    <stop offset="0.58" stop-color="#ff8a3a"/><stop offset="0.84" stop-color="#ffc24a"/><stop offset="1" stop-color="#ffe08a"/></linearGradient>
  <radialGradient id="rim" gradientUnits="userSpaceOnUse" cx="600" cy="370" r="200">
    <stop offset="0.55" stop-color="#ff6aa8" stop-opacity="0"/><stop offset="1" stop-color="#ff6aa8" stop-opacity="0.7"/></radialGradient>
  <radialGradient id="void" cx="0.5" cy="0.48" r="0.56">
    <stop offset="0" stop-color="#030208"/><stop offset="0.5" stop-color="#070410"/><stop offset="0.7" stop-color="#1c0a2a"/>
    <stop offset="0.84" stop-color="#5a1446" stop-opacity="0.7"/><stop offset="0.94" stop-color="#c03a5a" stop-opacity="0.25"/><stop offset="1" stop-color="#ff7a50" stop-opacity="0"/></radialGradient>
  <filter id="b2" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2"/></filter>
  <filter id="b8" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="8"/></filter>
  <filter id="b18" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="18"/></filter>
</defs>'''

# face shapes from the classic face-shape chart, as the right half (x offset from the centre line, y) from the top of the
# head to the chin; mirrored and smoothed. Pick one with `python3 make.py <shape>` (default: oval).
SHAPES = {
    "oval":     [(0, 204), (70, 210), (122, 242), (148, 296), (156, 356), (150, 414), (128, 464), (90, 504), (42, 528), (0, 534)],
    "round":    [(0, 212), (82, 218), (138, 254), (164, 320), (166, 384), (148, 446), (106, 498), (50, 524), (0, 530)],
    "heart":    [(0, 220), (44, 206), (104, 204), (152, 232), (168, 290), (160, 356), (132, 428), (86, 488), (38, 524), (0, 536)],
    "square":   [(0, 206), (96, 208), (146, 226), (160, 280), (162, 380), (158, 450), (134, 496), (74, 518), (0, 522)],
    "oblong":   [(0, 192), (70, 196), (118, 226), (136, 290), (138, 380), (132, 452), (106, 502), (58, 532), (0, 538)],
    "diamond":  [(0, 206), (52, 212), (100, 246), (146, 318), (160, 360), (144, 420), (100, 482), (46, 524), (0, 534)],
    "triangle": [(0, 206), (60, 210), (100, 250), (128, 330), (148, 400), (160, 452), (142, 490), (78, 512), (34, 526), (0, 530)],
}
FACE_SHAPE = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in SHAPES else "oval"

def smooth(pts, closed=True, k=1.0):
    n = len(pts); d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f} "
    for i in range(n if closed else n - 1):
        p0, p1, p2, p3 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        if not closed: p0, p3 = pts[max(i - 1, 0)], pts[min(i + 2, n - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 6, p1[1] + (p2[1] - p0[1]) * k / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) * k / 6, p2[1] - (p3[1] - p1[1]) * k / 6)
        d += f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} "
    return d + ("Z" if closed else "")

HALF = SHAPES[FACE_SHAPE]
FACE = smooth([(600 + x, y) for x, y in HALF] + [(600 - x, y) for x, y in reversed(HALF[1:-1])])
CHIN = HALF[-1][1]
def edge(side, inset):   # a soft highlight running down one cheek, following the face outline
    pts = [(600 + side * (x - inset), y) for x, y in HALF if 270 <= y <= 470]
    return smooth(pts, closed=False)

TONGUES = {   # rooted deep inside the head and swaying around their own base, so they never lift off
    "tongueM": ("M550,330 C542,204 588,132 604,52 C640,120 676,192 654,330 Z", "602 330", 4, 1.3),
    "tongueL": ("M494,350 C474,270 482,200 510,150 C528,210 552,252 556,340 Z", "522 340", 5, 1.1),
    "tongueR": ("M644,340 C648,252 670,204 694,152 C722,206 728,276 708,350 Z", "680 340", 5, 1.5),
    "tongueMR": ("M608,334 C612,250 636,196 648,124 C672,184 684,254 666,334 Z", "638 334", 5, 1.0),
    "tongueLL": ("M462,384 C438,322 442,262 464,212 C478,262 500,302 508,364 Z", "486 374", 6, 1.7),
    "tongueRR": ("M694,364 C700,302 722,262 736,212 C758,262 762,322 738,384 Z", "716 374", 6, 1.25),
}

def head():
    def eye(cx, cy):
        return (f'<ellipse cx="{cx}" cy="{cy}" rx="20" ry="24" fill="#3d6dff" opacity="0.6" filter="url(#b8)"/>'
                f'<ellipse cx="{cx}" cy="{cy}" rx="9" ry="12" fill="{BL}" filter="url(#b2)"/>'
                f'<ellipse cx="{cx}" cy="{cy - 1}" rx="4" ry="5.5" fill="#eef4ff"/>')
    eyes = (f'<g id="eyes-open">{eye(567, 352)}{eye(633, 352)}</g>'
            f'<g id="eyes-shut" opacity="0"><path d="M551,356 Q567,364 583,356 M617,356 Q633,364 649,356" stroke="{BL}" stroke-width="6" fill="none" '
            'stroke-linecap="round" filter="url(#b2)"/></g>')
    # LED bot mouth: a thin bar at rest, an equaliser while talking, a curved bar for the smile
    my = 432
    halo = lambda w, h: f'<rect x="{600 - w / 2}" y="{my - h / 2}" width="{w}" height="{h}" rx="{h / 2}" fill="#3d6dff" opacity="0.55" filter="url(#b8)"/>'
    bars = "".join(f'<rect x="{x - 4}" y="{my - h / 2}" width="8" height="{h}" rx="4" fill="{BL}"/>' for x, h in ((572, 10), (586, 22), (600, 32), (614, 22), (628, 10)))
    m = {
        "closed": halo(80, 20) + f'<rect x="574" y="{my - 3}" width="52" height="7" rx="3.5" fill="{BL}"/>',
        "o": halo(84, 44) + bars,
        "smile": halo(84, 26) + f'<path d="M572,{my - 8} Q600,{my + 14} 628,{my - 8}" stroke="{BL}" stroke-width="7" fill="none" stroke-linecap="round"/>',
    }
    mouths = "".join(f'<g id="m-{k}" class="mth" opacity="{1 if k == "smile" else 0}">{v}</g>' for k, v in m.items())
    hat = (  # black fedora: brim first, then the pinched crown with a band over its back half
        f'<path d="M386,266 C394,236 478,224 600,224 C722,224 806,236 814,266 C806,292 722,288 600,286 C478,288 394,292 386,266 Z" fill="{HAT}" stroke="{LINE}" stroke-width="{LW}" stroke-linejoin="round"/>'
        f'<path d="M404,272 C440,284 520,282 600,280 C680,282 760,284 796,272" stroke="{HAT_HI}" stroke-width="4" fill="none" stroke-linecap="round"/>'
        f'<path d="M478,258 C470,206 474,152 498,116 C538,100 572,122 600,112 C628,122 662,100 702,116 C726,152 730,206 722,258 C650,272 550,272 478,258 Z" fill="{HAT}" stroke="{LINE}" stroke-width="{LW}" stroke-linejoin="round"/>'
        f'<path d="M600,114 C596,140 598,170 604,196" stroke="{LINE}" stroke-width="3" fill="none" opacity="0.8"/>'
        f'<path d="M514,130 C500,160 496,200 500,236" stroke="{HAT_HI}" stroke-width="7" fill="none" stroke-linecap="round" opacity="0.8"/>'
        f'<path d="M480,222 C552,236 648,236 720,222 L722,258 C650,272 550,272 478,258 Z" fill="{BAND}" stroke="{LINE}" stroke-width="{LW}" stroke-linejoin="round"/>'
        f'<path d="M484,232 C556,246 644,246 716,232" stroke="#4a4a52" stroke-width="2.5" fill="none" opacity="0.8"/>')
    ear = lambda k: (f'<path d="M{600 + k * 146},330 C{600 + k * 186},318 {600 + k * 192},392 {600 + k * 150},404 Z" fill="{FACE_C}" stroke="{LINE}" stroke-width="{LW}" stroke-linejoin="round"/>'
                     f'<path d="M{600 + k * 158},344 C{600 + k * 176},346 {600 + k * 176},382 {600 + k * 158},388" stroke="#2c2a36" stroke-width="5" fill="none" stroke-linecap="round"/>')
    return f'''<g id="head"><g transform="translate(0 -34)">
  {ear(-1)}{ear(1)}
  <path d="{FACE}" fill="{FACE_C}" stroke="{LINE}" stroke-width="{LW}"/>
  <path d="{edge(-1, 22)}" stroke="#2a2833" stroke-width="12" fill="none" stroke-linecap="round" opacity="0.9" filter="url(#b8)"/>
  <ellipse cx="600" cy="380" rx="90" ry="110" fill="#000" opacity="0.5" filter="url(#b18)"/>
  {eyes}
  {mouths}
  <g id="hat">{hat}</g>
</g></g>'''

# ------------------------------------------------------------------ arm: thick sleeve from the shoulder seam, smooth elbow,
# rolled cuff near the wrist, bare wrist, big hand
def arm(side, rest_u, rest_f):
    flip = side == "R"; sx, sy = SHL if side == "L" else SHR
    s = -1 if flip else 1
    up_t = tube(0, U, 42, 37)
    fo_t = tube(0, F - 46, 37, 32)
    cuff = tube(F - 62, F - 36, 39, 37)
    wrist = tube(F - 40, F + 2, 22, 21)
    ink = lambda d: f'<path d="{d}" fill="{LINE}" stroke="{LINE}" stroke-width="{2 * LW}" stroke-linejoin="round"/>'
    hands = {"L": {"point": 0, "palm": -8, "thumb": -25}, "R": {"palm": 8, "point": 0}}[side]
    hg = "".join(f'<g id="arm{side}-{k}" opacity="0"><g transform="translate({F} 0) rotate({90 + hr})">{hand(k, flip)}</g></g>' for k, hr in hands.items())
    fore = f'transform="rotate({rest_f} {U} 0)"'
    return (f'<g id="arm{side}" transform="rotate({rest_u} {sx} {sy})"><g transform="translate({sx} {sy})">'
            f'{ink(up_t)}<g class="fore" {fore}><g transform="translate({U} 0)">{ink(fo_t)}{ink(wrist)}<circle r="{37 + LW}" fill="{LINE}"/></g></g>'
            f'<path d="{up_t}" fill="{SHIRT}"/><circle r="45" fill="{SHIRT}"/>'
            f'<path d="M30,-42 Q38,0 30,42" stroke="{LINE}" stroke-width="2.5" fill="none" opacity="0.8"/>'
            f'<path d="M46,{s * 26} L{U - 10},{s * 24}" stroke="{SHIRT_SH}" stroke-width="12" stroke-linecap="round"/>'
            f'<path d="M50,{-s * 28} L{U - 30},{-s * 26}" stroke="{SHIRT_HI}" stroke-width="5" stroke-linecap="round" opacity="0.9"/>'
            f'<g class="fore" {fore}><g transform="translate({U} 0)">'
            f'<path d="{wrist}" fill="{SKIN}"/><path d="M{F - 36},8 L{F},7" stroke="{SKIN_SH}" stroke-width="6" stroke-linecap="round"/>'
            f'{hg}'
            f'<circle r="37" fill="{SHIRT}"/><path d="{fo_t}" fill="{SHIRT}"/>'
            f'<path d="M-8,{-s * 20} Q6,{-s * 4} -4,{s * 16}" stroke="{LINE}" stroke-width="2.5" fill="none" stroke-linecap="round" opacity="0.8"/>'
            f'<path d="M12,{s * 22} L{F - 70},{s * 20}" stroke="{SHIRT_SH}" stroke-width="10" stroke-linecap="round"/>'
            f'<path d="{cuff}" fill="{CUFF}" stroke="{LINE}" stroke-width="{LW}" stroke-linejoin="round"/>'
            f'<path d="M{F - 49},-36 L{F - 49},36" stroke="{SHIRT_HI}" stroke-width="3" opacity="0.8"/>'
            f'</g></g></g></g>')

# ------------------------------------------------------------------ torso: open black overshirt over a white tee
def locket():
    """Silver chain with a round pendant carrying the @techinsixty 60 logo (logo60.png, embedded)."""
    import base64
    b64 = base64.b64encode(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo60.png"), "rb").read()).decode()
    chain = "M566,556 C566,610 584,642 600,650 C616,642 634,610 634,556"
    return (f'<path d="{chain}" stroke="{LINE}" stroke-width="7" fill="none" stroke-linecap="round"/>'
            f'<path d="{chain}" stroke="#c9ccd3" stroke-width="4" fill="none" stroke-dasharray="5 3" stroke-linecap="round"/>'
            f'<g id="pendant"><circle cx="600" cy="652" r="5" fill="none" stroke="#c9ccd3" stroke-width="3"/>'
            f'<clipPath id="lk"><circle cx="600" cy="690" r="29"/></clipPath>'
            f'<circle cx="600" cy="690" r="35" fill="#e2e4e9" stroke="{LINE}" stroke-width="3"/>'
            f'<circle cx="600" cy="690" r="29" fill="#000"/>'
            f'<image href="data:image/png;base64,{b64}" x="581" y="671" width="38" height="38" clip-path="url(#lk)"/>'
            f'<path d="M578,668 A30,30 0 0 1 604,660" stroke="#fff" stroke-width="2.5" fill="none" opacity="0.55"/></g>')

def body():
    sw = ("M540,548 C480,556 424,572 396,602 C374,624 366,652 366,700 L362,1010 L838,1010 L834,700 "
          "C834,652 826,624 804,602 C776,572 720,556 660,548 Z")
    tee = "M552,548 Q600,606 648,548 L674,1010 L526,1010 Z"   # crew neckline dips in front of the neck
    collar = lambda k: (f'<path d="M{600 - k * 46},544 L{600 - k * 96},556 Q{600 - k * 112},566 {600 - k * 104},588 L{600 - k * 56},640 L{600 - k * 42},586 Z" '
                        f'fill="{SHIRT}" stroke="{LINE}" stroke-width="{LW}" stroke-linejoin="round"/>'
                        f'<path d="M{600 - k * 94},566 L{600 - k * 58},620" stroke="{SHIRT_HI}" stroke-width="3" opacity="0.8"/>')
    pocket = lambda x: (f'<path d="M{x},698 L{x + 88},698 L{x + 88},786 Q{x + 44},794 {x},786 Z" fill="none" stroke="{LINE}" stroke-width="2.5" stroke-linejoin="round" opacity="0.9"/>'
                        f'<path d="M{x - 4},688 L{x + 92},688 L{x + 88},720 Q{x + 44},730 {x},720 Z" fill="{SHIRT}" stroke="{LINE}" stroke-width="{LW}" stroke-linejoin="round"/>'
                        f'<path d="M{x + 2},694 L{x + 86},694" stroke="{SHIRT_HI}" stroke-width="2.5" opacity="0.7"/>'
                        f'<circle cx="{x + 44}" cy="716" r="4.5" fill="{BTN}"/>')
    return f'''
  <path d="{sw}" fill="{SHIRT}" stroke="{LINE}" stroke-width="{LW}" stroke-linejoin="round"/>
  <clipPath id="swc"><path d="{sw}"/></clipPath>
  <g clip-path="url(#swc)">
    <path d="M708,600 C752,630 780,680 790,760 L800,1010 L736,1010 C744,860 740,720 708,600 Z" fill="{SHIRT_SH}"/>
    <path d="M412,650 C404,730 400,860 398,1010" stroke="{SHIRT_HI}" stroke-width="9" fill="none" opacity="0.7"/>
  </g>
  <path d="M548,552 C552,532 578,526 600,526 C622,526 648,532 652,552 Q600,566 548,552 Z" fill="{TEE_SH}" stroke="{LINE}" stroke-width="2.5"/>
  <path d="M570,440 C566,490 564,530 563,592 L637,592 C636,530 634,490 630,440 Z" fill="{FACE_C}" stroke="{LINE}" stroke-width="{LW}"/>
  <path d="M572,500 Q600,512 628,500" stroke="#2c2a36" stroke-width="5" fill="none" stroke-linecap="round"/>
  <path d="M566,560 Q600,574 634,560" stroke="#000" stroke-width="10" fill="none" opacity="0.45"/>
  <path d="{tee}" fill="{TEE}"/>
  <path d="M640,560 L664,1010 L674,1010 L648,548 Z" fill="{TEE_SH}"/>
  <path d="M552,550 Q600,606 648,550" stroke="{TEE_SH}" stroke-width="12" fill="none" stroke-linecap="round"/>
  <path d="M549,546 Q600,598 651,546" stroke="{LINE}" stroke-width="2.5" fill="none"/>
  <path d="M556,556 Q600,614 644,556" stroke="{LINE}" stroke-width="1.5" fill="none" opacity="0.5"/>
  <path d="M552,548 L526,1010 M648,548 L674,1010" stroke="{LINE}" stroke-width="{LW}"/>
  <path d="M542,600 L520,1010" stroke="{SHIRT_HI}" stroke-width="3" opacity="0.6"/>
  {"".join(f'<circle cx="{538 - (y - 600) * 0.05:.1f}" cy="{y}" r="5" fill="{BTN}"/>' for y in (700, 810, 920))}
  {collar(1)}{collar(-1)}
  {pocket(436)}{pocket(676)}
  {locket()}
  <path d="M470,860 C490,880 500,920 498,960 M730,850 C716,890 712,930 716,970" stroke="{LINE}" stroke-width="2.5" fill="none" stroke-linecap="round" opacity="0.6"/>'''

# ------------------------------------------------------------------ poses (u: shoulder angle, f: elbow bend; 90 = straight down)
POSES_L = {
    "rest":  dict(u=96, f=-4, hand="palm"),
    "up":    dict(u=172, f=96, hand="point"),
    "card":  dict(u=190, f=55, hand="point"),
    "palms": dict(u=128, f=100, hand="palm"),
    "shrug": dict(u=122, f=88, hand="palm"),
    "thumb": dict(u=162, f=108, hand="thumb"),
    "wave":  dict(u=170, f=94, hand="palm", wave=True),
}
POSES_R = {
    "rest":  dict(u=84, f=4, hand="palm"),
    "up":    dict(u=8, f=-96, hand="point"),
    "palms": dict(u=52, f=-100, hand="palm"),
    "shrug": dict(u=58, f=-88, hand="palm"),
}

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1000" width="1200" height="1000">
{DEFS}<g id="pres-body">
  {body()}
  {head()}
  {arm("L", POSES_L["rest"]["u"], POSES_L["rest"]["f"])}{arm("R", POSES_R["rest"]["u"], POSES_R["rest"]["f"])}
</g></svg>'''

here = os.path.dirname(os.path.abspath(__file__))
open(os.path.join(here, "character.svg"), "w").write(svg)
json.dump({
    "type": "svg", "file": "character.svg", "x": 60, "y": 1290, "width": 960,
    "head_origin": "600 500", "avatar_view": "380 40 440 500", "head_tilt": 0.35,
    "poses": list(POSES_L),
    "arms": [{"id": "armL", "shoulder": list(SHL), "upper": U, "hands": ["point", "palm", "thumb"], "poses": POSES_L},
             {"id": "armR", "shoulder": list(SHR), "upper": U, "hands": ["palm", "point"], "poses": POSES_R}],
    "brows": {"sel": "#hat", "raise": -10},
    "idle": [{"sel": "#pendant", "rot": 9, "period": 1.4, "origin": "600 652"}],
    "react": {"sel": "#pendant", "y": -8, "rot": 14, "origin": "600 652"},
}, open(os.path.join(here, "character.json"), "w"), indent=1)
print("wrote character.svg + character.json")
