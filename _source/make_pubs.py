import re, json, glob
MON = {m:i for i,m in enumerate(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],1)}
FIX = [('segmenation','segmentation'),('Structually','Structurally'),('Auchland','Auckland'),('Addis Abada','Addis Ababa'),
       ('June.','Jun.'),('May.','May'),('BMBC:Bilateral','BMBC: Bilateral'),('Massachusetts, Boston','Boston, Massachusetts'),
       ('in NeurIPS','in Proc. NeurIPS'),('Sept.','Sep.')]
out = []
for f in sorted(glob.glob('/home/claude/pubdata/*.txt')):
    k = 'conf' if 'conf_' in f else 'jour'
    for line in open(f):
        line = line.strip()
        if not line: continue
        for a,b in FIX: line = line.replace(a,b)
        no, y, au, ti, ve = [s.strip() for s in line.split(' | ')]
        n = int(no.strip('[]'))
        ve = re.sub(r'^in Proc\. ', '', ve)
        ve = re.sub(r'\.(\s*\(|$)', r'\1', ve).rstrip('.')
        ve = ve.replace('(Oral presentation)', '(Oral)').replace('(Highlight presentation)', '(Highlight)')
        m = 0
        for mm in re.findall(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', ve): m = MON[mm]
        out.append(dict(y=y, k=k, n=n, no=('C' if k=='conf' else 'J')+str(n), authors=au, title=ti, venue=ve, m=m))
for line in open('/home/claude/pubdata/extra.tsv'):
    line = line.strip()
    if not line: continue
    k, y, au, ti, ve = [x.strip() for x in line.split(' | ')]
    ve = re.sub(r'^in Proc\. ', '', ve)
    ve = re.sub(r'\.(\s*\(|$)', r'\1', ve).rstrip('.')
    m = 0
    for mm in re.findall(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', ve): m = MON[mm]
    prev = [q['n'] for q in out if q['k']==k and (int(q['y']), q['m']) <= (int(y), m)]
    out.append(dict(y=y, k=k, n=(max(prev) if prev else 0)+0.5, authors=au, title=ti, venue=ve, m=m))
for k in ('conf','jour'):
    for i, q in enumerate(sorted((q for q in out if q['k']==k), key=lambda q: (q['n'], int(q['y']), q['m'])), 1):
        q['n'] = i; q['no'] = ('C' if k=='conf' else 'J')+str(i)
nc = sum(p['k']=='conf' for p in out); nj = len(out)-nc
out.sort(key=lambda p: (-int(p['y']), -p['m'], p['k']!='conf', -p['n']))
lines = []
for p in out:
    d = {kk: p[kk] for kk in ('y','k','no','authors','title','venue')}
    lines.append(json.dumps(d, ensure_ascii=False))
open('/home/claude/pubdata/all.js','w').write(',\n'.join(lines))
print(nc, nj, len(out))
