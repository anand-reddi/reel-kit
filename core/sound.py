"""Music bed (code-made beat), sound effects from earshot placed on their peaks, voice on top; -14 LUFS."""
import json, os, shutil, subprocess
import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy.signal import resample_poly, butter, sosfilt

SR = 48000
def earshot():
    for p in [os.environ.get("REELKIT_EARSHOT", ""), shutil.which("earshot") or "", os.path.expanduser("~/earshot/.venv/bin/earshot"),
              os.path.expanduser("~/.cache/reelkit/earshot/.venv/bin/earshot"), "/root/earshot/.venv/bin/earshot", "/tmp/eb/.venv/bin/earshot"]:
        if p and os.path.exists(p): return p
    return None

KEYS = {"minor": [0, 0, 3, -2], "major": [0, 0, 5, -3], "dark": [0, -1, -4, -2]}
def beat(n, cfg):
    if cfg.get("style", "beat") == "none": return np.zeros(n)
    bpm = cfg.get("bpm", 100); spb = 60 / bpm; root = cfg.get("root", 38); prog = KEYS.get(cfg.get("key", "minor"), KEYS["minor"])
    rng = np.random.default_rng(3); mus = np.zeros(n)
    def add(sig, at, g):
        i = int(at * SR); m = min(len(sig), n - i)
        if m > 0: mus[i:i + m] += sig[:m] * g
    kx = np.arange(int(.35 * SR)) / SR; kick = np.sin(2 * np.pi * (45 + 90 * np.exp(-kx * 30)) * kx) * np.exp(-kx * 9)
    hx = np.arange(int(.05 * SR)) / SR; hat = sosfilt(butter(2, 7000, "high", fs=SR, output="sos"), rng.standard_normal(len(hx))) * np.exp(-hx * 90)
    cx = np.arange(int(.18 * SR)) / SR; clap = sosfilt(butter(2, [900, 4000], "band", fs=SR, output="sos"), rng.standard_normal(len(cx))) * np.exp(-cx * 22)
    k, b = 0, 0.0
    while b < n / SR:
        add(kick, b, .9 if k % 2 == 0 else .55)
        if k % 2: add(clap, b, .35)
        add(hat, b + spb / 2, .25); add(hat, b, .12)
        f = 440 * 2 ** ((root + prog[(k // 4) % 4] - 69) / 12); bx = np.arange(int(spb * .9 * SR)) / SR
        add(np.tanh(2 * np.sin(2 * np.pi * f * bx)) * np.exp(-bx * 3) * .5, b, .5); b += spb; k += 1
    mus = sosfilt(butter(2, 5000, "low", fs=SR, output="sos"), mus)
    t = np.arange(n) / SR; return mus * np.interp(t, [0, .2, n / SR - .6, n / SR], [0, 1, 1, 0])

def mix(work, cues, dur, cfg):
    n = int(dur * SR); m = pyln.Meter(SR)
    vo, _ = sf.read(os.path.join(work, "vo.wav")); vo = np.pad(vo, (0, max(0, n - len(vo))))[:n]
    mus = beat(n, cfg.get("music", {}))
    sfx = np.zeros(n + SR); ear = earshot(); os.makedirs(os.path.join(work, "sfx"), exist_ok=True); used = []
    if not ear: print("  ! earshot not found: rendering without sound effects (run setup.sh)")
    for k, (at, sid, g) in enumerate(cues if ear else []):
        out = os.path.join(work, "sfx", f"{k:03d}.wav")
        r = subprocess.run([ear, "sfx", "render", sid, "-o", out, "--json"], capture_output=True, text=True)
        if r.returncode: print(f"  ! sfx {sid}: {r.stderr.strip()[-120:]}"); continue
        pk = float(json.loads(r.stdout[r.stdout.index("{"):])["meta"]["peak_s"]); a, sr = sf.read(out); a = a.mean(1) if a.ndim > 1 else a
        if sr != SR: a = resample_poly(a, SR, sr)
        e = int(.003 * SR); a[:e] *= np.linspace(0, 1, e); a[-e:] *= np.linspace(1, 0, e)
        i0 = int((at - pk) * SR)
        if i0 < 0: a = a[-i0:]; i0 = 0
        if i0 >= n: continue
        sfx[i0:i0 + len(a)] += a[:n + SR - i0] * 10 ** (g / 20); used.append(sid)
    sfx = sfx[:n]
    lv = cfg.get("levels", {})
    norm = lambda x, L: x * 10 ** ((L - m.integrated_loudness(x)) / 20) if np.abs(x).max() > 0 else x
    out = norm(vo, -15) + norm(mus, lv.get("music", -31)) + norm(sfx, lv.get("sfx", -24))
    out = np.stack([out, out], 1); out = norm(out, -14)
    lim = 10 ** (-1.8 / 20)
    if np.abs(resample_poly(out, 4, 1, axis=0)).max() > lim: out = np.tanh(out / lim) * lim; out = norm(out, -14)
    f = int(.06 * SR); out[-f:] *= np.linspace(1, 0, f)[:, None]; out[:240] *= np.linspace(0, 1, 240)[:, None]
    sf.write(os.path.join(work, "mix.wav"), out.astype(np.float32), SR, subtype="FLOAT")
    return m.integrated_loudness(out), len(used)
