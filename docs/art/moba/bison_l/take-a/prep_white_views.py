"""Separate the existing design into four white modeling inputs, without redrawing."""
from pathlib import Path
import hashlib
import json
import zipfile

import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'white_views'
OUT.mkdir(exist_ok=True)
source = ROOT / 'sheet_raw.png'
im = Image.open(source).convert('RGB')
rgb = np.array(im)
r, g, b = np.moveaxis(rgb.astype(float), -1, 0)
magenta = (r > 100) & (b > 100) & (g < np.minimum(r, b) * .60) & (b > r * .65)
labels, _ = ndimage.label(~magenta, structure=np.ones((3, 3), dtype=bool))
counts = np.bincount(labels.ravel())
counts[0] = 0
objects = ndimage.find_objects(labels)
parts = {}
for index in np.argsort(counts)[-4:]:
    ys, xs = objects[index - 1]
    cy, cx = ndimage.center_of_mass(~magenta, labels, int(index))
    name = ('front' if cx < im.width / 2 else 'left') if cy < im.height / 2 else ('back' if cx < im.width / 2 else 'right')
    crop = rgb[ys, xs].copy()
    crop[labels[ys, xs] != index] = 255
    parts[name] = (Image.fromarray(crop), [xs.start, ys.start, xs.stop, ys.stop])
assert set(parts) == {'front', 'left', 'back', 'right'}
side, feet = 1024, 936
scale = 832 / max(part.width for part, _ in parts.values())
report = {'source': source.name, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'canvas': [side, side], 'shared_scale': scale, 'feet_baseline_exclusive': feet,
          'method': 'Existing art separated by connected components; magenta to white; common nearest-neighbour scale. No generation.',
          'views': {}}
for name in ['front', 'left', 'back', 'right']:
    part, box = parts[name]
    size = (round(part.width * scale), round(part.height * scale))
    big = part.resize(size, Image.Resampling.NEAREST)
    x, y = (side - big.width) // 2, feet - big.height
    assert x >= 64 and y >= 64
    sheet = Image.new('RGB', (side, side), 'white')
    sheet.paste(big, (x, y))
    name_out = f'bison_{name}.png'
    sheet.save(OUT / name_out)
    report['views'][name] = {'file': name_out, 'source_box': box, 'output_box': [x, y, x+big.width, feet]}
    check = np.array(Image.open(OUT / name_out))
    assert check.shape == (1024, 1024, 3)
    assert np.all(check[:64] == 255) and np.all(check[-64:] == 255)
(OUT / 'prep.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
with zipfile.ZipFile(OUT / 'bison_four_white_views.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for name in report['views']:
        file = OUT / report['views'][name]['file']
        archive.write(file, arcname=file.name)
board = Image.new('RGB', (1024, 1024), 'white')
for name, xy in [('front', (0,0)), ('left', (512,0)), ('back', (0,512)), ('right', (512,512))]:
    panel = Image.open(OUT / f'bison_{name}.png').resize((512,512), Image.Resampling.NEAREST)
    board.paste(panel, xy)
board.save(OUT / 'review.png')
print(json.dumps(report, indent=2))
