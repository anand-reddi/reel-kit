#!/usr/bin/env bash
# reel-kit setup. Idempotent. usage: bash setup.sh [dest]   (default ~/reel-kit)
# Installs: the kit (your fork first), Python deps, the Kokoro voice model (GitHub release, ~350 MB, cached),
# earshot (sound effects), and checks for ffmpeg, node/npx and a headless Chrome for HyperFrames.
set -euo pipefail
DEST="${1:-$HOME/reel-kit}"
REPO="https://github.com/anand-reddi/reel-kit.git"; BRANCH="techinsixty"
if [ ! -f "$DEST/reel.py" ]; then
  git clone -q --depth 1 -b "$BRANCH" "$REPO" "$DEST" 2>/dev/null || git clone -q --depth 1 "$REPO" "$DEST"
fi
python3 -m pip install -q --break-system-packages kokoro-onnx soundfile pyloudnorm scipy numpy 2>/dev/null \
  || python3 -m pip install -q kokoro-onnx soundfile pyloudnorm scipy numpy
TTS="${REELKIT_TTS:-$HOME/.cache/reelkit/tts}"; mkdir -p "$TTS"
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  if [ -f "/root/tts/$f" ] && [ ! -f "$TTS/$f" ]; then ln -s "/root/tts/$f" "$TTS/$f"; fi
  [ -f "$TTS/$f" ] || curl -sSL -o "$TTS/$f" "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f"
done
if ! command -v earshot >/dev/null && [ ! -x "$HOME/earshot/.venv/bin/earshot" ]; then
  E="$HOME/earshot"; COMMIT=591fa3e028032e6dce56620a20e932e35667e8d8
  rm -rf "$E"; mkdir -p "$E"; ( cd "$E" && git init -q && { git fetch -q --depth 1 https://github.com/anand-reddi/earshot.git "$COMMIT" || git fetch -q --depth 1 https://github.com/Leonxlnx/earshot.git "$COMMIT"; } \
    && git -c advice.detachedHead=false checkout -q FETCH_HEAD && python3 -m venv .venv \
    && .venv/bin/pip install -q numpy scipy soundfile soxr librosa pyloudnorm scikit-learn pillow matplotlib "mcp>=2" requests && .venv/bin/pip install -q --no-deps -e . ) \
    || echo "WARN: earshot install failed; reels will render without sound effects" >&2
fi
command -v ffmpeg >/dev/null || echo "WARN: ffmpeg missing (apt-get install -y ffmpeg)" >&2
command -v npx >/dev/null || echo "WARN: node/npx missing (HyperFrames renders through npx)" >&2
ls /opt/pw-browsers/chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell "$HOME"/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell >/dev/null 2>&1 \
  || [ -n "${HYPERFRAMES_BROWSER_PATH:-}" ] || echo "NOTE: no local headless Chrome found; HyperFrames will try to download one (or set HYPERFRAMES_BROWSER_PATH)" >&2
echo "$DEST"
