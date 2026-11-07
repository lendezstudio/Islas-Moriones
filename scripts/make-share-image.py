"""Social share preview (Open Graph) for Islas Moriones Beach Resort.

Builds one 1200 x 630 JPG from one real resort photo. The photo stays sharp except where a
frosted, softly faded area carries the official logo and two lines of text. The page is
rendered with Playwright (so the site's own Google Fonts are used), then saved as an
optimised JPG with Pillow.

Layout: the picnic by the clear cove, with a light frosted haze in the centre carrying
the logo, "Come for the island, stay for the memories." and "Maniwaya Island, Marinduque".
Centred, so the text survives apps that crop the thumbnail to a square.

Run from the project root:  python scripts/make-share-image.py [output.jpg]
Needs: pip install playwright pillow  and  python -m playwright install chromium
"""
import base64, io, os, sys
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO = os.path.join(ROOT, 'assets', 'brand', 'logo-islas-moriones-teal-760.png')  # official logo, used as is
OUT = os.path.join(ROOT, 'assets', 'share', 'islas-moriones-share-v2.jpg')
W, H = 1200, 630
MAX_BYTES = 300 * 1024

def data_uri(path, mime):
    with open(path, 'rb') as f:
        return f'data:{mime};base64,' + base64.b64encode(f.read()).decode()

FONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;600&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=block">'
BASE = f'html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; }}'

def layout():
    photo = os.path.join(ROOT, 'assets', 'img', 'v5', 'n-picnic-1400.jpg')  # picnic by the clear cove, as used in the gallery
    # light frosted area in the centre of the image, fading softly on every side
    return f'''<style>{BASE}
  .photo {{ position: absolute; inset: 0; background: url({data_uri(photo, 'image/jpeg')}) 50% 40% / cover no-repeat; }}
  .frost {{ position: absolute; left: 230px; top: 110px; width: 740px; height: 410px;
    backdrop-filter: blur(4px); -webkit-backdrop-filter: blur(4px);
    background: rgba(247, 242, 233, .55);
    -webkit-mask-image: radial-gradient(closest-side, #000 62%, transparent 100%);
            mask-image: radial-gradient(closest-side, #000 62%, transparent 100%); }}
  .copy {{ position: absolute; inset: 0; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; }}
  .copy img {{ width: 300px; height: auto; display: block; }}
  .line {{ margin: 22px 0 0; font: italic 400 33px/1.18 Newsreader, Georgia, serif; color: #1F2421; }}
  .where {{ margin-top: 16px; font: 600 18px/1.4 Manrope, 'Segoe UI', sans-serif; color: #135B56; letter-spacing: .05em; }}
</style></head><body>
  <div class="photo"></div><div class="frost"></div>
  <div class="copy">
    <img src="{data_uri(LOGO, 'image/png')}" alt="">
    <p class="line">Come for the island,<br>stay for the memories.</p>
    <div class="where">Maniwaya Island, Marinduque</div>
  </div>'''

def render(layout, out):
    html = f'<!doctype html><html><head><meta charset="utf-8">{FONTS}{layout()}</body></html>'
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': W, 'height': H}, device_scale_factor=1)
        page.set_content(html, wait_until='networkidle')
        page.evaluate('document.fonts.ready')
        png = page.screenshot(type='png')
        browser.close()
    im = Image.open(io.BytesIO(png)).convert('RGB')
    assert im.size == (W, H), im.size
    os.makedirs(os.path.dirname(out), exist_ok=True)
    for q in (90, 88, 86, 84, 82, 80, 78, 75, 72, 70):
        buf = io.BytesIO()
        im.save(buf, 'JPEG', quality=q, optimize=True, progressive=True, subsampling='4:4:4' if q >= 86 else '4:2:0')
        if buf.tell() <= MAX_BYTES:
            break
    with open(out, 'wb') as f:
        f.write(buf.getvalue())
    print(f'{os.path.relpath(out, ROOT)}  {W}x{H}  {buf.tell() // 1024} KB  (quality {q})')

if __name__ == '__main__':
    out = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else OUT
    render(layout, out)
