# Extract a reference creature from a ChatGPT PNG (2026-10-13). The creature is the solid pixels (alpha >= CUT);
# glow and fringe are partly transparent and are dropped. Largest piece kept, holes filled, alpha made binary.
#   python tools/art/extract_alpha_ref.py <src> <out> [cut]
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as nd
src, out = sys.argv[1], sys.argv[2]
cut = int(sys.argv[3]) if len(sys.argv) > 3 else 200
im = np.asarray(Image.open(src).convert("RGBA")).copy()
mask = im[:, :, 3] >= cut
lab, n = nd.label(mask)
if n > 1:
    sizes = nd.sum(mask, lab, range(1, n + 1))
    big = sizes.max()
    mask = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s >= big * 0.02])   # the body plus any detached part over 2% of it
mask = nd.binary_fill_holes(mask)
im[:, :, 3] = np.where(mask, 255, 0)
Image.fromarray(im, "RGBA").save(out)
print("%s: %d pieces, kept %.3f of the canvas" % (out, n, mask.mean()))
