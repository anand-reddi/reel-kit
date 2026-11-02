"""sketchbook_dark: the sketchbook style (Looseleaf hand-drawn paper UI) in the krishexplainz look: near-black dotted page,
dark paper, one red accent, and a black cat sticker that reacts with expressions (it never talks). Docs: ../sketchbook/STYLE.md."""
from styles.sketchbook import compose
from styles.sketchbook.compose import CARDS
SIZE = (1080, 1920); LAYOUT_QA = False
def build(script, timing, work, sdir): return compose.build(script, timing, work, sdir, look="dark")
def render(script, timing, work, sdir, quality="looks"): return compose.render(script, timing, work, sdir, quality)
