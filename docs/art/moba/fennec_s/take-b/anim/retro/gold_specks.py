"""Clears stray gold specks Retro left near the fennec's feet (Claude, animation lane, 2026-11-04).

In the staged Retro frames (frames/walk_*, kick_* except the still frames), a gold or cream island (#b8923a, #f0d27a,
#fff4d6) under 6 px that sits below row 140 and is not the tail tip is repainted with its most common non-gold
neighbour, or cleared where most neighbours are transparent. Usage: python gold_specks.py
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = Path(__file__).parent
GOLD = [(0xB8, 0x92, 0x3A), (0xF0, 0xD2, 0x7A), (0xFF, 0xF4, 0xD6)]

for p in sorted(HERE.glob("frames/*.png")):
    a = np.asarray(Image.open(p).convert("RGBA")).copy()
    gold = np.any([np.all(a[..., :3] == c, -1) for c in GOLD], 0) & (a[..., 3] > 0)
    lab, n = ndimage.label(gold)
    fixed = 0
    for i in range(1, n + 1):
        m = lab == i
        ys, xs = np.nonzero(m)
        if m.sum() >= 6 or ys.min() < 140:
            continue
        for y, x in zip(ys, xs):
            nb = [a[yy, xx] for yy in range(y - 1, y + 2) for xx in range(x - 1, x + 2)
                  if (yy, xx) != (y, x) and 0 <= yy < 192 and 0 <= xx < 192 and not gold[yy, xx]]
            op = [tuple(c) for c in nb if c[3] > 0]
            if len(op) * 2 < len(nb):
                a[y, x] = 0
            else:
                a[y, x] = max(set(op), key=op.count)
            fixed += 1
    if fixed:
        Image.fromarray(a).save(p)
        print(p.name, "gold speck px fixed", fixed)
