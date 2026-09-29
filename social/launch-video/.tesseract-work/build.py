#!/usr/bin/env python3
"""Builds WeirdCatsLaunch.tsrct: 24s vertical launch video for TikTok/Instagram.

120 BPM grid (beat = 0.5s). Beats:
  0.0-3.0  hook: phone buzzing with notifications, text types "TEM ALGO NO SEU CELULAR..."
  3.0      drop: flash, Glitch bursts out of the phone ("CHEGAMOS!")
  5/7/9    Lucky, Smoke, Beanie pop out, one per bar; all dance on the beat
  11-17    chaos: cat rain, hue strobe, phone feed doomscrolls ("O SEU FEED")
  17-19    glitch break ("ERRO: GATO NORMAL NÃO ENCONTRADO")
  19-24    end card: logo slam, cats line up, "AGORA NO TIKTOK / E NO INSTAGRAM / SEGUE A GENTE"
Re-run to rebuild the document from scratch; every layer stays editable in Tesseract.
"""
import json, os, subprocess, shutil, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(ROOT, '..', '..'))
SRC = os.path.join(HERE, 'src')
AUD = os.path.join(HERE, 'audio')
T = os.path.expanduser('~/.local/share/Tesseract/bin/tsrct')
PROJ = os.path.join(ROOT, 'WeirdCatsLaunch.tsrct')
W, H, DUR = 1080, 1920, 24.0
MS = lambda s: int(round(s * 1000))

# Optional GPT-generated replacements (drop files here and rebuild):
#   gpt/background.png  -> vertical neon room replaces the neon-room.mp4 background
#   gpt/phone.png       -> phone art (transparent PNG) replaces the native phone body
GPT = os.path.join(ROOT, 'gpt')


def run(*a):
    r = subprocess.run([T, *a], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"{' '.join(a)}\n{r.stdout}\n{r.stderr}")
    return r.stdout


# ---------------------------------------------------------------- JS helpers
LIB = ("var t=input.time.seconds;"
       "function cl(x){return Math.max(0,Math.min(1,x));}"
       "function eo(x){x=cl(x);return 1-Math.pow(1-x,3);}"
       "function ob(x){x=cl(x);var c1=2.2,c3=c1+1;return 1+c3*Math.pow(x-1,3)+c1*Math.pow(x-1,2);}"
       "function lerp(a,b,p){return a+(b-a)*p;}"
       "function h(n){var x=Math.sin(n*12.9898+78.233)*43758.5453;return x-Math.floor(x);}")

entries = []


def anim(layer_id, prop, body):
    entries.append({"target": {"kind": "layer", "layerId": layer_id, "propertyType": prop},
                    "animator": {"type": "jsScript", "layerTimeJsCode": LIB + body}})


_next = [1]


def nid():
    _next[0] += 1
    return _next[0]


def tf(pos=(0, 0), anchor=(0, 0), scale=100, rot=0, op=100):
    s = scale if isinstance(scale, (list, tuple)) else (scale, scale)
    return {"anchorPoint": list(anchor), "position": list(pos), "scale": list(s), "rotation": rot, "opacity": op}


def rng(start, end):
    return {"start": MS(start), "duration": MS(end - start)}


def rect(name, start, end, size, color, pos, anchor=None, round_=0, stroke=None, op=100):
    L = {"type": "Rect", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(start, end),
         "transform": tf(pos, anchor if anchor else (size[0] / 2, size[1] / 2), op=op),
         "rect": {"size": list(size), "fillColor": list(color), "roundness": round_}}
    if stroke:
        L["rect"].update(strokeEnabled=True, strokeColor=list(stroke[1]), strokeWidth=stroke[0])
    return L


def text(name, start, end, s, pos, size, font="PS", color=(1, 1, 1, 1), stroke=10, just="center", effects=None, glow=None):
    fam, sty = ("Press Start 2P", "Regular") if font == "PS" else ("Silkscreen", "Bold")
    L = {"type": "Text", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(start, end),
         "transform": tf(pos),
         "sourceText": {"text": s, "fontFamily": fam, "fontStyle": sty, "fontSize": size,
                        "fillColor": list(color), "strokeWidth": stroke, "strokeColor": [0.035, 0, 0.07, 1],
                        "applyStroke": stroke > 0, "strokeOverFill": False, "justification": just}}
    if effects:
        L["effects"] = effects
    if glow:
        L["layerStyles"] = [{"id": nid(), "style": {"type": "outerGlow", "enabled": True, "color": list(glow),
                                                    "size": max(18, size * 0.35), "spread": 8, "range": 50,
                                                    "blendMode": "screen"}}]
    return L


def image(name, start, end, asset, pos, anchor, scale=100, rot=0):
    return {"type": "Image", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(start, end),
            "transform": tf(pos, anchor, scale, rot), "source": {"assetId": asset, "fit": "contain"}}


def group(name, start, end, layers, pos=(0, 0), anchor=(0, 0), scale=100):
    return {"type": "Group", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(start, end),
            "transform": tf(pos, anchor, scale), "layers": layers}


def adjust(name, start, end, effects):
    return {"type": "Adjustment", "id": nid(), "name": name, "blendMode": "normal", "activeRange": rng(start, end),
            "transform": tf(), "effects": [{"id": nid(), "effect": e} for e in effects]}


def audio(name, asset, at, dur_s, vol):
    return {"type": "Audio", "id": nid(), "name": name, "source": {"assetId": asset},
            "activeRange": rng(at, min(DUR, at + dur_s)), "sourceRange": {"start": 0, "duration": MS(min(DUR, at + dur_s) - at)},
            "sourceIntrinsicDuration": MS(dur_s), "volume": vol, "captionsEnabled": False}


