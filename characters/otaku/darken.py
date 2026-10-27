"""Deepen the near-black areas (hair, hoodie, cat) without touching skin, eyes or the logo: dark, unsaturated
pixels are scaled down by up to `amount`. Usage: darken.py <in_dir> <out_dir> [amount=0.42]"""
import os, sys, numpy as np, cv2
from multiprocessing import Pool
IN, OUT = sys.argv[1], sys.argv[2]; AMT = float(sys.argv[3]) if len(sys.argv) > 3 else 0.42
def one(name):
    im = cv2.imread(os.path.join(IN, name), cv2.IMREAD_UNCHANGED).astype(np.float32)
    bgr = im[..., :3]; lum = 0.11 * bgr[..., 0] + 0.59 * bgr[..., 1] + 0.3 * bgr[..., 2]; sat = bgr.max(-1) - bgr.min(-1)
    w = np.clip((120 - lum) / 50, 0, 1) * np.clip((60 - sat) / 40, 0, 1)
    im[..., :3] = bgr * (1 - AMT * w)[..., None]
    cv2.imwrite(os.path.join(OUT, name), np.clip(im + 0.5, 0, 255).astype(np.uint8))
if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True); names = sorted(f for f in os.listdir(IN) if f.endswith(".png"))
    with Pool(2) as p: p.map(one, names, chunksize=8)
    print(len(names), "frames")
