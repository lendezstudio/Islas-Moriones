"""Version 5 image derivatives from 'Assets from Client/October 26, 2026' (and earlier folders).
- Originals are never modified.
- 'crop' (left, top, right, bottom as fractions) removes the phone's "vivo Y27 / date" mark in the
  bottom-left corner of staff photos; full-size cleaned copies go to edited-images/v5/.
- Web derivatives (JPEG + WebP) go to assets/img/v5/.
Run from the project root:  python _tools/build_v5_images.py
"""
import os, subprocess, tempfile
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEW = os.path.join(ROOT, 'Assets from Client', 'October 26, 2026')
OUT = os.path.join(ROOT, 'assets', 'img', 'v5')
CLEAN = os.path.join(ROOT, 'edited-images', 'v5')
os.makedirs(OUT, exist_ok=True); os.makedirs(CLEAN, exist_ok=True)

MARK_L = (0, 0, 1, .89)   # landscape staff photo: trim the bottom strip holding the phone mark
MARK_P = (0, 0, 1, .92)   # portrait staff photo

# id, source file, crop, output widths
JOBS = [
    # The resort
    ('dusk-pool',        'IMG_1857 2.JPG', None, (640, 1215)),
    ('main-building',    'viber_image_2026-10-20_16-40-24-711.jpg', MARK_P, (640, 1200)),
    ('lobby-lounge',     'viber_image_2026-10-21_06-38-24-660.jpg', MARK_L, (800, 1424)),
    ('reception',        'viber_image_2026-10-21_08-30-39-336.jpg', MARK_P, (640, 1200)),
    ('beach-palms',      'viber_image_2026-10-21_08-43-10-706.jpg', MARK_L, (800, 1424)),
    ('tower-blue',       'viber_image_2026-10-21_08-43-10-998.jpg', MARK_P, (640, 1200)),
    ('tower-wide',       'viber_image_2026-10-21_08-43-11-069.jpg', MARK_L, (800, 1424)),
    ('tower-storm',      'IMG_8835.HEIC', None, (640, 1100)),
    ('palms-sky',        'IMG_1077.HEIC', None, (640, 1100)),
    ('corridor',         'viber_image_2026-10-20_16-40-23-831.jpg', MARK_P, (640, 1200)),
    # Pool Suite Room (matches the Pool Suite photo on the resort's own rate sheet)
    ('poolsuite-room',   'IMG_2159 2.HEIC', None, (800, 1200)),
    ('poolsuite-bed',    'IMG_2160 2.HEIC', None, (800, 1200)),
    ('poolsuite-bar',    'IMG_2161 2.HEIC', None, (800, 1200)),
    ('poolsuite-pantry', 'IMG_2162 2.HEIC', None, (800, 1200)),
    ('poolsuite-family', 'IMG_2168 2.HEIC', None, (800, 1200)),
    ('poolsuite-loft',   'IMG_2171.HEIC', None, (800, 1200)),
    ('poolsuite-bath',   'IMG_2166 2.HEIC', None, (800, 1200)),
    # Luxury Kubo
    ('kubo-exterior',    'IMG_1068.HEIC', None, (640, 1100)),
    ('kubo-living',      'IMG_2176.HEIC', None, (800, 1200)),
    ('kubo-bedroom',     'IMG_2181 2.JPG', None, (800, 1080)),
    ('kubo-loftbeds',    'IMG_2183 2.JPG', None, (800, 1080)),
    ('kubo-bath',        'IMG_2182 2.JPG', None, (640, 976)),
    # Main-building rooms (matched by bed set-up to the rate sheets; see notes)
    ('room-single',      'viber_image_2026-10-20_18-20-57-643.jpg', MARK_L, (800, 1424)),
    ('room-superior',    'viber_image_2026-10-20_18-42-48-996.jpg', MARK_L, (800, 1424)),
    ('room-deluxe',      'viber_image_2026-10-20_16-41-17-547.jpg', MARK_L, (800, 1424)),
    ('room-suiteloft',   'viber_image_2026-10-20_16-45-33-108.jpg', MARK_L, (800, 1424)),
    ('room-execloft',    'viber_image_2026-10-20_17-15-20-146.jpg', MARK_P, (640, 1200)),
    ('room-loftsingles', 'viber_image_2026-10-20_17-06-58-304.jpg', MARK_L, (800, 1424)),
    ('room-bath',        'viber_image_2026-10-20_16-44-51-697.jpg', MARK_P, (640, 1200)),
    # Tents
    ('tent',             '309AD28B-9FEB-4664-9C5C-4FA98A62EBED.heic', None, (640, 1100)),
    # Campsite tents: the resort's social post; crop inside the white frame line and above the logo/text
    ('tents-campsite',   'Initial Images/469518456_605136372186168_174922518552061940_n.jpg', (72/1080, 54/1080, 1008/1080, 932/1080), (800, 936)),
    # Water and island
    ('kayak-clear',      'IMG_2380.HEIC', None, (640, 1100)),
    ('kayak-clear-2',    'IMG_2372.HEIC', None, (640, 1100)),
    ('boat-longinus',    'IMG_9169.JPG', MARK_L, (800, 1424)),
    ('boat-rogelius',    'IMG_9170.JPG', MARK_L, (800, 1424)),
    ('boat-omon',        'IMG_9171.JPG', MARK_L, (800, 1424)),
    ('ecart',            'RESORT PRINTABLES (2).png', None, (640, 1200)),
    ('bikes',            'IMG_1159.jpg', None, (640, 1100)),
    ('bikes-crop',       'IMG_1159.jpg', (0, .40, 1, 1), (800, 1400)),
    ('kayak-pov',        'IMG_2380.HEIC', (0, .50, 1, 1), (800, 1400)),
    ('kayak-pov-2',      'IMG_2372.HEIC', (0, .50, 1, 1), (800, 1400)),
    ('ungab',            'IMG_4354.heic', None, (640, 1100)),
    ('ungab-arch',       'IMG_4355.heic', None, (640, 1100)),
    ('sandbar-aerial',   'image (1).png', None, (800, 1080)),
    ('reef-raft',        'Screenshot 2025-10-02 at 8.57.18 AM.png', None, (572,)),
    ('maniwaya-rocks',   'IMG_1156.jpg', None, (640, 1100)),
    ('pingpong-darts',   'viber_image_2026-10-20_16-40-24-808.jpg', MARK_L, (800, 1424)),
    ('darts',            '1df6a445c2cbbc474487db571a2e7874.jpg', None, (600,)),
    ('kayak-float',      '37d7ae8d44e5e5d5804f941192a827ea.jpg', None, (895,)),
    # Photos extracted from ISLAS BROCHURE 2026 (1).pdf (pypdf) into edited-images/brochure/
    ('pool-loungers',    'edited-images/brochure/pool-loungers.jpg', None, (640, 908)),
    ('main-palms',       'edited-images/brochure/main-building-palms.jpg', None, (800, 1210)),
    ('resort-sign',      'edited-images/brochure/resort-sign.jpg', None, (800, 1600)),
    ('morion-statues',   'edited-images/brochure/morion-statues.jpg', None, (540,)),
    ('century-tree-b',   'edited-images/brochure/century-cliff-tree.jpg', None, (768,)),
    ('sunong-bato-b',    'edited-images/brochure/sunong-bato.jpg', None, (756,)),
    ('beach-loungers',   'viber_image_2026-10-21_08-43-10-768.jpg', MARK_L, (800, 1424)),
    ('bonfire-smores',   '749f2544-eec8-425f-98f1-c7b7e0e02762-md.jpeg', None, (800,)),
    ('badminton',        '69d30c820f458aa14e24c2487352050a.jpg', None, (640, 736)),
    # The Genesis Events Place
    ('genesis-hall',     'IMG_1212.HEIC', None, (800, 1200)),
    ('genesis-tables',   'IMG_1213.HEIC', None, (800, 1200)),
    ('genesis-setup',    'IMG_1216.HEIC', None, (800, 1200)),
    ('genesis-dinner',   'IMG_1225.heic', None, (800, 1200)),
    ('genesis-lawn',     'IMG_1250.heic', None, (800, 1200)),
    ('genesis-front',    'IMG_1249.heic', None, (800, 1200)),
    # Dining
    ('skylight',         'viber_image_2026-10-20_16-40-23-113.jpg', MARK_L, (800, 1424)),
    ('skylight-2',       'viber_image_2026-10-20_16-40-23-429.jpg', MARK_L, (800, 1424)),
]

