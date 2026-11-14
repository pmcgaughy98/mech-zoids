"""The rhino's idle in the five 35-degree views (rhino camera-angle lane, Claude, 2026-11-04).

Preston approved views_cam35 ("Thats it looks good") and then, through the hub, "Swap now". The idle is the pose the
rhino rests in, so it is built from the approved cam35 stills themselves, by the playbook's diag_idle.py method: the
body rises 0, 1, 1, 1, 0 px and the row at the cut is repeated to close the gap. Frame 0 is the still.

One change from diag_idle.py: the cut is set per view instead of a fixed 13 rows over the feet. From 35 degrees
the far feet sit higher on the page (up to about 30 rows in se and ne), so a fixed cut could lift a far foot.

Writes frames/ (raw) and frames_selout/ (sel-out, as the packer reads) with the packer's names: front, se, side,
ne, back. Reads ../../views_cam35_touchup only; writes only inside this folder. Prints a check.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ANIM = HERE.parent
# 2026-11-04: Preston kept the touch-up lane's recolour of the cam35 views ("Keep, game sel-out"); same alpha as
# views_cam35, colours only. The idle built from views_cam35 stays in frames_pre_touchup and frames_selout_pre_touchup.
VIEWS = ANIM.parent / "views_cam35_touchup"
sys.path.insert(0, str(ANIM))
from selout_rhino import selout  # noqa: E402

NAMES = [("s", "front"), ("se", "se"), ("e", "side"), ("ne", "ne"), ("n", "back")]
LIFT = [0, 1, 1, 1, 0]  # f0-f4 at 200 ms, as diag_idle.py
FEET = 160


def runs(row):
    r = np.diff(np.concatenate([[0], row.astype(int), [0]]))
    return int((r == 1).sum())


# Cut row per view, chosen on a marked strip of the lower bodies (2026-11-04). A run-count search alone mistook the
# horn, jaw and tail for gaps between legs. se and ne cut at 131 because a far foot sits between rows 131 and 140
# there; s, e and n cut through the knee discs as diag_idle.py does. Rows from the cut down never move.
CUT = {"s": 152, "se": 131, "e": 141, "ne": 131, "n": 142}


def find_cut(a, v):
    return CUT[v]


def breath(a, k, cut):
    if k == 0:
        return a.copy()
    out = a.copy()
    out[:cut - k] = a[k:cut]
    out[cut - k:cut] = a[cut - 1]
    return out


def main():
    (HERE / "frames").mkdir(exist_ok=True)
    (HERE / "frames_selout").mkdir(exist_ok=True)
    lines = []
    for v, name in NAMES:
        still = np.asarray(Image.open(VIEWS / f"{v}.png").convert("RGBA")).copy()
        cut = find_cut(still, v)
        ys = np.nonzero(still[..., 3] > 0)[0]
        for i, k in enumerate(LIFT):
            f = breath(still, k, cut)
            Image.fromarray(f).save(HERE / "frames" / f"{name}_f{i}.png")
            Image.fromarray(selout(f)[0]).save(HERE / "frames_selout" / f"{name}_f{i}.png")
            assert (f[cut:] == still[cut:]).all(), f"{name} f{i}: rows from the cut down moved"
        f0_same = (np.asarray(Image.open(HERE / "frames" / f"{name}_f0.png")) == still).all()
        lines.append(f"{name} ({v}): cut row {cut} ({FEET - cut} rows over the feet row), top row {ys.min()}, "
                     f"lowest row {ys.max()}, f0 identical to the still {f0_same}, rows {cut}-191 fixed in all frames")
    txt = "\n".join(lines)
    print(txt)
    (HERE / "build_check.txt").write_text(txt + "\n")


if __name__ == "__main__":
    main()
