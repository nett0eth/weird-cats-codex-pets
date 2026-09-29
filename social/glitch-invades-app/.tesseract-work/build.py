#!/usr/bin/env python3
"""GLITCH INVADES THE APP: 15s vertical TikTok/Reels.

A calm "normal cat video" inside a generic short-video UI gets wrecked by the Weird Cats:
 2.0s paw steals the like button     3.3s Glitch eats the caption
 5.5s Beanie crushes the progress bar (it bends and rewinds)
 7.5s Lucky knocks the comment icon off   9.5s the whole UI breaks
11.0s giant Glitch face: "this is our feed now."   13.0s end card
The UI is a generic neon pixel UI (not a copy of any platform's layout). Re-run to rebuild.
"""
import json, os, subprocess, glob, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(ROOT, "..", ".."))
LAUNCH = os.path.join(REPO, "social", "launch-video")
GPT = os.path.join(LAUNCH, "gpt")
LW = os.path.join(LAUNCH, ".tesseract-work")
ICONS = os.path.join(HERE, "icons")
T = os.path.expanduser("~/.local/share/Tesseract/bin/tsrct")
PROJ = os.path.join(ROOT, "GlitchInvadesApp.tsrct")
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


def rect(name, a, b, size, color, pos, anchor=None, round_=0, stroke=None):
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


def fall(L, t0, x0, y0, vx, rot_speed):
    """after scene time t0 the layer drops with gravity (layer lives in a group starting at 0)."""
    anim(L["id"], "positionX", f"var u=t-{t0}; return u<0?{x0}:{x0}+{vx}*u;")
    anim(L["id"], "positionY", f"var u=t-{t0}; return u<0?{y0}:{y0}-500*u+3600*u*u;")
    anim(L["id"], "rotation", f"var u=t-{t0}; return u<0?0:{rot_speed}*u;")


PINK, CYAN, YELLOW, WHITE, RED = (1, 0.19, 0.77, 1), (0.12, 0.92, 1, 1), (1, 0.91, 0.27, 1), (1, 0.97, 1, 1), (1, 0.3, 0.4, 1)
GPTF = lambda n: os.path.join(GPT, n + ".png")

# ---------------------------------------------------------------- SFX
SR = 48000
os.makedirs(os.path.join(HERE, "audio"), exist_ok=True)


def save(name, x, peak_db=-6):
    x = x / (np.max(np.abs(x)) + 1e-9) * 10 ** (peak_db / 20)
    p = os.path.join(HERE, "audio", name + ".wav")
    with wave.open(p, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.stack([x, x], 1) * 32767).astype("<i2").tobytes())
    return p


rng_ = np.random.default_rng(3)
tt = np.arange(int(0.16 * SR)) / SR
chomp = (rng_.uniform(-1, 1, len(tt)) * 0.6 + np.sign(np.sin(2 * np.pi * np.linspace(260, 90, len(tt)) * tt))) * np.exp(-tt * 28)
tt2 = np.arange(int(0.9 * SR)) / SR
rewind = np.sign(np.sin(2 * np.pi * np.cumsum(np.linspace(1400, 300, len(tt2))) / SR)) * np.exp(-tt2 * 1.5) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 18 * tt2)))
tt3 = np.arange(int(0.12 * SR)) / SR
bonk = np.sign(np.sin(2 * np.pi * np.linspace(900, 200, len(tt3)) * tt3)) * np.exp(-tt3 * 30)
SFX = {"chomp": save("chomp", chomp, -8), "rewind": save("rewind", rewind, -10), "bonk": save("bonk", bonk, -8)}
for n in ("whoosh", "impact", "glitch", "pop", "slam", "meow", "riser"):
    SFX[n] = os.path.join(LW, "audio", n + ".wav")

# ---------------------------------------------------------------- project
if os.path.exists(PROJ):
    os.remove(PROJ)
run("project", "create", "--project", PROJ)
for f in ("PressStart2P-Regular.ttf", "Silkscreen-Bold.ttf"):
    run("project", "import-font", "--project", PROJ, "--file", os.path.join(LW, "src", "fonts", f))
