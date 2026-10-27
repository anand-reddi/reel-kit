"""Voice: Kokoro reads each sentence in one go (a sentence can span several caption lines), so the intonation runs
through the lines instead of dropping at the end of every fragment; then each line's place inside the sentence is
found (the lines' solo lengths give the split, snapped to the quietest moment nearby, which is the gap between two
words). Per-word times are a character-weighted split of each line. Writes <work>/vo.wav and <work>/timing.json.
"voice": {"natural": false} goes back to one clip per line."""
import json, math, os, re
import numpy as np, soundfile as sf
from scipy.signal import resample_poly

SR = 48000
MODEL_DIRS = [os.environ.get("REELKIT_TTS", ""), os.path.expanduser("~/.cache/reelkit/tts"), "/root/tts"]

def _model():
    from kokoro_onnx import Kokoro
    for d in MODEL_DIRS:
        if d and os.path.exists(os.path.join(d, "kokoro-v1.0.onnx")):
            return Kokoro(os.path.join(d, "kokoro-v1.0.onnx"), os.path.join(d, "voices-v1.0.bin"))
    raise SystemExit("Kokoro model not found: run setup.sh (or set REELKIT_TTS to the folder with kokoro-v1.0.onnx).")

def plain(line):  # "*prompt*." -> "prompt."; "_viral_" (italic serif) -> "viral"
    return re.sub(r"(?<![A-Za-z0-9])_|_(?![A-Za-z0-9])", "", line.replace("*", ""))

def _trim(a):
    thr = 0.024 * np.abs(a).max(); nz = np.where(np.abs(a) > thr)[0]
    return a[max(0, nz[0] - 240): nz[-1] + 1200]

def _words(text, line, t0, d):
    raw = line.split(); words = text.split(); acc, ital, inside, iin = [], [], False, False
    for r in raw:                       # *one prompt* marks every word in the span; _word_ is italic serif
        if r.startswith("*"): inside = True
        if r.lstrip("*").startswith("_"): iin = True
        acc.append(inside); ital.append(iin)
        if r.rstrip(",.!?:;\"'").endswith("*"): inside = False
        if r.rstrip(",.!?:;\"'*").endswith("_"): iin = False
    wts = np.array([len(w.strip(",.!?:;")) + 2 for w in words], float)
    starts = t0 + np.concatenate([[0], np.cumsum(wts)[:-1]]) / wts.sum() * d * 0.94
    return [dict(w=w, accent=a_, italic=i_, t=round(s, 3)) for w, a_, i_, s in zip(words, acc, ital, starts)]

def _snap(a, i, win):
    """Move a split point to the quietest 10 ms within +-win samples (the gap between two words)."""
    lo, hi = max(0, i - win), min(len(a), i + win); hop = SR // 100
    if hi - lo < 2 * hop: return i
    e = [np.sqrt((a[j:j + hop] ** 2).mean()) for j in range(lo, hi - hop, hop // 2)]
    return lo + int(np.argmin(e)) * (hop // 2) + hop // 2

def speak(script, work):
    k = _model(); v_cfg = script.get("voice", {})
    voice, speed, lang = v_cfg.get("name", "am_puck"), v_cfg.get("speed", 1.0), v_cfg.get("lang", "en-us")
    say_map = v_cfg.get("say", {})          # pronunciation fixes: {"SQL": "sequel"}
    natural = v_cfg.get("natural", True)
    def said(text):
        for a, b in say_map.items(): text = text.replace(a, b)
        return text
    def synth(text):
        a, sr = k.create(said(text), voice=voice, speed=speed, lang=lang)
        return _trim(resample_poly(a, SR, sr))
    lines, clips, t = [], [], 0.0
    for si, sc in enumerate(script["scenes"]):
        src = sc["lines"]; groups, cur = [], []
        for li, line in enumerate(src):     # a sentence ends on . ? ! or : (or at the end of the scene)
            cur.append(li)
            if not natural or plain(line).rstrip().endswith((".", "?", "!", ":", "…")) or li == len(src) - 1: groups.append(cur); cur = []
        for gi, grp in enumerate(groups):
            gap = 0.2 if (si == 0 and gi == 0) else (0.24 if gi == 0 else (0.12 if natural else 0.06))
            texts = [plain(src[li]) for li in grp]
            a = synth(" ".join(texts)); t += gap; n = len(a)
            cuts = [0]
            if len(grp) > 1:
                solo = np.array([len(synth(x)) for x in texts], float)
                for b in (np.cumsum(solo)[:-1] / solo.sum() * n).astype(int): cuts.append(_snap(a, b, int(0.14 * SR)))
            cuts.append(n)
            for j, li in enumerate(grp):
                s0, s1 = t + cuts[j] / SR, t + cuts[j + 1] / SR
                lines.append(dict(scene=si, line=li, text=texts[j], start=round(s0, 3), end=round(s1, 3),
                                  words=_words(texts[j], src[li], s0, s1 - s0)))
            clips.append((t, a)); t += n / SR
    dur = script.get("duration") or math.ceil((t + 0.45) * 10) / 10
    if t > dur - 0.2: raise SystemExit(f"voice runs {t:.2f}s but duration is {dur}s: cut words or raise voice.speed")
    n = int(dur * SR); vo = np.zeros(n)
    for s, a in clips: i = int(s * SR); vo[i:i + len(a)] += a[:n - i]
    vo = vo / (np.abs(vo).max() + 1e-9) * 0.6
    sf.write(os.path.join(work, "vo.wav"), vo.astype(np.float32), SR)
    timing = dict(duration=dur, lines=lines)
    json.dump(timing, open(os.path.join(work, "timing.json"), "w"), indent=1)
    return timing
