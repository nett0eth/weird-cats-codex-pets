#!/usr/bin/env python3
"""WEIRD CATS TIER LIST: 15s vertical TikTok/Reels.

0-1.6   hook "RANKING THE WEIRD CATS / from normal to certified weird"
1.6     Lucky -> NORMAL?   3.6 Beanie -> WEIRD   5.6 Smoke -> VERY WEIRD
7.6     Glitch breaks the list; 9.6 everyone is dragged into CERTIFIED WEIRD
10.3    the other tiers fall off, CERTIFIED WEIRD rises to the top, 19 collection cats fill the screen
13-15   "they're all certified weird." / comment your ranking
Re-run to rebuild; every layer stays editable in Tesseract.
"""
import json, os, subprocess, glob, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(ROOT, "..", ".."))
LAUNCH = os.path.join(REPO, "social", "launch-video")
GPT = os.path.join(LAUNCH, "gpt")
LW = os.path.join(LAUNCH, ".tesseract-work")
T = os.path.expanduser("~/.local/share/Tesseract/bin/tsrct")
PROJ = os.path.join(ROOT, "TierList.tsrct")
W, H, DUR = 1080, 1920, 15.0
MS = lambda s: int(round(s * 1000))


def run(*a):
    r = subprocess.run([T, *a], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"{' '.join(a)}\n{r.stdout}\n{r.stderr}")
    return r.stdout


LIB = ("var t=input.time.seconds;"
       "function cl(x){return Math.max(0,Math.min(1,x));}"
       "function eo(x){x=cl(x);return 1-Math.pow(1-x,3);}"
       "function ei(x){x=cl(x);return x*x*x;}"
       "function ob(x){x=cl(x);var c1=2.2,c3=c1+1;return 1+c3*Math.pow(x-1,3)+c1*Math.pow(x-1,2);}"
       "function lerp(a,b,p){return a+(b-a)*p;}"
       "function h(n){var x=Math.sin(n*12.9898+78.233)*43758.5453;return x-Math.floor(x);}"
       "function rowY(t){return t<10.3?1310:lerp(1310,420,eo((t-10.3)/0.5));}")
entries = []
_id = [1]


def nid():
    _id[0] += 1
    return _id[0]


def anim(lid, prop, body):
    entries.append({"target": {"kind": "layer", "layerId": lid, "propertyType": prop},
                    "animator": {"type": "jsScript", "layerTimeJsCode": LIB + body}})


def tf(pos=(0, 0), anchor=(0, 0), scale=100, rot=0, op=100):
    return {"anchorPoint": list(anchor), "position": list(pos), "scale": [scale, scale], "rotation": rot, "opacity": op}


def rng(a, b):
    return {"start": MS(a), "duration": MS(b - a)}


def rect(name, a, b, size, color, pos, round_=0, stroke=None, anchor=None):
    L = {"type": "Rect", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(a, b),
         "transform": tf(pos, anchor if anchor else (size[0] / 2, size[1] / 2)),
         "rect": {"size": list(size), "fillColor": list(color), "roundness": round_}}
    if stroke:
        L["rect"].update(strokeEnabled=True, strokeColor=list(stroke[1]), strokeWidth=stroke[0])
    return L


def glow_style(color, size):
    return [{"id": nid(), "style": {"type": "outerGlow", "enabled": True, "color": list(color),
                                    "size": size, "spread": 8, "range": 50, "blendMode": "screen"}}]


def text(name, a, b, s, pos, size, font="PS", color=(1, 1, 1, 1), glow=None, stroke=6, just="center"):
    fam, sty = ("Press Start 2P", "Regular") if font == "PS" else ("Silkscreen", "Bold")
    L = {"type": "Text", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(a, b),
         "transform": tf(pos),
         "sourceText": {"text": s, "fontFamily": fam, "fontStyle": sty, "fontSize": size, "fillColor": list(color),
                        "strokeWidth": stroke, "strokeColor": [0.035, 0, 0.07, 1], "applyStroke": stroke > 0,
                        "strokeOverFill": False, "justification": just}}
    if glow:
        L["layerStyles"] = glow_style(glow, max(18, size * 0.35))
    return L


imported = set()


def img(path):
    aid = "img-" + os.path.basename(os.path.dirname(path)) + "-" + os.path.splitext(os.path.basename(path))[0]
    if aid not in imported:
        run("project", "import-asset", "--project", PROJ, "--file", path, "--asset-id", aid, "--kind", "image")
        imported.add(aid)
    return aid


def image(name, a, b, path, pos, anchor, scale=100):
    return {"type": "Image", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(a, b),
            "transform": tf(pos, anchor, scale), "source": {"assetId": img(path), "fit": "contain"}}