# ---------------------------------------------------------------- project + assets
if os.path.exists(PROJ):
    os.remove(PROJ)
run("project", "create", "--project", PROJ)
fonts = {}
for f in ("PressStart2P-Regular.ttf", "Silkscreen-Bold.ttf"):
    fonts[f] = json.loads(run("project", "import-font", "--project", PROJ, "--file", os.path.join(SRC, "fonts", f)))

frames = json.load(open(os.path.join(SRC, "frames_manifest.json")))
imported = set()


def img_asset(path):
    aid = "img-" + os.path.splitext(os.path.basename(path))[0].replace("_", "-")
    if aid not in imported:
        run("project", "import-asset", "--project", PROJ, "--file", path, "--asset-id", aid, "--kind", "image")
        imported.add(aid)
    return aid


gpt_bg = os.path.join(GPT, "background.png")
gpt_phone = os.path.join(GPT, "phone-open.png")
if not os.path.exists(gpt_bg):
    bgv = json.loads(run("project", "import-video", "--project", PROJ, "--file",
                         os.path.join(REPO, "assets/art/neon-room.mp4"), "--asset-id", "bg-neon-room"))
logo = img_asset(os.path.join(REPO, "assets/art/weird-cats-official-logo.png"))
AUDIO = {}
for n in ("buzz", "pop", "slam", "glitch", "meow", "whoosh", "impact", "riser"):
    run("project", "import-asset", "--project", PROJ, "--file", os.path.join(AUD, n + ".wav"),
        "--asset-id", "aud-" + n, "--kind", "audio")
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                          os.path.join(AUD, n + ".wav")], capture_output=True, text=True).stdout
    AUDIO[n] = float(out)

PINK = (1, 0.18, 0.6, 1)
CYAN = (0.25, 0.94, 1, 1)
YELLOW = (1, 0.89, 0.25, 1)
PURPLE = (0.1, 0.04, 0.18, 1)
WHITE = (1, 1, 1, 1)
BLACK = (0, 0, 0, 1)

top = []      # front-most first
bottom = []   # appended back-to-front at the end

# ---------------------------------------------------------------- background
bg_layers = []
if os.path.exists(gpt_bg):
    a = img_asset(gpt_bg)
    L = {"type": "Image", "id": nid(), "name": "BG GPT room", "blendMode": "normal", "activeRange": rng(0, DUR),
         "transform": tf((W / 2, H / 2), (W / 2, H / 2)), "source": {"assetId": a, "fit": "cover"}}
    bg_layers.append(L)
else:
    vd = bgv["durationMs"] / 1000.0
    t0 = 0.0
    while t0 < DUR - 1e-6:
        d = min(vd, DUR - t0)
        bg_layers.append({"type": "Video", "id": nid(), "name": f"BG neon room {t0:.0f}s", "blendMode": "normal",
                          "activeRange": rng(t0, t0 + d), "sourceRange": {"start": 0, "duration": MS(d)},
                          "sourceIntrinsicDuration": bgv["durationMs"], "volume": 0.0,
                          "transform": tf((W / 2, H / 2), (W / 2, H / 2)),
                          "source": {"assetId": "bg-neon-room", "fit": "cover"}})
        t0 += d
for L in bg_layers:
    L["effects"] = [{"id": nid(), "effect": {"type": "gaussianBlur", "blurriness": 2.5 if os.path.exists(gpt_bg) else 6, "repeatEdgePixels": True}}]
    start = L["activeRange"]["start"] / 1000
    # slow push-in over the whole video, continuous across the looped clips
    anim(L["id"], "scaleX", f"var g=t+{start}; return 112+g*0.5;")
    anim(L["id"], "scaleY", f"var g=t+{start}; return 112+g*0.5;")

dim = rect("BG dim", 0, DUR, (W, H), (0.05, 0.0, 0.1, 1), (W / 2, H / 2))
anim(dim["id"], "opacity", "if(t<3) return 62; if(t<3.3) return lerp(62,30,eo((t-3)/0.3)); if(t<19) return 30; return lerp(30,55,eo((t-19)/0.5));")

# hue strobe on the background during the chaos section (one window per beat)
hues = [0, 70, 160, 250]
strobe = []
for i in range(12):
    s = 11.0 + i * 0.5
    hv = hues[i % 4]
    if hv:
        strobe.append(adjust(f"BG hue strobe {s:.1f}s", s, s + 0.5,
                             [{"type": "hueSaturation", "hue": hv, "saturation": 20, "lightness": 0}]))

# ---------------------------------------------------------------- phone
PC = (540, 1000)             # phone center in canvas coords (group-local == canvas)
PW, PH = 620, 1180
SW, SH = 556, 1100           # screen
SX0, SY0 = PC[0] - SW / 2, PC[1] - SH / 2 + 10
phone_children = []

# notch + stickers (front)
notch = rect("Phone notch", 0, DUR, (170, 36), (0.16, 0.1, 0.24, 1), (PC[0], SY0 + 34), round_=18)
st1 = rect("Sticker cyan", 0, DUR, (34, 34), CYAN, (PC[0] + PW / 2 - 40, PC[1] - PH / 2 + 40), round_=0, stroke=(5, BLACK))
st2 = rect("Sticker yellow", 0, DUR, (26, 26), YELLOW, (PC[0] - PW / 2 + 38, PC[1] + PH / 2 - 60), stroke=(5, BLACK))
st1["transform"]["rotation"] = 45
phone_children += [notch, st1, st2]

