"""Walk or gallop? For finished frames (frames128/ or a folder given with --dir), how many leg pixels change in the
viewer-left and viewer-right halves from each frame to the next (legs = the bottom 14 rows). A walk moves one
side then the other, so the two series alternate (correlation low or negative); a gallop or bound moves both
sides in the same frames (correlation high). Claude, 2026-11-04."""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).parent
args = sys.argv[1:]
src = HERE / "frames128"
if "--dir" in args:
    i = args.index("--dir")
    src = Path(args[i + 1])
    del args[i:i + 2]
for v in args or ("front", "back"):
    fr = [np.asarray(Image.open(p).convert("RGBA")) for p in sorted(src.glob(f"{v}_f[0-9].png"))]
    op = fr[0][..., 3] > 0
    ys, xs = np.where(op)
    floor, mid = ys.max(), (xs.min() + xs.max()) // 2
    zone = slice(floor - 14, floor + 1)
    L, R = [], []
    for i in range(len(fr)):
        a, b = fr[i][zone], fr[(i + 1) % len(fr)][zone]
        d = np.any(a != b, -1)
        L.append(int(d[:, :mid].sum()))
        R.append(int(d[:, mid:].sum()))
    c = np.corrcoef(L, R)[0, 1]
    verdict = "moves both sides together (gallop/bound)" if c > 0.5 else "alternates (walk)" if c < 0.2 else "mixed"
    print(f"{v}: left {L} right {R} corr {c:+.2f} -> {verdict}")
