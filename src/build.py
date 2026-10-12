"""Build outlined (font-free) SVG assets for the dwg7 logo v0.6.

Layout is measured in Chromium from the same CSS used for the v0.6 design,
so glyph positions (including kerning and letter-spacing) match exactly.
Glyph outlines come from Sora 500 and IBM Plex Mono 400 (SIL OFL 1.1).
"""
import asyncio, json, os, sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, '..', 'fonts')
SORA = os.path.join(FONTS, 'sora-latin-500-normal.woff')
PLEX = os.path.join(FONTS, 'ibm-plex-mono-latin-400-normal.woff')
OUT = os.path.join(HERE, 'dist')

BLUE = '#1E5AA0'
INK = '#13233A'
SEVEN = 'M4 17 H62 L30 88'          # viewBox 0 0 74 92, stroke 13, miter
SEVEN_SMALL = 'M6 15 H64 L30 90'    # for 16px icons, stroke 18

fonts = {'sora': TTFont(SORA), 'plex': TTFont(PLEX)}

def glyph_path(font, ch, x, y, size):
    f = fonts[font]
    upm = f['head'].unitsPerEm
    gs = f.getGlyphSet()
    name = f.getBestCmap()[ord(ch)]
    s = size / upm
    pen = SVGPathPen(gs)
    gs[name].draw(TransformPen(pen, (s, 0, 0, -s, x, y)))
    return pen.getCommands()

PAGE = """<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:Sora;font-weight:500;src:url(file://%s)}
@font-face{font-family:Plex;font-weight:400;src:url(file://%s)}
body{margin:0;font-family:Plex}
.wm{display:inline-flex;align-items:baseline;font-family:Sora;font-weight:500;line-height:1;letter-spacing:-0.03em}
.k{display:inline-flex;margin-left:-0.2em}
.bl{display:inline-block;width:0;height:0}
</style></head><body><div id="root" style="position:absolute;left:0;top:0"></div><script>
const S=(w,h)=>'<svg id="seven" width="'+w+'" height="'+h+'" viewBox="0 0 74 92" style="display:block"><path d="M4 17 H62 L30 88" fill="none" stroke="#000" stroke-width="13"/></svg>';
window.layout=(kind,f,h,t,gap)=>{
  const wm='<div class="wm" style="font-size:'+f+'px"><span id="dwg">dwg<span class="bl" id="bl1"></span></span><span class="k">'+S(Math.round(h*74/92),h)+'</span></div>';
  const tg=t?'<div id="tag" style="font-size:'+t+'px">test new technologies.<span class="bl" id="bl2"></span></div>':'';
  let html;
  if(kind==='primary') html='<div style="display:flex;flex-direction:column;gap:'+gap+'px">'+wm+tg+'</div>';
  else if(kind==='horizontal') html='<div style="display:flex;align-items:baseline;gap:'+gap+'px">'+wm+tg+'</div>';
  else html=wm;
  document.getElementById('root').innerHTML=html;
  const pos=(el)=>{const out=[];const n=el.firstChild;for(let i=0;i<n.length;i++){const r=document.createRange();r.setStart(n,i);r.setEnd(n,i+1);out.push([n.data[i],r.getBoundingClientRect().left]);}return out;};
  const res={dwg:pos(document.getElementById('dwg')),base1:document.getElementById('bl1').getBoundingClientRect().top,seven:document.getElementById('seven').getBoundingClientRect().toJSON()};
  if(t){res.tag=pos(document.getElementById('tag'));res.base2=document.getElementById('bl2').getBoundingClientRect().top;}
  return res;
};
document.fonts.load('500 10px Sora').then(()=>document.fonts.load('10px Plex')).then(()=>document.title='ready');
</script></body></html>"""

async def measure(specs):
    page_path = os.path.join(HERE, 'measure.html')
    open(page_path, 'w').write(PAGE % (os.path.abspath(SORA).replace('.woff', '.woff2'), os.path.abspath(PLEX).replace('.woff', '.woff2')))
    out = {}
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page()
        await pg.goto('file://' + page_path)
        await pg.wait_for_function("document.title==='ready'")
        for key, spec in specs.items():
            out[key] = await pg.evaluate('([k,f,h,t,g])=>layout(k,f,h,t,g)', spec)
        await b.close()
    return out