# screen content (masked by the screen matte)
scr = []
# lock screen 0-3s
lock_bg = rect("Lock screen", 0, 3.0, (SW, SH), (0.14, 0.05, 0.26, 1), (PC[0], SY0 + SH / 2))
clock = text("Lock clock", 0, 3.0, "23:59", (PC[0], SY0 + 190), 64, color=WHITE, stroke=0)
anim(clock["id"], "textContent", "return t<2.6?'23:59':(h(Math.floor(t*20))>0.5?'??:??':'00:00');")
notifs = []
msgs = [(0.55, "incoming signal..."), (1.45, "psst. look up"), (2.15, "MEOW MEOW MEOW")]
for i, (at, body) in enumerate(msgs):
    y = SY0 + 330 + i * 172
    card = rect("Notif card", 0, SH, (520, 150), (0.1, 0.04, 0.18, 0.97), (PC[0], y), round_=26, stroke=(4, PINK))
    icon = image("Notif icon", 0, 3.0, img_asset(frames["glitch"][0]), (PC[0] - 196, y + 58), (384, 832), 13)
    ttl = text("Notif title", 0, 3.0, "WEIRD CATS", (PC[0] - 132, y - 16), 26, color=PINK, stroke=0, just="left")
    bod = text("Notif body", 0, 3.0, body, (PC[0] - 132, y + 40), 38, font="SK", color=WHITE, stroke=0, just="left")
    for L in (card, icon, ttl, bod):
        L["activeRange"] = rng(0, 3.0 - at)
    g = group(f"Notification {i + 1}", at, 3.0, [bod, ttl, icon, card], (0, 0))
    anim(g["id"], "positionX", "return lerp(620,0,ob(t/0.35));")
    notifs.append(g)
# Glitch's eye peeking from the bottom of the screen
peek = image("Peek Glitch", 1.9, 3.0, img_asset(frames["glitch"][0]), (PC[0], SY0 + SH + 420), (384, 416), 95)
anim(peek["id"], "positionY", f"return {SY0 + SH + 420}-eo(t/0.9)*300 + Math.sin(t*40)*4;")
# feed 3-19s: doomscroll cards
feed_cards = []
rain_files = sorted(glob.glob(os.path.join(SRC, "rain4x", "*.png")))
card_cols = [PINK, CYAN, YELLOW, (0.62, 0.36, 1, 1)]
N, GAP = 8, 450
for k in range(N * 2):
    y = SY0 + 280 + k * GAP
    c = rect("Feed card", 0, 16.0, (480, 410), (0.09, 0.03, 0.17, 1), (PC[0], y), round_=28, stroke=(6, card_cols[k % 4]))
    im = image("Feed cat", 0, 16.0, img_asset(rain_files[(k * 3) % len(rain_files)]), (PC[0], y + 190), (384, 832), 44)
    feed_cards += [im, c]
feed = group("Feed scroll", 3.0, 19.0, feed_cards)
anim(feed["id"], "positionY",
     f"var g=t+3; var d=500*Math.min(g-3,8)+1500*Math.max(0,Math.min(g-11,6)); return -(d%{N * GAP});")
feed_bg = rect("Feed bg", 3.0, 19.0, (SW, SH), (0.035, 0, 0.07, 1), (PC[0], SY0 + SH / 2))
portal_l = []
if os.path.exists(os.path.join(GPT, "portal.png")):
    pl = image("Portal", 2.3, 3.4, img_asset(os.path.join(GPT, "portal.png")), (PC[0], SY0 + SH / 2), (540, 960), 1)
    anim(pl["id"], "scaleX", "return 1+80*eo(t/0.7);")
    anim(pl["id"], "scaleY", "return 1+80*eo(t/0.7);")
    anim(pl["id"], "rotation", "return -t*540;")
    portal_l.append(pl)
scr = portal_l + [peek] + notifs + [clock, lock_bg, feed, feed_bg]
screen_group = group("Screen content", 0, 19.5, scr)
matte = rect("Screen matte", 0, 19.5, (SW, SH), WHITE, (PC[0], SY0 + SH / 2), round_=60)
screen_group["trackMatte"] = {"layer": matte["id"], "mode": "alpha"}
screen_black = rect("Screen", 0, 19.5, (SW, SH), BLACK, (PC[0], SY0 + SH / 2), round_=60)
phone_children += [screen_group, matte, screen_black]

if os.path.exists(gpt_phone):
    from PIL import Image as _I
    iw, ih = _I.open(gpt_phone).size
    # user-generated art (transparent PNG): centered on the phone, scaled so its height covers the phone body
    # screen hole in phone-open.png is x220-861, y319-1572: map it onto the matte (SW x SH at screen centre)
    body = image("Phone body GPT", 0, 19.5, img_asset(gpt_phone), (PC[0], SY0 + SH / 2), (540.5, 945.5), 87)
    phone_children[:] = [c for c in phone_children if c["name"] not in ("Phone notch", "Sticker cyan", "Sticker yellow")]
    cracked = os.path.join(GPT, "phone-cracked.png")
    if os.path.exists(cracked):
        ck = image("Phone CRACKED", 2.85, 3.6, img_asset(cracked), (PC[0], SY0 + SH / 2), (540.5, 945.5), 87)
        anim(ck["id"], "opacity", "return t<0.55?100:100*(1-(t-0.55)/0.2);")
        phone_children.insert(0, ck)
else:
    body = rect("Phone body", 0, 19.5, (PW, PH), (0.043, 0.024, 0.094, 1), PC, round_=86, stroke=(16, PINK))
    btn1 = rect("Phone button", 0, 19.5, (16, 120), PINK, (PC[0] + PW / 2 + 6, PC[1] - 300), round_=6)
    btn2 = rect("Phone button", 0, 19.5, (16, 80), PINK, (PC[0] - PW / 2 - 6, PC[1] - 360), round_=6)
    phone_children += [btn1, btn2]
