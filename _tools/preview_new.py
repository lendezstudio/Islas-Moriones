"""Make 1600px previews of every image in a client folder (HEIC via ffmpeg), plus a size manifest.
Originals are never modified. Usage: python preview_new.py <src_dir> <out_dir>"""
import subprocess, sys, os, tempfile
from PIL import Image, ImageOps

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
rows = []
files = sorted(f for f in os.listdir(src) if f.lower().endswith(('.heic', '.jpg', '.jpeg', '.png')))
for i, name in enumerate(files, 1):
    pid = f"n{i:03d}"
    path = os.path.join(src, name)
    try:
        if name.lower().endswith('.heic'):
            tmp = os.path.join(tempfile.gettempdir(), f"heic_{pid}.png")
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', path, '-frames:v', '1', tmp], check=True)
            im = Image.open(tmp)
        else:
            im = Image.open(path)
            im = ImageOps.exif_transpose(im)
        w, h = im.size
        im = im.convert('RGB')
        im.thumbnail((1600, 1600))
        im.save(os.path.join(out, pid + '.jpg'), quality=85)
        rows.append(f"{pid}|{w}x{h}|{name}")
    except Exception as e:
        rows.append(f"{pid}|ERROR {e}|{name}")
with open(os.path.join(out, 'map.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(rows) + '\n')
print('\n'.join(rows))
