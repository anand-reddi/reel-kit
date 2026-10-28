"""Icon library for every card: Iconify JSON sets, about 17,000 icons, all free licences.

Names are "set:name", e.g. "logos:openai-icon", "simple-icons:github", "lucide:key", "devicon:python".
  lucide, tabler        UI icons (stroke, take the text colour)               ISC / MIT
  simple-icons          brand marks of 3,700+ companies and tools, one colour  CC0 (brands keep their trademarks)
  logos                 full-colour company and dev-tool logos (2,300)          CC0
  devicon               full-colour programming languages and dev tools (1,000) MIT
  fluent-emoji-flat     full-colour objects in a flat emoji style (key, rocket) MIT
setup.sh installs them into ~/.cache/reelkit/icons (or $REELKIT_ICONS); a missing set is installed with npm on first use.
Find names with `python3 reel.py icons <word>`. Never draw icons with emoji or text glyphs."""
import json, os, re, subprocess

SETS = ["logos", "simple-icons", "devicon", "lucide", "tabler", "fluent-emoji-flat"]
DIR = os.environ.get("REELKIT_ICONS", os.path.expanduser("~/.cache/reelkit/icons"))
_sets, _uid = {}, [0]


def _load(name):
    if name in _sets: return _sets[name]
    path = os.path.join(DIR, "node_modules", "@iconify-json", name, "icons.json")
    if not os.path.exists(path):
        os.makedirs(DIR, exist_ok=True)
        subprocess.run(["npm", "i", "-s", "--no-audit", "--no-fund", "--prefix", DIR, f"@iconify-json/{name}"], check=True)
    _sets[name] = json.load(open(path))
    return _sets[name]


def _find(spec):
    if ":" not in spec: raise KeyError(spec)
    s, n = spec.split(":", 1)
    if s not in SETS: raise KeyError(f"unknown icon set '{s}' (sets: {', '.join(SETS)})")
    d = _load(s); ic = d["icons"].get(n); al = d.get("aliases", {})
    while ic is None and n in al: n = al[n]["parent"]; ic = d["icons"].get(n)
    if ic is None:
        near = search(n.split("-")[0], 8, [s])
        raise KeyError(f"no icon '{spec}'" + (f"; close: {', '.join(near)}" if near else ""))
    return d, ic


def exists(spec):
    try: _find(spec); return True
    except (KeyError, OSError, subprocess.CalledProcessError): return False


def svg(spec, size=96, color=None, cls=""):
    """Inline <svg> for "set:name". Monochrome sets use currentColor (pass `color` or set CSS color)."""
    d, ic = _find(spec)
    w, h = ic.get("width", d.get("width", 16)), ic.get("height", d.get("height", 16))
    x0, y0 = ic.get("left", d.get("left", 0)), ic.get("top", d.get("top", 0))
    body = ic["body"]
    ids = set(re.findall(r'id="([^"]+)"', body))
    if ids:   # the same logo twice on a page must not share gradient ids
        _uid[0] += 1; u = _uid[0]
        for i in sorted(ids, key=len, reverse=True):
            body = body.replace(f'id="{i}"', f'id="{i}-u{u}"').replace(f"#{i})", f"#{i}-u{u})").replace(f'"#{i}"', f'"#{i}-u{u}"')
    st = f' style="color:{color}"' if color else ""
    c = f' class="{cls}"' if cls else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {w} {h}" width="{size}" height="{round(size * h / w)}"'
            f'{c}{st}>{body}</svg>')


def search(q, limit=40, sets=None):
    q = q.lower().strip(); hits = []
    for s in sets or SETS:
        try: d = _load(s)
        except Exception: continue
        names = list(d["icons"]) + list(d.get("aliases", {}))
        exact = [n for n in names if n == q]
        pre = [n for n in names if n.startswith(q) and n != q]
        sub = [n for n in names if q in n and not n.startswith(q)]
        hits += [(rank, f"{s}:{n}") for rank, group in ((0, exact), (1, pre), (2, sub)) for n in group]
    hits.sort(key=lambda r: r[0])
    return [n for _, n in hits[:limit]]
