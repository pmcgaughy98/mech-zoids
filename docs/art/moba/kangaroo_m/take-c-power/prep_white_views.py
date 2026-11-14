"""Package one generated reference as four white modeling sheets, no redraw."""
from pathlib import Path
import hashlib
import json
import zipfile
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'white_views'
OUT.mkdir(exist_ok=True)
source = ROOT / 'sheet_raw.png'
im = Image.open(source).convert('RGBA')
rgba = np.array(im)
mask = rgba[:, :, 3] >= 128
labels, _ = ndimage.label(mask, structure=np.ones((3, 3), dtype=bool))
counts = np.bincount(labels.ravel())
counts[0] = 0
objects = ndimage.find_objects(labels)
parts = {}
for index in np.argsort(counts)[-4:]:
    ys, xs = objects[index - 1]
    cy, cx = ndimage.center_of_mass(mask, labels, int(index))
    name = ('front' if cx < im.width / 2 else 'left') if cy < im.height / 2 else ('back' if cx < im.width / 2 else 'right')
    crop = rgba[ys, xs].copy()
    crop[:, :, 3] = np.where(labels[ys, xs] == index, crop[:, :, 3], 0)
    parts[name] = (Image.fromarray(crop), [xs.start, ys.start, xs.stop, ys.stop])
assert set(parts) == {'front', 'left', 'back', 'right'}
side, feet = 1024, 936
scale = min(832 / max(part.width for part, _ in parts.values()),
            832 / max(part.height for part, _ in parts.values()))
report = {'source': source.name, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'canvas': [side, side], 'shared_scale': scale, 'feet_baseline_exclusive': feet,
          'method': 'Four largest alpha>=128 components; preserve interior alpha; composite on white at one nearest-neighbour scale. Low-opacity external halo excluded.',
          'views': {}}
for name in ['front', 'left', 'back', 'right']:
    part, box = parts[name]
    big = part.resize((round(part.width * scale), round(part.height * scale)), Image.Resampling.NEAREST)
    x, y = (side - big.width) // 2, feet - big.height
    assert x >= 64 and y >= 64
    sheet = Image.new('RGBA', (side, side), 'white')
    sheet.alpha_composite(big, (x, y))
    name_out = f'kangaroo_{name}.png'
    sheet.convert('RGB').save(OUT / name_out)
    report['views'][name] = {'file': name_out, 'source_box': box,
                            'source_dimensions': list(part.size),
                            'output_box': [x, y, x+big.width, feet]}
    check = np.array(Image.open(OUT / name_out))
    assert check.shape == (1024, 1024, 3)
    assert np.all(check[:64] == 255) and np.all(check[-64:] == 255)
heights = [part.height for part, _ in parts.values()]
report['source_height_spread_fraction'] = (max(heights) - min(heights)) / max(heights)
(OUT / 'prep.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
with zipfile.ZipFile(OUT / 'kangaroo_four_white_views.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for name in report['views']:
        file = OUT / report['views'][name]['file']
        archive.write(file, arcname=file.name)
board = Image.new('RGB', (1024, 1024), 'white')
for name, xy in [('front', (0,0)), ('left', (512,0)), ('back', (0,512)), ('right', (512,512))]:
    panel = Image.open(OUT / f'kangaroo_{name}.png').resize((512,512), Image.Resampling.NEAREST)
    board.paste(panel, xy)
board.save(OUT / 'review.png')
print(json.dumps(report, indent=2))
