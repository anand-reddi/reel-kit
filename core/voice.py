"""Voice: Kokoro reads each sentence in one go (a sentence can span several caption lines), so the intonation runs
through the lines instead of dropping at the end of every fragment; then each line's place inside the sentence is
found (the lines' solo lengths give the split, snapped to the quietest moment nearby, which is the gap between two
words). Per-word times are a character-weighted split of each line. Writes <work>/vo.wav and <work>/timing.json.
"voice": {"natural": false} goes back to one clip per line. Text becomes phonemes through core/pronounce.py (misaki
dictionaries + core/lexicon.json, espeak only as fallback) and every guessed word is reported; "g2p": "espeak" goes back."""
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

INTRO = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "sounds", "intro-repulsor.wav")
def intro(script):
    """The opening sound on every video (the user's standing choice). "intro": false turns it off;
    {"sound": "path.wav", "gain": -9, "lead": 0.4} swaps it; lead = seconds the first words wait."""
    cfg = script.get("intro", {})
    if cfg is False: return None
    cfg = dict(cfg) if isinstance(cfg, dict) else {}
    snd = cfg.get("sound", INTRO)
    return dict(sound=snd, gain=cfg.get("gain", -9), lead=cfg.get("lead", 0.3)) if os.path.exists(snd) else None
def intro_lead(script):
    i = intro(script); return i["lead"] if i else 0.0

def silent(script, work):
    """A reel without a voice ("voice": false): scenes last "beats" each on the script's tempo; writes a silent vo.wav."""
    bpm = script.get("bpm", script.get("music", {}).get("bpm", 120)); spb = 60 / bpm; t = 0.0; sc = []
    for s in script["scenes"]:
        d = s.get("beats", 4) * spb; sc.append([round(t, 4), round(t + d, 4)]); t += d
    timing = {"duration": round(t, 3), "lines": [], "scenes": sc}
    sf.write(os.path.join(work, "vo.wav"), np.zeros(int(t * SR) + SR, dtype=np.float32), SR)
    json.dump(timing, open(os.path.join(work, "timing.json"), "w"), indent=1)
    return timing

def speak(script, work):
    if script.get("voice") is False: return silent(script, work)
    k = _model(); v_cfg = script.get("voice", {})
    voice, speed, lang = v_cfg.get("name", "am_puck"), v_cfg.get("speed", 1.0), v_cfg.get("lang", "en-us")
    say_map = v_cfg.get("say", {})          # pronunciation fixes, whole words: {"SQL": "sequel"} or {"Cindy": "/sˈɪndi/"}
    natural = v_cfg.get("natural", True)
    use_misaki = v_cfg.get("g2p", "misaki") == "misaki" and lang == "en-us"
    if use_misaki:
        from . import pronounce
        all_lines = [plain(l) for sc in script["scenes"] for l in sc["lines"]]
        report, guessed = pronounce.audit(all_lines, say_map)
        open(os.path.join(work, "pronounce.txt"), "w").write(report + "\n")
        print(f"    pronunciation: {len(all_lines)} lines checked, report in {os.path.join(work, 'pronounce.txt')}")
        if guessed:
            print(f"    WARN guessed pronunciations (check, then fix in voice.say or core/lexicon.json): {', '.join(guessed)}")
    def synth(text):
        if use_misaki:
            ps = pronounce.phonemes(text, say_map)[0]
            a, sr = k.create(ps, voice=voice, speed=speed, lang=lang, is_phonemes=True)
        else:
            for x, y in say_map.items(): text = re.sub(rf"(?<![\w]){re.escape(x)}(?![\w])", y, text)
            a, sr = k.create(text, voice=voice, speed=speed, lang=lang)
        return _trim(resample_poly(a, SR, sr))
    lines, clips, t = [], [], intro_lead(script)
    # Sentences, not lines, are what gets voiced: a sentence ends on . ? ! or : ("…" is a breath, not an end).
    # A scene whose last line is left open ("," "…" or no punctuation before a scene that starts lower-case) runs on
    # into the next scene, so a sentence split across two visuals is still read in one breath.
    allv = [(si, li, line) for si, sc in enumerate(script["scenes"]) for li, line in enumerate(sc["lines"])]
    groups, cur = [], []
    for q, (si, li, line) in enumerate(allv):
        cur.append(q); txt = plain(line).rstrip(); last_in_scene = li == len(script["scenes"][si]["lines"]) - 1
        nxt = allv[q + 1] if q + 1 < len(allv) else None
        runs_on = (natural and last_in_scene and nxt is not None and (txt.endswith((",", "…", "—")) or
                   (not txt.endswith((".", "?", "!", ":")) and plain(nxt[2])[:1].islower())))
        if not natural or txt.endswith((".", "?", "!", ":")) or (last_in_scene and not runs_on) or nxt is None: groups.append(cur); cur = []
    for gi, grp in enumerate(groups):
        si0 = allv[grp[0]][0]; first_of_scene = allv[grp[0]][1] == 0
        gap = 0.2 if gi == 0 else (0.24 if first_of_scene else (0.12 if natural else 0.06))
        if first_of_scene: gap += script["scenes"][si0].get("pause_before", 0)   # a beat of silence before the scene
        texts = [plain(allv[q][2]) for q in grp]
        a = synth(" ".join(texts)); t += gap; n = len(a)
        cuts = [0]
        if len(grp) > 1:
            solo = np.array([len(synth(x)) for x in texts], float)
            for b in (np.cumsum(solo)[:-1] / solo.sum() * n).astype(int): cuts.append(_snap(a, b, int(0.14 * SR)))
        cuts.append(n)
        for j, q in enumerate(grp):
            si, li, raw = allv[q]; s0, s1 = t + cuts[j] / SR, t + cuts[j + 1] / SR
            lines.append(dict(scene=si, line=li, text=texts[j], start=round(s0, 3), end=round(s1, 3),
                              words=_words(texts[j], raw, s0, s1 - s0)))
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