def group(name, a, b, layers, pos=(0, 0), anchor=(0, 0)):
    return {"type": "Group", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(a, b),
            "transform": tf(pos, anchor), "layers": layers}


def adjust(name, a, b, effects):
    return {"type": "Adjustment", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(a, b),
            "transform": tf(), "effects": [{"id": nid(), "effect": e} for e in effects]}


PINK, CYAN, YELLOW, WHITE, VIOLET = (1, 0.19, 0.77, 1), (0.12, 0.92, 1, 1), (1, 0.91, 0.27, 1), (1, 0.97, 1, 1), (0.62, 0.36, 1, 1)
DARK = (0.035, 0, 0.07, 1)
GPTF = lambda n: os.path.join(GPT, n + ".png")

# ---------------------------------------------------------------- project + audio
if os.path.exists(PROJ):
    os.remove(PROJ)
run("project", "create", "--project", PROJ)
for f in ("PressStart2P-Regular.ttf", "Silkscreen-Bold.ttf"):
    run("project", "import-font", "--project", PROJ, "--file", os.path.join(LW, "src", "fonts", f))
SR = 48000
os.makedirs(os.path.join(HERE, "audio"), exist_ok=True)
tt = np.arange(int(0.05 * SR)) / SR
tick = np.sign(np.sin(2 * np.pi * 1100 * tt)) * np.exp(-tt * 80)
tp = os.path.join(HERE, "audio", "tick.wav")
with wave.open(tp, "wb") as w:
    x = tick / np.max(np.abs(tick)) * 10 ** (-8 / 20)
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.stack([x, x], 1) * 32767).astype("<i2").tobytes())
SFX = {"tick": tp, "bonk": os.path.join(REPO, "social", "glitch-invades-app", ".tesseract-work", "audio", "bonk.wav")}
for n in ("whoosh", "pop", "glitch", "impact", "riser", "slam"):
    SFX[n] = os.path.join(LW, "audio", n + ".wav")
SFX_DUR = {}
for n, p in SFX.items():
    run("project", "import-asset", "--project", PROJ, "--file", p, "--asset-id", "aud-" + n, "--kind", "audio")
    SFX_DUR[n] = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                      capture_output=True, text=True).stdout)
auds = []


def sfx(n, at, vol=0.6):
    d = SFX_DUR[n]
    auds.append({"type": "Audio", "id": nid(), "name": f"SFX {n} {at:.2f}", "source": {"assetId": "aud-" + n},
                 "activeRange": rng(at, min(DUR, at + d)), "sourceRange": {"start": 0, "duration": MS(min(DUR, at + d) - at)},
                 "sourceIntrinsicDuration": MS(d), "volume": vol, "captionsEnabled": False})


# ---------------------------------------------------------------- background + board
bg = image("BG room", 0, DUR, GPTF("background"), (540, 960), (540, 960), 112)
bg["effects"] = [{"id": nid(), "effect": {"type": "gaussianBlur", "blurriness": 6, "repeatEdgePixels": True}}]
dim = rect("BG dim", 0, DUR, (W, H), DARK, (540, 960))
dim["transform"]["opacity"] = 62

TIERS = [("NORMAL", CYAN, 560), ("WEIRD", YELLOW, 810), ("VERY\nWEIRD", PINK, 1060), ("CERTIFIED\nWEIRD", VIOLET, 1310)]


def tier_row(label, col, y):
    kids = [text(f"Tier label {label}", 0, DUR, label, (170, y + (10 if "\n" not in label else -8)), 34 if "\n" in label else 40,
                 font="SK", color=DARK, stroke=0),
            rect(f"Tier box {label}", 0, DUR, (250, 220), col, (170, y), round_=18),
            rect(f"Tier lane {label}", 0, DUR, (1000, 230), (0.07, 0.02, 0.13, 0.9), (540, y), round_=22, stroke=(5, col))]
    return group(f"TIER {label.replace(chr(10), ' ')}", 0, DUR, kids)


rows = [tier_row(*t) for t in TIERS]
# rows 0-2 fall off at 10.3; the CERTIFIED row rises to the top (its content is re-positioned by rowY)
for i, r in enumerate(rows[:3]):
    t0 = 10.3 + i * 0.08
    anim(r["id"], "positionY", f"var u=t-{t0}; return u<0?0:-300*u+3400*u*u;")
    anim(r["id"], "rotation", f"var u=t-{t0}; return u<0?0:{(-1) ** i * 25}*u;")