if os.path.exists(gpt_phone):
    phone_children.insert(1 if phone_children and phone_children[0]["name"] == "Phone CRACKED" else 0, body)
else:
    phone_children.append(body)
phone_glow = {"type": "Rect", **rect("Phone glow", 0, 19.5, (PW + 40, PH + 40), PINK, PC, round_=100)}
phone_glow["effects"] = [{"id": nid(), "effect": {"type": "gaussianBlur", "blurriness": 60}}]
anim(phone_glow["id"], "opacity", "var p=(t/0.5)%1; return t<3?35:45+35*Math.exp(-p*6);")
phone_children.append(phone_glow)
phone = group("PHONE", 0, 19.5, phone_children, PC, PC)
BUZZ = [0.55, 1.45, 2.15]
buzz_js = "var j=0;" + "".join(
    f"if((t>={b}&&t<{b + 0.32})||(t>={b + 0.45}&&t<{b + 0.77})) j=1;" for b in BUZZ)
anim(phone["id"], "rotation", buzz_js +
     "if(t<3) return j*4*Math.sin(t*2*Math.PI*24) + (t>2.6?(t-2.6)*25*Math.sin(t*2*Math.PI*31):0);"
     "if(t<19) return 0; return 720*eo((t-19)/0.45);")
anim(phone["id"], "positionX", buzz_js +
     "if(t<3) return 540 + j*10*Math.sin(t*2*Math.PI*27) + (t>2.6?(t-2.6)*40*Math.sin(t*2*Math.PI*37):0); return 540;")
anim(phone["id"], "positionY", "if(t<3) return 1000; return lerp(1000,1180,eo((t-3)/0.5));")
phone_scale = ("var s; if(t<0.35) s=100*ob(t/0.35); else if(t<2.6) s=100; else if(t<3) s=100+10*(t-2.6)/0.4;"
               "else if(t<3.5) s=lerp(110,74,eo((t-3)/0.5)); else if(t<19){var p=(t/0.5)%1; s=74*(1+0.025*Math.exp(-p*9));}"
               "else s=74*(1-eo((t-19)/0.45));")
anim(phone["id"], "scaleX", phone_scale + "var q=t>=3&&t<19?Math.exp(-(t-3)*14)*0.28:0; return s*(1+q);")
anim(phone["id"], "scaleY", phone_scale + "var q=t>=3&&t<19?Math.exp(-(t-3)*14)*0.28:0; return s*(1-q);")

# ---------------------------------------------------------------- main cats
CATS = [  # name, pop time, dance spot (feet), finale spot
    ("glitch", 3.0, (290, 880), (170, 1790)),
    ("lucky", 5.0, (800, 880), (410, 1790)),
    ("smoke", 7.0, (200, 1720), (670, 1790)),
    ("beanie", 9.0, (860, 1720), (910, 1790)),
]
NAMES = {"glitch": "GLITCH", "lucky": "LUCKY", "smoke": "SMOKE", "beanie": "BEANIE"}
cat_groups = []
for name, S, (X, Y), (FX, FY) in CATS:
    kids = []
    tag = text(f"{NAMES[name]} tag", 0.35, 19.0 - S, NAMES[name], (0, 130), 84, color=(1, 0.97, 1, 1), stroke=6, glow=PINK)
    kids.append(tag)
    for k, path in enumerate(frames[name]):
        L = image(f"{name} frame {k}", 0, DUR - S, img_asset(path), (0, 0), (384, 832), 100)
        anim(L["id"], "opacity",
             f"var g=t+{S}; var idx; if(t<0.45) idx=0; else if(g>=22.9) idx=8;"
             f"else if(g>=17&&g<19) idx=Math.floor(h(Math.floor(g*12)+{S})*8);"
             f"else idx=Math.floor(g/0.25)%8; return idx=={k}?100:0;")
        kids.append(L)
    g = group(f"CAT {NAMES[name]}", S, DUR, kids)
    B, FB = 52, 38
    hop = ("var g=t+" + str(S) + "; var b=g/0.5; var p=b-Math.floor(b);"
           "var amp=(g>=11&&g<17)?95:45; if(g>=19) amp=30;")
    anim(g["id"], "positionX",
         f"var g=t+{S}; if(t<0.45) return lerp(540,{X},eo(t/0.45));"
         f"if(g<11) return {X}; if(g<17) return {X}+Math.sin(g*Math.PI*2)*30;"
         f"if(g<19) return {X}+(h(Math.floor(g*12)+{S})-0.5)*90;"
         f"return lerp({X},{FX},eo((g-19)/0.45));")
    anim(g["id"], "positionY", hop +
         f"if(t<0.45){{var q=t/0.45; return lerp(1150,{Y},q)-600*4*q*(1-q);}}"
         f"var base=g<19?{Y}:lerp({Y},{FY},eo((g-19)/0.45));"
         "var j=(g>=22.9&&g<23.5)?260*Math.sin(Math.PI*(g-22.9)/0.6):0;"
         "if(g>=17&&g<19) return base;"
         "return base-amp*4*p*(1-p)-j;")
    sc = hop + (f"var s; if(t<0.45) s=lerp(6,{B},ob(t/0.45)); else if(g<19) s={B}; else s=lerp({B},{FB},eo((g-19)/0.45));"
                "if(g>=17&&g<19) s=s*(0.8+0.45*h(Math.floor(g*12)+3));"
                "var sq=t<0.45?0:Math.exp(-p*12);")
    anim(g["id"], "scaleX", sc + "return s*(1+0.10*sq);")
    anim(g["id"], "scaleY", sc + "return s*(1-0.14*sq);")
    anim(g["id"], "rotation", hop +
         "if(t<0.45) return 540*(1-eo(t/0.45));"
         "var dir=(Math.floor(b)%2==0)?1:-1; var R=(g>=11&&g<17)?20:9;"
         "if(g>=17&&g<19) return (h(Math.floor(g*12)+7)-0.5)*40;"
         "return dir*R*Math.sin(Math.PI*p);")
    cat_groups.append(g)