def lockup_svg(m, f, t, wm_color, tag_color, pad, bg=None):
    parts_wm, parts_tag = [], []
    for ch, x in m['dwg']:
        parts_wm.append(glyph_path('sora', ch, x, m['base1'], f))
    sv = m['seven']
    sx, sy = sv['width'] / 74, sv['height'] / 92
    seven = (f'<path d="{SEVEN}" fill="none" stroke="{wm_color}" stroke-width="13" '
             f'stroke-linejoin="miter" transform="translate({sv["x"]:.3f} {sv["y"]:.3f}) scale({sx:.5f} {sy:.5f})"/>')
    if t:
        for ch, x in m['tag']:
            if ch != ' ':
                parts_tag.append(glyph_path('plex', ch, x, m['base2'], t))
    # bounds: use measured boxes (ink extents approximated by layout boxes)
    xs = [m['dwg'][0][1], sv['x'] + sv['width']]
    top = sv['y']
    bottom = m['base1'] + f * 0.24  # descender of g
    if t:
        last = m['tag'][-1][1] + t * 0.6
        xs.append(last)
        bottom = max(bottom, m['base2'] + t * 0.25)
    x0, x1 = min(xs) - pad, max(xs) + pad
    y0, y1 = top - pad, bottom + pad
    w, h = x1 - x0, y1 - y0
    body = ''
    if bg:
        body += f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{bg}"/>'
    body += f'<path d="{"".join(parts_wm)}" fill="{wm_color}"/>' + seven
    if t:
        body += f'<path d="{"".join(parts_tag)}" fill="{tag_color}"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.2f} {y0:.2f} {w:.2f} {h:.2f}" '
            f'width="{w:.0f}" height="{h:.0f}" role="img" aria-label="dwg7 — test new technologies.">'
            f'<title>dwg7</title>{body}</svg>\n')

def icon_svg(size_class='standard', bg=BLUE, fg='#FFFFFF'):
    # 128-unit artboard, radius 22% as in v0.6
    if size_class == 'small':
        w7, h7, d, sw = 128 * 0.56, 128 * 0.69, SEVEN_SMALL, 18
    else:
        w7, h7, d, sw = 128 * 0.49, 128 * 0.61, SEVEN, 13
    x, y = (128 - w7) / 2, (128 - h7) / 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="128" height="128" role="img" aria-label="dwg7">'
            f'<title>dwg7</title><rect width="128" height="128" rx="28" fill="{bg}"/>'
            f'<path d="{d}" fill="none" stroke="{fg}" stroke-width="{sw}" stroke-linejoin="miter" '
            f'transform="translate({x:.3f} {y:.3f}) scale({w7/74:.5f} {h7/92:.5f})"/></svg>\n')

def mark_svg(color=BLUE):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 74 92" width="74" height="92" role="img" aria-label="dwg7">'
            f'<title>dwg7</title><path d="{SEVEN}" fill="none" stroke="{color}" stroke-width="13" stroke-linejoin="miter"/></svg>\n')

def main():
    os.makedirs(OUT, exist_ok=True)
    specs = {
        'primary': ['primary', 90, 114, 20, 18],
        'horizontal': ['horizontal', 45, 57, 18, 22],
        'wordmark': ['wordmark', 90, 114, 0, 0],
    }
    m = asyncio.run(measure(specs))
    json.dump(m, open(os.path.join(HERE, 'measure.json'), 'w'), indent=1)
    DARK_WM = sys.argv[1] if len(sys.argv) > 1 else '#6FA8E8'
    variants = {
        # name: (wordmark color, tagline color, background)
        '': (BLUE, INK, None),
        '-mono-black': ('#111111', '#111111', None),
        '-mono-white': ('#FFFFFF', '#FFFFFF', None),
        '-reversed': ('#FFFFFF', '#FFFFFF', BLUE),
        '-dark': (DARK_WM, '#E6EDF3', None),
    }
    for kind, (_, f, _, t, _) in specs.items():
        for suf, (wc, tc, bg) in variants.items():
            open(os.path.join(OUT, f'dwg7-{kind}{suf}.svg'), 'w').write(
                lockup_svg(m[kind], f, t, wc, tc, pad=f * 0.25, bg=bg))
    open(os.path.join(OUT, 'dwg7-icon.svg'), 'w').write(icon_svg())
    open(os.path.join(OUT, 'dwg7-icon-small.svg'), 'w').write(icon_svg('small'))
    open(os.path.join(OUT, 'dwg7-mark.svg'), 'w').write(mark_svg())
    print('ok')

if __name__ == '__main__':
    main()