SFX_DUR = {}
for n, p in SFX.items():
    run("project", "import-asset", "--project", PROJ, "--file", p, "--asset-id", "aud-" + n, "--kind", "audio")
    SFX_DUR[n] = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                      capture_output=True, text=True).stdout)
auds = []


def sfx(n, at, vol=0.6):
    d = SFX_DUR[n]
    auds.append({"type": "Audio", "id": nid(), "name": f"SFX {n} {at}", "source": {"assetId": "aud-" + n},
                 "activeRange": rng(at, min(DUR, at + d)), "sourceRange": {"start": 0, "duration": MS(min(DUR, at + d) - at)},
                 "sourceIntrinsicDuration": MS(d), "volume": vol, "captionsEnabled": False})


# ---------------------------------------------------------------- background + the "normal cat"
bg = image("BG room", 0, DUR, GPTF("background"), (540, 960), (540, 960), 112)
bg["effects"] = [{"id": nid(), "effect": {"type": "gaussianBlur", "blurriness": 3, "repeatEdgePixels": True}}]
dim = rect("BG dim", 0, DUR, (W, H), (0.035, 0, 0.07, 1), (540, 960))
anim(dim["id"], "opacity", "return t<9.5?38:t<13?55:62;")
calm = image("Normal cat (Mellow)", 0, 10.4, os.path.join(LW, "src", "rain4x", "mellow.png"), (470, 1420), (384, 832), 62)
anim(calm["id"], "scaleY", "return t<9.5?62*(1+0.02*Math.sin(t*3)):62;")
fall(calm, 9.7, 470, 1420, -200, -160)

hook = text("Hook POV", 0, 2.0, "POV: you're watching\na normal cat video", (540, 300), 60, font="SK", color=WHITE, glow=CYAN)

# ---------------------------------------------------------------- generic short-video UI
RX = 960
ui = []
avatar_ring = rect("UI avatar ring", 0, DUR, (116, 116), (0.06, 0.02, 0.12, 1), (RX, 820), round_=58, stroke=(6, PINK))
avatar = image("UI avatar (Glitch face)", 0, DUR, GPTF("cat-giant-face"), (RX, 822), (540, 960), 10)
heart = image("UI heart", 0, DUR, os.path.join(ICONS, "heart.png"), (RX, 1000), (52, 48), 100)
heart_n = text("UI heart count", 0, DUR, "9.9K", (RX, 1095), 26, color=WHITE, stroke=5)
comment = image("UI comment", 0, DUR, os.path.join(ICONS, "comment.png"), (RX, 1190), (52, 44), 100)
comment_n = text("UI comment count", 0, DUR, "420", (RX, 1280), 26, color=WHITE, stroke=5)
book = image("UI bookmark", 0, DUR, os.path.join(ICONS, "bookmark.png"), (RX, 1370), (40, 44), 100)
book_n = text("UI bookmark count", 0, DUR, "69", (RX, 1460), 26, color=WHITE, stroke=5)
share = image("UI share", 0, DUR, os.path.join(ICONS, "share.png"), (RX, 1550), (52, 48), 100)
handle = text("UI handle", 0, DUR, "@weirdcats_nft", (60, 1660), 30, color=WHITE, stroke=5, just="left")
CAP = "normal cat. nothing weird here."
caption = text("UI caption", 0, DUR, CAP, (60, 1720), 34, font="SK", color=WHITE, stroke=5, just="left")
sound = text("UI sound", 0, DUR, "original sound - weird cats", (60, 1775), 28, font="SK", color=(0.8, 0.8, 0.9, 1), stroke=4, just="left")
bar_bg_l = rect("UI bar track L", 0, DUR, (480, 14), (1, 1, 1, 0.35), (540, 1840), anchor=(480, 7))
bar_bg_r = rect("UI bar track R", 0, DUR, (480, 14), (1, 1, 1, 0.35), (540, 1840), anchor=(0, 7))
bar = rect("UI bar progress", 0, DUR, (960, 14), PINK, (60, 1840), anchor=(0, 7))

