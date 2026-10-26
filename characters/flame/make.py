"""The @techinsixty flame head: an original faceless presenter. A soft gradient flame shaped as a triangle face (small
rounded forehead, straight sides flaring to a heavy jaw with clear corners, short pointed chin), a dark void that
follows the face with two blue eyes and a blue LED bot mouth, in an open black overshirt over a white tee.
Arms are built like a cartoon explainer presenter: broad shoulders, thick sleeves from the shoulder seam, smooth elbow,
rolled cuffs near the wrist, a bare wrist and big hands with thin outlines. Two-bone arm rig.
Run: python3 make.py -> character.svg + character.json"""
import json, math, os

# ------------------------------------------------------------------ palette
SHIRT, SHIRT_SH, SHIRT_HI, CUFF = "#232327", "#17171a", "#3b3b42", "#2e2e34"     # black overshirt
TEE, TEE_SH = "#f3f1ec", "#d8d4cb"                                              # white tee
LINE, LW = "#0c0c0e", 3
BTN = "#9a9aa2"
SKIN, SKIN_SH, SKIN_LN, HAND_OUT = "#3a3442", "#2a2531", "#5a5368", "#121016"  # shadow-figure neck and hands
BL = "#8fb2ff"

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

# triangle face (as in a face-shape chart): small rounded forehead, straight sides flaring out, wide heavy jaw with clear
# corners, then the jaw line runs in to a short pointed chin
FACE = ("M600,206 C650,206 690,226 702,262 L742,384 C752,414 762,442 754,462 C744,482 712,496 676,506 L632,520 "
        "Q600,530 568,520 L524,506 C488,496 456,482 446,462 C438,442 448,414 458,384 L498,262 C510,226 550,206 600,206 Z")
TONGUES = {   # rooted deep inside the head and swaying around their own base, so they never lift off
    "tongueM": ("M550,330 C542,204 588,132 604,52 C640,120 676,192 654,330 Z", "602 330", 4, 1.3),
    "tongueL": ("M494,350 C474,270 482,200 510,150 C528,210 552,252 556,340 Z", "522 340", 5, 1.1),
    "tongueR": ("M644,340 C648,252 670,204 694,152 C722,206 728,276 708,350 Z", "680 340", 5, 1.5),
}

