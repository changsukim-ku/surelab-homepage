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
nc = sum(p['k']=='conf' for p in out); nj = len(out)-nc
assert sorted(p['n'] for p in out if p['k']=='conf') == list(range(1,249)), 'conf gaps'
assert sorted(p['n'] for p in out if p['k']=='jour') == list(range(1,109)), 'jour gaps'
out.sort(key=lambda p: (-int(p['y']), -p['m'], p['k']!='conf', -p['n']))
lines = []
for p in out:
    d = {kk: p[kk] for kk in ('y','k','no','authors','title','venue')}
    lines.append(json.dumps(d, ensure_ascii=False))
open('/home/claude/pubdata/all.js','w').write(',\n'.join(lines))
print(nc, nj, len(out))
