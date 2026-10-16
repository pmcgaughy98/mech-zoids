# Cut a creature out of a dark glowing background (ChatGPT references, 2026-10-13).
# Background = what the picture's border reaches through near-black pixels or smooth dim gradient (the glow).
# Flat creature colours next to the black outline have a hard edge there, so the fill stops at the outline.
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as nd
src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB"); a = np.asarray(im).astype(float) / 255
v = a.max(axis=2)
rng = nd.maximum_filter(v, 7) - nd.minimum_filter(v, 7)
passable = (v < 0.1) | ((v < 0.36) & (rng < 0.07))
lab, n = nd.label(passable)
border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
bg = np.isin(lab, border[border > 0])
mask = ~bg
mask = nd.binary_opening(mask, iterations=2)
mask = nd.binary_closing(mask, iterations=3)
mask = nd.binary_fill_holes(mask)
lab2, n2 = nd.label(mask)
if n2 > 1:
    sizes = nd.sum(mask, lab2, range(1, n2 + 1)); mask = lab2 == (1 + int(np.argmax(sizes)))
Image.fromarray(np.dstack([np.asarray(im), (mask * 255).astype(np.uint8)]), "RGBA").save(out)
print("mask", round(mask.mean(), 3))
