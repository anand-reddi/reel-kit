"""Helpers: remove a near-white background connected to the image border, keep interior whites (eyes, label)."""
import numpy as np
from PIL import Image
from scipy import ndimage as nd

def cut_white(rgb, thr=26, soft=60):
    a = np.asarray(rgb.convert("RGB")).astype(float)
    d = np.sqrt(((255 - a) ** 2).sum(2))                 # distance from white
    near = d < thr
    lab, n = nd.label(near)
    edge = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
    bg = np.isin(lab, list(edge))
    band = nd.binary_dilation(bg, iterations=2) & ~bg
    alpha = np.ones(d.shape); alpha[bg] = 0
    alpha[band] = np.clip((d[band] - thr * 0.5) / soft, 0, 1)
    A = alpha[..., None]
    fg = np.where(A > 0.05, (a - (1 - A) * 255) / np.maximum(A, 0.05), a)   # un-mix the white fringe
    return Image.fromarray(np.dstack([np.clip(fg, 0, 255), alpha * 255]).astype(np.uint8), "RGBA")

def grid(img, box, scale, step, path):
    from PIL import ImageDraw
    c = img.convert("RGB").crop(box); c = c.resize((int(c.width * scale), int(c.height * scale))); d = ImageDraw.Draw(c)
    for x in range(box[0] - box[0] % step, box[2], step):
        X = (x - box[0]) * scale; d.line([(X, 0), (X, c.height)], fill=(0, 200, 0)); d.text((X + 2, 2), str(x), fill=(0, 120, 0))
    for y in range(box[1] - box[1] % step, box[3], step):
        Y = (y - box[1]) * scale; d.line([(0, Y), (c.width, Y)], fill=(0, 200, 0)); d.text((2, Y + 2), str(y), fill=(0, 120, 0))
    c.save(path)