cat_groups.reverse()  # later pops in front

# ---------------------------------------------------------------- cat rain (11-17s)
rain = []
for i in range(34):
    f = rain_files[i % len(rain_files)]
    st = 10.9 + (i * 0.173) % 5.6
    dur = 1.5 + ((i * 7) % 5) * 0.18
    x = 80 + ((i * 263) % 920)
    sc = 26 + (i * 11) % 18
    spin = ((i * 97) % 500) - 250
    L = image(f"Rain {os.path.basename(f)[:-4]}", st, min(17.0, st + dur), img_asset(f), (x, -300), (384, 416), sc)
    anim(L["id"], "positionY", f"return lerp(-320,2300,t/{dur});")
    anim(L["id"], "positionX", f"return {x}+Math.sin(t*5+{i})*60;")
    anim(L["id"], "rotation", f"return t*{spin};")
    rain.append(L)

# ---------------------------------------------------------------- headlines
HL_Y = 270
heads = []
typ = text("Hook type-on", 0.25, 3.0, "SOMETHING'S IN\nYOUR PHONE...", (90, 250), 72, font="SK", stroke=6, just="left", glow=CYAN)
anim(typ["id"], "textContent",
     "var s='SOMETHING\\'S IN\\nYOUR PHONE...'; var n=Math.floor(t*14); return s.substring(0,Math.min(n,s.length));")
heads.append(typ)


def slam(label, s, start, end, size=96, font="PS", color=WHITE, y=HL_Y, ca=True):
    L = text(label, start, end, s, (540, y), size, font=font, color=color, stroke=7, glow=color,
             effects=[{"id": nid(), "effect": {"type": "chromaticAberration", "amount": 0.25, "direction": 0}}] if ca else None)
    anim(L["id"], "scaleX", "if(t<0.16) return lerp(190,100,eo(t/0.16)); var p=((t)/0.5)%1; return 100+5*Math.exp(-p*9);")
    anim(L["id"], "scaleY", "if(t<0.16) return lerp(190,100,eo(t/0.16)); var p=((t)/0.5)%1; return 100+5*Math.exp(-p*9);")
    anim(L["id"], "rotation", "if(t<0.16) return lerp(-10,0,eo(t/0.16)); return Math.sin(t*6)*2;")
    return L


heads.append(slam("WE'RE OUT.", "WE'RE OUT.", 3.0, 5.0, 90, color=PINK))
heads.append(slam("THE WEIRD CATS", "THE WEIRD\nCATS", 5.0, 7.0, 92, color=(1, 0.97, 1, 1)))
heads.append(slam("ESCAPED. OBVIOUSLY.", "ESCAPED.\nOBVIOUSLY.", 7.0, 9.0, 100, font="SK", color=CYAN))
heads.append(slam("AND WE'RE NOT LEAVING", "AND WE'RE\nNOT LEAVING", 9.0, 11.0, 78, color=YELLOW))
feed_t = slam("LIVING IN YOUR FEED", "LIVING IN\nYOUR FEED", 11.0, 17.0, 90, color=PINK)
anim(feed_t["id"], "positionY", "return 270+Math.sin(t*Math.PI*4)*18;")
heads.append(feed_t)
err = text("Glitch error", 17.0, 19.0, "ERROR: NORMAL CAT\nNOT FOUND", (540, 900), 62, font="SK",
           color=(1, 0.3, 0.4, 1), stroke=8, glow=(1, 0.1, 0.3, 1))
anim(err["id"], "positionX", "return 540+(h(Math.floor(t*14))-0.5)*70;")
anim(err["id"], "opacity", "return h(Math.floor(t*16)+5)>0.18?100:0;")

# ---------------------------------------------------------------- end card
logoL = image("LOGO", 19.0, DUR, logo, (540, 600), (768, 512), 64)
anim(logoL["id"], "scaleX", "if(t<0.3) return lerp(260,64,ob(t/0.3)); var p=((t+19)/0.5)%1; return 64*(1+0.035*Math.exp(-p*9));")
anim(logoL["id"], "scaleY", "if(t<0.3) return lerp(260,64,ob(t/0.3)); var p=((t+19)/0.5)%1; return 64*(1+0.035*Math.exp(-p*9));")
anim(logoL["id"], "rotation", "if(t<0.3) return lerp(-25,0,eo(t/0.3)); return Math.sin(t*3)*2.5;")
def logo_line(label, start, parts, y):
    # parts: text or ("logo", key); monospace 52px advance per char, 18px gaps around 100px icons
    kids, x = [], 0
    widths = [len(p) * 52 if isinstance(p, str) else 100 for p in parts]
    total = sum(widths) + 18 * (len(parts) - 1)
    x = 540 - total / 2
    for p, w_ in zip(parts, widths):
        if isinstance(p, str):
            kids.append(text(f"{label} '{p}'", 0, DUR - start, p, (x, y), 52, color=CYAN, stroke=6, glow=CYAN, just="left"))
        elif os.path.exists(os.path.join(GPT, p[1] + ".png")):
            ic = image(f"{label} icon", 0, DUR - start, img_asset(os.path.join(GPT, p[1] + ".png")), (x + 50, y - 22), (540, 540), 9.5)
            anim(ic["id"], "rotation", f"var b=(t+{start})/0.5; return Math.sin(b*Math.PI)*10;")
            anim(ic["id"], "scaleX", f"var b=(t+{start})/0.5; var p=b-Math.floor(b); return 9.5*(1+0.15*Math.exp(-p*10));")
            anim(ic["id"], "scaleY", f"var b=(t+{start})/0.5; var p=b-Math.floor(b); return 9.5*(1+0.15*Math.exp(-p*10));")
            kids.append(ic)
        x += w_ + 18
    g = group(label, start, DUR, kids)
    anim(g["id"], "positionX", "return lerp(900,0,ob(t/0.3));")
    return g


