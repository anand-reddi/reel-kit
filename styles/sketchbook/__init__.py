"""sketchbook: Looseleaf's hand-drawn paper UI (original look: sage desk, light paper, Stubby the pencil). Docs: STYLE.md.
The dark krishexplainz version is the separate style `sketchbook_dark`."""
from . import compose
from .compose import CARDS
SIZE = (1080, 1920); LAYOUT_QA = False
def build(script, timing, work, sdir): return compose.build(script, timing, work, sdir, look="original")
def render(script, timing, work, sdir, quality="looks"): return compose.render(script, timing, work, sdir, quality)
