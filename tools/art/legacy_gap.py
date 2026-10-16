"""How far a sprite sits from Zoids Legacy's battle sprites on the measures that separated ours from theirs
(Claude, 2026-10-14; docs/reference/sprite-rules-legacy-2026-10-14-gap.md). The Legacy numbers are medians and
quartiles measured from 84 battle sprites on Preston's saved sheets; no Legacy art is read or stored here.
    python tools/art/legacy_gap.py <sprite.png> [...]
fill: body share of its bounding box; thin: share of body pixels within 2 px of an edge; L: brightness 0-255;
dark: share with L < 40; lit: share with L > 150. A star marks a value outside the Legacy quartiles."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

LEGACY = {"fill": (0.44, 0.51, 0.57), "thin": (0.20, 0.22, 0.27), "mean": (83, 96, 105), "L10": (32, 45, 54),
          "dark": (0.03, 0.08, 0.13), "lit": (0.07, 0.12, 0.19)}   # (p25, median, p75), measured 2026-10-14


def stats(path):
    a = np.array(Image.open(path).convert("RGBA")).astype(float)
    m = a[:, :, 3] > 128
    ys, xs = np.nonzero(m)
    m, a = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1], a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    L = (0.299 * a[:, :, 0] + 0.587 * a[:, :, 1] + 0.114 * a[:, :, 2])[m]
    return {"fill": m.sum() / m.size, "thin": (ndimage.distance_transform_edt(m)[m] <= 2).mean(), "mean": L.mean(),
            "L10": np.percentile(L, 10), "dark": (L < 40).mean(), "lit": (L > 150).mean()}


if __name__ == "__main__":
    print("%-44s" % "legacy median (quartiles)", "  ".join("%s %s (%s-%s)" % (k, v[1], v[0], v[2]) for k, v in LEGACY.items()))
    for p in sys.argv[1:]:
        r = stats(p)
        cells = []
        for k, (lo, med, hi) in LEGACY.items():
            t = ("%.0f" if k in ("mean", "L10") else "%.2f") % r[k]
            cells.append("%s %s%s" % (k, t, "" if lo <= r[k] <= hi else "*"))
        print("%-44s" % p[-44:], "  ".join(cells))
