"""Voice: one Kokoro clip per caption line, laid end to end with fixed gaps, plus per-word times.
Writes <work>/vo.wav and <work>/timing.json. Word times are a character-weighted split of each clip,
which stays within a few frames for short lines (the kit keeps every line short on purpose)."""
import json, math, os
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

def plain(line):  # "*prompt*." -> "prompt."
    return line.replace("*", "")

def speak(script, work):
    k = _model(); v_cfg = script.get("voice", {})
    voice, speed, lang = v_cfg.get("name", "am_michael"), v_cfg.get("speed", 1.18), v_cfg.get("lang", "en-us")
    say_map = v_cfg.get("say", {})          # pronunciation fixes: {"SQL": "sequel"}
    lines, clips, t = [], [], 0.0
    for si, sc in enumerate(script["scenes"]):
        for li, line in enumerate(sc["lines"]):
            gap = 0.2 if (si == 0 and li == 0) else (0.06 if li else 0.22)
            text = plain(line)
            said = text
            for a, b in say_map.items(): said = said.replace(a, b)
            a, sr = k.create(said, voice=voice, speed=speed, lang=lang)
            a = resample_poly(a, SR, sr); thr = 0.024 * np.abs(a).max()
            nz = np.where(np.abs(a) > thr)[0]; a = a[max(0, nz[0] - 240): nz[-1] + 1200]
            t += gap; d = len(a) / SR; clips.append((t, a))
            raw = line.split(); words = text.split(); acc, inside = [], False
            for r in raw:                       # *one prompt* marks every word in the span
                if r.startswith("*"): inside = True
                acc.append(inside)
                if r.rstrip(",.!?:;\"'").endswith("*"): inside = False
            wts = np.array([len(w.strip(",.!?:;")) + 2 for w in words], float)
            starts = t + np.concatenate([[0], np.cumsum(wts)[:-1]]) / wts.sum() * d * 0.94
            lines.append(dict(scene=si, line=li, text=text, start=round(t, 3), end=round(t + d, 3),
                              words=[dict(w=w, accent=a_, t=round(s, 3)) for w, a_, s in zip(words, acc, starts)]))
            t += d
    dur = script.get("duration") or math.ceil((t + 0.45) * 10) / 10
    if t > dur - 0.2: raise SystemExit(f"voice runs {t:.2f}s but duration is {dur}s: cut words or raise voice.speed")
    n = int(dur * SR); vo = np.zeros(n)
    for s, a in clips: i = int(s * SR); vo[i:i + len(a)] += a[:n - i]
    vo = vo / (np.abs(vo).max() + 1e-9) * 0.6
    sf.write(os.path.join(work, "vo.wav"), vo.astype(np.float32), SR)
    timing = dict(duration=dur, lines=lines)
    json.dump(timing, open(os.path.join(work, "timing.json"), "w"), indent=1)
    return timing