anim(rows[3]["id"], "positionY", "return rowY(t)-1310;")
board_in = "return t<0.25?0:100*eo((t-0.25)/0.3);"
for r in rows:
    anim(r["id"], "opacity", board_in)

# ---------------------------------------------------------------- the four main cats
CATS = [  # key, name, trait, start, slot x, target tier index
    ("cat-lucky-jump", "LUCKY", "wins every coin flip.\nseems normal?", 1.6, 0, 550),
    ("cat-beanie-dance", "BEANIE", "cold ears.\nzero chill.", 3.6, 1, 700),
    ("cat-smoke-dance", "SMOKE", "sunglasses\nindoors.", 5.6, 2, 850),
    ("cat-glitch-jump", "GLITCH", "desyncs when\nnervous.", 7.6, 3, 400),
]
HB, SB = 50, 21
overlay = rect("Hero dim", 0, DUR, (W, H), DARK, (540, 960))
anim(overlay["id"], "opacity", "var o=0;" + "".join(
    f"if(t>={S}&&t<{S + 1.3}) o=Math.max(o,70*Math.min(eo((t-{S})/0.15),1-eo((t-{S + 1.1})/0.2)));" for _, _, _, S, _, _ in CATS)
     + "return o;")
heroes, labels = [], []
for key, name, trait, S, tier, cx in CATS:
    sx, sy = 400, TIERS[tier][2]
    fly = S + 1.3
    L = image(f"CAT {name}", S, DUR, GPTF(key), (540, 1000), (540, 960), HB)
    # hero -> own tier slot -> (9.6) certified row -> (10.3) rises with the row
    anim(L["id"], "positionX",
         f"var g=t+{S}; if(g<{fly}) return 540; var x=lerp(540,{sx},eo((g-{fly})/0.4));"
         f"if({tier}<3&&g>=9.6) x=lerp({sx},{cx},eo((g-9.6)/0.5)); return x;")
    anim(L["id"], "positionY",
         f"var g=t+{S}; if(g<{fly}) return 1000+Math.sin(g*6)*12; var y=lerp(1000,{sy},eo((g-{fly})/0.4));"
         f"if({tier}<3&&g>=9.6) y=lerp({sy},1310,eo((g-9.6)/0.5)); if(g>=10.3) y=y-1310+rowY(g); return y;")
    sc = (f"var g=t+{S}; var s; if(t<0.3) s={HB}*ob(t/0.3); else if(g<{fly}) s={HB}; else s=lerp({HB},{SB},eo((g-{fly})/0.4));"
          f"var b=g/0.5; var p=b-Math.floor(b); var k=g>={fly}+0.4?0.08*Math.exp(-p*10):0;")
    anim(L["id"], "scaleX", sc + "return s*(1+k);")
    anim(L["id"], "scaleY", sc + "return s*(1-k);")
    anim(L["id"], "rotation", f"var g=t+{S}; if(t<0.3) return lerp(-25,0,eo(t/0.3)); if(g<{fly}) return Math.sin(g*5)*5; return Math.sin(g*Math.PI*2)*6;")
    heroes.append(L)
    labels.append(text(f"{name} name", S + 0.15, fly, name, (540, 1540), 92, color=YELLOW, glow=YELLOW, stroke=7))
    labels.append(text(f"{name} trait", S + 0.3, fly, trait, (540, 1660), 46, font="SK", color=WHITE, glow=PINK))
    sfx("pop", S, 0.55); sfx("whoosh", fly - 0.05, 0.45)
    if tier < 3:
        sfx("bonk", fly + 0.38, 0.6)
heroes.reverse()

# ---------------------------------------------------------------- glitch breaks the list
GA = [{"type": "mosaic", "horizontalBlocks": 72, "verticalBlocks": 128, "sharpColors": True},
      {"type": "chromaticAberration", "amount": 0.35, "direction": 0}]
GB = [{"type": "shiftChannels", "takeRedFrom": "blue", "takeGreenFrom": "green", "takeBlueFrom": "red"},
      {"type": "chromaticAberration", "amount": 0.45, "direction": 90}]
glitches = [adjust(f"Glitch {c} {8.9 + i * 0.12:.2f}", 8.9 + i * 0.12, 8.9 + (i + 1) * 0.12, GA if c == "A" else GB)
            for i, c in enumerate("ABxBA") if c in "AB"]
glitches.append(adjust("Glitch hit 10.3", 10.3, 10.45, GA))
sfx("glitch", 8.9, 0.6); sfx("impact", 9.6, 0.7); sfx("riser", 9.3, 0.4); sfx("slam", 10.3, 0.6)

