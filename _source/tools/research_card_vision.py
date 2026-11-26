import math, random, importlib.util, sys
sys.path.insert(0,'/home/claude/hero')
from cards import col, wrap, centroid, W, H
def vision():
    r=random.Random(12); b=[]
    VX,VY=262,64
    def lane(x0,bend):
        # quadratic from bottom (x0,H+6) to vanishing point with lateral bend
        cx,cy=(x0+VX)/2+bend,(H+VY)/2+18
        return lambda t:((1-t)**2*x0+2*(1-t)*t*cx+t*t*VX,(1-t)**2*(H+6)+2*(1-t)*t*cy+t*t*VY)
    # road surface
    L=lane(-40,30); R=lane(560,30)
    pts=[L(k/40) for k in range(41)]+[R(1-k/40) for k in range(41)]
    defs='<linearGradient id="road" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#E7DEF7"/><stop offset="1" stop-color="#F7F3FC" stop-opacity="0.3"/></linearGradient>'
    b.append('<path d="M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y in pts)+' Z" fill="url(#road)"/>')
    # horizon / skyline contour
    sky=[(x, VY-6-7*math.sin(x/47.0)-5*math.sin(x/19.0+1.3)-3*math.sin(x/9.0)) for x in range(0,W+1,4)]
    b.append('<path d="M0,'+str(VY)+' L'+' L'.join(f'{x:.1f},{y:.1f}' for x,y in sky)+f' L{W},{VY} Z" fill="#E4DCF5" fill-opacity="0.7"/>')
    b.append('<path d="M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y in sky)+'" fill="none" stroke="#B9AEDB" stroke-width="1" stroke-opacity="0.9"/>')
    b.append(f'<line x1="0" y1="{VY}" x2="{W}" y2="{VY}" stroke="#A99BD3" stroke-width="0.8" stroke-opacity="0.6"/>')
    # depth isolines across road (perspective spacing)
    for k in range(1,9):
        t=1-1/(1+0.45*k)  # param along lanes
        (xl,yl),(xr,yr)=L(t),R(t)
        b.append(f'<line x1="{xl:.1f}" y1="{yl:.1f}" x2="{xr:.1f}" y2="{yr:.1f}" stroke="{col(k/8)}" stroke-width="{1.6-0.12*k:.2f}" stroke-opacity="{0.55-0.04*k:.2f}"/>')
    # lanes (eigenlanes) as particle strands + glow line
    lanes=[(40,24),(190,22),(340,20),(490,18)]
    for i,(x0,bend) in enumerate(lanes):
        f=lane(x0,bend); c=col(0.12+i*0.26)
        b.append('<path d="M'+' L'.join(f'{f(k/50)[0]:.1f},{f(k/50)[1]:.1f}' for k in range(46))+f'" fill="none" stroke="{c}" stroke-width="2.4" stroke-opacity="0.35" stroke-linecap="round"/>')
        for m in range(40):
            t=r.random()*0.9; x,y=f(t); s=(1-t)
            b.append(f'<circle cx="{x+r.gauss(0,1.2*s):.1f}" cy="{y:.1f}" r="{0.8+2.6*s:.1f}" fill="{c}" opacity="{0.45+0.45*s:.2f}"/>')
    # object (car ahead) segmentation contour
    t=0.52; (xa,ya),(xb,yb)=lane(190,22)(t),lane(340,20)(t)
    cx=(xa+xb)/2; base=(ya+yb)/2; w=(xb-xa)*0.62; h=w*0.62; cy=base-h/2
    car=(f'M{cx-w/2:.1f},{base:.1f} L{cx-w/2:.1f},{base-h*0.55:.1f} Q{cx-w/2:.1f},{base-h*0.62:.1f} {cx-w*0.42:.1f},{base-h*0.64:.1f} '
         f'L{cx-w*0.3:.1f},{base-h:.1f} L{cx+w*0.3:.1f},{base-h:.1f} L{cx+w*0.42:.1f},{base-h*0.64:.1f} '
         f'Q{cx+w/2:.1f},{base-h*0.62:.1f} {cx+w/2:.1f},{base-h*0.55:.1f} L{cx+w/2:.1f},{base:.1f} Z')
    b.append(f'<path d="{car}" fill="#FCCB3A" fill-opacity="0.28" stroke="#F7894A" stroke-width="2" stroke-dasharray="5 3" stroke-linejoin="round"/>')
    b.append(f'<line x1="{cx-w*0.36:.1f}" y1="{base-h*0.64:.1f}" x2="{cx+w*0.36:.1f}" y2="{base-h*0.64:.1f}" stroke="#F7894A" stroke-width="1.2" stroke-opacity="0.7"/>')
    b.append(centroid(cx,base-h*0.32,'#F7894A',0))
    # anchors on lanes
    for i,(x0,bend) in enumerate(lanes[1:3]):
        x,y=lane(x0,bend)(0.25); b.append(centroid(x,y,col(0.38+i*0.26),i+1))
    return wrap(defs,''.join(b),'Road scene with lanes, depth contours and a segmented vehicle')
open('/home/claude/assets/card_vision.svg','w').write(vision())
