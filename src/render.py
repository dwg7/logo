"""Render PNG/ICO from the outlined SVGs, and a verification sheet."""
import asyncio, os, glob
from PIL import Image
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, 'dist')
PNG = os.path.join(DIST, 'png')

async def svg_to_png(pg, svg, out, width=None, height=None, scale=1):
    src = open(svg).read()
    import re
    vb = re.search(r'viewBox="([^"]+)"', src).group(1).split()
    vw, vh = float(vb[2]), float(vb[3])
    if width and not height:
        height = round(width * vh / vw)
    if height and not width:
        width = round(height * vw / vh)
    await pg.set_viewport_size({'width': width, 'height': height})
    html = ('<html><body style="margin:0;background:transparent">'
            f'<img src="file://{svg}" style="display:block;width:{width}px;height:{height}px"></body></html>')
    tmp = os.path.join(HERE, '_r.html'); open(tmp, 'w').write(html)
    await pg.goto('file://' + tmp)
    await pg.wait_for_load_state('load')
    await pg.screenshot(path=out, omit_background=True)

async def main():
    os.makedirs(PNG, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(device_scale_factor=1)
        for svg in sorted(glob.glob(os.path.join(DIST, 'dwg7-*.svg'))):
            name = os.path.basename(svg)[:-4]
            if name.startswith('dwg7-icon'):
                sizes = [16, 32, 48] if name.endswith('small') else [64, 128, 180, 256, 512]
                for s in sizes:
                    await svg_to_png(pg, svg, os.path.join(PNG, f'{name}-{s}.png'), width=s, height=s)
            elif name == 'dwg7-mark':
                await svg_to_png(pg, svg, os.path.join(PNG, f'{name}-512.png'), height=512)
            else:
                for w in [600, 1200]:
                    await svg_to_png(pg, svg, os.path.join(PNG, f'{name}-{w}w.png'), width=w)
        await b.close()
    # favicon.ico: small mark at 16/32/48, standard at 64
    imgs = [Image.open(os.path.join(PNG, f'dwg7-icon-small-{s}.png')) for s in (16, 32, 48)]
    imgs[2].save(os.path.join(DIST, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)], append_images=imgs[:2])
    print('ok')

asyncio.run(main())
