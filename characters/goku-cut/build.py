"""Builds the goku-cut rig from the user's art: src/master.png (front, white bg) + src/parts.png (parts sheet).
Every layer is a full 1254x1254 canvas PNG so they stack exactly. Run: python3 build.py (after cutting parts/)."""
import math, json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cut import cut_white

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
W = H = 1254
master = cut_white(Image.open("src/master.png"))
M = np.array(master).astype(float)

def poly_mask(pts, feather=0):
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).polygon(pts, fill=255)
    return m.filter(ImageFilter.GaussianBlur(feather)) if feather else m

def take(img, mask):        # pixels of img inside mask
    a = np.array(img).copy(); a[..., 3] = (a[..., 3].astype(float) * np.array(mask) / 255).astype(np.uint8); return Image.fromarray(a, "RGBA")

def remove(img, mask):      # img with mask cut away
    a = np.array(img).copy(); a[..., 3] = (a[..., 3].astype(float) * (1 - np.array(mask) / 255)).astype(np.uint8); return Image.fromarray(a, "RGBA")

def canvas(): return Image.new("RGBA", (W, H), (0, 0, 0, 0))

# ---------------------------------------------------------------- kitten tail and right ear as their own layers
tail_cut = poly_mask([(956, 575), (950, 470), (958, 395), (985, 350), (1070, 340), (1075, 600)])
tail_take = poly_mask([(938, 580), (936, 470), (950, 390), (985, 345), (1072, 336), (1078, 605)])
ear_cut = poly_mask([(917, 398), (905, 340), (930, 305), (1000, 290), (995, 330), (972, 372), (952, 404)])
ear_take = poly_mask([(910, 410), (898, 335), (928, 296), (1004, 284), (1000, 334), (976, 378), (956, 414)])
tail = take(master, tail_take); ear = take(master, ear_take)
base = remove(remove(master, tail_cut), ear_cut)

# ---------------------------------------------------------------- his right forearm (viewer left), below the sleeve hem
fore_cut = poly_mask([(112, 1012), (250, 1038), (348, 1046), (366, 1100), (356, 1254), (112, 1254)])
fore_rest = take(base, fore_cut)
body = remove(base, fore_cut)          # body without that forearm (used by the gesture poses)
def clear_white(img, region):          # white background trapped between arm and torso (not reachable by the flood fill)
    a = np.array(img).copy(); r = np.array(region) > 0; wh = (a[..., :3].min(2) > 228) & r
    from scipy import ndimage as nd
    a[..., 3][wh] = 0; edge = nd.binary_dilation(wh, iterations=1) & ~wh & r
    a[..., 3][edge] = (a[..., 3][edge] * 0.5).astype(np.uint8); return Image.fromarray(a, "RGBA")
ARM_REGION = poly_mask([(100, 990), (380, 990), (380, 1254), (100, 1254)])
body = clear_white(body, ARM_REGION)

# ---------------------------------------------------------------- gesture forearms: his own drawn forearm, rotated at the elbow
PIV, WREST = (278, 1046), (318, 1200)                   # elbow (at the sleeve hem) and wrist, in the rest pose
strip = clear_white(take(master, poly_mask([(214, 1046), (340, 1046), (356, 1100), (356, 1206), (272, 1206), (236, 1120)])), ARM_REGION)
hem = take(body, poly_mask([(228, 1008), (336, 1010), (336, 1050), (228, 1046)], 1.5))
BELOW_HEM = poly_mask([(90, 1030), (210, 1036), (352, 1040), (400, 1040), (400, 1254), (90, 1254)], 1.0)
REST_ANG = math.degrees(math.atan2(WREST[1] - PIV[1], WREST[0] - PIV[0]))
def forearm(theta, hand, extra=0.0, hscale=1.25, absolute=None):
    """theta: direction elbow->wrist in image degrees (0 = right, -90 = up). Hand continues along it (+extra), or at `absolute`."""
    delta = theta - REST_ANG
    lay = canvas(); lay.alpha_composite(strip.rotate(-delta, resample=Image.BICUBIC, center=PIV))
    r = math.radians(delta); vx, vy = WREST[0] - PIV[0], WREST[1] - PIV[1]
    wx, wy = PIV[0] + vx * math.cos(r) - vy * math.sin(r), PIV[1] + vx * math.sin(r) + vy * math.cos(r)
    h = Image.open(f"parts/{hand}.png"); h = h.resize((int(h.width * hscale), int(h.height * hscale)), Image.LANCZOS)
    pad = Image.new("RGBA", (h.width * 3, h.height * 3), (0, 0, 0, 0)); pad.alpha_composite(h, (h.width, h.height))
    wrist = (h.width * 1.5, h.height * 2 - 10)
    ang = (absolute if absolute is not None else theta) + 90 + extra       # sprite points up (-90)
    pad = pad.rotate(-ang, resample=Image.BICUBIC, center=wrist)
    lay.alpha_composite(pad, (int(wx - wrist[0]), int(wy - wrist[1])))
    lay = remove(lay, BELOW_HEM)                                              # nothing of the arm below the sleeve line
    return lay

