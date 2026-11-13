"""Code-made music beds for explainers (no recorded audio inside).

curious(): a quiet "something is being revealed" bed, modelled on the measured shape of the user's reference reel
(about 120 BPM, D major / Lydian colour, sparse ticks and plucks, a sub-bass lift in the middle third, voice on top):
a plucked arpeggio with a dotted-eighth echo, a soft pad, clock-like ticks, a sub pulse and a soft kick that come in
for the middle section, and a bell on every fourth bar. Everything is synthesised here, mono, 48 kHz.
"""
import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000


def _hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def _lp(x, f, order=2):
    return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x)


def _fade(x, sec=0.012):
    k = min(len(x), int(sec * SR)); x = x.copy(); x[-k:] *= np.linspace(1, 0, k); return x


def _hp(x, f, order=2):
    return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x)


# D Lydian loop, one chord per bar: D maj7#11, B m9, F# m7, E/D (the Lydian lift)
CHORDS = [
    (38, [62, 66, 69, 73, 68]),   # D2 bass; D4 F#4 A4 C#5 G#4
    (35, [59, 62, 66, 69, 61]),   # B1; B3 D4 F#4 A4 C#4
    (42, [61, 64, 66, 69, 73]),   # F#2; C#4 E4 F#4 A4 C#5
    (38, [64, 68, 71, 76, 66]),   # D2; E4 G#4 B4 E5 F#4
]
ARP = [0, 2, 1, 3, 2, 4, 1, 3]    # which chord tone on each eighth note


def curious(n, cfg=None):
    cfg = cfg or {}
    bpm = cfg.get("bpm", 120); spb = 60.0 / bpm; bar = 4 * spb
    shift = cfg.get("transpose", 0)
    dur = n / SR
    rng = np.random.default_rng(cfg.get("seed", 7))
    # arrangement: light intro, fuller middle (sub + kick), light again, gentle end
    a, b = cfg.get("build", (0.18, 0.72))
    lift = lambda t: 1.0 if a * dur <= t < b * dur else 0.0
    out = np.zeros(n + SR * 4)

    def add(sig, at, g):
        i = int(at * SR)
        if i >= len(out): return
        m = min(len(sig), len(out) - i)
        out[i:i + m] += sig[:m] * g

    # voices
    def pluck(f, length=0.42):
        x = np.arange(int(length * SR)) / SR
        tone = np.sin(2 * np.pi * f * x) + 0.35 * np.sin(2 * np.pi * 2 * f * x) * np.exp(-x * 18) + 0.12 * np.sin(2 * np.pi * 3 * f * x) * np.exp(-x * 30)
        env = (1 - np.exp(-x * 900)) * np.exp(-x * 7.5)
        return _fade(_lp(tone * env, 5200))

    def pad(notes, length):
        x = np.arange(int(length * SR)) / SR; s = np.zeros_like(x)
        for m in notes:
            for d in (-0.07, 0.0, 0.07):
                f = _hz(m + d); ph = rng.uniform(0, 2 * np.pi)
                s += 2 * ((f * x + ph / (2 * np.pi)) % 1.0) - 1      # saw
        env = np.minimum(1, x / 0.7) * np.minimum(1, (length - x) / 0.5)
        return _lp(s * env, 900, 4) / (3 * len(notes))

    def tick(accent):
        x = np.arange(int(0.012 * SR)) / SR
        nz = _hp(rng.standard_normal(len(x)), 7500) * np.exp(-x * 520)
        return _fade(nz * (1.0 if accent else 0.45), 0.003)

    def sub(f, length):
        x = np.arange(int(length * SR)) / SR
        env = np.minimum(1, x / 0.02) * np.exp(-x * 2.2)
        return _fade(np.sin(2 * np.pi * f * x) * env, 0.04)

    def kick():
        x = np.arange(int(0.3 * SR)) / SR
        return _fade(np.sin(2 * np.pi * (42 + 70 * np.exp(-x * 35)) * x) * np.exp(-x * 11))

    def bell(f):
        x = np.arange(int(2.2 * SR)) / SR
        s = sum(g * np.sin(2 * np.pi * f * r * x) * np.exp(-x * d) for r, g, d in ((1, 1, 2.2), (2.76, .45, 3.5), (5.4, .2, 6), (8.93, .08, 9)))
        return _fade(s * np.minimum(1, x / 0.004), 0.2)

    arp_bus = np.zeros_like(out)
    k = 0; t = 0.0
    while t < dur:
        bass, tones = CHORDS[k % len(CHORDS)]
        bass += shift; tones = [m + shift for m in tones]
        add(pad(tones[:4], bar + 0.4), t, 0.14)
        for j, idx in enumerate(ARP):                       # eighth-note arpeggio
            at = t + j * spb / 2; f = _hz(tones[idx])
            i = int(at * SR); s = pluck(f); m = min(len(s), len(arp_bus) - i)
            if m > 0: arp_bus[i:i + m] += s[:m] * (0.85 if j % 2 == 0 else 0.6)
        for j in range(16):                                 # sixteenth ticks, accents on the beat
            at = t + j * spb / 4
            if j % 4 == 0 or rng.random() < 0.55: add(tick(j % 4 == 0), at, 0.22)
        if k % 4 == 0: add(bell(_hz(tones[0] + 12)), t, 0.14)
        if lift(t):                                         # the middle lift: sub pulse and a soft kick
            for j in range(4):
                add(sub(_hz(bass - 12 if bass - 12 > 26 else bass), spb * 0.95), t + j * spb, 0.32)
            add(kick(), t, 0.5); add(kick(), t + 2 * spb, 0.38)
        t += bar; k += 1

    # dotted-eighth echo on the arpeggio, darker on each repeat
    d = int(0.75 * spb * SR); echo = arp_bus.copy(); tap = arp_bus.copy()
    for g in (0.38, 0.2, 0.1):
        tap = _lp(np.concatenate([np.zeros(d), tap[:-d]]), 2400)
        echo += tap * g
    out += echo * 0.5

    out = _hp(out, 32)
    # a short computed room: decaying filtered noise convolved via FFT
    ir_len = int(0.9 * SR); x = np.arange(ir_len) / SR
    ir = _lp(rng.standard_normal(ir_len), 5000) * np.exp(-x * 6.5); ir[0] = 0; ir /= np.abs(ir).sum() / 6
    L = 1 << int(np.ceil(np.log2(len(out) + ir_len)))
    wet = np.fft.irfft(np.fft.rfft(out, L) * np.fft.rfft(ir, L), L)[:len(out)]
    out = out + 0.22 * wet
    out = out[:n]
    tt = np.arange(n) / SR
    fade = np.interp(tt, [0, 0.6, dur - 1.2, dur], [0, 1, 1, 0])
    return out * fade / (np.abs(out).max() + 1e-9)
