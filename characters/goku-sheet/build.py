"""Assembles the presenter from the user's parts sheet (src/parts.png) only: blank head + torso + sheet eyes, mouths,
arms and kitten. Nose, bandage, moustache and goatee are not on the sheet, so they are drawn here in the same ink.
All layers are full-canvas PNGs (CANVAS) so they stack exactly. Run: python3 build.py -> rig/"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE); sys.path.insert(0, HERE)
from cut import cut_white

SHEET = Image.open("src/parts.png").convert("RGB")
CW, CH = 720, 740
INK = (22, 22, 30)

def part(box, thr=28):
    """Cut a sheet region from its white background; returns (sprite, its top-left in sheet coords)."""
    c = cut_white(SHEET.crop(box), thr=thr); return c, (box[0], box[1])

def canvas(): return Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
def put(dst, spr, x, y): dst.alpha_composite(spr, (int(round(x)), int(round(y)))); return dst
def mask_poly(pts, size, feather=0):
    m = Image.new("L", size, 0); ImageDraw.Draw(m).polygon(pts, fill=255)
    return m.filter(ImageFilter.GaussianBlur(feather)) if feather else m
def cut_away(img, pts, feather=1):
    a = np.array(img).copy(); m = np.array(mask_poly(pts, img.size, feather)) / 255
    a[..., 3] = (a[..., 3] * (1 - m)).astype(np.uint8); return Image.fromarray(a, "RGBA")

# ---------------------------------------------------------------- placement (sheet -> canvas)
TORSO_BOX = (18, 588, 442, 944); TORSO_AT = (130, 330)            # torso neck top lands at canvas y 330
HEAD_BOX = (8, 12, 308, 366)
t_off = (TORSO_AT[0] - TORSO_BOX[0], TORSO_AT[1] - TORSO_BOX[1])   # sheet->canvas for torso coords
# head neck (sheet 163, 362) goes onto the torso neck (sheet 225, 628)
h_off = (225 + t_off[0] - 163, 628 + t_off[1] - 362)
H = lambda x, y: (x + h_off[0], y + h_off[1])                      # head-sheet coords -> canvas

torso, _ = part(TORSO_BOX); head, _ = part(HEAD_BOX)
# the blank head's label text sits under the neck: clear anything below the neck line
head = cut_away(head, [(0, 352), (300, 352), (300, 354), (0, 354)] and [(0, 355 - 12), (300, 355 - 12), (300, 354), (0, 354)], 0)

# ---------------------------------------------------------------- face parts from the sheet
def sprite(box, scale, flip=False, thr=28):
    s, _ = part(box, thr); s = s.crop(s.getbbox())
    if flip: s = s.transpose(Image.FLIP_LEFT_RIGHT)
    return s.resize((max(1, int(s.width * scale)), max(1, int(s.height * scale))), Image.LANCZOS)

EYE_SC = 0.42; MOUTH_SC = 0.58
EYES = {"open": (340, 75, 495, 170), "half": (525, 75, 680, 170), "closed": (710, 75, 865, 170), "left": (890, 75, 1045, 170), "right": (1075, 75, 1230, 170)}
MOUTHS = {"closed": (30, 430, 150, 530), "slight": (180, 430, 300, 530), "a": (330, 420, 465, 535), "o": (490, 425, 610, 530),
          "e": (630, 430, 760, 530), "smile": (780, 430, 910, 530), "smirk": (930, 430, 1060, 530), "laugh": (1090, 420, 1225, 535)}
EYE_R, EYE_L = H(195, 234), H(133, 234)        # eye centres on the blank face (viewer right / left)
MOUTH_C = H(164, 285)

def eye_anchor(spr):
    """Centre of the eye opening inside a sprite: the white/iris area under the brow (fallback: lower-middle)."""
    a = np.array(spr).astype(float); h = a.shape[0]
    white = (a[..., :3].min(2) > 225) & (a[..., 3] > 200); white[: int(h * 0.35)] = False
    if white.sum() < 20:
        dark = (a[..., :3].max(2) < 90) & (a[..., 3] > 200); dark[: int(h * 0.45)] = False; white = dark
    ys, xs = np.nonzero(white); return (xs.mean(), ys.mean()) if len(xs) else (a.shape[1] / 2, h * 0.6)

def eyes_layer(kind):
    c = canvas()
    base = sprite(EYES["open"], EYE_SC); ax, ay = eye_anchor(base)          # anchor from the open eye so every state lines up
    for flip, (cx, cy) in ((True, EYE_L), (False, EYE_R)):
        sp = sprite(EYES[kind], EYE_SC, flip=flip); ox = (sp.width - ax) if flip else ax
        put(c, soft_patch(sp, 3), cx - ox, cy - ay)
    return c

def soft_patch(spr, pad=6):
    """Feather a mouth sprite's skin patch so it melts into the face."""
    a = np.array(spr).astype(float); al = Image.fromarray(a[..., 3].astype(np.uint8))
    er = al.filter(ImageFilter.MinFilter(pad * 2 + 1)).filter(ImageFilter.GaussianBlur(pad * 0.8))
    a[..., 3] = np.minimum(a[..., 3], np.array(er)); return Image.fromarray(a.astype(np.uint8), "RGBA")

