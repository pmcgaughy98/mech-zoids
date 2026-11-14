"""Measure the raw four-view concept without changing any image pixels."""
from pathlib import Path
import hashlib
import json
from collections import Counter

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent
path = ROOT / 'sheet_raw.png'
im = Image.open(path).convert('RGBA')
a = np.asarray(im)
rgb = a[:, :, :3].astype(np.int16)
key = ((rgb[:, :, 0] > 160) & (rgb[:, :, 2] > 160)
       & (rgb[:, :, 1] < 110)
       & (rgb[:, :, 0] > rgb[:, :, 1] * 1.5)
       & (rgb[:, :, 2] > rgb[:, :, 1] * 1.5))
solid = (a[:, :, 3] > 0) & ~key
views = {}
labels, _ = ndimage.label(solid, structure=np.ones((3, 3), dtype=bool))
counts = np.bincount(labels.ravel())
counts[0] = 0
objects = ndimage.find_objects(labels)
for component in np.argsort(counts)[-4:]:
    ys, xs = objects[component - 1]
    x0, x1, y0, y1 = xs.start, xs.stop, ys.start, ys.stop
    cy, cx = ndimage.center_of_mass(solid, labels, int(component))
    name = ('front' if cx < im.width / 2 else 'left') if cy < im.height / 2 else ('back' if cx < im.width / 2 else 'right')
    region = labels[y0:y1, x0:x1] == component
    yy, xx = np.nonzero(region)
    if not len(xx):
        raise ValueError(f'{name}: empty cell')
    box = [int(xx.min()), int(yy.min()), int(xx.max()) + 1, int(yy.max()) + 1]
    colours = Counter(map(tuple, rgb[y0:y1, x0:x1][region].tolist()))
    views[name] = {
        'component_box_in_sheet_xyxy': [x0, y0, x1, y1],
        'object_box_in_cell_xyxy': box,
        'width': box[2] - box[0], 'height': box[3] - box[1],
        'estimated_body_pixels': int(region.sum()),
        'raw_visible_rgb_count': len(colours),
        'top_16_rgb_share': sum(n for _, n in colours.most_common(16)) / len(xx),
        'touches_sheet_border': bool(x0 == 0 or y0 == 0 or x1 == im.width or y1 == im.height),
        'crosses_requested_vertical_cell_split': bool(x0 < im.width // 2 < x1),
    }
heights = [v['height'] for v in views.values()]
result = {
    'source': path.name,
    'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
    'image_size': list(im.size),
    'method': 'Four largest 8-connected components after magenta-family mask; no pixels changed.',
    'views': views,
    'height_spread_fraction': (max(heights) - min(heights)) / max(heights),
    'not_a_finished_sprite': True,
    'layout_issue': 'Profiles cross the requested equal-cell split. Crop components, not equal quadrants.',
    'limitations': ['Colour-key measurements approximate the silhouette.',
                   'Bounding boxes do not prove matching 3D anatomy or camera projection.',
                   'Actual generation token usage and monetary cost are not exposed.'],
}
(ROOT / 'reference_audit.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
