#!/usr/bin/env python3
"""PAUSE TO FIND YOUR WEIRD CAT: 15s vertical TikTok/Reels quiz.

0-1.6s   hook: "PAUSE THE VIDEO / TO FIND YOUR WEIRD CAT"
1.6-12.6 cards flicker (0.25s at first, then 0.1s = 3 frames each) in a shuffled order
12.6-15  end card: "WHO DID YOU GET?" + logo + handle
Re-run to rebuild; every layer stays editable in Tesseract.
"""
import json, os, subprocess, glob, random, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(ROOT, "..", ".."))
LAUNCH = os.path.join(REPO, "social", "launch-video")
GPT = os.path.join(LAUNCH, "gpt")
T = os.path.expanduser("~/.local/share/Tesseract/bin/tsrct")
PROJ = os.path.join(ROOT, "PauseYourCat.tsrct")
W, H, DUR = 1080, 1920, 15.0
MS = lambda s: int(round(s * 1000))

CATS = [  # file, display name, trait (\n where a line would overflow the card)
    ("beanie", "BEANIE", "cold ears.\nzero chill."),
    ("drip", "DRIP", "cries in purple"),
    ("frog-hat", "FROG HAT", "thinks he's a frog.\nlet him."),
    ("glitch", "GLITCH", "desyncs when\nnervous"),
    ("hypno", "HYPNO", "stares until\nyou blink"),
    ("lucky", "LUCKY", "wins every\ncoin flip"),
    ("mellow", "MELLOW", "unbothered.\nalways."),
    ("nova", "NOVA", "main character\nenergy"),
    ("orbit", "ORBIT", "overthinks\nin circles"),
    ("patch", "PATCH", "held together\nby vibes"),
    ("phantom", "PHANTOM", "only seen at 3am"),
    ("prism", "PRISM", "chronically extra"),
    ("rusty", "RUSTY", "fixes nothing.\nbreaks everything."),
    ("slime", "SLIME", "sticky personality"),
    ("spectrum", "SPECTRUM", "every mood\nat once"),
    ("stereo", "STEREO", "sees in 3D.\nlives in 2D."),
    ("tux", "TUX", "overdressed for\neverything"),
    ("violet", "VIOLET", "sleepy but\njudging you"),
    ("weirdo", "WEIRDO", "certified weirdo"),
    ("wink", "WINK", "flirts with\nthe camera"),
]
N = len(CATS)
T0, T1 = 1.6, 12.6          # shuffle window


def run(*a):
    r = subprocess.run([T, *a], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"{' '.join(a)}\n{r.stdout}\n{r.stderr}")
    return r.stdout


LIB = ("var t=input.time.seconds;"
       "function cl(x){return Math.max(0,Math.min(1,x));}"
       "function eo(x){x=cl(x);return 1-Math.pow(1-x,3);}"
       "function ob(x){x=cl(x);var c1=2.2,c3=c1+1;return 1+c3*Math.pow(x-1,3)+c1*Math.pow(x-1,2);}"
       "function lerp(a,b,p){return a+(b-a)*p;}"
       "function h(n){var x=Math.sin(n*12.9898+78.233)*43758.5453;return x-Math.floor(x);}")
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


def rect(name, a, b, size, color, pos, round_=0, stroke=None):
    L = {"type": "Rect", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(a, b),
         "transform": tf(pos, (size[0] / 2, size[1] / 2)),
         "rect": {"size": list(size), "fillColor": list(color), "roundness": round_}}
    if stroke:
        L["rect"].update(strokeEnabled=True, strokeColor=list(stroke[1]), strokeWidth=stroke[0])
    return L


def text(name, a, b, s, pos, size, font="PS", color=(1, 1, 1, 1), glow=None, stroke=6, just="center"):
    fam, sty = ("Press Start 2P", "Regular") if font == "PS" else ("Silkscreen", "Bold")
    L = {"type": "Text", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(a, b),
         "transform": tf(pos),
         "sourceText": {"text": s, "fontFamily": fam, "fontStyle": sty, "fontSize": size, "fillColor": list(color),
                        "strokeWidth": stroke, "strokeColor": [0.035, 0, 0.07, 1], "applyStroke": stroke > 0,
                        "strokeOverFill": False, "justification": just}}
    if glow:
        L["layerStyles"] = [{"id": nid(), "style": {"type": "outerGlow", "enabled": True, "color": list(glow),
                                                    "size": max(18, size * 0.35), "spread": 8, "range": 50,
                                                    "blendMode": "screen"}}]
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


