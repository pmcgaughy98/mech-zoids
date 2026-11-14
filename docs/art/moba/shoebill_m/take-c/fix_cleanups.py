"""Shoebill take C cleanups (Claude, 2026-11-03). Preston: "do the cleanups".

1. Far eye: the 3-pixel lens sliver past the bill root on se and sw becomes the helmet's blue shadow.
2. Back view: the bill's sides peek one pixel past the neck rings for four rows; those pixels go transparent.
3. Speckle: one pass over every view. A pixel with no 4-neighbour of a similar colour (sprite_director's lone rule,
   summed RGB difference under 30) takes the commonest colour among its opaque neighbours. Lens colours are kept.
Reads views/, writes fixed/. No new colours.

    python fix_cleanups.py        (from this folder)
"""
import os
from collections import Counter

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = os.path.join(HERE, "views"), os.path.join(HERE, "fixed")
LENS = {(0x1F, 0x9F, 0x95), (0x4F, 0xE3, 0xCF), (0xDC, 0xFF, 0xF8)}
BLUE_SHADOW = (0x3F, 0x5B, 0x92, 255)
GOLD = {(0xF2, 0xCF, 0x6A), (0xD1, 0xA2, 0x38), (0x9C, 0x70, 0x20), (0x5A, 0x3C, 0x0E)}
# Crop-local (x, y) of the far eye, read from the head pixel map: x from the bbox left, y from the bbox top.
FAR_EYE = {"sw": [(13, 8), (14, 8), (14, 9), (14, 10)], "se": [(41, 8), (41, 9), (41, 10)]}


def despeckle(a):
    h, w = a.shape[:2]
    out = a.copy()
    fixed = 0
    for y in range(h):
        for x in range(w):
            if a[y, x, 3] == 0 or tuple(a[y, x, :3]) in LENS:
                continue
            nbrs = [tuple(a[yy, xx]) for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
                    if 0 <= yy < h and 0 <= xx < w and a[yy, xx, 3] > 0]
            if not nbrs:
                continue
            here = a[y, x, :3].astype(int)
            if any(np.abs(here - np.array(n[:3], int)).sum() < 30 for n in nbrs):
                continue
            out[y, x] = Counter(nbrs).most_common(1)[0][0]
            fixed += 1
    return out, fixed


os.makedirs(OUT, exist_ok=True)
for name in ("n", "ne", "nw", "e", "w", "s", "se", "sw"):
    a = np.array(Image.open(os.path.join(SRC, name + ".png")).convert("RGBA"))
    ys, xs = np.nonzero(a[:, :, 3])
    y0, x0 = ys.min(), xs.min()
    notes = []
    for dx, dy in FAR_EYE.get(name, []):
        if tuple(a[y0 + dy, x0 + dx, :3]) in LENS:
            a[y0 + dy, x0 + dx] = BLUE_SHADOW
            notes.append("eye")
    if name == "n":
        for y in range(y0 + 15, y0 + 19):
            for x in (x0 + 14, x0 + 29):
                if tuple(a[y, x, :3]) in GOLD:
                    a[y, x, 3] = 0
                    notes.append("sliver")
    a, n = despeckle(a)
    Image.fromarray(a).save(os.path.join(OUT, name + ".png"))
    print("%-2s far-eye %d, slivers %d, speckle %d" % (name, notes.count("eye"), notes.count("sliver"), n))
