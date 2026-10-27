"""Upscale keyed RGBA frames 1.5x for close-ups: premultiplied Lanczos, line sharpening inside the character,
a slightly firmer alpha edge. Usage: up.py <in_dir> <out_dir> [scale]"""
import os, sys, numpy as np, cv2
from multiprocessing import Pool
IN, OUT = sys.argv[1], sys.argv[2]; K = float(sys.argv[3]) if len(sys.argv) > 3 else 1.5
def one(name):
    im = cv2.imread(os.path.join(IN, name), cv2.IMREAD_UNCHANGED).astype(np.float32) / 255.0   # BGRA
    h, w = im.shape[:2]; W, H = int(round(w * K)), int(round(h * K))
    a = im[..., 3:4]; pm = im[..., :3] * a
    pm2 = cv2.resize(pm, (W, H), interpolation=cv2.INTER_LANCZOS4)
    a2 = np.clip(cv2.resize(a, (W, H), interpolation=cv2.INTER_LANCZOS4), 0, 1)[..., None]
    # sharpen the lines (unsharp on premultiplied colour, radius ~1 px at the new size)
    blur = cv2.GaussianBlur(pm2, (0, 0), 1.1)
    pm2 = np.clip(pm2 + 0.85 * (pm2 - blur), 0, None)
    # firmer edge: steepen the alpha ramp a little (keeps it anti-aliased)
    a3 = np.clip((a2 - 0.5) * 1.35 + 0.5, 0, 1)
    rgb = np.where(a2 > 0.02, pm2 / np.maximum(a2, 1e-4), 0)
    rgb = np.clip(rgb, 0, 1)
    # same colour guards as the keyer: sharpening pushes the warm-dark outline towards red, and must never add green
    B, G, R = rgb[..., 0], rgb[..., 1], rgb[..., 2]; lum = 0.3 * R + 0.59 * G + 0.11 * B
    hot = (R - np.maximum(G, B) > 30 / 255) & (lum < 95 / 255)
    rgb[hot] = (lum[hot][:, None] * np.array([0.92, 0.96, 1.12]))   # BGR: a neutral warm dark
    rgb[..., 1] = np.minimum(rgb[..., 1], np.maximum(rgb[..., 0], rgb[..., 2]))
    rgb = np.clip(rgb, 0, 1)
    rgb[a3[..., 0] < 0.02] = 0          # empty pixels black (keeps the WebM small)
    out = np.concatenate([rgb, a3], -1)
    cv2.imwrite(os.path.join(OUT, name), (out * 255 + 0.5).astype(np.uint8))
if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    names = sorted(f for f in os.listdir(IN) if f.endswith(".png"))
    if len(sys.argv) > 4: names = names[int(sys.argv[4]):int(sys.argv[5])]
    with Pool(2) as p: p.map(one, names, chunksize=8)
    print(len(names), "frames")