GESTURES = {   # pose -> forearm angle, hand sprite, options
    "up":    (-98, "h-point", dict(extra=4)),
    "card":  (-128, "h-point", dict(extra=8)),
    "palms": (-150, "h-palm", dict(extra=30, hscale=1.15)),
    "wave":  (-112, "h-wave", dict(extra=8, hscale=1.15)),
    "thumb": (-38, "h-thumb", dict(absolute=-100, hscale=1.2)),
}
os.makedirs("rig", exist_ok=True)
def save(img, name): img.save(f"rig/{name}.png", optimize=True)
rest = canvas(); rest.alpha_composite(body); rest.alpha_composite(fore_rest); save(rest, "pose-rest")
for name, (th, hand, opt) in GESTURES.items():
    p = canvas(); p.alpha_composite(body); p.alpha_composite(forearm(th, hand, **opt)); save(p, f"pose-{name}")
save(tail, "tail"); save(ear, "ear")

# ---------------------------------------------------------------- mouths from the sheet, fitted onto his lips
LIP_C, LIP_ANG = (610, 372), -10.5        # lip-line centre under the moustache, tilt
def mouth_layer(name, scale):
    s = np.array(Image.open(f"parts/{name}.png")).astype(float)
    skin = np.median(s[s[..., 3] > 250][:, :3], 0)
    dist = np.sqrt(((s[..., :3] - skin) ** 2).sum(2))
    from scipy import ndimage as nd
    inner = nd.binary_erosion(s[..., 3] > 200, iterations=9)
    keep = (dist > 34) & inner
    keep = nd.binary_dilation(keep, iterations=2)
    a = Image.fromarray((keep * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    spr = Image.fromarray(s.astype(np.uint8), "RGBA"); spr.putalpha(a)
    bb = spr.getbbox(); spr = spr.crop(bb)
    spr = spr.resize((int(spr.width * scale), int(spr.height * scale)), Image.LANCZOS).rotate(-LIP_ANG, resample=Image.BICUBIC, expand=True)
    c = canvas(); c.alpha_composite(spr, (int(LIP_C[0] - spr.width / 2), int(LIP_C[1] - 6 - spr.height * 0.18))); return c
MOUTHS = {"m-slight": 0.78, "m-a": 0.62, "m-o": 0.8, "m-e": 0.66, "m-smirk": 0.72}
for n, sc in MOUTHS.items(): save(mouth_layer(n, sc), n)

# ---------------------------------------------------------------- blink: skin over each eye + a closed lid line
def blink():
    S = 4; c = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    eyes = [((514, 282, 584, 316), (516, 270, 584, 306), (560, 330)), ((618, 264, 694, 300), (620, 256, 694, 292), (660, 312))]
    out = canvas()
    for box, arc, sample in eyes:
        skin = tuple(int(v) for v in np.median(M[sample[1]:sample[1] + 8, sample[0] - 15:sample[0] + 15, :3].reshape(-1, 3), 0))
        m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).ellipse(box, fill=255); m = m.filter(ImageFilter.GaussianBlur(2.5))
        lay = Image.new("RGBA", (W, H), skin + (0,)); lay.putalpha(m); out.alpha_composite(lay)
        d.arc([v * S for v in arc], 18, 162, fill=(30, 20, 18, 255), width=4 * S)
    out.alpha_composite(c.resize((W, H), Image.LANCZOS)); return out
save(blink(), "blink")

# kitten blink: black fur over each eye + a soft closed curve
def kblink():
    S = 4; c = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    for (cx, cy, rx, ry) in ((778, 365, 25, 27), (838, 381, 28, 30)):
        d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], fill=(20, 21, 27, 255))
        d.arc([(cx - rx * 0.8) * S, (cy - ry * 0.7) * S, (cx + rx * 0.8) * S, (cy + ry * 0.5) * S], 20, 160, fill=(105, 110, 128, 255), width=4 * S)
    return c.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.6))
save(kblink(), "kblink")

# avatar for the profile card: face crop on the paper accent red
av = Image.new("RGBA", (420, 420), (229, 55, 45, 255)); face = master.crop((395, 140, 815, 560)); av.alpha_composite(face); av.save("rig/avatar.png")
print("layers:", sorted(os.listdir("rig")))
