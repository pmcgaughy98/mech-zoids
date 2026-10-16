# Near-duplicate colours in installed sprites (Claude, 2026-10-12, after PixelLab's workbench scored every machine down
# for them): pairs of colours used in a sprite that sit closer than THRESH in RGB, with pixel counts, so a palette can
# merge them. Legacy-style sprites keep every shade a clear step apart.
#   python tools/art/near_duplicates.py [threshold] [machine_id ...]
import os, sys
from itertools import combinations
import numpy as np
from PIL import Image

THRESH = float(sys.argv[1]) if len(sys.argv) > 1 else 24.0
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "art", "machines")
ids = sys.argv[2:] or sorted(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d, "views")))
for m in ids:
    counts = {}
    for v in ("e", "se", "s", "sw", "w", "nw", "n", "ne"):
        p = os.path.join(root, m, "views", v + ".png")
        if not os.path.exists(p):
            continue
        a = np.array(Image.open(p).convert("RGBA")); px = a[a[..., 3] > 0][:, :3]
        for c, n in zip(*np.unique(px, axis=0, return_counts=True)):
            counts[tuple(int(x) for x in c)] = counts.get(tuple(int(x) for x in c), 0) + int(n)
    pairs = []
    for c1, c2 in combinations(sorted(counts), 2):
        d = float(np.linalg.norm(np.array(c1) - np.array(c2)))
        if d < THRESH:
            pairs.append((d, c1, c2))
    print("%s: %d colours, %d near-duplicate pairs (< %.0f)" % (m, len(counts), len(pairs), THRESH))
    for d, c1, c2 in sorted(pairs)[:12]:
        print("   %02x%02x%02x (%5d px)  %02x%02x%02x (%5d px)  dist %.1f" % (*c1, counts[c1], *c2, counts[c2], d))
