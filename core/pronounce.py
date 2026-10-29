"""Pronunciation: text -> the phonemes Kokoro was trained on (misaki), with an audit of every word.

Kokoro-onnx on its own phonemizes with espeak, whose letter rules guess names, acronyms and tech words (VS Code ->
"vees code", macOS -> "mackoss", $20 -> "dollar twenty"). Here the text is first normalised (prices, multipliers,
k/M amounts, domains, symbols), then misaki's US gold/silver dictionaries give each word, `core/lexicon.json` and the
script's `voice.say` override them, and espeak is only the fallback for words in none of these. Every guessed word
(espeak fallback, acronym, number, symbol) is listed in the audit so it can be checked before a render goes out.

`voice.say` in a script: {"ThatPet": "that pet"} replaces whole words; {"Cindy": "/sˈɪndi/"} gives phonemes directly.
Check any text: python3 reel.py say "Claude Code on macOS for $20/month"."""
import json, os, re, warnings

HERE = os.path.dirname(os.path.abspath(__file__))
_g2p = None


def _engine():
    global _g2p
    if _g2p: return _g2p
    warnings.filterwarnings("ignore")
    import espeakng_loader
    from phonemizer.backend.espeak.wrapper import EspeakWrapper
    EspeakWrapper.set_library(espeakng_loader.get_library_path()); EspeakWrapper.set_data_path(espeakng_loader.get_data_path())
    import spacy, spacy.util
    is_pkg, load = spacy.util.is_package, spacy.load
    spacy.util.is_package = lambda name: True                    # no model download: misaki only needs the tokenizer
    def blank(name, **kw):   # tokenizer only, plus the punctuation tags misaki needs to keep , . ? ! as pauses
        nlp = spacy.blank("en")
        from spacy.language import Language
        if "punct_tags" not in Language.factories:
            @Language.component("punct_tags")
            def punct_tags(doc):
                for t in doc:
                    if t.is_punct or t.text in "$#":
                        t.tag_ = {"(": "-LRB-", ")": "-RRB-", '"': "``", "“": "``", "”": "''", "…": ":", "—": ":", "–": ":", ";": ":", "!": ".", "?": "."}.get(t.text, t.text)
                return doc
        nlp.add_pipe("punct_tags"); return nlp
    spacy.load = blank
    try:
        from misaki import en, espeak
        _g2p = en.G2P(trf=False, british=False, fallback=espeak.EspeakFallback(british=False))
    finally:
        spacy.util.is_package, spacy.load = is_pkg, load
    lex = {k: v for k, v in json.load(open(os.path.join(HERE, "lexicon.json"))).items() if not k.startswith("_")}
    _g2p.lexicon.golds.update(lex)
    _g2p.lexicon.golds.update({k.lower(): v for k, v in lex.items() if k.lower() not in lex})
    _g2p.custom = set(lex) | {k.lower() for k in lex}
    return _g2p


NUM = r"\d+(?:[.,]\d+)?"
RULES = [
    (re.compile(rf"\$({NUM})\s*([kKmMbB])\b"), lambda m: f"{m[1]} {dict(k='thousand', m='million', b='billion')[m[2].lower()]} dollars"),
    (re.compile(rf"\$({NUM})(?:\s*/\s*|\s+per\s+)(mo|month|yr|year|day|user|seat)\b"),
     lambda m: f"{m[1]} dollars a {dict(mo='month', yr='year').get(m[2], m[2])}"),
    (re.compile(rf"\$({NUM})"), lambda m: f"{m[1]} dollars"),
    (re.compile(rf"(?<![\w.])({NUM})\s*[xX×](?![\w])"), lambda m: f"{m[1]} times"),
    (re.compile(rf"(?<![\w.])({NUM})\s*([kKmMbB])\+?(?![\w])"), lambda m: f"{m[1]} {dict(k='thousand', m='million', b='billion')[m[2].lower()]}"),
    (re.compile(rf"({NUM})\s*%"), lambda m: f"{m[1]} percent"),
    (re.compile(r"\b([A-Za-z][\w-]*)\.(js|ts)\b"), lambda m: f"{m[1]} {'J S' if m[2] == 'js' else 'T S'}"),
    (re.compile(r"\b((?:[a-z0-9-]+\.)+(?:app|com|io|ai|dev|org|net|so|sh|co|gg|xyz|me|tv))((?:/[\w-]+)*)\b"),
     lambda m: " dot ".join(m[1].split(".")) + "".join(f" slash {p}" for p in m[2].split("/") if p)),
    (re.compile(r"\bvs\.?(?=\s)"), lambda m: "versus"),
    (re.compile(r"\be\.g\.", re.I), lambda m: "for example"),
    (re.compile(r"\bi\.e\.", re.I), lambda m: "that is"),
    (re.compile(r"\s*&\s*"), lambda m: " and "),
    (re.compile(r"\s*(?:->|→|=>)\s*"), lambda m: " to "),
    (re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿]"), lambda m: ""),
]


def normalise(text, say=None):
    for a, b in (say or {}).items():       # whole words only ("Pi" must not touch "Pixel")
        rep = f"[{a}]({b})" if b.startswith("/") else b
        text = re.sub(rf"(?<![\w]){re.escape(a)}(?![\w])", lambda m: rep, text)
    for rx, fn in RULES:
        text = rx.sub(fn, text)
    return re.sub(r"\s+", " ", text).strip()


def phonemes(text, say=None):
    """(phoneme string for Kokoro, audit rows) for one sentence or line."""
    g = _engine(); norm = normalise(text, say)
    ps, toks = g(norm)
    rows = []
    for t in toks:
        if not t.phonemes or not re.search(r"\w", t.text): continue
        w = t.text.strip(",.!?:;\"'()")
        why = ("custom" if w in g.custom else "say" if say and w in say else
               "guessed" if (t.rating or 0) <= 2 else
               "acronym" if re.fullmatch(r"[A-Z]{2,}s?", w) else
               "number" if re.search(r"\d", w) else
               "mixed case" if re.search(r"[a-z][A-Z]|[A-Z]{2}[a-z]", w) else None)
        if why: rows.append(dict(word=w, ph=t.phonemes, why=why))
    return ps, rows, norm


def audit(lines, say=None):
    """Report of every word the voice had to guess, per line; returns (text, guessed words)."""
    out, guessed = [], []
    for ln in lines:
        _, rows, norm = phonemes(ln, say)
        flag = [r for r in rows if r["why"] not in ("custom", "say")]
        if norm != re.sub(r"\s+", " ", ln).strip(): out.append(f"  read as: {norm}")
        for r in rows:
            out.append(f"  {'?' if r in flag else ' '} {r['word']:18s} /{r['ph']}/  {r['why']}")
        guessed += [r["word"] for r in flag if r["why"] == "guessed"]
    return "\n".join(out), sorted(set(guessed))
