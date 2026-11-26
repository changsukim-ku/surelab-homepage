#!/usr/bin/env python3
"""Render the design-canvas pages (.dc.html) into a plain static website."""
import html, json, os, re, shutil, subprocess, sys

SRC = sys.argv[1]   # folder with *.dc.html
OUT = sys.argv[2]   # output site folder
ASSETS = sys.argv[3]  # folder with images

PAGES = {  # source -> (output file, page title)
    'Main.dc.html': ('index.html', 'SuRe Lab · Superintelligence Representation Lab'),
    'People.dc.html': ('people.html', 'People · SuRe Lab'),
    'Publications.dc.html': ('publications.html', 'Publications · SuRe Lab'),
    'Join.dc.html': ('join.html', 'Join us · SuRe Lab'),
    'Seminars.dc.html': ('seminars.html', 'Seminars · SuRe Lab'),
}
BLOBS = {
    '/_blob/eb78a1e16175a13c8873a8f7041376aa': 'images/cskim.jpg',
    '/_blob/783912d736126c95b5de85192345e40a': 'images/people/jiwon_kim.jpg',
    '/_blob/09bf4bf43c3dff5297d26a142de54c83': 'images/people/junhyeok_heo.jpg',
    '/_blob/1b074af8ee16053049137c13335e7093': 'images/people/youngeon_kim.jpg',
    '/_blob/d7fdd4f5d7154b88cba05ed9cb625c17': 'images/people/minseo_cho.jpg',
    '/_blob/311cec25340ae8e15078fa79a2401e47': 'images/people/jinwon_ko.jpg',
    '/_blob/38a38d37f12352a3567c465beaef63db': 'images/people/jaeseok_jang.jpg',
    '/_blob/5c749ba680f200760b3a82e4e8cbf377': 'images/people/seungmin_jeon.jpg',
    '/_blob/bb01036d2bcbcdc07958dbd3c2262285': 'images/people/donghyun_son.jpg',
    '/_blob/3104470b54c6270561a1d031b57ab750': 'images/people/hanbin_jeon.jpg',
    '/_blob/5583ebb25b09567b8a8654c6176e422a': 'images/card_order.svg',
    '/_blob/e94a593d9b08112bc906aab7616e7bae': 'images/card_compress.svg',
    '/_blob/0687550905e7399cd1c8c2c51ee1ffcc': 'images/card_vision.svg',
    '/_blob/db56b41b023cd010f91c2a727716c49d': 'images/hero.svg',
    '/_blob/83b91072d1403df0a48cb584c65ba301': 'images/sel/bli.jpg',
    '/_blob/ccb93590fcaeae9dae3b5b572996fd34': 'images/sel/conord.jpg',
    '/_blob/e40b11f7ef250d51daa900c0d772d3e8': 'images/sel/gol.jpg',
    '/_blob/2db5780d7e32c1e1e9c30a72d63029c8': 'images/sel/dpict.jpg',
    '/_blob/fd29455553f5810313fd228ea9e24e44': 'images/sel/ol.jpg',
    '/_blob/f974175da39b420d18efb99c63e7a00e': 'images/sel/brs.jpg',
}

DOTS = ''.join(f'<circle cx="{x}" cy="{y}" r="7" fill="{c}"/>' for x, y, c in [
    (12, 12, '#D6D3CE'), (36, 12, '#D6D3CE'), (60, 12, '#862633'), (12, 36, '#D6D3CE'), (36, 36, '#862633'),
    (60, 36, '#862633'), (12, 60, '#862633'), (36, 60, '#862633'), (60, 60, '#862633')])
FAVICON = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 72 72">{DOTS}</svg>'

PUB_FILTER_JS = """<script>
(function () {
  var btns = document.querySelectorAll('[data-filter]');
  function show(k) {
    btns.forEach(function (b) {
      var on = b.getAttribute('data-filter') === k;
      b.style.background = on ? '#17171B' : '#FFFFFF';
      b.style.color = on ? '#FFFFFF' : '#17171B';
      b.style.borderColor = on ? '#17171B' : '#D6D3CE';
    });
    document.querySelectorAll('[data-kind]').forEach(function (r) {
      r.style.display = (k === 'all' || r.getAttribute('data-kind') === k) ? '' : 'none';
    });
    document.querySelectorAll('[data-year]').forEach(function (y) {
      var any = Array.prototype.some.call(y.querySelectorAll('[data-kind]'), function (r) { return r.style.display !== 'none'; });
      y.style.display = any ? '' : 'none';
    });
  }
  btns.forEach(function (b) { b.addEventListener('click', function () { show(b.getAttribute('data-filter')); }); });
})();
</script>"""


