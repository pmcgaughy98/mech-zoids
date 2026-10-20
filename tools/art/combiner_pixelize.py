"""Quick pixelizer for the combination machine, v1 (Claude, 2026-10-19).

    python tools/art/combiner_pixelize.py <render.png> <out.png> [xSCALE]

The detail pixelizer works per machine palette, and the combiner carries six machines' colour families whose hue
bands overlap (the wolf's, kangaroo's and pangolin's reds; two blues) plus the gorilla's built-in green. Until a merged
palette exists, v1 takes the render down by area average (alpha by coverage, cut at half) and quantizes the opaque
pixels to 48 colours with median cut, then draws a one-shade-darker outline of each edge pixel's own colour.
"""
import sys
import numpy as np
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
k = float(sys.argv[3][1:]) if len(sys.argv) > 3 else 4.4
im = Image.open(src).convert("RGBA")
w, h = int(round(im.width / k)), int(round(im.height / k))
a = np.array(im).astype(float)
pre = a.copy(); pre[..., :3] *= a[..., 3:4] / 255.0   # premultiply so the background does not bleed into edges
small = np.array(Image.fromarray(pre.astype(np.uint8), "RGBA").resize((w, h), Image.BOX)).astype(float)
alpha = small[..., 3]
rgb = np.where(alpha[..., None] > 0, small[..., :3] * 255.0 / np.maximum(alpha[..., None], 1), 0)
solid = alpha >= 128
q = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), "RGB").quantize(48, method=Image.Quantize.MEDIANCUT)
out = np.zeros((h, w, 4), np.uint8)
out[..., :3] = np.array(q.convert("RGB")); out[..., 3] = np.where(solid, 255, 0)
edge = solid & ~(np.roll(solid, 1, 0) & np.roll(solid, -1, 0) & np.roll(solid, 1, 1) & np.roll(solid, -1, 1))
out[edge, :3] = (out[edge, :3].astype(float) * 0.62).astype(np.uint8)
ys, xs = solid.nonzero()
Image.fromarray(out, "RGBA").crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(dst)
print("%s: %dx%d px" % (dst, xs.max() - xs.min() + 1, ys.max() - ys.min() + 1))
