"""Free tool fixes for kangaroo cam35 take 2 (Preston: "Free fixes first", 2026-11-05).

1. Front (s) eyes: each eye is 1 px of eye glow with the dark accent socket pixel directly above it. The approved front
   eye is 2 px tall (one column, two rows), so the socket pixel above each eye becomes eye glow. The socket keeps its
   upper row of accent.
2. One despeckle pass on all five views (the four-neighbour rule from despeckle.py, eye and accent colours kept), so
   the five stay consistent through a turn.
Reads views/ (Codex's output, left untouched), writes fixed/ and fix-report.txt here.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROLES = {tuple(bytes.fromhex(c["hex"])): c["role"] for c in json.loads((HERE / "palette.json").read_text())}


def despeckle(a):
    """Copied from despeckle.py (which runs on sheet_finished.png when imported): one simultaneous pass, a pixel
    that differs from every same-role four-neighbour takes the most common such neighbour; eye and accent kept."""
    from collections import Counter
    h, w = a.shape[:2]
    out = a.copy()
    fixed = 0
    for y in range(h):
        for x in range(w):
            if a[y, x, 3] == 0 or tuple(a[y, x, :3]) in LENS:
                continue
            nbrs = [tuple(a[yy, xx]) for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
                    if 0 <= yy < h and 0 <= xx < w and a[yy, xx, 3] > 0]
            nbrs = [n for n in nbrs if ROLES.get(tuple(n[:3])) == ROLES.get(tuple(a[y, x, :3]))]
            if not nbrs:
                continue
            here = a[y, x, :3].astype(int)
            if any(np.abs(here - np.array(n[:3], int)).sum() < 30 for n in nbrs):
                continue
            out[y, x] = Counter(nbrs).most_common(1)[0][0]
            fixed += 1
    return out, fixed


VIEWS = ["s", "se", "e", "ne", "n"]
GLOW = (0x6F, 0xF0, 0xDC)
ACC = (0x14, 0x12, 0x18)
LENS = {(0x6F, 0xF0, 0xDC), (0xE8, 0xFF, 0xFB), ACC}


def eye_px(a):
    g = np.zeros(a.shape[:2], bool)
    for c in [(0x6F, 0xF0, 0xDC), (0xE8, 0xFF, 0xFB)]:
        g |= np.all(a[..., :3] == c, axis=2)
    return g & (a[..., 3] > 0)


def lone_share(a):
    """Share of opaque pixels (not eye or accent) with no same-colour four-neighbour."""
    op = a[..., 3] > 0
    rgb = a[..., :3].astype(np.int32)
    code = (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]
    same = np.zeros(op.shape, bool)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        sh = np.roll(np.roll(code, dy, 0), dx, 1)
        sho = np.roll(np.roll(op, dy, 0), dx, 1)
        same |= (sh == code) & sho
    keep = op.copy()
    for c in LENS:
        keep &= ~np.all(a[..., :3] == c, axis=2)
    return float((keep & ~same).sum() / keep.sum())


out_dir = HERE / "fixed"
out_dir.mkdir(exist_ok=True)
lines = []
for v in VIEWS:
    a = np.array(Image.open(HERE / "views" / f"{v}.png").convert("RGBA"))
    before_lone = lone_share(a)
    eyes_before = int(eye_px(a).sum())
    changed_eye = []
    if v == "s":
        ys, xs = np.nonzero(eye_px(a))
        for y, x in zip(ys.tolist(), xs.tolist()):
            if tuple(a[y - 1, x, :3]) == ACC and a[y - 1, x, 3] > 0:
                a[y - 1, x, :3] = GLOW
                changed_eye.append((y - 1, x))
        assert len(changed_eye) == 2, f"expected two socket pixels above the eyes, got {changed_eye}"
    a, n = despeckle(a)
    Image.fromarray(a).save(out_dir / f"{v}.png")
    lines.append(f"{v}: eye px {eyes_before} -> {int(eye_px(a).sum())}"
                 + (f" (socket px made eye glow at {changed_eye})" if changed_eye else "")
                 + f"; despeckle changed {n} px; lone share {before_lone:.3f} -> {lone_share(a):.3f}")
(HERE / "fix-report.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
