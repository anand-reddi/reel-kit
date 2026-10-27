"""Clean keying for a character on a flat backdrop.
- alpha from colour distance to the backdrop, then only the big connected shapes (drops stars / sparkles)
- small enclosed gaps (nostrils, finger creases, shadow under the chin, inside the ears) are filled when their colour
  is not the backdrop's: they are the character's own reddish shadows; trapped backdrop (between hair strands, next to
  the cat, between arm and body) stays transparent
- everything 2 px inside the silhouette is fully opaque and keeps its original colour (no green tint)
- only the outer edge band is soft, with the backdrop's red removed from it"""
import numpy as np
from scipy import ndimage
def key(im, bg, hole_px=900):
    d = np.sqrt(((im - bg) ** 2).sum(2)); soft = np.clip((d - 38) / 44, 0, 1)
    m = soft > 0.35
    lab, n = ndimage.label(m)
    if n:
        sizes = ndimage.sum(np.ones_like(soft), lab, range(1, n + 1))
        m = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s > 0.02 * sizes.max()])
    filled = ndimage.binary_fill_holes(m); holes = filled & ~m
    bd = np.percentile(d[~filled], 99.5) if (~filled).any() else 20   # how far real backdrop pixels stray from its colour
    holes &= d > bd + 6                                               # only the character's own reddish shadows, never trapped backdrop
    hl, hn = ndimage.label(holes)
    if hn:
        hs = ndimage.sum(np.ones_like(soft), hl, range(1, hn + 1))
        m = m | np.isin(hl, [i + 1 for i, s in enumerate(hs) if s < hole_px])
    core = ndimage.binary_erosion(m, iterations=2)
    band = ndimage.binary_dilation(m, iterations=2) & ~core
    a = np.where(core, 1.0, np.where(band, soft, 0.0))
    a = np.maximum(ndimage.gaussian_filter(a, 0.6), core)
    ae = np.maximum(a, 1e-3)[..., None]
    un = np.clip((im - (1 - ae) * bg) / ae, 0, 255)
    fg = np.where(core[..., None], im, un)
    fg[a < 0.025] = 0                                      # empty pixels black: compresses far better
    return np.dstack([fg, a * 255]).astype(np.uint8), a
