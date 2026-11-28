# Last Dance GTD + FCFS scrolling list GIF. Run: python3 make_list.py FRAMEDIR
import sys, os, functools
sys.argv=[sys.argv[0],sys.argv[1]]
exec(open('make_results.py').read().split('LANES=')[0])  # reuse helpers/fonts/bg/logo
GTD=['logospaco','Iknowstuff07','Nobu_2k','zackanzen','ColdRye','childofrose_','rbagjamahesa','Cryptoismic','moonwalker408','stevevaisfan','RealAlienGuy','P1erre_deFermat','mikenftguy','istvanphoto','boyluuke','fauzxt','MatDav000','javapee006','lepcha_sui','Lexy841949','TkvitenT','RBraun71408','peterfamer66','potocoforeva','5597mq','FebriSense','jambujambu99p2','Vhanzj002','AnasseDazia','ChuckTardio','amir007_eth','IdealistRussian','aneeda01','dontfadeplease','annabellex_web3','MeloriKt','jiiiiiiii_i','brainystick','0xcryptow','Temi_eo','luyuban69','agunverse','SoangSoon','Ayaosans','yurnerou','mowiek50750','LesmanaHai9803']
FCFS=['XaeroDeath','ZachGibbons23','Suprprid3','Tucox_','TEENSONACID']
D=64; ROW=96; COLX=[W*0.19,W*0.5,W*0.81]
def block(names,col):
    rows=(len(names)+2)//3; im=Image.new('RGBA',(W,rows*ROW))
    for i,h in enumerate(names):
        r,c=divmod(i,3); x=COLX[c]; y=r*ROW+ROW/2
        rem=len(names)%3
        if rem and i>=len(names)-rem: x=[W/2] [0] if rem==1 else [W*0.34,W*0.66][i-(len(names)-rem)]
        p=pfp(h,D,col); im.alpha_composite(p,(int(x-p.width/2),int(y-p.height/2-10)))
        t=textimg('@'+h,15,WH,'g'); im.alpha_composite(t,(int(x-t.width/2),int(y+p.height/2-24)))
    return im
hg=textimg('GTD',44,Y); hf=textimg('FCFS',44,CY)
bg_=block(GTD,Y); bf=block(FCFS,CY)
strip_h=W+hg.height+bg_.height+60+hf.height+bf.height+W
STRIP=Image.new('RGBA',(W,strip_h)); y=W
STRIP.alpha_composite(hg,(int(W/2-hg.width/2),y)); y+=hg.height
STRIP.alpha_composite(bg_,(0,y)); y+=bg_.height+60
STRIP.alpha_composite(hf,(int(W/2-hf.width/2),y)); y+=hf.height
STRIP.alpha_composite(bf,(0,y)); y+=bf.height
END=y
FPS=12; INTRO=1.8; OUTRO=2.6; TRAVEL=END-W*0.55-(W-260)
SCROLL=TRAVEL/(11.0); DUR=INTRO+11.0+OUTRO; N=int(DUR*FPS)
PETS=[('beanie',30),('glitch',283),('lucky',536)]
def pets(fr,t):
    for j,(n,x) in enumerate(PETS):
        i=int((t*1000+j*80)/120)%5; fr.alpha_composite(pf(n,4,i),(x,W-170))
top=Image.new('RGBA',(W,W)); 
for yy in range(150): ImageDraw.Draw(top).line([(0,yy),(W,yy)],fill=(8,8,12,255 if yy<95 else int(255*(150-yy)/55)))
for k in range(N):
    t=k/FPS
    if t<INTRO:
        fr=BGL.copy()
        slam(fr,textimg('LAST DANCE',40,Y),W/2,240,t)
        slam(fr,textimg('GTD + FCFS',40,WH),W/2,315,t-0.4,seed=3)
        slam(fr,textimg('STAMPED ON YOUR TICKET',18,PK),W/2,385,t-0.8,seed=5)
        pets(fr,t)
    elif t<INTRO+11.0:
        fr=BGD.copy(); off=(W-260)+ (t-INTRO)*SCROLL
        fr.alpha_composite(STRIP.crop((0,int(off),W,int(off)+W)),(0,0))
        fr.alpha_composite(top)
    else:
        a=INTRO+11.0; fr=BGL.copy()
        slam(fr,textimg('CHECK YOUR|TICKET',36,Y),W/2,230,t-a)
        slam(fr,textimg('weirdcats.xyz/weirdlist',26,WH,'g'),W/2,330,t-a-0.4,seed=2)
        slam(fr,textimg('THANK YOU, WEIRDOS',20,PK),W/2,400,t-a-0.8,seed=4)
        pets(fr,t)
    fr.alpha_composite(sh,(19,19)); fr.alpha_composite(LOGO,(18,18))
    fr.convert('RGB').save(f'{OUT}/f{k:04d}.png')
print(N)
