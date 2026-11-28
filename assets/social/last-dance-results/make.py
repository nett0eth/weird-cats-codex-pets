# Last Dance results GIF (13 free mints). Run: python3 make.py FRAMEDIR
import random, functools, os, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
S='/tmp/claude-0/-home-user/ac119dfd-46c1-54de-9b3e-75a19c397be6/scratchpad/ldres'
REPO='/home/user/weird-cats-codex-pets'
W=720; FPS=12; OUT=sys.argv[1]; os.makedirs(OUT,exist_ok=True)
BG0=Image.open('/mnt/project-files/last-dance/abertura/S13PLATE.jpg').convert('RGB')
s=min(BG0.size); BG0=BG0.crop(((BG0.width-s)//2,(BG0.height-s)//2,(BG0.width+s)//2,(BG0.height+s)//2)).resize((W,W),Image.LANCZOS)
BGD=ImageEnhance.Brightness(BG0).enhance(0.38).convert('RGBA')
BGL=ImageEnhance.Brightness(BG0).enhance(0.6).convert('RGBA')
def PF(sz): return ImageFont.truetype(f'{S}/PressStart2P.ttf',sz)
def GF(sz):
    f=ImageFont.truetype(f'{S}/SpaceGrotesk.ttf',sz)
    try: f.set_variation_by_name('Bold')
    except Exception: pass
    return f
@functools.lru_cache(None)
def textimg(s,size,fill,font='p'):
    f=PF(size) if font=='p' else GF(size); lines=s.split('|'); sw=max(3,size//7) if font=='p' else 3; lh=int(size*1.4); pad=sw+16
    wd=int(max(f.getlength(l) for l in lines))+2*pad; ht=lh*len(lines)+2*pad
    im=Image.new('RGBA',(wd,ht)); d=ImageDraw.Draw(im); ms=Image.new('L',(wd,ht)); dm=ImageDraw.Draw(ms)
    for i,l in enumerate(lines):
        x=(wd-f.getlength(l))/2; y=pad+i*lh
        dm.text((x,y),l,font=f,fill=255,stroke_width=sw+4); d.text((x,y),l,font=f,fill=fill,stroke_width=sw,stroke_fill='#000')
    out=Image.new('RGBA',(wd,ht)); out.putalpha(ms.filter(ImageFilter.GaussianBlur(7)).point(lambda v:int(v*.7))); out.alpha_composite(im); return out
def slam(base,img,cx,cy,age,seed=0,big=1.6):
    if age<0: return
    if age<0.12: s=big+(0.94-big)*(age/0.12)
    elif age<0.2: s=0.94+0.06*(age-0.12)/0.08
    else: s=1
    dx=dy=0
    if 0.08<age<0.34:
        r=random.Random(int(age*60)+seed); k=(0.34-age)/0.26*7; dx=r.uniform(-k,k); dy=r.uniform(-k,k)
    im=img if s==1 else img.resize((max(1,int(img.width*s)),max(1,int(img.height*s))),Image.BILINEAR)
    base.alpha_composite(im,(int(cx-im.width/2+dx),int(cy-im.height/2+dy)))
@functools.lru_cache(None)
def sheet(n): return Image.open(f'{REPO}/assets/{n}.webp').convert('RGBA')
NFR={4:5}; MS={4:120}
@functools.lru_cache(None)
def pf(n,row,i,sc=0.8):
    c=sheet(n).crop((i*192,row*208,i*192+192,row*208+208)); return c.resize((int(192*sc),int(208*sc)),Image.NEAREST)
@functools.lru_cache(None)
def pfp(h,d,ring):
    im=Image.open(f'{S}/pfp/{h}.png').convert('RGBA').resize((d*4,d*4),Image.LANCZOS)
    m=Image.new('L',(d*4,d*4)); ImageDraw.Draw(m).ellipse((0,0,d*4-1,d*4-1),fill=255); im.putalpha(m)
    im=im.resize((d,d),Image.LANCZOS)
    R=d+16; o=Image.new('RGBA',(R*4,R*4)); dd=ImageDraw.Draw(o); dd.ellipse((0,0,R*4-1,R*4-1),fill='#000'); dd.ellipse((8,8,R*4-9,R*4-9),fill=ring)
    o=o.resize((R,R),Image.LANCZOS); o.alpha_composite(im,(8,8)); return o
def pop(base,img,cx,cy,age):
    if age<0: return
    s=min(1,age/0.16); s=1.12*s if s<1 else 1
    if 0.16<=age<0.26: s=1.12-0.12*(age-0.16)/0.1
    im=img.resize((max(1,int(img.width*s)),max(1,int(img.height*s))),Image.BILINEAR)
    base.alpha_composite(im,(int(cx-im.width/2),int(cy-im.height/2)))
LOGO=Image.open('/mnt/project-files/last-dance/infografico/weirdcats-logo.png').convert('RGBA')
LOGO=LOGO.crop(LOGO.getbbox()); LOGO=LOGO.resize((170,int(170*LOGO.height/LOGO.width)),Image.LANCZOS)
sh=Image.new('RGBA',LOGO.size,(0,0,0,0)); sh.putalpha(LOGO.getchannel('A').point(lambda v:int(v*.6)))
Y='#ffe900'; WH='#ffffff'; PK='#ff5fb4'; CY='#2de2ff'
LANES=[(3.6,6.6,'VIDEO',PK,['hajime_umemiva','axcelz07','KPbeden','Dmr98384402','AndriOkey007','Ianfield77']),
       (6.6,8.8,'GIF',CY,['NFdoctor03','chicken_6fr','Big_Prim3']),
       (8.8,11.0,'MEME',Y,['CaaSi_5','coremsn9099','CryptoSpineX'])]
DUR=16.0; N=int(DUR*FPS)
PETS=[('beanie',30),('glitch',283),('lucky',536)]
def pets(fr,t,y=W-170):
    for j,(n,x) in enumerate(PETS):
        i=int((t*1000+j*80)/MS[4])%NFR[4]; fr.alpha_composite(pf(n,4,i),(x,y))
for k in range(N):
    t=k/FPS
    if t<3.6 or t>=13.2: fr=BGL.copy()
    else: fr=BGD.copy()
    if t<2.0:
        slam(fr,textimg('LAST DANCE',46,Y),W/2,250,t)
        slam(fr,textimg('RESULTS',40,WH),W/2,330,t-0.45,seed=3)
        pets(fr,t)
    elif t<3.6:
        slam(fr,textimg('13 FREE MINTS',44,Y),W/2,270,t-2.0)
        slam(fr,textimg('THE WEIRDEST|DANCERS ON THE FLOOR',20,PK),W/2,360,t-2.5,seed=5)
        pets(fr,t)
    elif t<11.0:
        for (a,b,name,col,hs) in LANES:
            if not a<=t<b: continue
            slam(fr,textimg(name,40,col),W/2,135,t-a)
            slam(fr,textimg(f'{len(hs)} FREE MINTS' if len(hs)>1 else 'FREE MINT',16,WH),W/2,188,t-a-0.15,seed=7)
            if len(hs)==6: pos=[(W/2+(c-1)*225,300+r*215) for r in range(2) for c in range(3)]; d=128
            else: pos=[(W/2+(c-1)*225,390) for c in range(3)]; d=150
            for i,(h,(x,y)) in enumerate(zip(hs,pos)):
                ag=t-a-0.35-i*0.12
                pop(fr,pfp(h,d,col),x,y,ag)
                if ag>0.1: 
                    ti=textimg('@'+h,21,WH,'g'); fr.alpha_composite(ti,(int(x-ti.width/2),int(y+d/2+6)))
    elif t<13.2:
        a=11.0
        slam(fr,textimg('WEIRDEST|OF ALL',40,PK),W/2,150,t-a)
        pop(fr,pfp('WH2U5',210,PK),W/2,395,t-a-0.4)
        if t-a>0.55:
            ti=textimg('@WH2U5',28,WH,'g'); fr.alpha_composite(ti,(int(W/2-ti.width/2),532))
        slam(fr,textimg('+1 FREE MINT',16,Y),W/2,610,t-a-0.8,seed=9)
    else:
        a=13.2
        slam(fr,textimg('GTD + FCFS',40,Y),W/2,200,t-a)
        slam(fr,textimg('STAMPED ON|YOUR TICKET',26,WH),W/2,290,t-a-0.4,seed=2)
        slam(fr,textimg('THANK YOU, WEIRDOS',20,PK),W/2,385,t-a-0.9,seed=4)
        pets(fr,t)
    fr.alpha_composite(sh,(19,19)); fr.alpha_composite(LOGO,(18,18))
    fr.convert('RGB').save(f'{OUT}/f{k:04d}.png')
print(N)
