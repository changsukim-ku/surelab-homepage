import math, random
def hx(h): return tuple(int(h[i:i+2],16) for i in (1,3,5))
S=[hx(c) for c in ['#1B0C8F','#5B12B8','#A21C9F','#DC4B7A','#F7894A','#FCCB3A']]
def col(t):
    t=max(0,min(1,t)); n=len(S)-1; k=min(int(t*n),n-1); u=t*n-k; a,b=S[k],S[k+1]
    return '#%02x%02x%02x'%tuple(round(a[i]+(b[i]-a[i])*u) for i in range(3))
W,H=480,200
BG=('<radialGradient id="bg" cx="50%" cy="55%" r="65%"><stop offset="0" stop-color="#EFE9FB"/><stop offset="1" stop-color="#FBFAFD"/></radialGradient>'
    '<filter id="halo" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="6"/></filter>'
    '<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="1.4"/></filter>')
def wrap(defs,body,label): return f'<svg viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{label}"><defs>{BG}{defs}</defs><rect width="{W}" height="{H}" fill="url(#bg)"/>{body}</svg>'
def centroid(x,y,c,k):
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="15" fill="{c}" opacity="0.7" filter="url(#halo)"><animate attributeName="opacity" values="0.45;0.9;0.45" dur="4s" begin="{k*0.7}s" repeatCount="indefinite"/></circle>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8.5" fill="#FFFFFF" opacity="0.9"/><circle cx="{x:.1f}" cy="{y:.1f}" r="6.8" fill="{c}"/><circle cx="{x:.1f}" cy="{y:.1f}" r="2.8" fill="#FFFFFF"/>')

def order():
    r=random.Random(2); b=[]
    f=lambda t:(40+400*t, 130-60*t+18*math.sin(t*math.pi*1.6))
    for j,(off,w,op) in enumerate(((-26,1.4,0.5),(-34,0.8,0.3),(26,0.8,0.3))):
        pts=[f(k/60) for k in range(61)]
        b.append('<path d="M'+' L'.join(f'{x:.1f},{y+off:.1f}' for x,y in pts)+f'" fill="none" stroke="url(#lg)" stroke-width="{w}" stroke-opacity="{op}" stroke-linecap="round"/>')
    parts=[]
    for i in range(230):
        t=r.random(); x,y=f(t); parts.append((t,x+r.gauss(0,6),y+r.gauss(0,10),r.random()))
    for t,x,y,d in parts: b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{1.2+2.6*d:.1f}" fill="{col(t)}" opacity="{0.4+0.55*d:.2f}"/>')
    for k in range(4):
        t=0.1+0.27*k; x,y=f(t); b.append(centroid(x,y,col(t),k))
    defs='<linearGradient id="lg" x1="0" x2="1">'+''.join(f'<stop offset="{i/5}" stop-color="{col(i/5)}"/>' for i in range(6))+'</linearGradient>'
    return wrap(defs,''.join(b),'Instances ordered by rank with reference points')

def compress():
    r=random.Random(9); b=[]
    n=12; s=11; x0,y0=34,100-n*s/2
    for i in range(n):
        for j in range(n):
            v=0.5+0.5*math.sin(i*0.55+j*0.35)*math.cos(j*0.4-i*0.2); v=min(1,max(0,v+r.gauss(0,0.12)))
            b.append(f'<rect x="{x0+j*s:.0f}" y="{y0+i*s:.0f}" width="{s-2}" height="{s-2}" rx="1.5" fill="{col(v)}" opacity="{0.35+0.45*v:.2f}"/>')
    tokens=[(380,62),(380,100),(380,138),(430,81),(430,119)]
    for k,(tx,ty) in enumerate(tokens):
        for m in range(7):
            sy=y0+r.uniform(0.1,0.9)*n*s; sx=x0+n*s+4
            b.append(f'<path d="M{sx:.0f},{sy:.0f} C{sx+80:.0f},{sy:.0f} {tx-90:.0f},{ty:.0f} {tx-12:.0f},{ty:.0f}" fill="none" stroke="{col(k/4)}" stroke-width="0.9" stroke-opacity="0.35"/>')
    for k,(tx,ty) in enumerate(tokens): b.append(centroid(tx,ty,col(k/4),k))
    return wrap('',''.join(b),'Many pixels compressed into a few tokens')

def vision():
    r=random.Random(4); b=[]
    # depth-like isolines
    cx,cy=300,118
    for k in range(9):
        rr=16+k*17; pts=[]
        for a in range(0,361,8):
            ang=math.radians(a); w=1+0.12*math.sin(3*ang+k*0.7)+0.06*math.cos(5*ang)
            pts.append((cx+rr*1.55*w*math.cos(ang), cy+rr*0.82*w*math.sin(ang)))
        b.append('<path d="M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y in pts)+f' Z" fill="none" stroke="{col(1-k/8)}" stroke-width="{1.6-k*0.1:.2f}" stroke-opacity="{0.75-k*0.06:.2f}"/>')
    # segmented object blob
    pts=[]
    for a in range(0,361,10):
        ang=math.radians(a); rr=34*(1+0.25*math.sin(2*ang+0.5)+0.12*math.sin(5*ang))
        pts.append((cx+rr*math.cos(ang),cy+rr*0.9*math.sin(ang)))
    d='M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y in pts)+' Z'
    b.append(f'<path d="{d}" fill="#FCCB3A" fill-opacity="0.28" stroke="#F7894A" stroke-width="2.2" stroke-dasharray="5 4"/>')
    # click points (interactive segmentation)
    b.append(centroid(cx-8,cy+4,'#F7894A',0)); b.append(centroid(118,64,'#5B12B8',1))
    # pixel scatter on left
    for i in range(90):
        x=r.uniform(24,170); y=r.uniform(24,176); t=r.random()*0.5
        b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r.uniform(0.8,2.2):.1f}" fill="{col(t)}" opacity="{r.uniform(0.2,0.55):.2f}"/>')
    return wrap('',''.join(b),'Depth contours and a segmented object')
for n,f in (('order',order),('compress',compress),('vision',vision)): open(f'/home/claude/assets/card_{n}.svg','w').write(f())