PINK, CYAN, YELLOW, WHITE = (1, 0.19, 0.77, 1), (0.12, 0.92, 1, 1), (1, 0.91, 0.27, 1), (1, 0.97, 1, 1)

# ---------------------------------------------------------------- card order + clock (shared by visuals and audio)
random.seed(7)
order = []
while len(order) < 140:
    perm = list(range(N))
    random.shuffle(perm)
    if order and perm[0] == order[-1]:
        perm[0], perm[1] = perm[1], perm[0]
    order += perm
# tick clock: 4 slow cards (0.25s) then 0.1s (3 frames) each
TICK_JS = "function tick(g){var u=g-%s; if(u<0) return -1; if(u<1) return Math.floor(u/0.25); return 4+Math.floor((u-1)/0.1);}" % T0
ticks = [T0 + i * 0.25 for i in range(4)] + [T0 + 1 + i * 0.1 for i in range(int((T1 - T0 - 1) / 0.1))]
ORDER_JS = "var ORD=[%s];" % ",".join(map(str, order))

# ---------------------------------------------------------------- audio: one ticker track + end sting
SR = 48000


def save(path, x, peak_db=-6):
    x = x / (np.max(np.abs(x)) + 1e-9) * 10 ** (peak_db / 20)
    st = np.stack([x, x], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype("<i2").tobytes())


buf = np.zeros(int(DUR * SR))
for i, t0 in enumerate(ticks):
    f = 700 + 60 * (i % 7) + (0 if i < 4 else 200)
    n = int(0.035 * SR); tt = np.arange(n) / SR
    blip = np.sign(np.sin(2 * np.pi * f * tt)) * np.exp(-tt * 90)
    s = int(t0 * SR); buf[s:s + n] += blip * (0.9 if i < 4 else 0.55)
# end sting: rising arpeggio + "freeze" hit
for k, m in enumerate((72, 76, 79, 84)):
    f = 440 * 2 ** ((m - 69) / 12); n = int(0.12 * SR); tt = np.arange(n) / SR
    s = int((T1 + k * 0.07) * SR); buf[s:s + n] += np.sign(np.sin(2 * np.pi * f * tt)) * np.exp(-tt * 18) * 0.7
os.makedirs(os.path.join(HERE, "audio"), exist_ok=True)
TICKER = os.path.join(HERE, "audio", "ticker.wav")
save(TICKER, buf, -4)
MEOW = os.path.join(LAUNCH, ".tesseract-work", "audio", "meow.wav")

# ---------------------------------------------------------------- project
if os.path.exists(PROJ):
    os.remove(PROJ)
run("project", "create", "--project", PROJ)
for f in ("PressStart2P-Regular.ttf", "Silkscreen-Bold.ttf"):
    run("project", "import-font", "--project", PROJ, "--file", os.path.join(LAUNCH, ".tesseract-work", "src", "fonts", f))
run("project", "import-asset", "--project", PROJ, "--file", TICKER, "--asset-id", "aud-ticker", "--kind", "audio")
run("project", "import-asset", "--project", PROJ, "--file", MEOW, "--asset-id", "aud-meow", "--kind", "audio")

# background: GPT bedroom, dimmed and blurred, slow push; portal spins behind the card
bg = image("BG room", 0, DUR, os.path.join(GPT, "background.png"), (540, 960), (540, 960), 112)
bg["effects"] = [{"id": nid(), "effect": {"type": "gaussianBlur", "blurriness": 5, "repeatEdgePixels": True}}]
anim(bg["id"], "scaleX", "return 112+t*0.6;")
anim(bg["id"], "scaleY", "return 112+t*0.6;")
dim = rect("BG dim", 0, DUR, (W, H), (0.035, 0, 0.07, 1), (540, 960))
dim["transform"]["opacity"] = 55
portal = image("Portal", 0, DUR, os.path.join(GPT, "portal.png"), (540, 900), (540, 960), 150)
anim(portal["id"], "rotation", f"return -t*({'t<%s?90:t<%s?420:60' % (T0, T1)});")
anim(portal["id"], "opacity", "return 55;")

