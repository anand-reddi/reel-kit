"""Rigs the @techinsixty presenter from the user's own art (src/master.png, white background).
Nothing is redrawn: the art is cut into parts with pivots (character-rigging), areas hidden behind moving parts are
in-painted so motion never tears, and only the pieces that do not exist in the art are painted to match: open-mouth
shapes, closed eyelids, kitten blink. Output: rig/*.png (full-canvas layers) + rig/character.json.
Run: python3 build.py"""
import json, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as nd

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
SRC = np.array(Image.open("src/master.png").convert("RGB")).astype(np.uint8)
H, W = SRC.shape[:2]

# ---------------------------------------------------------------- background removal (white, border-connected)
def alpha_from_white(a, thr=58):
    d = np.sqrt(((255.0 - a) ** 2).sum(2)); lab, _ = nd.label(d < thr)
    bg = np.isin(lab, list(set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}))
    band = nd.binary_dilation(bg, iterations=2) & ~bg
    al = np.ones(d.shape); al[bg] = 0; al[band] = np.clip((d[band] - 40) / 70, 0, 1)
    return al
ALPHA = alpha_from_white(SRC.astype(float))
A3 = ALPHA[..., None]
RGB = np.clip(np.where(A3 > 0.05, (SRC - (1 - A3) * 255) / np.maximum(A3, 0.05), SRC), 0, 255).astype(np.uint8)   # de-fringed

def poly(pts, feather=0):
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).polygon([tuple(p) for p in pts], fill=255)
    if feather: m = m.filter(ImageFilter.GaussianBlur(feather))
    return np.array(m) / 255.0

def inpaint(rgb, mask, r=6):
    return cv2.inpaint(rgb, (mask > 0).astype(np.uint8) * 255, r, cv2.INPAINT_TELEA)

def layer(rgb, alpha):
    return Image.fromarray(np.dstack([rgb, np.clip(alpha * 255, 0, 255)]).astype(np.uint8), "RGBA")

os.makedirs("rig", exist_ok=True)
def save(img, name): img.save(f"rig/{name}.png", optimize=True)

# ---------------------------------------------------------------- region masks
KITTEN_POLY = [(755, 312), (778, 228), (998, 296), (978, 330), (946, 390), (936, 410), (940, 440), (946, 590), (760, 590), (745, 470), (744, 432), (731, 401), (719, 370), (725, 345)]
TAIL_POLY = [(946, 590), (940, 440), (936, 410), (946, 390), (978, 330), (1065, 330), (1080, 610)]
HEAD_POLY = [(300, 0), (800, 0), (790, 228), (755, 312), (725, 345), (719, 370), (731, 401), (722, 406), (706, 398), (692, 360),
             (682, 388), (662, 412), (640, 430), (612, 439), (590, 432), (560, 419), (525, 396), (510, 372), (505, 452), (300, 452)]
shirt = (SRC[..., 2].astype(int) - SRC[..., 0] >= 15) & (SRC[..., 2] > 40) & (SRC[..., 0] < 90)
# every pixel belongs to exactly one part (so no edge pixel is left behind as a ghost when a part moves)
inK, inT = poly(KITTEN_POLY) > 0.5, poly(TAIL_POLY) > 0.5
YY = np.mgrid[0:H, 0:W][0]
# the shirt = the one big connected navy region (kitten fur has bluish pixels too, but they are not connected to it)
navy = (SRC[..., 2].astype(int) - SRC[..., 0] >= 22) & (SRC[..., 2] >= 48) & (ALPHA > 0.6)
lab, n = nd.label(navy); sizes = nd.sum(navy, lab, range(1, n + 1))
shirt_strong = lab == (int(np.argmax(sizes)) + 1)
shirt_strong = nd.binary_closing(shirt_strong, iterations=2) & (ALPHA > 0.6) & (YY > 440)
KIT = inK & ~shirt_strong
XX = np.mgrid[0:H, 0:W][1]
TAIL = inT & ~inK & ~shirt_strong
HEADR = (poly(HEAD_POLY) > 0.5) & ~inK & ~inT
SOLID = ALPHA > 0.5
KITv, TAILv = KIT & SOLID, TAIL & SOLID
# the seam where the kitten touches his hair: light anti-alias pixels there would show as a sliver once either part moves
XX0 = np.mgrid[0:H, 0:W][1]
SEAM = nd.binary_dilation(KIT, iterations=7) & nd.binary_dilation(HEADR & SOLID, iterations=7) & (YY < 470) & (XX0 < 800)
LIGHT = (SRC.astype(int).min(2) > 95)
ALPHA = np.where(SEAM & LIGHT, 0.0, ALPHA); A3 = ALPHA[..., None]
SOLID = ALPHA > 0.5; KITv = KIT & SOLID

