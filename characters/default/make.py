"""Draws the kit's default presenter (an original placeholder character) into character.svg.
Run: python3 make.py. A custom character only has to keep the ids listed in CHARACTER.md."""
PAPER, INK, RED, GREY, MID, CARD, SKIN, SKIN2, BLUE, LINE = "#efece6", "#141414", "#e5372d", "#c9c4ba", "#8a857c", "#1b1b1d", "#e9b994", "#cf9a76", "#2f7bf6", "#2a2a2e"
# ------------------------------------------------------------ presenter (original character)
def hand(x, y, kind, rot=0):
    """kind: point (index up), palm (open), fist."""
    f = ""
    if kind == "point":
        f = f'<rect x="-9" y="-78" width="18" height="60" rx="9" fill="{SKIN}"/><path d="M-30,-10 q-6,-24 8,-30" stroke="{SKIN2}" stroke-width="4" fill="none"/>'
    elif kind == "palm":
        f = "".join(f'<rect x="{-28 + i * 15}" y="{-74 + abs(i - 1.5) * 10}" width="14" height="52" rx="7" fill="{SKIN}"/>' for i in range(4)) + f'<rect x="26" y="-30" width="14" height="40" rx="7" fill="{SKIN}" transform="rotate(35 33 -10)"/>'
    elif kind == "thumb":
        f = f'<rect x="-8" y="-76" width="18" height="52" rx="9" fill="{SKIN}"/>'
    return f'<g transform="translate({x} {y}) rotate({rot})">{f}<ellipse rx="40" ry="36" fill="{SKIN}"/><path d="M-30,6 q30,22 60,0" stroke="{SKIN2}" stroke-width="4" fill="none"/></g>'

def arm(sh, el, hd, kind, rot=0):
    pts = f"M{sh[0]},{sh[1]} Q{el[0]},{el[1]} {hd[0]},{hd[1] + 30}"
    return (f'<path d="{pts}" stroke="{INK}" stroke-width="86" stroke-linecap="round" fill="none"/>'
            f'<path d="{pts}" stroke="url(#cdots)" stroke-width="86" stroke-linecap="round" fill="none" opacity="0.5"/>'
            f'<circle cx="{hd[0]}" cy="{hd[1] + 34}" r="44" fill="{LINE}"/>' + hand(hd[0], hd[1], kind, rot))

SL, SR_ = (400, 560), (800, 560)
POSES = {   # name -> (left arm, right arm) ; None = arm hangs out of frame
    "up":    (arm(SL, (250, 560), (300, 330), "point", -8), None),
    "palms": (arm(SL, (230, 700), (210, 520), "palm", -25), arm(SR_, (970, 700), (990, 520), "palm", 25)),
    "card":  (None, arm(SR_, (1000, 560), (930, 330), "point", 12)),
    "shrug": (arm(SL, (260, 720), (230, 520), "palm", -40), arm(SR_, (940, 720), (970, 520), "palm", 40)),
    "wave":  (None, arm(SR_, (1010, 600), (950, 360), "palm", 14)),
    "thumb": (arm(SL, (300, 760), (420, 640), "thumb", -10), None),
}
def mouth(kind):
    if kind == "o": return f'<ellipse cx="0" cy="96" rx="22" ry="17" fill="{INK}"/><ellipse cx="0" cy="104" rx="12" ry="6" fill="{RED}"/>'
    if kind == "smile": return f'<path d="M-36,86 Q0,124 36,86 Q0,104 -36,86 Z" fill="{INK}"/>'
    return f'<path d="M-30,92 Q0,108 30,92" stroke="{INK}" stroke-width="7" fill="none" stroke-linecap="round"/>'
def eyes(blink=False):
    if blink: return "".join(f'<path d="M{x - 22},12 q22,10 44,0" stroke="{INK}" stroke-width="7" fill="none" stroke-linecap="round"/>' for x in (-62, 62))
    return "".join(f'<ellipse cx="{x}" cy="10" rx="13" ry="16" fill="{INK}"/><circle cx="{x + 5}" cy="4" r="4.5" fill="#fff"/>' for x in (-62, 62))