# cards
cards = []
for k, (f, name, trait) in enumerate(CATS):
    kids = [
        text(f"{name} trait", 0, DUR, trait, (540, 1450), 46, font="SK", color=WHITE, glow=PINK),
        text(f"{name} name", 0, DUR, name, (540, 1350), 84, color=YELLOW, glow=YELLOW),
        text(f"{name} number", 0, DUR, f"WEIRD CAT #{k + 1:02d}", (540, 470), 34, color=CYAN, glow=CYAN),
        image(f"{name} art", 0, DUR, os.path.join(LAUNCH, ".tesseract-work", "src", "rain4x", f + ".png"),
              (540, 1250), (384, 832), 84),
    ]
    for L in kids: L["activeRange"] = rng(0, DUR - T0)
    kids[2]["activeRange"] = rng(0, T1 - T0)  # number hides under the end title
    g = group(f"CARD {name}", 0, DUR - T0, kids)
    # visible while the shuffle clock points at this cat; the last card stays frozen for the end card
    anim(g["id"], "opacity", ORDER_JS + TICK_JS +
         f"var n=tick(Math.min(t+{T0},{T1 - 0.001})); if(n<0) return 0; return ORD[n]=={k}?100:0;")
    cards.append(g)
card_bg = rect("Card frame", 0, DUR - T0, (880, 1260), (0.06, 0.02, 0.12, 0.93), (540, 1000), round_=60, stroke=(8, PINK))
card_bg["layerStyles"] = [{"id": nid(), "style": {"type": "outerGlow", "enabled": True, "color": list(PINK),
                                                   "size": 40, "spread": 10, "range": 50, "blendMode": "screen"}}]
deck = group("CARD DECK", T0, DUR, cards + [card_bg], (540, 1000), (540, 1000))
anim(deck["id"], "scaleX", TICK_JS + "var g=t+%s; var e=g>=%s?Math.exp(-(g-%s)*6)*18:0;"
     "var s=t<0.25?100*ob(t/0.25):100; var n=tick(Math.min(g,%s)); var u=g-%s;"
     "var f=u<1?(u/0.25)%%1:((u-1)/0.1)%%1; if(g>=%s) f=1; return s*(1+0.03*Math.exp(-f*6))+e;" % (T0, T1, T1, T1 - 0.001, T0, T1))
anim(deck["id"], "scaleY", TICK_JS + "var g=t+%s; var e=g>=%s?Math.exp(-(g-%s)*6)*18:0;"
     "var s=t<0.25?100*ob(t/0.25):100; var u=g-%s;"
     "var f=u<1?(u/0.25)%%1:((u-1)/0.1)%%1; if(g>=%s) f=1; return s*(1+0.03*Math.exp(-f*6))+e;" % (T0, T1, T1, T0, T1))
anim(deck["id"], "rotation", "var g=t+%s; if(g>=%s) return Math.sin((g-%s)*18)*6*Math.exp(-(g-%s)*3); return (h(Math.floor(g*10))-0.5)*3;" % (T0, T1, T1, T1))

# hook, header, footer, end card
hook1 = text("Hook PAUSE", 0, T0, "PAUSE\nTHE VIDEO", (540, 760), 110, color=PINK, glow=PINK, stroke=8)
hook2 = text("Hook subline", 0.35, T0, "TO FIND YOUR\nWEIRD CAT", (540, 1120), 72, font="SK", color=WHITE, glow=CYAN)
for L, d in ((hook1, 0), (hook2, 0.35)):
    anim(L["id"], "scaleX", "var s=t<0.18?lerp(190,100,eo(t/0.18)):100+4*Math.exp(-((t/0.5)%1)*9); return s;")
    anim(L["id"], "scaleY", "var s=t<0.18?lerp(190,100,eo(t/0.18)):100+4*Math.exp(-((t/0.5)%1)*9); return s;")
    anim(L["id"], "rotation", "return t<0.18?lerp(-8,0,eo(t/0.18)):Math.sin(t*7)*2;")
