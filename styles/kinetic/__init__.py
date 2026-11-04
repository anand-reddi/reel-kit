"""kinetic: kinetic-type motion design in 9:16 -- huge words on every beat, ground colour flips, whip pans, 3D type the
camera flies through, slot counters, comets, a film strip of blocks on the music's beat grid. Docs: STYLE.md."""
from . import compose
from .compose import CARDS, BLOCKS
SIZE = (1080, 1920); LAYOUT_QA = False; BOARD = True
def build(script, timing, work, sdir): return compose.build(script, timing, work, sdir)
def render(script, timing, work, sdir, quality="looks"): return compose.render(script, timing, work, sdir, quality)
