"""The fennec's idle in the five 35-degree views (fleet redraw lane, Claude, 2026-11-05).

Preston kept the touch-up of the fennec's cam35 views ("Keep", 2026-11-05) and said "Yes, pack it here". The idle is
the pose the fennec rests in, so it is built from those stills, by the rhino's cam35-idle method
(rhino_l/take-a/anim/cam35-idle/build_cam35_idle.py, from the playbook's diag_idle.py): the body rises 0, 1, 1, 1, 0 px
and the row at the cut is repeated to close the gap. Frame 0 is the still.

The stills are 160x160 with the feet on row 140; the game's cells are 192 with the feet on row 160, so each still is
placed at +16,+20, as pack_fennec_3d.py places them. Cut rows are in the 192 cell. Each view's cut sits above every
steel foot and the steel parts on the tail (found by colour on 2026-11-05), so nothing that stands on the ground lifts;
the body and the upper tail rise 1 px.

Writes frames/ (raw; the packer adds sel-out) with the packer's names: front, se, side, ne, back.
Reads ../../views_cam35_touchup only; writes only inside this folder. Prints a check.
"""
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
VIEWS = HERE.parents[1] / "views_cam35_touchup"
NAMES = [("s", "front"), ("se", "se"), ("e", "side"), ("ne", "ne"), ("n", "back")]
LIFT = [0, 1, 1, 1, 0]
CELL, AT, FEET = 192, (16, 20), 160
# In the 160 still: s 125, se 123, e 121, ne 118, n 123 (the highest steel foot or tail part starts one row lower).
CUT = {"s": 145, "se": 143, "e": 141, "ne": 138, "n": 143}


def breath(a, k, cut):
    if k == 0:
        return a.copy()
    out = a.copy()
    out[:cut - k] = a[k:cut]
    out[cut - k:cut] = a[cut - 1]
    return out


def main():
    (HERE / "frames").mkdir(exist_ok=True)
    lines = []
    for v, name in NAMES:
        canvas = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
        canvas.alpha_composite(Image.open(VIEWS / f"{v}.png").convert("RGBA"), AT)
        still = np.asarray(canvas).copy()
        cut = CUT[v]
        ys = np.nonzero(still[..., 3] > 0)[0]
        assert ys.max() == FEET, (v, ys.max())
        for i, k in enumerate(LIFT):
            f = breath(still, k, cut)
            assert (f[cut:] == still[cut:]).all(), f"{name} f{i}: rows from the cut down moved"
            Image.fromarray(f).save(HERE / "frames" / f"{name}_f{i}.png")
        lines.append(f"{name} ({v}): cut row {cut} ({FEET - cut} rows over the feet row), top row {ys.min()}, "
                     f"lowest row {ys.max()}, f0 is the still, rows {cut}-191 fixed in all frames")
    txt = "\n".join(lines)
    print(txt)
    (HERE / "build_check.txt").write_text(txt + "\n")


if __name__ == "__main__":
    main()
