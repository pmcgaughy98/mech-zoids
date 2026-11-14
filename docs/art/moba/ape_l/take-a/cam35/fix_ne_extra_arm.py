"""Remove the extra arm from the gorilla's cam35 ne view (fleet redraw lane, Claude, 2026-11-04).

Preston, on the pilot board: "79x77 has extra arm in front. needs fixed get rid of with tools", then, after a first try
took out the far hind leg by mistake: "you removed the leg ... The extra arm is in front of head".
The extra arm is an orange forearm with a steel cap and two glow pixels rising above the near gauntlet, in front of where
the head is (texels x 101 to 112, rows 72 to 86 on the 160 canvas). The approved ne has nothing there. This works from
Codex's original (ne_codex_original.png), so the hind leg is untouched, and:
  - rows 72 to 86, x 101 and right: every orange, steel and glow pixel made transparent;
  - one-pixel gaps left inside the green shoulder (a removed pixel with opaque pixels left and right) filled with green
    shadow 47693a;
  - leftover specks with fewer than two opaque neighbours cleared;
  - any accent or steel-shadow pixel left on the new outer edge made deep green, so no dark line runs round the outside.
Only the 15 palette colours are used. slices/ keeps Codex's output.
"""
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
VIEW = HERE / "take1_views" / "ne.png"  # take 1 is kept here; views_cam35 now holds take 2
ORIG = HERE / "ne_codex_original.png"
if not ORIG.exists():
    ORIG.write_bytes(VIEW.read_bytes())
a = np.asarray(Image.open(ORIG).convert("RGBA")).copy()


def is_(arr, hexes):
    m = np.zeros(arr.shape[:2], bool)
    for h in hexes:
        m |= np.all(arr[..., :3] == tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)), axis=2)
    return m & (arr[..., 3] > 0)


orange = is_(a, ["f2ac5c", "d4853b", "9c5e28", "55331a"])
steel = is_(a, ["dfe2e9", "8a8a93", "4a4950"])
glow = is_(a, ["1b9a52", "3fe07f", "d6ffe6"])
Y, X = np.mgrid[:a.shape[0], :a.shape[1]]
zone = (Y >= 72) & (Y <= 86) & (X >= 101)
cut = zone & (orange | steel | glow)
before = int((a[..., 3] > 0).sum())
a[cut] = 0
op = a[..., 3] > 0
for y, x in zip(*np.nonzero(cut)):
    if op[y, x - 1] and op[y, x + 1]:
        a[y, x] = (0x47, 0x69, 0x3A, 255)
near = (Y >= 70) & (Y <= 88) & (X >= 99)
for _ in range(2):
    op = a[..., 3] > 0
    p = np.pad(op, 1)
    nb = p[:-2, 1:-1].astype(int) + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]
    a[op & near & (nb < 2)] = 0
op = a[..., 3] > 0
p = np.pad(op, 1)
outer = op & ~(p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:])
a[outer & near & is_(a, ["141a16", "4a4950"])] = (0x22, 0x30, 0x1D, 255)
Image.fromarray(a).save(VIEW)
op = a[..., 3] > 0
ys, xs = np.nonzero(op)
print(f"removed {before - int(op.sum())} px net; ne now {xs.max() - xs.min() + 1}x{ys.max() - ys.min() + 1}, "
      f"lowest row {ys.max()}, glow px left in rows 72-86 right of x 100: {int((is_(a, ['1b9a52', '3fe07f', 'd6ffe6']) & zone).sum())}")
