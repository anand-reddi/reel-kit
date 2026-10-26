"""The @techinsixty kitty: an original small black cat sitting full body (flat warm-black silhouette, big amber-ringed eyes,
brown fur lines, curled tail). One front leg is a two-bone rig, so the paw lifts to point, wave and gesture; the head
tilts, the ears perk on accented words and twitch, the tail sways, the eyes blink and the mouth mews with the voice.
Run: python3 make.py -> character.svg + character.json"""
import json, os

BLACK, FUR, EAR_IN, AMBER, PUPIL = "#17120f", "#4a3a2e", "#3a2b22", "#e9a24a", "#0d0a08"
NOSE, MOUTH, BEAN, WHISK = "#3d2b25", "#a8545e", "#e8a0a6", "#2b221c"

SH = (566, 616)          # front-leg "shoulder" (chest)
U, F = 72, 80            # upper leg, lower leg

def head():
    shape = "M490,432 C488,378 522,346 600,345 C678,346 712,378 710,432 C710,484 670,516 600,516 C530,516 490,484 490,432 Z"
    ear = lambda o, t, i: (f'<path d="M{o[0]},{o[1]} L{t[0]},{t[1]} L{i[0]},{i[1]} Z" fill="{BLACK}" stroke="{BLACK}" stroke-width="10" stroke-linejoin="round"/>')
    ears = (f'<g id="ears"><g id="earL">{ear((496, 404), (502, 296), (566, 352))}'
            f'<path d="M508,392 L510,318 L552,354 Z" fill="{EAR_IN}"/><path d="M514,372 l14,4 M516,384 l12,0" stroke="{FUR}" stroke-width="2.5" stroke-linecap="round"/></g>'
            f'<g id="earR">{ear((704, 404), (698, 296), (634, 352))}'
            f'<path d="M692,392 L690,318 L648,354 Z" fill="{EAR_IN}"/><path d="M686,372 l-14,4 M684,384 l-12,0" stroke="{FUR}" stroke-width="2.5" stroke-linecap="round"/></g></g>')
    def eye(cx, px):
        return (f'<circle cx="{cx}" cy="428" r="27" fill="{AMBER}"/><circle cx="{px}" cy="428" r="20.5" fill="{PUPIL}"/>'
                f'<circle cx="{px + 6}" cy="420" r="4" fill="#f6e7d4"/>')
    eyes = (f'<g id="eyes-open">{eye(550, 553)}{eye(650, 647)}</g>'
            f'<g id="eyes-shut" opacity="0"><path d="M525,430 Q550,446 575,430 M625,430 Q650,446 675,430" stroke="{AMBER}" stroke-width="5" fill="none" stroke-linecap="round"/></g>')
    nose = f'<path d="M590,449 Q600,444 610,449 Q606,459 600,461 Q594,459 590,449 Z" fill="{NOSE}"/>'
    base = f'<path d="M600,461 L600,467" stroke="{FUR}" stroke-width="3" stroke-linecap="round"/>'
    m = {
        "closed": base + f'<path d="M588,470 Q594,474 600,467 Q606,474 612,470" stroke="{FUR}" stroke-width="3" fill="none" stroke-linecap="round"/>',
        "o": base + f'<ellipse cx="600" cy="476" rx="9" ry="8" fill="{MOUTH}"/><path d="M586,470 Q593,474 600,467 Q607,474 614,470" stroke="{FUR}" stroke-width="3" fill="none" stroke-linecap="round"/>',
        "smile": base + f'<path d="M584,468 Q592,478 600,467 Q608,478 616,468" stroke="{FUR}" stroke-width="3" fill="none" stroke-linecap="round"/>',
    }
    mouths = "".join(f'<g id="m-{k}" class="mth" opacity="{1 if k == "smile" else 0}">{v}</g>' for k, v in m.items())
    whisk = "".join(f'<path d="M{600 + s * 82},{y} L{600 + s * 150},{y + dy}" stroke="{WHISK}" stroke-width="2.4" stroke-linecap="round"/>'
                    for s in (-1, 1) for y, dy in ((452, -10), (460, 4), (468, 20)))
    return f'<g id="head">{ears}<path d="{shape}" fill="{BLACK}"/>{whisk}{eyes}{nose}{mouths}</g>'

