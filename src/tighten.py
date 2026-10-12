"""Set each lockup's viewBox to the true ink box plus equal padding (0.25 x font size of 'dwg')."""
import asyncio, os, re, glob
from PIL import Image
from playwright.async_api import async_playwright
HERE=os.path.dirname(os.path.abspath(__file__)); D=os.path.join(HERE,'dist')
PAD={'primary':90*0.25,'horizontal':45*0.25,'wordmark':90*0.25}
K=4
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page()
        for kind in PAD:
            base=os.path.join(D,f'dwg7-{kind}.svg'); s=open(base).read()
            vb=[float(v) for v in re.search(r'viewBox="([^"]+)"',s).group(1).split()]
            W,H=round(vb[2]*K),round(vb[3]*K)
            await pg.set_viewport_size({'width':W,'height':H})
            open(os.path.join(HERE,'_t.html'),'w').write(f'<html><body style="margin:0"><img src="file://{base}" style="display:block;width:{W}px;height:{H}px"></body></html>')
            await pg.goto('file://'+os.path.join(HERE,'_t.html')); await pg.wait_for_load_state('load')
            await pg.screenshot(path=os.path.join(HERE,'_t.png'),omit_background=True)
            x0,y0,x1,y1=Image.open(os.path.join(HERE,'_t.png')).split()[-1].getbbox()
            pad=PAD[kind]
            nx,ny=vb[0]+x0/K-pad, vb[1]+y0/K-pad
            nw,nh=(x1-x0)/K+2*pad,(y1-y0)/K+2*pad
            for f in glob.glob(os.path.join(D,f'dwg7-{kind}*.svg')):
                t=open(f).read()
                t=re.sub(r'viewBox="[^"]+" width="[^"]+" height="[^"]+"',f'viewBox="{nx:.2f} {ny:.2f} {nw:.2f} {nh:.2f}" width="{nw:.0f}" height="{nh:.0f}"',t,count=1)
                t=re.sub(r'<rect x="[^"]+" y="[^"]+" width="[^"]+" height="[^"]+"',f'<rect x="{nx:.2f}" y="{ny:.2f}" width="{nw:.2f}" height="{nh:.2f}"',t)
                open(f,'w').write(t)
            print(kind, round(nw,1), round(nh,1))
        await b.close()
asyncio.run(main())
