import numpy as np, wave, sys
sr=44100; T=20.0; n=int(sr*T); out=np.zeros(n); np.random.seed(5)
def env(t,d): return np.exp(-t*d)
def sq(f,dur,duty=0.5,vol=0.2,dec=6):
    t=np.arange(int(sr*dur))/sr; return np.where((t*f)%1<duty,1.0,-1.0)*env(t,dec)*vol
def tri(f,dur,vol=0.3):
    t=np.arange(int(sr*dur))/sr; return (2*np.abs(2*((t*f)%1)-1)-1)*np.minimum(1,(dur-t)*20)*vol
def noise(dur,vol=0.3,dec=30):
    t=np.arange(int(sr*dur))/sr; return np.random.uniform(-1,1,len(t))*env(t,dec)*vol
def kick(vol=0.6):
    t=np.arange(int(sr*0.28))/sr; f=45+130*np.exp(-t*28); return np.sin(2*np.pi*np.cumsum(f)/sr)*env(t,10)*vol
def add(s,at):
    i=int(at*sr); j=min(n,i+len(s)); 
    if i<n: out[i:j]+=s[:j-i]
# 1) boring part: sparse elevator notes
for k,(f,at) in enumerate([(261.6,0.4),(329.6,1.0),(392,1.6),(329.6,2.2),(293.7,2.8)]):
    add(tri(f,0.5,0.10),at)
for c in [1.2,1.45,2.1,2.3,2.5]: add(noise(0.03,0.25,200),c)
for s in [0.4,1.5,2.6]: add(kick(0.35),s)
# record scratch at 3.6
t=np.arange(int(sr*0.28))/sr; f=900*np.exp(-t*9)+60; add(np.sign(np.sin(2*np.pi*np.cumsum(f)/sr))*0.25*np.minimum(1,(0.28-t)*15)+noise(0.28,0.12,6),3.6)
# 2) groove
bpm=128; beat=60/bpm; step=beat/4
roots=[220.0,174.61,261.63,196.0]; arps=[[0,3,7,12],[0,4,7,12],[0,4,7,12],[0,4,7,10]]
def groove(a,b,heavy=False):
    t=a
    while t<b-1e-6:
        k=int(round((t-a)/step)); bar=(k//16)%4; r=roots[bar]
        add(sq(r*2**(arps[bar][k%4]/12)*2,step*0.9,0.25,0.10),t)
        if k%4==0: add(tri(r/2,beat*0.9,0.30),t); add(kick(0.6 if heavy else 0.5),t)
        if k%8==4: add(noise(0.14,0.25,22),t)
        if k%2==1: add(noise(0.04,0.08,90),t)
        if heavy and k%16==0: add(sq(r*4,beat*2,0.5,0.05,1.5),t)
        t+=step
groove(3.9,12.0)
# riser into the wall drop
t=np.arange(int(sr*0.6))/sr; add(np.random.uniform(-1,1,len(t))*(t/0.6)**2*0.25,11.4)
groove(12.3,16.3,heavy=True)
for s in [3.95,7.1,9.7,12.3,13.7,16.5]:
    add(kick(0.95),s); add(noise(0.35,0.35,9),s); add(sq(880,0.22,0.5,0.08),s)
# 3) end: logo hit + slow outro arp
add(kick(1.0),16.3); add(noise(1.0,0.32,3),16.3); add(tri(110,1.2,0.32),16.3)
for i,f in enumerate([440,523.3,659.3,880,659.3,523.3,440,523.3,659.3,880]):
    add(sq(f,0.25,0.25,0.06),16.9+i*0.25)
add(kick(1.0),19.0); add(tri(110,1.0,0.3),19.0); add(noise(0.9,0.25,3),19.0)
fade=np.ones(n); fs=int(19.3*sr); fade[fs:]=np.linspace(1,0,n-fs); out*=fade
out=out/np.max(np.abs(out))*0.89
w=wave.open(sys.argv[1],'w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((out*32767).astype(np.int16).tobytes()); w.close()
