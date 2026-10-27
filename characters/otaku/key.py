"""Clean keying for a line-art character on a flat backdrop: no green, no red fringe, a crisp outline.
1. mask from colour distance to the backdrop; only the big connected shapes stay (drops stars / sparkles)
2. enclosed gaps: trapped backdrop (between hair strands, next to the cat, between arm and body) stays transparent;
   gaps that hold no backdrop colour (open mouth, nostrils, finger creases, chin shadow, inner ear) are filled solid
3. the interior keeps the source colours exactly
4. the silhouette edge is rebuilt from the mask shape: 1 px wider than the mask (where the drawn outline sits), smooth
   alpha, and a dark line colour, because the source's colour subsampling smeared backdrop red into the real outline
5. dark pixels with a strong red cast (backdrop smear in hair edges and lines) become a warm neutral dark
6. green is never allowed to exceed both red and blue, so no pixel can carry a green cast"""
import numpy as np
from scipy import ndimage
LUM = np.array([0.3, 0.59, 0.11])
def key(im, bg):
    d = np.sqrt(((im - bg) ** 2).sum(2)); m = d > 53
    lab, n = ndimage.label(m)
    if n:
        sizes = ndimage.sum(np.ones_like(d), lab, range(1, n + 1))
        m = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s > 0.02 * sizes.max()])
    filled = ndimage.binary_fill_holes(m)
    far = ~ndimage.binary_dilation(filled, iterations=10)
    bd = np.percentile(d[far], 98) if far.any() else 10
    hl, hn = ndimage.label(filled & ~m)
    if hn:
        idx = range(1, hn + 1); mins = ndimage.minimum(d, hl, idx); means = ndimage.mean(d, hl, idx)
        m = m | np.isin(hl, [i + 1 for i, (v, mu) in enumerate(zip(mins, means)) if v > bd + 14 and mu > 35])
    m = ndimage.binary_opening(m, iterations=1) | ndimage.binary_erosion(m, iterations=2)   # drop 1-px whiskers
    core = ndimage.binary_erosion(m, iterations=1)
    shape = ndimage.binary_dilation(m, iterations=1)
    a = np.clip(ndimage.gaussian_filter(shape.astype(float), 0.7) * 1.15, 0, 1); a = np.maximum(a, core); a[~ndimage.binary_dilation(shape, iterations=2)] = 0
    _, (iy, ix) = ndimage.distance_transform_edt(~core, return_indices=True)
    near = im[iy, ix]; nl = near @ LUM
    line = np.where((nl < 110)[..., None], nl[..., None] * np.array([1.0, 0.97, 0.95]), np.array([58.0, 44, 38]))
    fg = np.where(core[..., None], im, line)
    # backdrop red smeared into dark lines (hair edges, outlines, gaps): any dark pixel with a strong red cast becomes a
    # warm neutral dark; skin, lips, tongue and the cat's ears are brighter and stay untouched
    lum = fg @ LUM; red = (fg[..., 0] - np.maximum(fg[..., 1], fg[..., 2]) > 30) & (lum < 95)
    fg[red] = lum[red, None] * np.array([1.12, 0.96, 0.92])
    # no green cast anywhere: green may not exceed the larger of red and blue (tears stay blue, skin and teeth neutral)
    mx = np.maximum(fg[..., 0], fg[..., 2]); fg[..., 1] = np.minimum(fg[..., 1], mx)
    fg[a < 0.025] = 0
    return np.dstack([fg.clip(0, 255), a * 255]).astype(np.uint8), a