# ---------------------------------------------------------------- body (shirt, neck, arms in pockets)
body_alpha = ALPHA * ~HEADR * ~KIT * ~TAIL
body_rgb = RGB.copy()
# what the head and kitten hide: fill so tilts never open a hole (neck under the jaw, shirt under the kitten)
jaw_band = (poly(HEAD_POLY) > 0.5) & (poly([(522, 380), (700, 345), (705, 460), (520, 460)]) > 0.5)
under_kit = KITv & nd.binary_dilation(shirt_strong, iterations=26)
fill = (jaw_band & SOLID) | under_kit | (TAILv & nd.binary_dilation(shirt_strong & (XX < 960), iterations=10))
body_rgb = inpaint(body_rgb, fill, 9)
body_alpha = np.maximum(body_alpha, fill * 1.0)
save(layer(body_rgb, body_alpha), "body")

# ---------------------------------------------------------------- head (hair + face), with hair continued under the kitten
head_alpha = ALPHA * HEADR
head_rgb = RGB.copy()
hair_under = KIT & nd.binary_dilation(HEADR & SOLID, iterations=24) & (YY < 450) & (XX0 < 800)
HAIR_C = np.median(RGB[HEADR & SOLID & (RGB.max(2) < 60)].reshape(-1, 3), 0).astype(np.uint8)
head_rgb[hair_under] = HAIR_C; head_alpha = np.maximum(head_alpha, nd.gaussian_filter(hair_under * 1.0, 1.0) * hair_under)

# skin field: a smooth fill computed only from skin pixels (never pulls in hair, brows or lashes)
f = SRC.astype(int)
yy, xx = np.mgrid[0:H, 0:W]
SKIN = (f[..., 0] > 150) & (f[..., 0] - f[..., 1] > 25) & (f[..., 1] - f[..., 2] > 10) & (f[..., 2] > 70) & (f[..., 2] < 200)
def skin_fill(sigma=7):
    m = SKIN.astype(float); num = np.dstack([nd.gaussian_filter(RGB[..., i] * m, sigma) for i in range(3)])
    den = nd.gaussian_filter(m, sigma)[..., None]; return np.clip(num / np.maximum(den, 1e-4), 0, 255).astype(np.uint8)
SKINF = skin_fill(7)

save(layer(head_rgb, head_alpha), "head")

# ---------------------------------------------------------------- blink: skin over the opening + a closed lash line
S = 4
EYE_PATCH = {"L": (505, 286, 583, 317), "R": (609, 262, 683, 295)}
CLOSED = {"L": [(510, 298), (526, 303), (544, 306), (561, 304), (575, 298), (583, 293)],
          "R": [(612, 279), (628, 284), (645, 286), (661, 283), (674, 276), (682, 270)]}
def blink():
    m = Image.new("L", (W, H), 0); d0 = ImageDraw.Draw(m)
    for box in EYE_PATCH.values(): d0.ellipse(box, fill=255)
    m = np.array(m.filter(ImageFilter.GaussianBlur(1.6))) / 255.0
    img = layer(SKINF, m)
    c = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    for k, pts in CLOSED.items():
        n = len(pts)
        for i in range(n - 1):   # tapered lash: thick in the middle, thin at the ends
            w = 1.4 + 2.6 * np.sin(np.pi * (i + 0.5) / (n - 1))
            d.line([(pts[i][0] * S, pts[i][1] * S), (pts[i + 1][0] * S, pts[i + 1][1] * S)], fill=(26, 20, 24, 255), width=int(w * S))
        cx = sum(p[0] for p in pts) / n
        d.arc([(cx - 22) * S, (pts[2][1] - 16) * S, (cx + 22) * S, (pts[2][1] - 2) * S], 200, 340, fill=(170, 105, 80, 150), width=int(1.4 * S))   # lid crease
    img.alpha_composite(c.resize((W, H), Image.LANCZOS)); return img
save(blink(), "blink")

# ---------------------------------------------------------------- mouths: the art's mouth is a closed slit; open shapes are painted to match
SLIT = [(579, 385), (596, 382), (614, 378), (630, 374), (642, 371)]
GOATEE = [(598, 386), (634, 383), (634, 402), (598, 404)]
gm = (poly(GOATEE) > 0.5) & (f.max(2) < 120)
goatee_layer = layer(RGB, nd.binary_dilation(gm, iterations=1) * ALPHA)
def slit_y(x):
    xs, ys = zip(*SLIT); return float(np.interp(x, xs, ys))