# -- 2.0 paw steals the like
paw = image("PAW grab", 1.95, 3.1, GPTF("cat-paw"), (1700, 1000), (540, 960), 46)
paw["transform"]["rotation"] = -90
anim(paw["id"], "positionX", "return t<0.35?lerp(1700,1020,eo(t/0.35)):lerp(1020,1800,ei((t-0.45)/0.6));")
anim(heart["id"], "positionX", f"return t<2.4?{RX}:lerp({RX},1620,ei((t-2.4)/0.6));")
anim(heart["id"], "rotation", "return t<2.4?0:(t-2.4)*-200;")
anim(heart_n["id"], "textContent", "return t<2.35?'9.9K':(t<3.2?'???':'0');")
sfx("whoosh", 1.95, 0.6); sfx("pop", 2.3, 0.6)
steal = text("Callout STOLEN", 2.4, 3.3, "hey!", (760, 900), 44, font="SK", color=YELLOW, glow=YELLOW)

# -- 3.3 Glitch eats the caption
eat = image("GLITCH eats caption", 3.3, 5.4, GPTF("cat-glitch-jump"), (150, 2400), (540, 960), 40)
anim(eat["id"], "positionY", "return t<0.3?lerp(2400,1720,eo(t/0.3)):(t<1.75?1720+Math.abs(Math.sin(t*14))*-30:lerp(1720,2500,ei((t-1.75)/0.35)));")
anim(eat["id"], "positionX", "return t<0.3?150:lerp(150,820,cl((t-0.3)/1.4));")
anim(eat["id"], "rotation", "return Math.sin(t*16)*10;")
n = len(CAP)
anim(caption["id"], "textContent",
     f"var s='{CAP}'; if(t<3.6) return s; var k=Math.floor(cl((t-3.6)/1.4)*{n}); var r=''; for(var i=0;i<{n};i++) r+= i<k?' ':s.charAt(i); return t>5.1?'':r;")
for i in range(5):
    sfx("chomp", 3.65 + i * 0.28, 0.55)
nom = text("Callout NOM", 3.7, 5.0, "nom nom nom", (560, 1560), 44, font="SK", color=PINK, glow=PINK)
anim(nom["id"], "positionY", "return 1560+Math.sin(t*20)*8;")

# -- 5.5 Beanie crushes the progress bar
bean = image("BEANIE crushes bar", 5.45, 7.4, GPTF("cat-beanie-jump"), (540, -500), (540, 1500), 30)
anim(bean["id"], "positionY", "return t<0.35?lerp(-500,1845,ei(t/0.35)):(t<1.3?1845+Math.sin((t-0.35)*30)*6:lerp(1845,-600,eo((t-1.3)/0.6)));")
anim(bean["id"], "scaleY", "var q=t>=0.35&&t<0.7?Math.exp(-(t-0.35)*10)*0.3:0; return 30*(1-q);")
anim(bean["id"], "scaleX", "var q=t>=0.35&&t<0.7?Math.exp(-(t-0.35)*10)*0.3:0; return 30*(1+q);")
BEND = "var b=t<5.8?0:(t<7.2?16*Math.exp(-(t-5.8)*0.8)*(1+0.15*Math.sin((t-5.8)*22)):lerp(16*Math.exp(-1.12),0,eo((t-7.2)/0.2)));"
anim(bar_bg_l["id"], "rotation", BEND + "return -b;")
anim(bar_bg_r["id"], "rotation", BEND + "return b;")
anim(bar["id"], "scaleX", "var p; if(t<5.8) p=t/15*100; else if(t<6.7) p=lerp(5.8/15*100,4,eo((t-5.8)/0.9)); else p=4+(t-6.7)/15*100; return Math.max(1,p);")
anim(bar["id"], "rotation", BEND + "return t<5.8?0:b*0.3;")
rew = text("Callout REWIND", 5.85, 7.0, "<< REWINDING", (540, 1600), 40, color=CYAN, glow=CYAN)
anim(rew["id"], "opacity", "return (Math.floor(t*8)%2==0)?100:30;")
sfx("impact", 5.8, 0.8); sfx("rewind", 5.85, 0.55)