def load(name):
    path = os.path.join(ROOT, name) if ('/' in name) else os.path.join(NEW, name)
    if not os.path.exists(path):  # some filenames contain a narrow no-break space
        key = name.replace(' ', '').lower()
        match = [f for f in os.listdir(NEW) if f.replace(' ', '').replace(' ', '').lower() == key]
        path = os.path.join(NEW, match[0])
    if name.lower().endswith('.heic'):
        tmp = os.path.join(tempfile.gettempdir(), 'v5_heic.png')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', path, '-frames:v', '1', tmp], check=True)
        return Image.open(tmp).convert('RGB')
    return ImageOps.exif_transpose(Image.open(path)).convert('RGB')

manifest = []
for jid, src, crop, widths in JOBS:
    im = load(src)
    W, H = im.size
    if crop:
        l, t, r, b = crop
        im = im.crop((round(l * W), round(t * H), round(r * W), round(b * H)))
        im.save(os.path.join(CLEAN, jid + '.jpg'), quality=92)
    sizes = []
    for w in widths:
        w = min(w, im.width)
        h = round(im.height * w / im.width)
        r = im.resize((w, h), Image.LANCZOS)
        r.save(os.path.join(OUT, f'{jid}-{w}.jpg'), quality=80, optimize=True, progressive=True)
        r.save(os.path.join(OUT, f'{jid}-{w}.webp'), quality=78, method=5)
        sizes.append(f'{w}x{h}')
    manifest.append(f'{jid}|{" ".join(sizes)}|{src}')
with open(os.path.join(OUT, 'manifest.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(manifest) + '\n')
print(len(manifest), 'images')
