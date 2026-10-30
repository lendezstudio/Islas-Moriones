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
    ('biker', 'Initial Images/Activities/pexels-enrico-musitelli-1035698384-34377533.jpg', None, (640, 1100)),
    ('vball', 'Initial Images/Pexels/pexels-helder-pereira-326724210-33490287.jpg', None, (640, 1100)),
    ('pingpong2', 'Initial Images/Pexels/pexels-haydar-acer-1111927873-33063727.jpg', None, (640, 1100)),
    ('darts2', 'Initial Images/Pexels/pexels-kevin-malik-8763232.jpg', (.1, 0, .8, 1), (800, 1200)),
    ('tents-bamboo', 'Assets from Client/October 30, 2026/images (2).jpg', None, (259,)),
    ('r-single-3', 'Assets from Client/October 30, 2026/room 4.jpg', MARK_P, (640, 1100)),
    ('r-single-bath2', 'Assets from Client/October 30, 2026/room 4 cr.jpg', MARK_P, (640, 1100)),
    ('r-single-bath3', 'Assets from Client/October 30, 2026/room 6 cr.jpg', MARK_P, (640, 1100)),
    ('r-superior-4', 'Assets from Client/October 30, 2026/room 5 (1).jpg', MARK_L, (800, 1424)),
    ('r-superior-bath2', 'Assets from Client/October 30, 2026/room 5 cr (1).jpg', MARK_P, (640, 1100)),
    ('r-superior-bath3', 'Assets from Client/October 30, 2026/room 2 cr.jpg', MARK_P, (640, 1100)),
    ('r-suite-bath2', 'Assets from Client/October 30, 2026/room 1 cr (1).jpg', MARK_P, (640, 1100)),
    ('r-suite-bath3', 'Assets from Client/October 30, 2026/room 8 cr.jpg', MARK_P, (640, 1100)),
    ('r-deluxe-4', 'Assets from Client/October 30, 2026/room 28 deluxe (1).jpg', MARK_P, (640, 1100)),
    ('r-deluxe-bath2', 'Assets from Client/October 30, 2026/room 28, cr.jpg', MARK_P, (640, 1100)),
    ('r-suiteloft-5', 'Assets from Client/October 30, 2026/room 25 suite loft.jpg', MARK_L, (800, 1424)),
    ('r-suiteloft-6', 'Assets from Client/October 30, 2026/room 25 suite loft (1).jpg', MARK_L, (800, 1424)),
    ('r-suiteloft-7', 'Assets from Client/October 30, 2026/room 26.jpg', MARK_L, (800, 1424)),
    ('r-suiteloft-8', 'Assets from Client/October 30, 2026/room 26 (1).jpg', MARK_P, (640, 1100)),
    ('r-suiteloft-9', 'Assets from Client/October 30, 2026/room 26 suite loft (1).jpg', MARK_P, (640, 1100)),
    ('r-suiteloft-10', 'Assets from Client/October 30, 2026/room 26, suite loft.jpg', MARK_P, (640, 1100)),
    ('r-suiteloft-11', 'Assets from Client/October 30, 2026/room 26, suite loft (1).jpg', MARK_L, (800, 1424)),
    ('r-suiteloft-bath2', 'Assets from Client/October 30, 2026/room 25 cr.jpg', MARK_P, (640, 1100)),
    ('r-suiteloft-bath3', 'Assets from Client/October 30, 2026/room 26 cr.jpg', MARK_P, (640, 1100)),
    ('r-exec-4', 'Assets from Client/October 30, 2026/room 27 executive loft (1).jpg', MARK_L, (800, 1424)),
    ('r-exec-bath2', 'Assets from Client/October 30, 2026/room 27 cr (1).jpg', MARK_P, (640, 1100)),
    ('ps-020', 'Assets from Client/October 30, 2026/pool suite room (1).HEIC', None, (800, 1200)),
    ('ps-021', 'Assets from Client/October 30, 2026/pool suite room (10).HEIC', None, (800, 1200)),
    ('ps-022', 'Assets from Client/October 30, 2026/pool suite room (11).HEIC', None, (800, 1200)),
    ('ps-023', 'Assets from Client/October 30, 2026/pool suite room (12).HEIC', None, (800, 1200)),
    ('ps-024', 'Assets from Client/October 30, 2026/pool suite room (13).HEIC', None, (800, 1200)),
    ('ps-025', 'Assets from Client/October 30, 2026/pool suite room (2).HEIC', None, (800, 1200)),
    ('ps-026', 'Assets from Client/October 30, 2026/pool suite room (3).HEIC', None, (800, 1200)),
    ('ps-027', 'Assets from Client/October 30, 2026/pool suite room (4).HEIC', None, (800, 1200)),
    ('ps-028', 'Assets from Client/October 30, 2026/pool suite room (5).HEIC', None, (800, 1200)),
    ('ps-029', 'Assets from Client/October 30, 2026/pool suite room (6).HEIC', None, (800, 1200)),
    ('ps-030', 'Assets from Client/October 30, 2026/pool suite room (7).HEIC', None, (800, 1200)),
    ('ps-031', 'Assets from Client/October 30, 2026/pool suite room (8).HEIC', None, (800, 1200)),
    ('ps-032', 'Assets from Client/October 30, 2026/pool suite room (9).HEIC', None, (800, 1200)),
    ('ps-033', 'Assets from Client/October 30, 2026/pool suite room.HEIC', None, (800, 1200)),
    ('ps-034', 'Assets from Client/October 30, 2026/pool suite room.HEIC.HEIC', None, (800, 1200)),
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
    ('maniwaya-cove',    'IMG_1188.HEIC', (0, .25, .62, .53), (800, 1300)),
    ('sandbar-boat',     'Screenshot 2025-12-20 at 12.26.39 AM.png', None, (738,)),
    ('sunset-boat-beach', 'edited-images/sunset-boat.jpg', (0, .22, .68, 1), (800, 1206)),
    # Client-labelled photos (Assets from Client/October 30, 2026)
    ('r-single-1', 'Assets from Client/October 30, 2026/room 3 single standard.jpg', MARK_L, (800, 1424)),
    ('r-single-2', 'Assets from Client/October 30, 2026/room 6, single standard.jpg', MARK_P, (640, 1100)),
    ('r-single-bath', 'Assets from Client/October 30, 2026/room 3 cr.jpg', MARK_P, (640, 1100)),
    ('r-deluxe-1', 'Assets from Client/October 30, 2026/room 23, deluxe.jpg', MARK_L, (800, 1424)),
    ('r-deluxe-2', 'Assets from Client/October 30, 2026/23, delux.jpg', MARK_P, (640, 1100)),
    ('r-deluxe-3', 'Assets from Client/October 30, 2026/room 28 deluxe.jpg', MARK_P, (640, 1100)),
    ('r-deluxe-bath', 'Assets from Client/October 30, 2026/23, cr.jpg', MARK_P, (640, 1100)),
    ('r-superior-1', 'Assets from Client/October 30, 2026/room 5 superior room.jpg', MARK_L, (800, 1424)),
    ('r-superior-2', 'Assets from Client/October 30, 2026/room 2, superior.jpg', MARK_L, (800, 1424)),
    ('r-superior-3', 'Assets from Client/October 30, 2026/room 5.jpg', MARK_L, (800, 1080)),
    ('r-superior-bath', 'Assets from Client/October 30, 2026/room 5 cr.jpg', MARK_P, (640, 1100)),
    ('r-suite-1', 'Assets from Client/October 30, 2026/room 1, suite.jpg', MARK_L, (800, 1424)),
    ('r-suite-2', 'Assets from Client/October 30, 2026/room 8 suite room.jpg', MARK_L, (800, 1424)),
    ('r-suite-bath', 'Assets from Client/October 30, 2026/room 1 cr.jpg', MARK_P, (640, 1100)),
    ('r-suiteloft-1', 'Assets from Client/October 30, 2026/room 25, suite loft.jpg', MARK_L, (800, 1424)),
    ('r-suiteloft-2', 'Assets from Client/October 30, 2026/room 24, suite loft.jpg', MARK_L, (800, 1424)),
    ('r-suiteloft-3', 'Assets from Client/October 30, 2026/room 26 suite loft.jpg', MARK_L, (800, 1424)),
    ('r-suiteloft-4', 'Assets from Client/October 30, 2026/suite loft 24.jpg', MARK_L, (800, 1424)),
    ('r-loftbeds', 'Assets from Client/October 30, 2026/loft beds .jpg', MARK_L, (800, 1424)),
    ('r-suiteloft-bath', 'Assets from Client/October 30, 2026/room 24, cr.jpg', MARK_P, (640, 1100)),
    ('r-exec-1', 'Assets from Client/October 30, 2026/room 27, executive loft.jpg', MARK_P, (640, 1100)),
    ('r-exec-2', 'Assets from Client/October 30, 2026/room 27 executive loft.jpg', MARK_L, (800, 1424)),
    ('r-exec-3', 'Assets from Client/October 30, 2026/loft (every suite loft and executive).jpg', MARK_L, (800, 1424)),
    ('r-exec-bath', 'Assets from Client/October 30, 2026/room 27 cr.jpg', MARK_P, (640, 1100)),
    ('kubo-ext2', 'Assets from Client/October 30, 2026/20910854c5c0d67368b83fc7afb197a13e21c86f.jpg', None, (705,)),
    ('kubo-lounge2', 'Assets from Client/October 30, 2026/KUBO.HEIC', None, (800, 1200)),
    ('kubo-bed2', 'Assets from Client/October 30, 2026/KUBO.JPG', None, (800, 1080)),
    ('kubo-living2', 'Assets from Client/October 30, 2026/KUBO (1).JPG', None, (800, 1071)),
    ('kayak-sign', 'Assets from Client/October 30, 2026/526872481.jpg', None, (576,)),
    ('maniwaya-aerial', 'Assets from Client/October 30, 2026/Marinduque-1-edited-scaled.jpg', None, (800, 1600)),
    ('rock-cove', 'Assets from Client/October 30, 2026/rock-formation.jpg', None, (800, 1200)),
    ('snorkel2', 'Assets from Client/October 30, 2026/pexels-pixabay-163313.jpg', None, (800, 1400)),
    ('sea-rocks', 'Assets from Client/October 30, 2026/images (3).jpg', None, (554,)),
    ('snorkel3', 'Assets from Client/October 30, 2026/pexels-thomas-balabaud-735585-6507342.jpg', None, (800, 1400)),
    ('sandbar-hop', 'image (1) (1).png', None, (800, 1080)),
    ('deck-table', 'Assets from Client/October 30, 2026/203add1d0cc6e9e797221bf8adcd6392bb06b5e0.jpg', (0, 0, 1, .76), (705,)),
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
    path = os.path.join(ROOT, *name.split('/')) if ('/' in name) else os.path.join(NEW, name)
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
