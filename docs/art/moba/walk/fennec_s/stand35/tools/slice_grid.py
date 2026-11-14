"""Slice a generated 3x3 direction sheet into the game's eight views, untouched (Claude, 2026-10-13).

Preston, 2026-10-13: the raw Nano Banana output is better than our finishing, so the pixels stay exactly as
generated; this only cuts and places. Grid sheets come back with each creature facing the centre (the way rotate
sheets do), so the cells map to directions by what they show:

    ne  n  nw
    e   .  w
    se  s  sw

Each creature is found as one connected shape (joined across 2-pixel gaps so a claw stays with its body); a shape
wider than a cell and a half is creatures standing close, cut at the emptiest columns near the cell lines. Each
view goes bottom-centred on the game's canvas.

    python tools/art/slice_grid.py <sheet.png> <out_dir> [--canvas 128] [--feet 104]
"""
import argparse
import os
from collections import deque
import numpy as np
from PIL import Image

CELLS = {(0, 0): "ne", (1, 0): "n", (2, 0): "nw", (0, 1): "e", (2, 1): "w", (0, 2): "se", (1, 2): "s", (2, 2): "sw"}


def shapes(m, join=2):
    H, W = m.shape
    grow = m.copy()
    for _ in range(join):
        g = grow.copy()
        g[1:] |= grow[:-1]; g[:-1] |= grow[1:]; g[:, 1:] |= grow[:, :-1]; g[:, :-1] |= grow[:, 1:]
        grow = g
    lab = np.full((H, W), -1)
    n = 0
    for y in range(H):
        for x in range(W):
            if grow[y, x] and lab[y, x] < 0:
                q = deque([(y, x)])
                lab[y, x] = n
                while q:
                    cy, cx = q.popleft()
                    for ny in (cy - 1, cy, cy + 1):
                        for nx in (cx - 1, cx, cx + 1):
                            if 0 <= ny < H and 0 <= nx < W and grow[ny, nx] and lab[ny, nx] < 0:
                                lab[ny, nx] = n
                                q.append((ny, nx))
                n += 1
    out = []
    for k in range(n):
        sel = (lab == k) & m
        if sel.sum() < 300:
            continue
        yy, xx = np.where(sel)
        if xx.max() - xx.min() > 1.5 * W / 3:
            cols = sel.sum(0)
            cuts = [int(c - 12 + np.argmin(cols[c - 12:c + 13])) for c in (W // 3, 2 * W // 3) if xx.min() < c < xx.max()]
            edges = [xx.min()] + cuts + [xx.max() + 1]
            for lo, hi in zip(edges[:-1], edges[1:]):
                part = sel.copy()
                part[:, :lo] = False
                part[:, hi:] = False
                out.append(part)
        else:
            out.append(sel)
    return sorted(out, key=lambda p: -int(p.sum()))[:8]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sheet")
    ap.add_argument("out")
    ap.add_argument("--canvas", type=int, default=128)
    ap.add_argument("--feet", type=int, default=104)
    a = ap.parse_args()
    img = np.array(Image.open(a.sheet).convert("RGBA"))
    m = img[..., 3] >= 128
    H, W = m.shape
    os.makedirs(a.out, exist_ok=True)
    got = []
    for sel in shapes(m):
        yy, xx = np.where(sel)
        d = CELLS.get((min(2, int(xx.mean() * 3 // W)), min(2, int(yy.mean() * 3 // H))), "centre")
        spr = np.zeros_like(img)
        spr[sel] = img[sel]
        spr[sel, 3] = 255
        spr = Image.fromarray(spr).crop((xx.min(), yy.min(), xx.max() + 1, yy.max() + 1))
        canvas = Image.new("RGBA", (a.canvas, a.canvas), (0, 0, 0, 0))
        canvas.alpha_composite(spr, (int(round(a.canvas / 2 - spr.width / 2)), a.feet + 1 - spr.height))
        canvas.save(os.path.join(a.out, d + ".png"))
        got.append(d)
    print("sliced %d views: %s" % (len(got), " ".join(sorted(got))))


if __name__ == "__main__":
    main()
