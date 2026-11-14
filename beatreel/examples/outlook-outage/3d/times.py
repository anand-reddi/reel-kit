"""Writes times.js: the named moments of the 3D film (absolute reel seconds) from the voice timing, and the shot ranges."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
tm = json.load(open(os.path.join(HERE, "..", "build", "outlook-outage", "timing.json")))
norm = lambda w: re.sub(r"[^a-z0-9'-]", "", w.lower())
def W(scene, word, nth=0, off=0.0):
    hits = [w["t"] for l in tm["lines"] if l["scene"] == scene for w in l["words"] if norm(w["w"]) == word]
    return round(hits[nth] - 0.06 + off, 3)
T = dict(
    rise=W(3, "huge"), scan=W(4, "each") + 0.1, one=W(4, "one"), sick=W(4, "sick"), pull=W(4, "pulled"),
    wave=W(5, "suddenly") + 0.06, dump=W(6, "their"), over=W(7, "overloaded"), fail2=W(7, "failed"),
    back=W(8, "came"), slam=W(8, "slammed"), down=W(8, "went"), rec=W(9, "brought"),
)
T["dark"] = round(W(8, "even"), 3)
R = {   # shot ranges [from, to]: each becomes one clip (its own camera)
    "rise": [W(3, "huge"), W(4, "each")], "scan": [W(4, "each"), W(4, "if")], "sick": [W(4, "if"), round(tm["lines"][5]["start"] - 0.12, 3)],
    "fail": [W(5, "suddenly"), W(5, "failed")], "dump": [round(tm["lines"][6]["start"] - 0.12, 3), W(6, "onto")],
    "over": [round(tm["lines"][7]["start"] - 0.12, 3), W(7, "spread")], "restart": [W(8, "servers"), W(8, "and")],
    "down": [W(8, "and"), round(tm["lines"][9]["start"] - 0.12, 3)], "rec": [W(9, "brought"), W(9, "checking")],
}
open(os.path.join(HERE, "times.js"), "w").write("window.T3 = " + json.dumps(T) + ";\nwindow.R3 = " + json.dumps(R) + ";\n")
print(json.dumps(T)); print(json.dumps(R))