header = text("Header", T0, T1, "PAUSE NOW!", (540, 250), 64, color=PINK, glow=PINK)
anim(header["id"], "opacity", "return (Math.floor(t*4)%2==0)?100:35;")
footer = text("Footer", T0, T1, "comment who you got", (540, 1740), 44, font="SK", color=CYAN, glow=CYAN)
end1 = text("End WHO", T1, DUR, "WHO DID\nYOU GET?", (540, 230), 84, color=PINK, glow=PINK, stroke=8)
anim(end1["id"], "scaleX", "return t<0.2?100*ob(t/0.2):100+4*Math.exp(-((t/0.5)%1)*9);")
anim(end1["id"], "scaleY", "return t<0.2?100*ob(t/0.2):100+4*Math.exp(-((t/0.5)%1)*9);")
end2 = text("End CTA", T1 + 0.3, DUR, "comment below", (540, 1740), 46, font="SK", color=CYAN, glow=CYAN)
flash = rect("Freeze flash", T1, T1 + 0.25, (W, H), WHITE, (540, 960))
anim(flash["id"], "opacity", "return 90*(1-eo(t/0.25));")
vign = {"type": "Adjustment", "id": nid(), "name": "Vignette", "blendMode": "normal", "activeRange": rng(0, DUR),
        "transform": tf(), "effects": [{"id": nid(), "effect": {"type": "vignette", "amount": 0.45, "radius": 0.85, "feather": 0.6}}]}

# stickers orbit the card during the shuffle
stk = sorted(glob.glob(os.path.join(GPT, "stickers", "*.png")))
stickers = []
for i, f in enumerate(stk):
    a0 = i / len(stk) * 6.283
    L = image(f"Sticker {os.path.basename(f)[:-4]}", T0, DUR, f, (540, 1000), (130, 110), 70)
    anim(L["id"], "positionX", f"var g=t+{T0}; var sp=g<{T1}?1.6:0.4; return 540+Math.cos({a0:.3f}+g*sp)*500;")
    anim(L["id"], "positionY", f"var g=t+{T0}; var sp=g<{T1}?1.6:0.4; return 1000+Math.sin({a0:.3f}+g*sp)*720;")
    anim(L["id"], "rotation", f"return t*{(-1) ** i * 90};")
    stickers.append(L)

audio = [{"type": "Audio", "id": nid(), "name": "SFX ticker + sting", "source": {"assetId": "aud-ticker"},
          "activeRange": rng(0, DUR), "sourceRange": {"start": 0, "duration": MS(DUR)},
          "sourceIntrinsicDuration": MS(DUR), "volume": 0.7, "captionsEnabled": False},
         {"type": "Audio", "id": nid(), "name": "SFX meow", "source": {"assetId": "aud-meow"},
          "activeRange": rng(T1 + 0.3, T1 + 1.0), "sourceRange": {"start": 0, "duration": 700},
          "sourceIntrinsicDuration": 700, "volume": 0.6, "captionsEnabled": False}]

layers = ([flash, vign, hook1, hook2, header, footer, end1, end2] + stickers + [deck, portal, dim, bg] + audio)
doc = {"$schema": "https://jerboa.dev/schemas/fx-composition/editable/v1/document.schema.json", "formatVersion": 1,
       "dimensions": {"width": W, "height": H}, "duration": DUR, "backgroundColor": [0.035, 0, 0.07, 1],
       "composition": {"id": "main", "name": "Pause to find your Weird Cat", "layers": layers,
                       "dynamics": {"entries": entries}}}
out = os.path.join(HERE, "editable.json")
json.dump(doc, open(out, "w"), indent=1)
run("project", "commit", "--project", PROJ, "--file", out)
os.remove(out)
print("built", PROJ, "cards:", N, "ticks:", len(ticks))