def render_vals(script):
    js = ('class DCLogic{constructor(){this.props={};this.state={}}setState(){}}\n' + script +
          '\nprocess.stdout.write(JSON.stringify(new Component().renderVals(),(k,v)=>typeof v==="function"?undefined:v));')
    return json.loads(subprocess.run(['node', '-e', js], capture_output=True, text=True, check=True).stdout)


def lookup(path, ctx):
    path = path.strip()
    if path in ('true', 'false'):
        return path == 'true'
    cur = None
    parts = path.split('.')
    for scope in reversed(ctx):
        if parts[0] in scope:
            cur = scope[parts[0]]
            break
    else:
        raise KeyError(path)
    for p in parts[1:]:
        cur = cur[p]
    return cur


def fill_holes(text, ctx):
    return re.sub(r'\{\{\s*([\w.$]+)\s*\}\}', lambda m: html.escape(str(lookup(m.group(1), ctx)), quote=True), text)


def render(tpl, ctx):
    out = []
    i = 0
    while True:
        j = tpl.find('<sc-for', i)
        if j < 0:
            out.append(fill_holes(tpl[i:], ctx))
            break
        out.append(fill_holes(tpl[i:j], ctx))
        tag_end = tpl.index('>', j)
        tag = tpl[j:tag_end + 1]
        depth, k = 1, tag_end + 1
        while depth:
            o = tpl.find('<sc-for', k)
            c = tpl.find('</sc-for>', k)
            if o != -1 and o < c:
                depth += 1
                k = o + 7
            else:
                depth -= 1
                k = c + 9
        body = tpl[tag_end + 1:k - 9]
        lst = lookup(re.search(r'list="\{\{\s*([\w.$]+)\s*\}\}"', tag).group(1), ctx)
        name = re.search(r'as="(\w+)"', tag).group(1)
        for idx, item in enumerate(lst):
            out.append(render(body, ctx + [{name: item, '$index': idx}]))
        i = k
    return ''.join(out)


def build_page(src_name, out_name, title):
    s = open(os.path.join(SRC, src_name), encoding='utf-8').read()
    helmet = re.search(r'<helmet>(.*?)</helmet>', s, re.S).group(1)
    body = re.search(r'<x-dc>(.*?)</x-dc>', s, re.S).group(1)
    body = re.sub(r'<helmet>.*?</helmet>', '', body, flags=re.S)
    script = re.search(r'<script type="text/x-dc" data-dc-script[^>]*>(.*?)</script>', s, re.S).group(1)
    vals = render_vals(script)
    body = re.sub(r'\s(hint-[\w-]+|onClick)="[^"]*"', '', body)
    body = render(body, [vals])
    for blob, path in BLOBS.items():
        body = body.replace(blob, path)
    for src, (dst, _) in PAGES.items():
        body = body.replace(f'href="{src}', f'href="{dst}')
    body = body.replace('href="#" style="color: #862633; border-bottom', f'href="{out_name}" style="color: #862633; border-bottom')
    body = body.replace('<a href="#" style="display: flex; align-items: center; gap: 12px">', '<a href="index.html" style="display: flex; align-items: center; gap: 12px">')
    if src_name == 'Publications.dc.html' and 'data-filter' in body:
        body += PUB_FILTER_JS
    page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="SuRe Lab (Superintelligence Representation Lab), School of Electrical Engineering, Korea University. Order learning, learned compression, and visual understanding.">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
{helmet.strip()}
</head>
<body>
{body.strip()}
</body>
</html>
'''
    assert '{{' not in page and '<sc-for' not in page and '.dc.html' not in page and '/_blob/' not in page, out_name
    open(os.path.join(OUT, out_name), 'w', encoding='utf-8').write(page)


os.makedirs(os.path.join(OUT, 'images'), exist_ok=True)
for src, (dst, title) in PAGES.items():
    build_page(src, dst, title)
shutil.copy(os.path.join(ASSETS, 'cskim2.jpg'), os.path.join(OUT, 'images', 'cskim.jpg'))
shutil.copy(os.path.join(ASSETS, 'hero.svg'), os.path.join(OUT, 'images', 'hero.svg'))
for _n in ('order','compress','vision'): shutil.copy(os.path.join(ASSETS, f'card_{_n}.svg'), os.path.join(OUT, 'images', f'card_{_n}.svg'))
shutil.copytree(os.path.join(ASSETS, 'people'), os.path.join(OUT, 'images', 'people'), dirs_exist_ok=True)
shutil.copytree(os.path.join(ASSETS, 'sel'), os.path.join(OUT, 'images', 'sel'), dirs_exist_ok=True)
open(os.path.join(OUT, 'favicon.svg'), 'w').write(FAVICON)
open(os.path.join(OUT, 'robots.txt'), 'w').write('User-agent: *\nAllow: /\n')
print('built', sorted(os.listdir(OUT)))
