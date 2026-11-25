import math, random
def hx(h): return tuple(int(h[i:i+2],16) for i in (1,3,5))
S=[hx(c) for c in ['#1B0C8F','#5B12B8','#A21C9F','#DC4B7A','#F7894A','#FCCB3A']]
def col(t):
    n=len(S)-1; k=min(int(t*n),n-1); u=t*n-k; a,b=S[k],S[k+1]
    return '#%02x%02x%02x'%tuple(round(a[i]+(b[i]-a[i])*u) for i in range(3))
def rot(v,ax,ay,az):
    x,y,z=v
    y,z=y*math.cos(ax)-z*math.sin(ax), y*math.sin(ax)+z*math.cos(ax)
    x,z=x*math.cos(ay)+z*math.sin(ay), -x*math.sin(ay)+z*math.cos(ay)
    x,y=x*math.cos(az)-y*math.sin(az), x*math.sin(az)+y*math.cos(az)
    return x,y,z
W,H=460,420; cx,cy,R=230,210,170
AX,AY,AZ=math.radians(25),math.radians(-10),math.radians(-20)
def _n(v):
    L=math.sqrt(sum(c*c for c in v)); return tuple(c/L for c in v)
A0=_n((-0.72,-0.62,0.32)); A1=_n((-0.42,0.38,1.0)); A2=_n((0.70,0.62,0.36))
def _c(t): return _n(tuple((1-t)**2*A0[i]+2*(1-t)*t*A1[i]*1.35+t*t*A2[i] for i in range(3)))
def onband(t,off=0.0,lift=0.0):
    p=_c(t); q=_c(min(1,t+0.01)) if t<0.99 else p; pr=_c(max(0,t-0.01))
    tg=_n(tuple(q[i]-pr[i] for i in range(3)))
    lat=_n((p[1]*tg[2]-p[2]*tg[1], p[2]*tg[0]-p[0]*tg[2], p[0]*tg[1]-p[1]*tg[0]))
    return _n(tuple(p[i]+lat[i]*off for i in range(3)))
def P(v,r=R): return cx+v[0]*r, cy-v[1]*r, v[2]
def build(anim=False):
    rnd=random.Random(5); el=[]
    defs=['<defs>',
      '<radialGradient id="glow" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#EDE7FB" stop-opacity="0.9"/><stop offset="0.7" stop-color="#F6F2FB" stop-opacity="0.5"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>',
      '<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.2"/></filter>',
      '<filter id="halo" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="6"/></filter>']
    el.append(f'<circle cx="{cx}" cy="{cy}" r="{R*1.18:.0f}" fill="url(#glow)"/>'); el.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#B9B2CC" stroke-opacity="0.45" stroke-width="0.9"/>')
    # faint latitude / longitude lines of the sphere
    for lat in (-45,0,45):
        pts=[P(rot((math.cos(math.radians(lat))*math.cos(math.radians(a)),math.cos(math.radians(lat))*math.sin(math.radians(a)),math.sin(math.radians(lat))),AX,AY,AZ)) for a in range(0,361,6)]
        el.append('<path d="M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y,z in pts)+'" fill="none" stroke="#B9B2CC" stroke-opacity="0.35" stroke-width="0.8"/>')
    for lon in (30,90,150):
        pts=[P(rot((math.cos(math.radians(a))*math.cos(math.radians(lon)),math.cos(math.radians(a))*math.sin(math.radians(lon)),math.sin(math.radians(a))),AX,AY,AZ)) for a in range(0,361,6)]
        el.append('<path d="M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y,z in pts)+'" fill="none" stroke="#B9B2CC" stroke-opacity="0.22" stroke-width="0.8"/>')
    # flowing streamlines with gradient
    for j,(off,w,op) in enumerate(((0.26,1.6,0.55),(0.20,0.9,0.35),(-0.22,0.9,0.3),(0.32,0.6,0.25))):
        pts=[P(onband(0.02+0.96*k/80,off)) for k in range(81)]
        gid=f'g{j}'; (x0,y0,_),(x1,y1,_)=pts[0],pts[-1]
        defs.append(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x0:.0f}" y1="{y0:.0f}" x2="{x1:.0f}" y2="{y1:.0f}">'+''.join(f'<stop offset="{i/5}" stop-color="{col(i/5)}"/>' for i in range(6))+'</linearGradient>')
        el.append(f'<path d="M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y,z in pts)+f'" fill="none" stroke="url(#{gid})" stroke-width="{w}" stroke-opacity="{op}" stroke-linecap="round"/>')
    # particles
    parts=[]
    for i in range(360):
        t=rnd.random(); off=rnd.gauss(0,0.085)
        x,y,z=P(onband(t,off)); parts.append((z,t,x,y))
    # sparse dust
    for i in range(70):
        u=rnd.uniform(-1,1); a=rnd.uniform(0,2*math.pi); v=(math.sqrt(1-u*u)*math.cos(a),math.sqrt(1-u*u)*math.sin(a),u)
        x,y,z=P(v); el.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{0.8+0.7*(z+1)/2:.1f}" fill="#9C93B8" opacity="{0.15+0.25*(z+1)/2:.2f}"/>')
    parts.sort()
    for z,t,x,y in parts:
        d=(z+1)/2; r=1.0+3.0*d**1.4; op=0.35+0.6*d
        el.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{col(t)}" opacity="{op:.2f}"/>')
    # glowing anchors
    for k in range(5):
        t=0.1+0.2*k; x,y,z=P(onband(t))
        c=col(t); el.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="19" fill="{c}" opacity="0.7" filter="url(#halo)"><animate attributeName="opacity" values="0.5;0.95;0.5" dur="4s" begin="{k*0.8}s" repeatCount="indefinite"/></circle>')
        el.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="10.5" fill="#FFFFFF" opacity="0.9"/><circle cx="{x:.1f}" cy="{y:.1f}" r="8.5" fill="{c}"/><circle cx="{x:.1f}" cy="{y:.1f}" r="3.6" fill="#FFFFFF"/>')
    defs.append('</defs>')
    return f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Ordered representations on a hypersphere">{"".join(defs)}{"".join(el)}</svg>'
open('hero_art.svg','w').write(build())
