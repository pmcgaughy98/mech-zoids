"""Measure how a sprite is drawn, to compare ours with finished game sprites (Claude, 2026-10-12).

    python tools/art/sprite_quality.py <sprite.png> [more sprites]

Per sprite:
  colours      distinct colours
  cluster      mean size of same-colour connected regions (clean pixel art: big, even clusters)
  stray        share of pixels that match none of their four neighbours (speckle; clean art: low)
  light        brightness of top edges minus bottom edges (light from above)
  highlight    share of pixels in the brightest fifth of the sprite's own value range
  outline      share of edge pixels that are near-black
"""
import sys, colorsys
from collections import deque
import numpy as np
from PIL import Image


def measure(path):
    a = np.array(Image.open(path).convert("RGBA")).astype(int)
    if (a[..., 3] > 128).all():   # no transparency: treat the corner colour as background
        bg = (a[..., :3] == a[0, 0, :3]).all(2)
        a[bg, 3] = 0
    m = a[..., 3] > 128
    H, W = m.shape
    key = a[..., 0] * 65536 + a[..., 1] * 256 + a[..., 2]
    cols = len(set(key[m].tolist()))
    seen = np.zeros_like(m); sizes = []
    for y in range(H):
        for x in range(W):
            if m[y, x] and not seen[y, x]:
                q = deque([(y, x)]); seen[y, x] = True; n = 0
                while q:
                    cy, cx = q.popleft(); n += 1
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        yy, xx = cy + dy, cx + dx
                        if 0 <= yy < H and 0 <= xx < W and m[yy, xx] and not seen[yy, xx] and key[yy, xx] == key[cy, cx]:
                            seen[yy, xx] = True; q.append((yy, xx))
                sizes.append(n)
    stray = 0; edge = []; dark_edge = 0
    for y in range(H):
        for x in range(W):
            if not m[y, x]:
                continue
            nb = [(y + dy, x + dx) for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            inside = [(yy, xx) for yy, xx in nb if 0 <= yy < H and 0 <= xx < W and m[yy, xx]]
            if inside and all(key[yy, xx] != key[y, x] for yy, xx in inside):
                stray += 1
            if len(inside) < 4:
                edge.append((y, x))
                if a[y, x, :3].sum() < 120:
                    dark_edge += 1
    v = a[..., :3].max(2) / 255.0
    lo, hi = np.percentile(v[m], 2), np.percentile(v[m], 98)
    highlight = ((v > hi - (hi - lo) * 0.2) & m).sum() / m.sum()
    tops = [a[y, x, :3].sum() for y, x in edge if y == 0 or not m[y - 1, x]]
    bots = [a[y, x, :3].sum() for y, x in edge if y == H - 1 or not m[y + 1, x]]
    return dict(colours=cols, cluster=float(np.mean(sizes)), stray=stray / m.sum(),
                light=float(np.mean(tops) - np.mean(bots)) if tops and bots else 0.0,
                highlight=float(highlight), outline=dark_edge / max(len(edge), 1))


if __name__ == "__main__":
    print("%-34s %7s %8s %7s %7s %9s %8s" % ("sprite", "colours", "cluster", "stray", "light", "highlight", "outline"))
    for p in sys.argv[1:]:
        r = measure(p)
        print("%-34s %7d %8.1f %6.0f%% %7.0f %8.0f%% %7.0f%%" % (p.replace("\\", "/").split("/")[-1][:34], r["colours"],
              r["cluster"], 100 * r["stray"], r["light"], 100 * r["highlight"], 100 * r["outline"]))