# header text track
hook = text("Hook", 0, 1.6, "RANKING THE\nWEIRD CATS", (540, 190), 64, color=PINK, glow=PINK, stroke=7)
hook2 = text("Hook sub", 0.3, 1.6, "from normal to certified weird", (540, 390), 38, font="SK", color=WHITE, glow=CYAN)
wait = text("Wait", 8.9, 9.6, "wait.", (540, 260), 70, font="SK", color=WHITE, glow=PINK)
none_ = text("None normal", 9.6, 10.9, "none of them\nare normal.", (540, 200), 62, font="SK", color=PINK, glow=PINK)
for L in (hook, none_):
    anim(L["id"], "scaleX", "return t<0.18?lerp(180,100,eo(t/0.18)):100+4*Math.exp(-((t/0.5)%1)*9);")
    anim(L["id"], "scaleY", "return t<0.18?lerp(180,100,eo(t/0.18)):100+4*Math.exp(-((t/0.5)%1)*9);")

# ---------------------------------------------------------------- collection cats fill the screen
coll = [f for f in sorted(glob.glob(os.path.join(LW, "src", "rain4x", "*.png"))) if os.path.basename(f) != "frog-hat.png"]
grid = []
for i, f in enumerate(coll):
    col, row = i % 5, i // 5
    x, y = 150 + col * 195, 760 + row * 230
    at = 10.9 + i * 0.11
    L = image(f"Grid {os.path.basename(f)[:-4]}", at, DUR, f, (x, y), (384, 832), 23)
    anim(L["id"], "positionY", f"return t<0.25?lerp({y - 900},{y},ei(t/0.25)):{y}-30*4*((t/0.5)%1)*(1-(t/0.5)%1)*(t>1?1:0);")
    anim(L["id"], "scaleY", "var q=t>=0.25?Math.exp(-(t-0.25)*14)*0.3:0; return 23*(1-q);")
    anim(L["id"], "scaleX", "var q=t>=0.25?Math.exp(-(t-0.25)*14)*0.3:0; return 23*(1+q);")
    grid.append(L)
    sfx("tick", at + 0.24, 0.5)
end1 = text("End ALL", 13.0, DUR, "they're ALL\ncertified weird.", (540, 1640), 52, font="SK", color=VIOLET, glow=VIOLET)
end2 = text("End CTA", 13.4, DUR, "comment your ranking", (540, 1770), 40, font="SK", color=CYAN, glow=CYAN)
for L in (end1, end2):
    anim(L["id"], "positionX", "return lerp(1300,540,ob(t/0.3));")

# ---------------------------------------------------------------- camera
scene = ([wait, none_, hook, hook2, end1, end2] + labels + heroes + [overlay] + grid + rows + [dim, bg])
camera = group("CAMERA", 0, DUR, scene, (540, 960), (540, 960))
amp = ("var A=0; var hits=[%s]; for(var i=0;i<hits.length;i++){var u=t-hits[i]; if(u>=0&&u<0.4) A=Math.max(A,12*Math.exp(-u*9));}"
       "if(t>=8.9&&t<9.6) A=24; if(t>=9.6&&t<10.1) A=Math.max(A,30*Math.exp(-(t-9.6)*6)); if(t>=10.3&&t<10.8) A=Math.max(A,26*Math.exp(-(t-10.3)*6));"
       % ",".join(f"{S + 1.7:.2f}" for *_, S, _, _ in [(c[0], c[1], c[2], c[3], c[4], c[5]) for c in CATS]))
anim(camera["id"], "positionX", amp + "return 540+(h(Math.floor(t*30))-0.5)*2*A;")
anim(camera["id"], "positionY", amp + "return 960+(h(Math.floor(t*30)+99)-0.5)*2*A;")
anim(camera["id"], "rotation", "return (t>=8.9&&t<9.6)?(h(Math.floor(t*12)+5)-0.5)*6:0;")
vign = adjust("Vignette", 0, DUR, [{"type": "vignette", "amount": 0.4, "radius": 0.85, "feather": 0.6}])

layers = glitches + [vign, camera] + auds
doc = {"$schema": "https://jerboa.dev/schemas/fx-composition/editable/v1/document.schema.json", "formatVersion": 1,
       "dimensions": {"width": W, "height": H}, "duration": DUR, "backgroundColor": list(DARK),
       "composition": {"id": "main", "name": "Weird Cats tier list", "layers": layers, "dynamics": {"entries": entries}}}
out = os.path.join(HERE, "editable.json")
json.dump(doc, open(out, "w"), indent=1)
run("project", "commit", "--project", PROJ, "--file", out)
os.remove(out)
print("built", PROJ, "animators:", len(entries), "grid cats:", len(grid))