# -- 7.5 Lucky knocks the comment icon off
luck = image("LUCKY kicks comment", 7.45, 9.5, GPTF("cat-lucky-jump"), (-400, 1230), (540, 960), 36)
anim(luck["id"], "positionX", "return t<0.4?lerp(-400,720,eo(t/0.4)):(t<1.6?720:lerp(720,-500,ei((t-1.6)/0.45)));")
anim(luck["id"], "rotation", "return t<0.4?lerp(-30,8,eo(t/0.4)):8*Math.sin(t*9);")
fall(comment, 7.85, RX, 1190, 420, 720)
fall(comment_n, 7.85, RX, 1280, 300, -360)
sfx("whoosh", 7.45, 0.5); sfx("bonk", 7.85, 0.7)
oops = text("Callout OOPS", 8.0, 9.3, "oops.", (640, 900), 50, font="SK", color=YELLOW, glow=YELLOW)

# -- 9.5 total breakdown: everything left falls
for i, L in enumerate([avatar_ring, avatar, heart_n, book, book_n, share, handle, sound, caption]):
    x0 = L["transform"]["position"][0]; y0 = L["transform"]["position"][1]
    fall(L, 9.55 + (i % 4) * 0.07, x0, y0, (i % 3 - 1) * 300, ((-1) ** i) * 400)
for L in (bar_bg_l, bar_bg_r, bar):
    anim(L["id"], "opacity", "return t<9.6?100:0;")
err = text("ERROR", 9.6, 11.1, "ERROR:\nAPP TAKEN OVER\nBY WEIRD CATS", (540, 820), 70, font="SK", color=RED, glow=(1, 0.1, 0.3, 1), stroke=8)
anim(err["id"], "positionX", "return 540+(h(Math.floor(t*14))-0.5)*60;")
anim(err["id"], "opacity", "return h(Math.floor(t*16)+3)>0.15?100:0;")
GA = [{"type": "mosaic", "horizontalBlocks": 72, "verticalBlocks": 128, "sharpColors": True},
      {"type": "chromaticAberration", "amount": 0.35, "direction": 0}]
GB = [{"type": "shiftChannels", "takeRedFrom": "blue", "takeGreenFrom": "green", "takeBlueFrom": "red"},
      {"type": "chromaticAberration", "amount": 0.45, "direction": 90}]
glitches = [adjust(f"Glitch {c} {9.5 + i * 0.15:.2f}", 9.5 + i * 0.15, 9.5 + (i + 1) * 0.15, GA if c == "A" else GB)
            for i, c in enumerate("ABxAB xBA") if c in "AB"]
glitches.append(adjust("Glitch hit 2.0", 1.95, 2.1, GB))
glitches.append(adjust("Glitch hit 5.8", 5.8, 5.95, GA))
sfx("glitch", 9.5, 0.6); sfx("glitch", 10.2, 0.5); sfx("riser", 9.9, 0.45)

# -- 11.0 giant face
face = image("GIANT FACE peek", 11.0, 13.1, GPTF("cat-giant-face"), (540, 2600), (540, 960), 100)
anim(face["id"], "positionY", "return t<0.5?lerp(2600,1150,eo(t/0.5)):1150+Math.sin(t*2)*10;")
anim(face["id"], "rotation", "return t<0.5?lerp(10,0,eo(t/0.5)):Math.sin(t*1.5)*2;")
face["effects"] = [{"id": nid(), "effect": {"type": "chromaticAberration", "amount": 0.15, "direction": 0}}]
feed = text("THIS IS OUR FEED NOW", 11.5, 13.1, "this is our\nfeed now.", (540, 330), 76, font="SK", color=WHITE, glow=PINK)
anim(feed["id"], "textContent", "var s='this is our\\nfeed now.'; return s.substring(0,Math.min(s.length,Math.floor(t*16)));")
sfx("impact", 11.0, 0.8)

# -- 13.0 end card
flash = rect("Flash end", 13.0, 13.3, (W, H), PINK, (540, 960))
anim(flash["id"], "opacity", "return 90*(1-eo(t/0.3));")
logo = image("LOGO", 13.0, DUR, os.path.join(REPO, "assets", "art", "weird-cats-official-logo.png"), (540, 760), (768, 512), 66)
anim(logo["id"], "scaleX", "return t<0.3?lerp(240,66,ob(t/0.3)):66*(1+0.035*Math.exp(-((t/0.5)%1)*9));")
anim(logo["id"], "scaleY", "return t<0.3?lerp(240,66,ob(t/0.3)):66*(1+0.035*Math.exp(-((t/0.5)%1)*9));")
anim(logo["id"], "rotation", "return t<0.3?lerp(-20,0,eo(t/0.3)):Math.sin(t*3)*2;")
cta = text("CTA follow", 13.35, DUR, "follow before they\nbreak your app", (540, 1250), 58, font="SK", color=CYAN, glow=CYAN)
hnd = text("CTA handle", 13.6, DUR, "@weirdcats_nft", (540, 1450), 44, color=PINK, glow=PINK)
for L in (cta, hnd):
    anim(L["id"], "positionX", "return lerp(1300,540,ob(t/0.3));")