def head():
    bloom = "".join(f'<path d="{d}" fill="url(#fl)"/>' for d in [FACE] + [d for d, *_ in TONGUES.values()])
    tongues = "".join(f'<g id="{k}"><path d="{d}" fill="url(#fl)" filter="url(#b2)"/></g>' for k, (d, *_) in TONGUES.items())
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
    void = 'transform="translate(600 384) scale(0.74 0.8) translate(-600 -384)"'
    core = 'transform="translate(600 378) scale(0.44 0.56) translate(-600 -378)"'
    return f'''<g id="head">
  <g opacity="0.55" filter="url(#b18)">{bloom}</g>
  <g id="flames">{tongues}</g>
  <path d="{FACE}" fill="url(#fl)" filter="url(#b2)"/>
  <path d="{FACE}" fill="url(#rim)" filter="url(#b2)"/>
  <path d="M708,282 L740,384 C750,414 756,436 752,452" stroke="#fff3d6" stroke-width="13" fill="none" stroke-linecap="round" opacity="0.55" filter="url(#b8)"/>
  <path d="M598,98 C588,132 572,164 562,204" stroke="#fff6dc" stroke-width="10" fill="none" stroke-linecap="round" opacity="0.5" filter="url(#b8)"/>
  <path d="M490,290 L460,384 C452,414 448,436 452,456" stroke="#ff4f9a" stroke-width="15" fill="none" stroke-linecap="round" opacity="0.5" filter="url(#b8)"/>
  <path d="M530,512 Q600,536 670,512" stroke="#4f7dff" stroke-width="10" fill="none" stroke-linecap="round" opacity="0.5" filter="url(#b8)"/>
  <path d="{FACE}" fill="url(#void)" {void} filter="url(#b8)"/>
  <path d="{FACE}" fill="#050309" opacity="0.85" {core} filter="url(#b18)"/>
  {eyes}
  {mouths}
</g>'''

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
def body():
    sw = ("M540,548 C480,556 424,572 396,602 C374,624 366,652 366,700 L362,1010 L838,1010 L834,700 "
          "C834,652 826,624 804,602 C776,572 720,556 660,548 Z")
    tee = "M552,548 Q600,540 648,548 L674,1010 L526,1010 Z"
    collar = lambda k: (f'<path d="M{600 - k * 46},544 L{600 - k * 96},556 Q{600 - k * 112},566 {600 - k * 104},588 L{600 - k * 56},640 L{600 - k * 42},586 Z" '
                        f'fill="{SHIRT}" stroke="{LINE}" stroke-width="{LW}" stroke-linejoin="round"/>'
                        f'<path d="M{600 - k * 94},566 L{600 - k * 58},620" stroke="{SHIRT_HI}" stroke-width="3" opacity="0.8"/>')
    pocket = lambda x: (f'<path d="M{x},698 L{x + 88},698 L{x + 88},786 Q{x + 44},794 {x},786 Z" fill="none" stroke="{LINE}" stroke-width="2.5" stroke-linejoin="round" opacity="0.9"/>'
                        f'<path d="M{x - 4},688 L{x + 92},688 L{x + 88},720 Q{x + 44},730 {x},720 Z" fill="{SHIRT}" stroke="{LINE}" stroke-width="{LW}" stroke-linejoin="round"/>'
                        f'<path d="M{x + 2},694 L{x + 86},694" stroke="{SHIRT_HI}" stroke-width="2.5" opacity="0.7"/>'
                        f'<circle cx="{x + 44}" cy="716" r="4.5" fill="{BTN}"/>')
    return f'''
  <path d="M566,460 C562,500 560,530 560,566 L640,566 C640,530 638,500 634,460 Z" fill="{SKIN}"/>
  <path d="M562,520 Q600,546 638,520 L640,566 L560,566 Z" fill="{SKIN_SH}"/>
  <path d="M548,552 C548,530 576,522 600,522 C624,522 652,530 652,552 Z" fill="{SHIRT_SH}" stroke="{LINE}" stroke-width="{LW}"/>
  <path d="{sw}" fill="{SHIRT}" stroke="{LINE}" stroke-width="{LW}" stroke-linejoin="round"/>
  <clipPath id="swc"><path d="{sw}"/></clipPath>
  <g clip-path="url(#swc)">
    <path d="M708,600 C752,630 780,680 790,760 L800,1010 L736,1010 C744,860 740,720 708,600 Z" fill="{SHIRT_SH}"/>
    <path d="M412,650 C404,730 400,860 398,1010" stroke="{SHIRT_HI}" stroke-width="9" fill="none" opacity="0.7"/>
  </g>
  <path d="{tee}" fill="{TEE}"/>
  <path d="M640,560 L664,1010 L674,1010 L648,548 Z" fill="{TEE_SH}"/>
  <path d="M554,550 Q600,580 646,550" stroke="{TEE_SH}" stroke-width="10" fill="none" stroke-linecap="round"/>
  <path d="M554,550 Q600,580 646,550" stroke="{LINE}" stroke-width="2" fill="none" opacity="0.5"/>
  <path d="M552,548 L526,1010 M648,548 L674,1010" stroke="{LINE}" stroke-width="{LW}"/>
  <path d="M542,600 L520,1010" stroke="{SHIRT_HI}" stroke-width="3" opacity="0.6"/>
  {"".join(f'<circle cx="{538 - (y - 600) * 0.05:.1f}" cy="{y}" r="5" fill="{BTN}"/>' for y in (700, 810, 920))}
  {collar(1)}{collar(-1)}
  {pocket(436)}{pocket(676)}
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
    "type": "svg", "file": "character.svg", "x": -60, "y": 1130, "width": 1200,
    "head_origin": "600 530", "avatar_view": "380 40 440 500", "head_tilt": 0.35,
    "poses": list(POSES_L),
    "arms": [{"id": "armL", "shoulder": list(SHL), "upper": U, "hands": ["point", "palm", "thumb"], "poses": POSES_L},
             {"id": "armR", "shoulder": list(SHR), "upper": U, "hands": ["palm", "point"], "poses": POSES_R}],
    "brows": {"sel": "#flames", "raise": -16},
    "idle": [{"sel": "#" + k, "rot": r, "period": p, "origin": o} for k, (d, o, r, p) in TONGUES.items()],
}, open(os.path.join(here, "character.json"), "w"), indent=1)
print("wrote character.svg + character.json")