def body():
    torso = ("M548,500 C524,530 514,566 512,606 C508,654 494,700 496,740 C498,764 514,774 542,774 L664,774 "
             "C694,774 716,762 716,734 C718,688 708,620 690,570 C680,536 666,510 652,500 Z")
    tail = "M532,744 C500,726 468,716 464,736 C460,758 492,774 530,778"
    return f'''
  <path d="{torso}" fill="{BLACK}"/>
  <ellipse cx="516" cy="768" rx="24" ry="10" fill="{BLACK}"/><ellipse cx="700" cy="768" rx="26" ry="10" fill="{BLACK}"/>
  <path d="M624,560 L622,760" stroke="{BLACK}" stroke-width="36" stroke-linecap="round"/>
  <ellipse cx="626" cy="766" rx="20" ry="11" fill="{BLACK}"/>
  <path d="M620,766 l0,-8 M632,766 l0,-8" stroke="{FUR}" stroke-width="2.5" stroke-linecap="round"/>
  <path d="M642,590 C646,650 646,710 644,758 M694,628 C674,664 666,700 670,744 M704,758 l0,-8 M692,760 l0,-8 M506,708 C508,730 510,748 512,760"
        stroke="{FUR}" stroke-width="2.6" fill="none" stroke-linecap="round"/>
  <path d="M588,524 l-6,14 M604,526 l4,12 M596,540 l0,12" stroke="{FUR}" stroke-width="2.2" stroke-linecap="round" opacity="0.7"/>
  <g id="tail"><path d="{tail}" stroke="{BLACK}" stroke-width="24" fill="none" stroke-linecap="round"/>
    <path d="M500,734 C486,732 478,738 478,746" stroke="{FUR}" stroke-width="2.4" fill="none" stroke-linecap="round" opacity="0.8"/></g>'''

def leg():
    """Viewer-left front leg as a two-bone 'arm': #armL rotates at the chest, .fore bends at the elbow."""
    sx, sy = SH
    tube = lambda x0, x1, w0, w1: f"M{x0},{-w0} L{x1},{-w1} L{x1},{w1} L{x0},{w0} Z"
    paw = (f'<ellipse cx="0" cy="-8" rx="19" ry="14" fill="{BLACK}"/>'
           f'<path d="M-6,-20 l0,8 M6,-20 l0,8" stroke="{FUR}" stroke-width="2.5" stroke-linecap="round"/>')
    beans = (f'<ellipse cx="0" cy="-10" rx="21" ry="17" fill="{BLACK}"/><ellipse cx="0" cy="-5" rx="9" ry="7" fill="{BEAN}"/>'
             + "".join(f'<circle cx="{x}" cy="{y}" r="4.2" fill="{BEAN}"/>' for x, y in ((-12, -16), (-4.5, -22), (4.5, -22), (12, -16))))
    hands = "".join(f'<g id="armL-{k}" opacity="0"><g transform="translate({F} 0) rotate(90)">{v}</g></g>' for k, v in (("paw", paw), ("beans", beans)))
    fore = 'transform="rotate(0 %d 0)"' % U
    return (f'<g id="armL" transform="rotate(90 {sx} {sy})"><g transform="translate({sx} {sy})">'
            f'<path d="{tube(-14, U, 19, 17)}" fill="{BLACK}"/><circle r="20" fill="{BLACK}"/>'
            f'<path d="M14,15 L{U},14" stroke="{FUR}" stroke-width="2.4" stroke-linecap="round" opacity="0.85"/>'
            f'<g class="fore" {fore}><g transform="translate({U} 0)">{hands}<circle r="17" fill="{BLACK}"/>'
            f'<path d="{tube(0, F - 6, 17, 15)}" fill="{BLACK}"/>'
            f'<path d="M4,13 L{F - 14},12" stroke="{FUR}" stroke-width="2.4" stroke-linecap="round" opacity="0.85"/></g></g>'
            f'</g></g>')

POSES = {
    "rest":  dict(u=90, f=0, hand="paw"),
    "up":    dict(u=200, f=80, hand="beans"),
    "card":  dict(u=215, f=40, hand="beans"),
    "palms": dict(u=170, f=60, hand="beans"),
    "shrug": dict(u=160, f=50, hand="beans"),
    "thumb": dict(u=195, f=88, hand="beans"),
    "wave":  dict(u=198, f=84, hand="beans", wave=True),
}

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1000" width="1200" height="1000">
<g id="pres-body">{body()}{head()}{leg()}</g></svg>'''

here = os.path.dirname(os.path.abspath(__file__))
open(os.path.join(here, "character.svg"), "w").write(svg)
json.dump({
    "type": "svg", "file": "character.svg", "x": -60, "y": 1130, "width": 1200,
    "head_origin": "600 506", "avatar_view": "478 282 244 244",
    "poses": list(POSES),
    "arms": [{"id": "armL", "shoulder": list(SH), "upper": U, "hands": ["paw", "beans"], "poses": POSES}],
    "brows": {"sel": "#ears", "raise": -7},
    "idle": [{"sel": "#tail", "rot": 6, "period": 2.0, "origin": "532 750"}],
    "twitch": [{"sel": "#earR", "rot": 12, "every": 2.8, "offset": 1.3, "origin": "668 360"}],
}, open(os.path.join(here, "character.json"), "w"), indent=1)
print("wrote character.svg + character.json")
