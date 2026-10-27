"""Scan every frame of a keyed sequence (PNG dir) or a WebM: count visible green-tinted pixels anywhere and backdrop-red
pixels near the edge, per clip. Saves crops of the worst frames."""
import sys, os, json, glob, subprocess, numpy as np
from PIL import Image
from scipy import ndimage
from concurrent.futures import ProcessPoolExecutor
src, clips_f, outdir = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(outdir, exist_ok=True)
clips = json.load(open(clips_f))
def check(arr):
    rgb = arr[..., :3].astype(int); a = arr[..., 3]
    vis = a > 128; lum = rgb @ [0.3, 0.59, 0.11]
    green = vis & (lum > 50) & (rgb[..., 1] - rgb[..., 0] >= 6) & (rgb[..., 1] - rgb[..., 2] >= 6)   # green dominant: never right on him
    red = vis & (lum < 95) & (rgb[..., 0] - np.maximum(rgb[..., 1], rgb[..., 2]) > 40)            # dark red smear
    return int(green.sum()), int(red.sum()), green, red
def one(f):
    arr = np.array(Image.open(f).convert("RGBA")); g, r, _, _ = check(arr); return f, g, r
if os.path.isdir(src):
    files = sorted(glob.glob(f"{src}/*.png"))
else:
    tmp = os.path.join(outdir, "dec"); os.makedirs(tmp, exist_ok=True)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-c:v", "libvpx-vp9", "-i", src, f"{tmp}/%05d.png"], check=True)
    files = sorted(glob.glob(f"{tmp}/*.png"))
with ProcessPoolExecutor() as ex: res = list(ex.map(one, files, chunksize=20))
fps = 24
for name, (a, b) in clips.items():
    rows = res[int(round(a * fps)):int(round(b * fps))]
    if not rows: continue
    worst = max(rows, key=lambda x: x[1] + x[2])
    print(f"{name:13s} green max {max(r[1] for r in rows):4d}  edge-red max {max(r[2] for r in rows):4d}  worst {os.path.basename(worst[0])}")
    if worst[1] + worst[2] > 0:
        arr = np.array(Image.open(worst[0]).convert("RGBA")); _, _, g, r = check(arr)
        ys, xs = np.where(g | r); y0, x0 = max(0, int(np.median(ys)) - 90), max(0, int(np.median(xs)) - 90)
        bg = Image.new("RGBA", (1200, 720), (239, 236, 230, 255)); bg.alpha_composite(Image.fromarray(arr, "RGBA"))
        bg.convert("RGB").crop((x0, y0, x0 + 180, y0 + 180)).resize((360, 360), Image.NEAREST).save(f"{outdir}/{name}.png")
