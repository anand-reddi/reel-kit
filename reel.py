#!/usr/bin/env python3
"""reel-kit: script.json -> 9:16 explainer reel (voice, word-synced captions, UI cards, presenter, beat, SFX).

  python3 reel.py make styles/paper/examples/one-prompt.json -o out.mp4   # full pipeline
  python3 reel.py make script.json --stills                      # also writes a contact sheet of key frames
  python3 reel.py styles | cards [style]                         # list styles / a style's cards
"""
import argparse, glob, json, os, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
from core import voice, sound

def style(name):
    try: return importlib.import_module(f"styles.{name}")
    except ModuleNotFoundError: sys.exit(f"unknown style '{name}'; have: {', '.join(styles())}")

def styles():
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "styles")
    return sorted(n for n in os.listdir(d) if os.path.isfile(os.path.join(d, n, "__init__.py")))

def browser():
    if os.environ.get("HYPERFRAMES_BROWSER_PATH"): return os.environ["HYPERFRAMES_BROWSER_PATH"]
    roots = [os.environ.get("PLAYWRIGHT_BROWSERS_PATH", ""), "/opt/pw-browsers", os.path.expanduser("~/.cache/ms-playwright")]
    for r in roots:
        hits = sorted(glob.glob(os.path.join(r, "chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell")))
        if hits: return hits[-1]
    return None

def run(cmd, cwd=None, env=None):
    r = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    if r.returncode: sys.exit(f"failed: {' '.join(cmd)}\n{(r.stdout + r.stderr)[-1500:]}")
    return r.stdout + r.stderr

def make(a):
    script = json.load(open(a.script)); sdir = os.path.dirname(os.path.abspath(a.script))
    name = os.path.splitext(os.path.basename(a.script))[0]
    work = os.path.abspath(a.work or os.path.join(sdir, "build", name)); os.makedirs(work, exist_ok=True)
    out = os.path.abspath(a.o or os.path.join(sdir, f"{name}.mp4")); os.makedirs(os.path.dirname(out), exist_ok=True)
    print("1/4 voice"); tm = voice.speak(script, work)
    print(f"    {len(tm['lines'])} lines, {tm['duration']} s")
    st = style(script.get("style", "paper"))
    print(f"2/4 picture ({script.get('style', 'paper')})"); cues = st.build(script, tm, work, sdir)
    env = dict(os.environ); b = browser()
    if b: env["HYPERFRAMES_BROWSER_PATH"] = b
    fdir = os.path.join(work, "film")
    lint = run(["npx", "-y", "hyperframes", "lint"], fdir, env)
    if " 0 error" not in lint: print(lint[-800:])
    print("3/4 render"); run(["npx", "-y", "hyperframes", "render", ".", "-o", os.path.join(work, "video.mp4"), "-q", a.quality], fdir, env)
    print("4/4 sound"); lufs, n = sound.mix(work, cues, tm["duration"], script)
    print(f"    {n} sound effects, {lufs:.1f} LUFS")
    run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(work, "video.mp4"), "-i", os.path.join(work, "mix.wav"), "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", out])
    if a.stills:
        sheet = os.path.splitext(out)[0] + "-frames.png"; ts = [ln["end"] - 0.15 for ln in tm["lines"]]
        ins = []
        for i, t in enumerate(ts):
            f = os.path.join(work, f"still{i}.png"); run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", out, "-frames:v", "1", "-vf", "scale=300:-1", f]); ins += ["-i", f]
        run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", f"hstack={len(ts)}" if len(ts) > 1 else "null", sheet])
        print("    frames:", sheet)
    print("done:", out)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    m = sp.add_parser("make"); m.add_argument("script"); m.add_argument("-o"); m.add_argument("--work"); m.add_argument("--stills", action="store_true")
    m.add_argument("--quality", default="looks", choices=["draft", "looks", "delivery"])
    c = sp.add_parser("cards"); c.add_argument("style", nargs="?", default="paper")
    sp.add_parser("styles")
    a = ap.parse_args()
    if a.cmd == "make": make(a)
    elif a.cmd == "styles": print("styles:", ", ".join(styles()))
    else: print(f"{a.style} cards:", ", ".join(style(a.style).CARDS))