end1 = logo_line("NOW ON TIKTOK", 19.45, ["NOW ON", ("logo", "logo-tiktok"), "TIKTOK"], 1060)
end2 = logo_line("+ INSTAGRAM", 19.7, ["+", ("logo", "logo-instagram"), "INSTAGRAM"], 1175)
pill_txt = text("FOLLOW US", 0, DUR - 20.0, "FOLLOW US", (0, 22), 56, color=(1, 0.97, 1, 1), stroke=0, glow=PINK)
pill_bg = rect("CTA pill", 0, DUR - 20.0, (760, 130), (0.07, 0.02, 0.13, 0.92), (0, 0), round_=65, stroke=(8, PINK))
pill = group("CTA", 20.0, DUR, [pill_txt, pill_bg], (540, 1335))
anim(pill["id"], "scaleX", "if(t<0.25) return 100*ob(t/0.25); var p=((t+20)/0.5)%1; return 100+7*Math.exp(-p*9);")
anim(pill["id"], "scaleY", "if(t<0.25) return 100*ob(t/0.25); var p=((t+20)/0.5)%1; return 100+7*Math.exp(-p*9);")
anim(pill["id"], "rotation", "return Math.sin(t*Math.PI*2)*3;")
coin = text("NORMAL CATS NOT ALLOWED.", 20.5, DUR, "NORMAL CATS NOT ALLOWED.", (540, 1465), 38, font="SK", color=(1, 0.66, 0.87, 1), stroke=0, glow=PINK)
anim(coin["id"], "opacity", "return eo(t/0.3)*100*(h(Math.floor(t*10))>0.08?1:0.3);")

# ---------------------------------------------------------------- GPT hero shots (skipped if a file is missing)
heroes = []
hero_sfx = []
GPTF = {k: os.path.join(GPT, f"{k}.png") for k in ("cat-glitch-jump", "cat-beanie-jump", "cat-beanie-dance", "cat-giant-face", "cat-lucky-jump", "cat-lucky-dance", "cat-smoke-jump", "cat-smoke-dance", "cat-paw", "meow-burst", "signal-frame", "logo-tiktok", "logo-instagram")}
have = {k: os.path.exists(v) for k, v in GPTF.items()}


def leap(label, key, start, dur=0.36):
    # character bursts out of the phone and flies through the camera, landing on the drop
    L = image(label, start, start + dur, img_asset(GPTF[key]), (540, 1060), (540, 960), 10)
    anim(L["id"], "scaleX", f"var q=cl(t/{dur}); return 10+330*q*q*q;")
    anim(L["id"], "scaleY", f"var q=cl(t/{dur}); return 10+330*q*q*q;")
    anim(L["id"], "rotation", f"return lerp(-40,12,eo(t/{dur}));")
    anim(L["id"], "positionY", f"return lerp(1060,860,eo(t/{dur}));")
    return L


if have["cat-glitch-jump"]:
    heroes.append(leap("LEAP Glitch", "cat-glitch-jump", 2.66))
    hero_sfx.append((2.62, "whoosh", 0.7))
for key, at in (("cat-lucky-jump", 4.66), ("cat-smoke-jump", 6.66)):
    if have[key]:
        heroes.append(leap("LEAP " + key[4:-5].title(), key, at))
        hero_sfx.append((at - 0.04, "whoosh", 0.6))
if have["cat-beanie-jump"]:
    heroes.append(leap("LEAP Beanie", "cat-beanie-jump", 8.66))
    hero_sfx.append((8.62, "whoosh", 0.7))
if have["cat-giant-face"]:
    face = image("GIANT FACE slam", 11.0, 11.8, img_asset(GPTF["cat-giant-face"]), (540, 980), (540, 960), 120)
    face["effects"] = [{"id": nid(), "effect": {"type": "chromaticAberration", "amount": 0.2, "direction": 0}}]
    fs = "var s; if(t<0.14) s=lerp(240,92,eo(t/0.14)); else if(t<0.5) s=92+4*Math.sin(t*60); else s=92+900*Math.pow((t-0.5)/0.3,2); "
    anim(face["id"], "scaleX", fs + "return s;")
    anim(face["id"], "scaleY", fs + "return s;")
    anim(face["id"], "rotation", "return t<0.5?(h(Math.floor(t*30))-0.5)*8:lerp(0,25,(t-0.5)/0.3);")
    anim(face["id"], "opacity", "return t<0.55?100:100*(1-cl((t-0.55)/0.25));")
    heroes.append(face)
    hero_sfx.append((11.0, "impact", 0.9))
    for s0 in (17.5, 18.33):
        f2 = image(f"GIANT FACE glitch {s0}", s0, s0 + 0.17, img_asset(GPTF["cat-giant-face"]), (540, 960), (540, 960), 135)
        f2["effects"] = [{"id": nid(), "effect": {"type": "shiftChannels", "takeRedFrom": "green", "takeGreenFrom": "blue", "takeBlueFrom": "red"}}]
        heroes.append(f2)