HEAD = f'''
  <rect x="-62" y="120" width="124" height="120" fill="{SKIN2}"/>
  <ellipse cx="-168" cy="20" rx="30" ry="40" fill="{SKIN}"/><ellipse cx="168" cy="20" rx="30" ry="40" fill="{SKIN}"/>
  <path d="M-160,-30 C-170,-180 -80,-230 0,-230 C90,-230 170,-180 160,-30 C160,90 100,170 0,172 C-100,170 -160,90 -160,-30 Z" fill="{SKIN}"/>
  <path d="M60,150 C120,120 158,60 160,-30 L160,40 C150,110 110,160 40,170 Z" fill="url(#cdots)" opacity="0.55"/>
  <path d="M-172,-40 C-190,-170 -110,-262 10,-258 C130,-256 196,-170 172,-40 C160,-90 150,-120 120,-140 C60,-110 -20,-150 -60,-190 C-80,-140 -130,-120 -160,-60 Z" fill="{INK}"/>
  <path d="M-60,-190 C-20,-150 60,-110 120,-140" stroke="{LINE}" stroke-width="6" fill="none"/>
  <g stroke="{INK}" stroke-width="9" fill="none"><rect x="-120" y="-24" width="104" height="72" rx="18"/><rect x="16" y="-24" width="104" height="72" rx="18"/><path d="M-16,4 L16,4 M-120,0 L-160,-10 M120,0 L160,-10"/></g>
  <path d="M-96,-50 l50,-8 M46,-58 l50,8" stroke="{INK}" stroke-width="10" stroke-linecap="round"/>
  <path d="M-4,40 q-14,30 4,34" stroke="{SKIN2}" stroke-width="6" fill="none" stroke-linecap="round"/>'''
def presenter():
    body = f'''
  <path d="M250,1000 C250,760 300,590 420,540 C480,515 720,515 780,540 C900,590 950,760 950,1000 Z" fill="{INK}"/>
  <path d="M760,560 C880,610 930,760 940,1000 L820,1000 C820,820 800,660 760,560 Z" fill="url(#cdots)" opacity="0.5"/>
  <path d="M500,535 Q600,640 700,535" stroke="{LINE}" stroke-width="14" fill="none"/>
  <path d="M540,580 L530,700 M660,580 L670,700" stroke="#f2efe9" stroke-width="7" stroke-linecap="round"/>
  <circle cx="530" cy="706" r="9" fill="{RED}"/><circle cx="670" cy="706" r="9" fill="{RED}"/>
  <g><path d="M440,560 C440,470 760,470 760,560" stroke="{LINE}" stroke-width="22" fill="none"/>
     <rect x="410" y="520" width="64" height="92" rx="26" fill="{RED}"/><rect x="726" y="520" width="64" height="92" rx="26" fill="{RED}"/></g>'''
    poses = ""
    for name, (l, r) in POSES.items():
        poses += f'<g id="pose-{name}" class="pose" opacity="0">{l or ""}{r or ""}</g>'
    faces = "".join(f'<g id="m-{k}" class="mth" opacity="{1 if k == "smile" else 0}">{mouth(k)}</g>' for k in ("closed", "o", "smile"))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1000" width="1200" height="1000"><defs><pattern id="cdots" width="10" height="10" patternUnits="userSpaceOnUse"><circle cx="5" cy="5" r="2.2" fill="#000"/></pattern></defs>
  <g id="pres-body">{body}{poses}
    <g id="head" transform="translate(600 320)">{HEAD}<g id="eyes-open">{eyes()}</g><g id="eyes-shut" class="hid" opacity="0">{eyes(True)}</g>{faces}</g>
  </g></svg>'''


open(__file__.replace("make.py", "character.svg"), "w").write(presenter())
print("wrote character.svg")