stk = sorted(glob.glob(os.path.join(GPT, "stickers", "*.png")))
spots = [(140, 420), (940, 460), (120, 1620), (960, 1640), (110, 1470), (975, 1470)]
end_stk = []
for i, (x, y) in enumerate(spots):
    L = image(f"End sticker {i}", 13.1 + i * 0.1, DUR, stk[(i * 3) % len(stk)], (x, y), (130, 110), 1)
    anim(L["id"], "scaleX", "return t<0.2?90*ob(t/0.2):90*(1+0.08*Math.exp(-((t/0.5)%1)*9));")
    anim(L["id"], "scaleY", "return t<0.2?90*ob(t/0.2):90*(1+0.08*Math.exp(-((t/0.5)%1)*9));")
    anim(L["id"], "rotation", f"return Math.sin(t*3+{i})*14;")
    end_stk.append(L)
sfx("slam", 13.0, 0.7); sfx("meow", 13.4, 0.6)

# ---------------------------------------------------------------- camera + layer order
ui_layers = [steal, nom, oops, rew, heart_n, heart, comment_n, comment, book_n, book, share, avatar, avatar_ring,
             handle, caption, sound, bar, bar_bg_l, bar_bg_r]
scene = ([err] + glitches + end_stk + [cta, hnd, logo, feed, face, hook, paw, eat, bean, luck] + ui_layers
         + [calm, dim, bg])
camera = group("CAMERA shake", 0, DUR, scene, (540, 960), (540, 960))
amp = ("var A=0; if(t>=2.3&&t<2.7) A=14*Math.exp(-(t-2.3)*8); if(t>=5.8&&t<6.4) A=40*Math.exp(-(t-5.8)*6);"
       "if(t>=7.85&&t<8.3) A=18*Math.exp(-(t-7.85)*8); if(t>=9.5&&t<11) A=26; if(t>=11&&t<11.6) A=30*Math.exp(-(t-11)*6);"
       "if(t>=13&&t<13.5) A=24*Math.exp(-(t-13)*7);")
anim(camera["id"], "positionX", amp + "return 540+(h(Math.floor(t*30))-0.5)*2*A;")
anim(camera["id"], "positionY", amp + "return 960+(h(Math.floor(t*30)+99)-0.5)*2*A;")
anim(camera["id"], "rotation", "return (t>=9.5&&t<11)?(h(Math.floor(t*12)+5)-0.5)*6:0;")
cs = "var s=100; if(t>=5.8) s+=8*Math.exp(-(t-5.8)*6); if(t>=11) s+=10*Math.exp(-(t-11)*6); if(t>=13) s+=8*Math.exp(-(t-13)*6);"
anim(camera["id"], "scaleX", cs + "return s;")
anim(camera["id"], "scaleY", cs + "return s;")
vign = adjust("Vignette", 0, DUR, [{"type": "vignette", "amount": 0.4, "radius": 0.85, "feather": 0.6}])

layers = [flash, vign, camera] + auds
doc = {"$schema": "https://jerboa.dev/schemas/fx-composition/editable/v1/document.schema.json", "formatVersion": 1,
       "dimensions": {"width": W, "height": H}, "duration": DUR, "backgroundColor": [0.035, 0, 0.07, 1],
       "composition": {"id": "main", "name": "Glitch invades the app", "layers": layers, "dynamics": {"entries": entries}}}
out = os.path.join(HERE, "editable.json")
json.dump(doc, open(out, "w"), indent=1)
run("project", "commit", "--project", PROJ, "--file", out)
os.remove(out)
print("built", PROJ, "animators:", len(entries))