# chaos hero: characters swap on every beat, 13-17s
cycle = [k for k in ("cat-beanie-dance", "cat-lucky-jump", "cat-smoke-dance", "cat-glitch-jump", "cat-lucky-dance", "cat-beanie-jump", "cat-smoke-jump", "cat-glitch-jump") if have[k]]
hero_dance = []
if cycle:
    for i in range(8):
        s0 = 13.0 + i * 0.5
        k = cycle[i % len(cycle)]
        L = image(f"HERO {k} {s0}", s0, s0 + 0.5, img_asset(GPTF[k]), (540, 1480), (540, 1500), 64)
        flip = -1 if i % 2 else 1
        anim(L["id"], "scaleX", f"var sq=Math.exp(-t*14); return {flip}*64*(1+0.12*sq);")
        anim(L["id"], "scaleY", "var sq=Math.exp(-t*14); return 64*(1-0.16*sq);")
        anim(L["id"], "positionY", "var p=t/0.5; return 1480-110*4*p*(1-p);")
        anim(L["id"], "rotation", f"return {flip}*14*Math.sin(Math.PI*t/0.5);")
        hero_dance.append(L)
    # the sprite Beanie steps aside while the big one dances
    for g in cat_groups:
        if g["name"] == "CAT BEANIE":
            anim(g["id"], "opacity", "var g=t+9; return (g>=13&&g<17)?0:100;")
hero_dance.reverse()

# paw swipes over everything into the end card; MEOW! burst lands on the final meow
if have["cat-paw"]:
    paw = image("PAW wipe", 18.55, 19.12, img_asset(GPTF["cat-paw"]), (540, 2900), (540, 960), 175)
    anim(paw["id"], "positionY", "return lerp(2900,1050,eo(t/0.38));")
    anim(paw["id"], "rotation", "return lerp(12,-4,eo(t/0.38));")
    heroes.insert(0, paw)
    hero_sfx.append((18.5, "whoosh", 0.8))
meow_l = []
if have["meow-burst"]:
    mb = image("MEOW burst", 22.88, DUR, img_asset(GPTF["meow-burst"]), (540, 880), (540, 960), 1)
    ms = "var s=t<0.22?85*ob(t/0.22):85*(1+0.05*Math.sin(t*25)*Math.exp(-(t-0.22)*3));"
    anim(mb["id"], "scaleX", ms + "return s;")
    anim(mb["id"], "scaleY", ms + "return s;")
    anim(mb["id"], "rotation", "return t<0.22?lerp(-30,-6,t/0.22):-6+Math.sin(t*20)*3*Math.exp(-t*2);")
    meow_l.append(mb)
# signal HUD frame over the hook and the glitch break
hud = []
if have["signal-frame"]:
    for a0, a1 in ((0, 3.0), (17.0, 19.0)):
        f = image(f"Signal frame {a0}", a0, a1, img_asset(GPTF["signal-frame"]), (540, 960), (540, 960), 100)
        anim(f["id"], "opacity", "return 70+30*(h(Math.floor(t*8))>0.2?1:0);")
        hud.append(f)
# stickers pop on the beat around the edges (5-11s) and fall with the rain (11-17s)
stk_files = sorted(glob.glob(os.path.join(GPT, "stickers", "*.png")))
stickers = []
spots = [(130, 560), (950, 600), (120, 1260), (960, 1300), (180, 470), (900, 1450), (140, 1500), (940, 460)]
for i in range(12) if stk_files else []:
    at = 5.0 + i * 0.5
    x, y = spots[i % len(spots)]
    L = image(f"Sticker pop {at}", at, at + 0.5, img_asset(stk_files[i % len(stk_files)]), (x, y), (130, 110), 1)
    anim(L["id"], "scaleX", "return t<0.12?95*ob(t/0.12):95*(1-eo((t-0.35)/0.15));")
    anim(L["id"], "scaleY", "return t<0.12?95*ob(t/0.12):95*(1-eo((t-0.35)/0.15));")
    anim(L["id"], "rotation", f"return {(-1) ** i * 14}+t*{(-1) ** i * 40};")
    stickers.append(L)
for i in range(14) if stk_files else []:
    st = 11.2 + (i * 0.41) % 5.4
    x = 90 + ((i * 331) % 900)
    L = image(f"Sticker rain {i}", st, min(17.0, st + 1.6), img_asset(stk_files[(i * 3) % len(stk_files)]), (x, -200), (130, 110), 110)
    anim(L["id"], "positionY", "return lerp(-200,2200,t/1.6);")
    anim(L["id"], "rotation", f"return t*{((i * 83) % 400) - 200};")
    stickers.append(L)
# platform logos bounce with the cats in the chaos section
plat = []
for key, x, ph in (("logo-tiktok", 175, 0), ("logo-instagram", 905, 1)):
    if have[key]:
        L = image(key.upper(), 11.8, 17.0, img_asset(GPTF[key]), (x, 1300), (540, 540), 32)
        anim(L["id"], "positionY", f"var g=t+11.8; var b=g/0.5+{ph * 0.5}; var p=b-Math.floor(b); return 1300-120*4*p*(1-p);")
        anim(L["id"], "scaleX", f"var g=t+11.8; var b=g/0.5+{ph * 0.5}; var p=b-Math.floor(b); var s=t<0.2?32*ob(t/0.2):32; return s*(1+0.12*Math.exp(-p*12));")
        anim(L["id"], "scaleY", f"var g=t+11.8; var b=g/0.5+{ph * 0.5}; var p=b-Math.floor(b); var s=t<0.2?32*ob(t/0.2):32; return s*(1-0.16*Math.exp(-p*12));")
        anim(L["id"], "rotation", f"var g=t+11.8; return Math.sin(g*Math.PI*2+{ph * 3.14})*16;")
        plat.append(L)