MOUTH_SCALES = {"a": 0.47, "e": 0.47, "laugh": 0.47}
def mouth_layer(kind):
    c = canvas(); m = soft_patch(sprite(MOUTHS[kind], MOUTH_SCALES.get(kind, MOUTH_SC)), 4)
    return put(c, m, MOUTH_C[0] - m.width / 2, MOUTH_C[1] - m.height * 0.45)

# ---------------------------------------------------------------- drawn features: nose, bandage, moustache, goatee, stubble
def features():
    S = 4; c = Image.new("RGBA", (CW * S, CH * S), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    P = lambda x, y: (x * S, y * S)
    nx, ny = H(165, 258)
    d.line([P(nx + 2, ny - 14), P(nx - 3, ny), P(nx + 2, ny + 3)], fill=(150, 90, 62, 255), width=int(2.2 * S), joint="curve")
    d.arc([P(nx - 7, ny - 2)[0], P(nx - 7, ny - 2)[1], P(nx + 7, ny + 6)[0], P(nx + 7, ny + 6)[1]], 25, 155, fill=(150, 90, 62, 200), width=int(1.6 * S))
    # bandage across the bridge
    bx, by = H(165, 248); band = Image.new("RGBA", (64 * S, 22 * S), (0, 0, 0, 0)); bd = ImageDraw.Draw(band)
    bd.rounded_rectangle([1 * S, 1 * S, 63 * S, 21 * S], radius=9 * S, fill=(238, 208, 165, 255), outline=(120, 86, 56, 255), width=int(1.6 * S))
    bd.rounded_rectangle([24 * S, 4 * S, 40 * S, 18 * S], radius=3 * S, fill=(248, 230, 200, 255), outline=(120, 86, 56, 200), width=int(1 * S))
    for x in (8, 13, 18, 46, 51, 56):
        for y in (8, 14): bd.ellipse([(x - 0.9) * S, (y - 0.9) * S, (x + 0.9) * S, (y + 0.9) * S], fill=(120, 86, 56, 255))
    band = band.resize((44 * S, 15 * S), Image.LANCZOS).rotate(8, resample=Image.BICUBIC, expand=True); c.alpha_composite(band, (int((bx - band.width / S / 2) * S), int((by - band.height / S / 2) * S)))
    # moustache: two tapered wings meeting under the nose
    mx, my = H(164, 274)
    for sgn in (-1, 1):
        d.polygon([P(mx, my - 4), P(mx + sgn * 10, my - 6), P(mx + sgn * 20, my - 3), P(mx + sgn * 27, my + 5), P(mx + sgn * 24, my + 7), P(mx + sgn * 15, my + 2), P(mx, my + 3)], fill=INK + (255,))
    # goatee under the lip and on the chin
    gx, gy = H(164, 299)
    d.polygon([P(gx - 8, gy - 4), P(gx, gy - 6), P(gx + 8, gy - 4), P(gx + 5, gy + 6), P(gx, gy + 9), P(gx - 5, gy + 6)], fill=INK + (255,))
    d.polygon([P(gx - 3, gy - 12), P(gx + 3, gy - 12), P(gx + 2, gy - 8), P(gx - 2, gy - 8)], fill=INK + (230,))
    # stubble along the jaw
    r = 17
    for i in range(60):
        t = math.radians(-70 + i * 140 / 59); r = (r * 1103515245 + 12345) & 0x7FFFFFFF
        x, y = H(164 + math.sin(t) * 56 * (0.9 + (r % 100) / 1250), 262 + (1 - math.cos(t)) * 34 + (r % 6))
        d.ellipse([P(x - 0.9, y - 0.9)[0], P(x - 0.9, y - 0.9)[1], P(x + 0.9, y + 0.9)[0], P(x + 0.9, y + 0.9)[1]], fill=INK + (110,))
    return c.resize((CW, CH), Image.LANCZOS)

# ---------------------------------------------------------------- arms: torso sleeves out, sheet arm sprites in
L_SLEEVE = [(30, 845), (165, 845), (160, 944), (30, 944)]                                   # forearm stub below the left sleeve (torso sheet coords)
R_SLEEVE = [(442 - x + 18, y) for x, y in L_SLEEVE]                                          # mirrored (viewer-right)
to_t = lambda pts: [(x - TORSO_BOX[0], y - TORSO_BOX[1]) for x, y in pts]
BENT, RAISED = (775, 655, 965, 915), (980, 575, 1235, 918)
ARM_SC = 0.9
def tight(s, px=1):
    """Shave the light fringe off a cut-out edge."""
    a = np.array(s); al = Image.fromarray(a[..., 3]).filter(ImageFilter.MinFilter(px * 2 + 1)).filter(ImageFilter.GaussianBlur(0.6))
    a[..., 3] = np.minimum(a[..., 3], np.array(al)); return Image.fromarray(a, "RGBA")

def arm_sprite(box, flip=False):
    s, _ = part(box, thr=40); s = tight(s)
    if flip: s = s.transpose(Image.FLIP_LEFT_RIGHT)
    return s.resize((int(s.width * ARM_SC), int(s.height * ARM_SC)), Image.LANCZOS)
# where each arm sprite's shoulder (sheet coords inside the sprite box) lands on the torso shoulder (torso sheet coords)
ARMS = {"bent": (BENT, (893, 672), (162, 652), False), "raised": (RAISED, (996, 690), (162, 652), True)}   # sprite anchor (sheet) -> torso anchor; flip for the left side

def pose(left=None, right=None):
    t = torso
    if left: t = cut_away(t, to_t(L_SLEEVE))
    if right: t = cut_away(t, to_t(R_SLEEVE))
    c = canvas()
    put(c, head, h_off[0] + HEAD_BOX[0], h_off[1] + HEAD_BOX[1])
    put(c, t, *TORSO_AT)
    for side, kind in (("L", left), ("R", right)):
        if not kind: continue
        box, sh, at, fl = ARMS[kind]
        flip = fl if side == "L" else not fl
        s = arm_sprite(box, flip=flip)
        bx0, by0 = box[0], box[1]
        ax = (at[0] if side == "L" else 442 - at[0] + 18) + t_off[0]; ay = at[1] + t_off[1]
        sx = (sh[0] - bx0) * ARM_SC; sy = (sh[1] - by0) * ARM_SC
        if flip: sx = s.width - sx
        put(c, s, ax - sx, ay - sy)
    c.alpha_composite(eyes_layer("open")); c.alpha_composite(mouth_layer("closed"))
    return c

# ---------------------------------------------------------------- kitten on the right shoulder
KIT_BODY, KIT_TAIL = (636, 1026, 755, 1175), (866, 1040, 935, 1158)
def kitten():
    c = canvas(); b = tight(sprite(KIT_BODY, 1.32, thr=34)); x, y = 440, 418 - b.height; put(c, b, x, y); return c, (x, y, b.width, b.height)
def tail():
    c = canvas(); t = tight(sprite(KIT_TAIL, 1.2)); put(c, t, 548, 268); return c

os.makedirs("rig", exist_ok=True)
def save(img, n): img.save(f"rig/{n}.png", optimize=True)
POSES = {"rest": pose(), "explain": pose(left="bent"), "point": pose(right="bent"), "both": pose(left="bent", right="bent"), "wave": pose(left="raised")}
for n, img in POSES.items(): save(img, f"pose-{n}")
for k in ("slight", "a", "e", "o", "smirk", "smile"): save(mouth_layer(k), f"m-{k}")
save(eyes_layer("closed"), "blink"); save(eyes_layer("left"), "look-left"); save(eyes_layer("right"), "look-right")
save(features(), "features")
kc, kb = kitten(); save(kc, "kitten"); save(tail(), "tail")
# kitten blink: black fur over its eyes + soft curves
S = 4; kbl = Image.new("RGBA", (CW * S, CH * S), (0, 0, 0, 0)); d = ImageDraw.Draw(kbl)
for ex, ey in ((kb[0] + 49, kb[1] + 82), (kb[0] + 96, kb[1] + 82)):
    d.ellipse([(ex - 16) * S, (ey - 16) * S, (ex + 16) * S, (ey + 16) * S], fill=(18, 18, 24, 255))
    d.arc([(ex - 10) * S, (ey - 8) * S, (ex + 10) * S, (ey + 6) * S], 20, 160, fill=(110, 112, 128, 255), width=3 * S)
save(kbl.resize((CW, CH), Image.LANCZOS), "kblink")
print("kitten box", kb)
