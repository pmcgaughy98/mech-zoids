"""Hippo sway, last step: straighten the ne belly edge beside the LH pad (walk_tools seams, 2026-11-05).
On the bob frames ne f1 and f2 the body drops 1 px, but next to the pinned LH pad the feather holds the belly back, so
its bottom edge on row 146 has dents beside the foot (open to the leg gap below). The approved still is solid there.
Each dent pixel takes the still's colour one row up (the still's belly edge, moved down by the 1 px bob). x 72-73 is
the still's own notch in the belly edge, carried down by the bob: kept. Judged at 8x; the other new slits (s f1/f5
jaw-gap edge, se f3 101,149, n f2 105,147) sit on real gaps and stay open (walk lane agrees).
Run after hippo_sway.py (it rewrites sway/).
"""
import numpy as np
from PIL import Image
from scipy.ndimage import binary_fill_holes, label
F = r"D:/dev/new-mech-rpg/docs/art/moba/walk/hippo_l/final"
A = lambda p: np.asarray(Image.open(p).convert("RGBA"))
st = A(F + "/stills/ne.png")
DENTS = {1: [(146, x) for x in range(57, 67)], 2: [(146, x) for x in range(55, 67)]}   # row 146, beside the LH pad
for i, pts in DENTS.items():
    p = f"sway/ne_f{i}.png"; a = A(p).copy(); done = []
    for y, x in pts:
        if a[y, x, 3] == 0 and a[y - 1, x, 3] and st[y - 1, x, 3]:
            a[y, x] = st[y - 1, x]
            done.append(x)
    m = a[..., 3] > 0
    assert label(m, np.ones((3, 3), int))[1] == 1 and not (binary_fill_holes(m) & ~m).any()
    Image.fromarray(a).save(p)
    print("ne f%d row 146 filled at x" % i, done, "colours", sorted({"%02x%02x%02x" % tuple(a[146, x, :3]) for x in done}))
