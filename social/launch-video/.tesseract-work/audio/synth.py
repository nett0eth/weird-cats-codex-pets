# Chiptune bed + SFX for Weird Cats launch video. 120 BPM (beat = 0.5s, bar = 2s).
import numpy as np, wave
SR=48000; BEAT=0.5; DUR=24.0
rng=np.random.default_rng(7)
def t_(d): return np.arange(int(d*SR))/SR
def env(n,a=0.003,r=0.08,hold=None):
    e=np.ones(n); na=max(1,int(a*SR)); e[:na]=np.linspace(0,1,na)
    nr=min(n,int(r*SR)); e[-nr:]*=np.linspace(1,0,nr)**2; return e
def sq(f,d,duty=0.5):
    ph=(np.cumsum(np.full(int(d*SR),f) if np.isscalar(f) else f)/SR)%1; return np.where(ph<duty,1.0,-1.0)
def tri(f,d):
    ph=(np.arange(int(d*SR))*f/SR)%1; return 4*np.abs(ph-0.5)-1
def midi(m): return 440*2**((m-69)/12)
def add(buf,x,at,g=1.0):
    i=int(at*SR); j=min(len(buf),i+len(x)); buf[i:j]+=x[:j-i]*g
def kick(d=0.25):
    t=t_(d); f=50+120*np.exp(-t*30); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*14)
def snare(d=0.18):
    t=t_(d); return (rng.uniform(-1,1,len(t))*0.8+0.3*tri(190,d))*np.exp(-t*22)
def hat(d=0.05):
    t=t_(d); n=rng.uniform(-1,1,len(t)); n=np.diff(n,prepend=0); return n*np.exp(-t*80)
def crush(x,bits=5,hold=4):
    x=np.round(x*(2**bits))/(2**bits); return np.repeat(x[::hold],hold)[:len(x)]
music=np.zeros(int(DUR*SR))
# chords per bar (A minor: Am F C G), roots midi
prog=[(57,[57,60,64]),(53,[53,57,60]),(48,[48,52,55]),(55,[55,59,62])]
lead_a=[76,74,72,69,72,74,76,79, 77,76,74,72,74,72,69,67]   # 8ths over 2 bars
lead_b=[81,79,76,79,81,84,81,79, 76,79,81,79,76,74,72,74]
# ---- INTRO 0-3s: tense pulse + riser
for i in range(6):
    add(music,sq(midi(45),0.12,0.25)*env(int(0.12*SR),r=0.1),i*BEAT,0.10)
t=t_(1.5); rise=rng.uniform(-1,1,len(t))*np.linspace(0,1,len(t))**2
rise=np.convolve(rise,np.ones(8)/8,'same'); add(music,rise,1.5,0.22)
add(music,sq(np.linspace(220,880,len(t)),1.5,0.125)*np.linspace(0,1,len(t))**3,1.5,0.07)
def groove(start,end,lead,energy=1.0):
    t0=start
    while t0<end-1e-6:
        bar=int(round((t0-3.0)/2.0))%4; root,ch=prog[bar]
        for b in range(4):
            bt=t0+b*BEAT
            if bt>=end: break
            add(music,kick(),bt,0.9)
            if b in (1,3): add(music,snare(),bt,0.45*energy)
            for h in ((0,0.125,0.25,0.375) if energy>1.1 else (0,0.25)): add(music,hat(),bt+h,0.12)
            # bass: octave bounce 8ths
            for k,off in enumerate((0,0.25)):
                n=root-12+(12 if k else 0); add(music,tri(midi(n),0.22)*env(int(0.22*SR)),bt+off,0.38)
            # arp 16ths
            for k in range(4):
                n=ch[(b*4+k)%3]+12; add(music,sq(midi(n),0.1,0.125)*env(int(0.1*SR),r=0.06),bt+k*0.125,0.045*energy)
        # lead 8ths across 2-bar phrase
        phrase=lead[(bar%2)*8:(bar%2)*8+8]
        for k,n in enumerate(phrase):
            nt=t0+k*0.25
            if nt>=end: break
            add(music,sq(midi(n)*(1+0.004*np.sin(2*np.pi*6*t_(0.22))),0.22,0.5)*env(int(0.22*SR),r=0.1),nt,0.09*energy)
        t0+=2.0
groove(3.0,11.0,lead_a)
groove(11.0,17.0,lead_a,1.2)
def crash(d=1.2):
    t=t_(d); n=rng.uniform(-1,1,len(t)); n=np.diff(n,prepend=0); return n*np.exp(-t*3.5)
for c in (3.0,11.0,19.0): add(music,crash(),c,0.35)
# ---- BREAK 17-19: stutter + tape stop
seg=music[int(15.0*SR):int(15.125*SR)].copy()
for i in range(8): add(music,crush(seg,4,6),17.0+i*0.125,0.9)
tape=music[int(15.0*SR):int(16.0*SR)].copy()
idx=np.cumsum(np.linspace(1,0.05,int(1.0*SR)));idx=idx[idx<len(tape)-1].astype(int)
add(music,tape[idx]*np.linspace(1,0.2,len(idx)),18.0,0.8)
# ---- FINAL HOOK 19-23
groove(19.0,23.0,lead_b,1.25)
add(music,kick(0.5),23.0,1.0)
fade=int(0.8*SR); music[int(23.2*SR):int(23.2*SR)+fade]*=np.linspace(1,0,fade); music[int(24.0*SR):]=0
music[int(23.2*SR)+fade:]=0
def save(name,x,peak_db=-3.0):
    x=np.tanh(x*1.2); x=x/np.max(np.abs(x))*10**(peak_db/20)
    st=np.stack([x,x],1)
    with wave.open(name,'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((st*32767).astype('<i2').tobytes())
save('music-v2.wav',music,-2.0)
# ---- SFX
t=t_(0.9); buzz=np.zeros(len(t))
for s in (0.0,0.45):
    m=(t>=s)&(t<s+0.32); buzz[m]=np.sign(np.sin(2*np.pi*150*t[m]))*(0.6+0.4*np.sin(2*np.pi*35*t[m]))
buzz=np.convolve(buzz,np.ones(20)/20,'same'); save('buzz.wav',buzz,-8)
t=t_(0.18); pop=sq(np.linspace(300,1400,len(t)),0.18,0.25)*np.exp(-t*20); save('pop.wav',pop,-6)
t=t_(0.6); g=crush(rng.uniform(-1,1,len(t))*np.sign(np.sin(2*np.pi*23*t)),3,12)*np.exp(-t*3); save('glitch.wav',g,-8)
t=t_(0.7); f=np.interp(t,[0,0.12,0.45,0.7],[520,880,700,420])*(1+0.03*np.sin(2*np.pi*9*t))
meow=(sq(f,0.7,0.3)*0.6+sq(f*2.01,0.7,0.5)*0.2)*env(len(t),a=0.02,r=0.3); save('meow.wav',meow,-5)
t=t_(0.35); sl=sq(np.linspace(1200,200,len(t)),0.35,0.5)*np.exp(-t*6); save('slam.wav',sl+np.concatenate([kick(0.35)]),-4)
print('ok')
