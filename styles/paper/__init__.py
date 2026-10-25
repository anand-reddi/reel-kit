"""paper: off-white dotted paper, black/white UI cards with one red accent, word-synced captions, presenter at the bottom.
Reference: a 66 s 'AI reels system' explainer reel (Oct 2026). Docs: STYLE.md."""
from .compose import Film
from .cards import CARDS
SIZE = (1080, 1920)

def build(script, timing, work, script_dir):
    """Writes <work>/film/index.html and returns the sound cues [(t, earshot_id, gain_db)]."""
    return Film(script, timing, work, script_dir).build()
