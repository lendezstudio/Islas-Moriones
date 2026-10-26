"""Labeled contact sheets for visual review. Usage: python contact_sheet.py <img_dir> <out_dir> [cols] [rows]"""
import os, sys
from PIL import Image, ImageDraw

src, out = sys.argv[1], sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 5
rows = int(sys.argv[4]) if len(sys.argv) > 4 else 4
cell, lab = 336, 22
os.makedirs(out, exist_ok=True)
files = sorted(f for f in os.listdir(src) if f.lower().endswith('.jpg'))
per = cols * rows
for s in range(0, len(files), per):
    sheet = Image.new('RGB', (cols * cell, rows * (cell + lab)), (40, 40, 40))
    d = ImageDraw.Draw(sheet)
    for k, f in enumerate(files[s:s + per]):
        im = Image.open(os.path.join(src, f)); im.thumbnail((cell - 6, cell - 6))
        x = (k % cols) * cell; y = (k // cols) * (cell + lab)
        sheet.paste(im, (x + (cell - im.width) // 2, y + lab + (cell - im.height) // 2))
        d.text((x + 4, y + 4), os.path.splitext(f)[0], fill=(255, 230, 0))
    sheet.save(os.path.join(out, f"sheet{s // per + 1:02d}.jpg"), quality=82)
print('sheets:', (len(files) + per - 1) // per)