# ---------------------------------------------------------------- flashes + glitch adjustments + vignette
flash1 = rect("Flash drop", 3.0, 3.35, (W, H), WHITE, (W / 2, H / 2))
flash3 = rect("Flash beanie", 9.0, 9.25, (W, H), CYAN, (W / 2, H / 2))
anim(flash3["id"], "opacity", "return 70*(1-eo(t/0.25));")
flash4 = rect("Flash face", 11.0, 11.12, (W, H), PINK, (W / 2, H / 2))
anim(flash4["id"], "opacity", "return 80*(1-t/0.12);")
anim(flash1["id"], "opacity", "return 100*(1-eo(t/0.35));")
flash2 = rect("Flash end", 19.0, 19.35, (W, H), PINK, (W / 2, H / 2))
anim(flash2["id"], "opacity", "return 90*(1-eo(t/0.35));")
GA = [{"type": "mosaic", "horizontalBlocks": 72, "verticalBlocks": 128, "sharpColors": True},
      {"type": "chromaticAberration", "amount": 0.35, "direction": 0}]
GB = [{"type": "shiftChannels", "takeRedFrom": "blue", "takeGreenFrom": "green", "takeBlueFrom": "red"},
      {"type": "chromaticAberration", "amount": 0.45, "direction": 90}]
glitch_adj = [adjust("Glitch hit pre-drop", 2.82, 3.0, GB), adjust("Glitch hit pre-end", 18.85, 19.0, GA)]
pattern = "ABxAxBABxxAB"
for i, c in enumerate(pattern):
    s = 17.0 + i * (2.0 / len(pattern))
    if c != "x":
        glitch_adj.append(adjust(f"Glitch break {c} {s:.2f}s", s, s + 2.0 / len(pattern), GA if c == "A" else GB))
vign = adjust("Vignette", 0, DUR, [{"type": "vignette", "amount": 0.45, "radius": 0.85, "feather": 0.6}])

# ---------------------------------------------------------------- audio
M = AUDIO
auds = []  # music comes from a trending Reels/TikTok track added in-app
for b in BUZZ:
    auds.append(audio(f"SFX buzz {b}", "aud-buzz", b, M["buzz"], 0.55))
auds.append(audio("SFX slam drop", "aud-slam", 3.0, M["slam"], 0.6))
for _, S, _, _ in CATS[1:]:
    auds.append(audio(f"SFX pop {S}", "aud-pop", S, M["pop"], 0.45))
auds.append(audio("SFX glitch 17", "aud-glitch", 17.0, M["glitch"], 0.5))
auds.append(audio("SFX glitch 18", "aud-glitch", 18.0, M["glitch"], 0.5))
auds.append(audio("SFX slam end", "aud-slam", 19.0, M["slam"], 0.6))
auds.append(audio("SFX meow", "aud-meow", 22.9, M["meow"], 0.6))
auds.append(audio("SFX riser into chaos", "aud-riser", 9.95, M["riser"], 0.6))
for at, k, v in hero_sfx:
    auds.append(audio(f"SFX {k} {at}", "aud-" + k, at, M[k], v))

scene = (hud + [err] + glitch_adj + meow_l + heroes + heads + [end1, end2, pill, coin] + hero_dance + plat + stickers
         + cat_groups + [logoL] + rain + [phone] + strobe + [dim] + bg_layers)
camera = group("CAMERA shake", 0, DUR, scene, (W / 2, H / 2), (W / 2, H / 2))
# beat punches everywhere, big hits on the drops, heavy shake in the chaos and glitch sections
cam_amp = ("var b=t/0.5; var p=b-Math.floor(b); var A=0;"
           "if(t>=3&&t<3.5) A=40*Math.exp(-(t-3)*7); if(t>=9&&t<9.4) A=28*Math.exp(-(t-9)*8);"
           "if(t>=11&&t<17) A=12+36*Math.exp(-(t-11)*5); if(t>=17&&t<19) A=26; if(t>=19&&t<19.5) A=30*Math.exp(-(t-19)*7);")
anim(camera["id"], "positionX", cam_amp + "return 540+(h(Math.floor(t*30))-0.5)*2*A;")
anim(camera["id"], "positionY", cam_amp + "return 960+(h(Math.floor(t*30)+99)-0.5)*2*A;")
anim(camera["id"], "rotation", "if(t>=11&&t<17) return Math.sin(t*Math.PI*2)*2.5+(h(Math.floor(t*15))-0.5)*3;"
                               "if(t>=17&&t<19) return (h(Math.floor(t*12)+5)-0.5)*8; return 0;")
cam_scale = ("var b=t/0.5; var p=b-Math.floor(b); var k=t<3?0:((t>=11&&t<17)?7:3.5);"
             "var s=100+k*Math.exp(-p*10);"
             "if(t>=3) s+=14*Math.exp(-(t-3)*6); if(t>=11) s+=18*Math.exp(-(t-11)*6); if(t>=19) s+=10*Math.exp(-(t-19)*6);"
             "if(t<3) s+=t*1.2;")
anim(camera["id"], "scaleX", cam_scale + "return s;")
anim(camera["id"], "scaleY", cam_scale + "return s;")
layers = [flash1, flash2, flash3, flash4, vign, camera] + auds
doc = {"$schema": "https://jerboa.dev/schemas/fx-composition/editable/v1/document.schema.json",
       "formatVersion": 1, "dimensions": {"width": W, "height": H}, "duration": DUR,
       "backgroundColor": list(PURPLE),
       "composition": {"id": "main", "name": "Weird Cats launch", "layers": layers,
                       "dynamics": {"entries": entries}}}
os.makedirs(os.path.join(HERE), exist_ok=True)
out = os.path.join(HERE, "editable.json")
json.dump(doc, open(out, "w"), indent=1, ensure_ascii=False)
run("project", "commit", "--project", PROJ, "--file", out)
print("built", PROJ, "layers:", len(layers), "animators:", len(entries))