def mouth(h, width=1.0, teeth=False, tongue=True, smirk=False):
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if h > 0:   # cover the soul-patch so it can drop with the jaw
        cov = nd.binary_dilation(gm, iterations=2)
        patch = inpaint(RGB, cov, 4); a = np.zeros((H, W)); a[cov] = 1
        base = layer(patch, nd.gaussian_filter(a, 0.7) * cov)
    c = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    x0, x1 = 583, 640; cx = (x0 + x1) / 2; hw = (x1 - x0) / 2 * width
    if h > 0:
        top = [(x, slit_y(x)) for x in np.linspace(cx - hw, cx + hw, 24)]
        bot = [(x, slit_y(x) + h * np.sin(np.pi * (x - (cx - hw)) / (2 * hw)) ** 0.8) for x in np.linspace(cx + hw, cx - hw, 24)]
        shape = [(x * S, y * S) for x, y in top + bot]
        d.polygon(shape, fill=(58, 24, 26, 255))
        if tongue and h >= 7:
            d.ellipse([(cx - hw * 0.45) * S, (slit_y(cx) + h * 0.55) * S, (cx + hw * 0.45) * S, (slit_y(cx) + h * 1.25) * S], fill=(150, 66, 66, 255))
        if teeth:
            d.polygon([(x * S, y * S) for x, y in top] + [(x * S, (y + min(3.2, h * 0.45)) * S) for x, y in reversed(top)], fill=(240, 234, 226, 255))
        m2 = Image.new("L", (W * S, H * S), 0); ImageDraw.Draw(m2).polygon(shape, fill=255)
        c.putalpha(Image.fromarray(np.minimum(np.array(c.split()[3]), np.array(m2))))
        d = ImageDraw.Draw(c)
        d.line(shape[:24], fill=(30, 18, 20, 255), width=int(2.2 * S))                                                    # upper lip edge
        d.line([(x * S, (y + 1.6) * S) for x, y in [(p[0] / S, p[1] / S) for p in shape[24:]]], fill=(196, 120, 96, 200), width=int(1.6 * S))   # lower lip light
    if smirk:
        d.line([(640 * S, 371.5 * S), (648 * S, 367 * S), (654 * S, 361 * S)], fill=(40, 24, 26, 255), width=int(2.4 * S), joint="curve")
    out = base; out.alpha_composite(c.resize((W, H), Image.LANCZOS))
    if h > 0: out.alpha_composite(goatee_layer, (0, int(round(h * 0.6))))
    return out
MOUTHS = {"m-slight": dict(h=4), "m-mid": dict(h=8), "m-open": dict(h=12), "m-e": dict(h=6, teeth=True, tongue=False),
          "m-o": dict(h=10, width=0.62), "m-smirk": dict(h=0, smirk=True)}
for n, kw in MOUTHS.items(): save(mouth(**kw), n)

# ---------------------------------------------------------------- kitten: body (paws), head, right ear, tail, blink
KHEAD_CUT = [(700, 200), (1000, 200), (1000, 455), (930, 452), (880, 468), (840, 470), (800, 466), (760, 458), (700, 455)]
EAR_POLY = [(900, 372), (901, 335), (925, 296), (998, 286), (992, 345), (962, 400), (938, 410)]
khead_m = KIT & (poly(KHEAD_CUT) > 0.5); ear_m = khead_m & (poly(EAR_POLY) > 0.5) & ~(poly([(890, 360), (930, 360), (930, 410), (890, 410)]) > 0.5)
kbody_m = KIT & ~khead_m
kit_rgb = RGB.copy()
# fur continues under the head (so a head tilt shows fur, not the shirt) and under the ear
under_head = nd.binary_dilation(khead_m & SOLID, iterations=1) & SOLID & (poly([(735, 430), (945, 430), (945, 476), (735, 476)]) > 0.5)
kb_rgb = inpaint(kit_rgb, under_head & ~kbody_m, 6)
under_tail = (poly([(936, 470), (962, 470), (962, 580), (936, 580)]) > 0.5) & ~shirt_strong & nd.binary_dilation(KITv, iterations=6) & (TAILv | KITv)
kb_rgb = inpaint(kb_rgb, under_tail & ~kbody_m, 6)
save(layer(kb_rgb, np.maximum(ALPHA * kbody_m, (under_head | under_tail) * 1.0)), "kbody")
under_ear = nd.binary_dilation(ear_m & SOLID, iterations=3) & (YY > 345) & ~(khead_m & ~ear_m & SOLID)
under_ear |= ear_m & SOLID & (YY > 345)
kh_rgb = inpaint(kit_rgb, under_ear, 6)
save(layer(kh_rgb, np.maximum(ALPHA * (khead_m & ~ear_m), under_ear * 1.0)), "khead")
save(layer(RGB, ALPHA * ear_m), "kear")
save(layer(RGB, ALPHA * TAIL), "ktail")
def kblink():
    c = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    for (ex, ey, r) in ((774, 370, 15), (849, 397, 19)):
        d.ellipse([(ex - r) * S, (ey - r) * S, (ex + r) * S, (ey + r) * S], fill=(22, 22, 28, 255))
        d.arc([(ex - r * 0.8) * S, (ey - r * 0.5) * S, (ex + r * 0.8) * S, (ey + r * 0.55) * S], 15, 165, fill=(150, 152, 168, 255), width=int(2.6 * S))
    return c.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.5))
save(kblink(), "kblink")

# avatar for the profile card: his face on the accent red
full = Image.new("RGBA", (W, H), (0, 0, 0, 0))
for n in ("ktail", "body", "head", "kbody", "khead", "kear"): full.alpha_composite(Image.open(f"rig/{n}.png"))
av = Image.new("RGBA", (420, 420), (229, 55, 45, 255)); av.alpha_composite(full.crop((395, 130, 815, 550))); av.save("rig/avatar.png")
print("layers:", sorted(os.listdir("rig")))
