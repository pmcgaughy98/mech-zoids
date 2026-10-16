# Where two outlines differ, column by column and row by row (2026-10-13, wolf pass 3: the part scores could not say
# where; this can). Prints, at evenly spaced fractions across each sprite's box, the top and bottom edge (fraction
# of the height) and how full the column is, for the reference and ours; then the same for rows (left and right).
#   python tools/art/column_profile.py <ours.png> <reference.png> [n]
import os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shadow_strip


def mask(p, ours):
    im = Image.open(p).convert("RGBA")
    im = shadow_strip.strip(im) if ours else im.crop(im.getchannel("A").getbbox())
    return np.array(im)[:, :, 3] > 128


def prof(m, axis, n):
    h, w = m.shape
    out = []
    for f in np.linspace(0.02, 0.98, n):
        line = m[:, int(f * (w - 1))] if axis == 0 else m[int(f * (h - 1)), :]
        idx = np.flatnonzero(line)
        size = h if axis == 0 else w
        out.append("%.2f-%.2f %3d%%" % (idx[0] / size, idx[-1] / size, 100 * line.mean()) if len(idx) else "   empty    ")
    return out


ours, ref = mask(sys.argv[1], True), mask(sys.argv[2], False)
n = int(sys.argv[3]) if len(sys.argv) > 3 else 11
print("w/h ours %.2f ref %.2f" % (ours.shape[1] / ours.shape[0], ref.shape[1] / ref.shape[0]))
print("columns (x across)  top-bottom fill:   ref            ours")
for f, a, b in zip(np.linspace(0.02, 0.98, n), prof(ref, 0, n), prof(ours, 0, n)):
    print("  x %.2f   %s   %s" % (f, a, b))
print("rows (y down)       left-right fill:   ref            ours")
for f, a, b in zip(np.linspace(0.02, 0.98, n), prof(ref, 1, n), prof(ours, 1, n)):
    print("  y %.2f   %s   %s" % (f, a, b))
