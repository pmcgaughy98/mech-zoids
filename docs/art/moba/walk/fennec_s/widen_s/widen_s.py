"""Walk lane, 2026-11-05. Preston: "Widen front view front legs a bit as it looks like its still walking in the sitting
position". Pulls the s view's front legs apart (192 canvas), leaving the gold chest plate exactly in place:
- shift: none down to row 140, 1 px each side on rows 141-144, SHIFT px each side from row 145 down;
- rows where the chest plate (gold fff4d6/f0d27a/b8923a joined to the centre) shows: the plate and the pixel either side
  of it stay put; everything left of that moves left, right of it moves right, and the leg's own colour next to the plate
  (skipping seam lines) is repeated to fill (the leg tops widen toward the plate, the plate keeps its point);
- rows without plate: split at the centre (x <= 95 left, x >= 96 right); the gap between the legs stays open.
Feet sit below row 145, so each moves by a constant SHIFT and stays locked. Usage: python widen_s.py SHIFT in_dir out_dir"""
import sys, os, numpy as np
from PIL import Image
from scipy import ndimage
SHIFT = int(sys.argv[1]); src, dst = sys.argv[2], sys.argv[3]
os.makedirs(dst, exist_ok=True)
GOLD = [(0xff, 0xf4, 0xd6), (0xf0, 0xd2, 0x7a), (0xb8, 0x92, 0x3a)]
def shift_for(y):
    return 0 if y <= 140 else (min(1, SHIFT) if y <= 144 else SHIFT)
def plate_mask(a):
    g = np.zeros(a.shape[:2], bool)
    for c in GOLD:
        g |= (a[..., 0] == c[0]) & (a[..., 1] == c[1]) & (a[..., 2] == c[2]) & (a[..., 3] > 0)
    lab, n = ndimage.label(g, structure=np.ones((3, 3)))
    ids = {lab[y, x] for y in range(130, 150) for x in (94, 95, 96, 97) if lab[y, x]}
    return np.isin(lab, list(ids)) if ids else np.zeros_like(g)
DARK = {(0x14, 0x12, 0x18), (0x21, 0x1e, 0x27)}
def leg_colour(row, x, step):
    # first pixel outward from the plate that is not a seam or shadow line, so the fill is leg, not a dark smudge
    while 0 <= x < len(row) and row[x, 3] and tuple(row[x, :3]) in DARK:
        x += step
    return row[x] if 0 <= x < len(row) else row[x - step]
def widen(a):
    out = a.copy(); plate = plate_mask(a)
    for y in range(141, a.shape[0]):
        s = shift_for(y); row = a[y]; new = np.zeros_like(row)
        xs = np.nonzero(plate[y])[0]
        if len(xs):
            p0, p1 = xs.min() - 1, xs.max() + 1            # plate plus the pixel either side stays put
            new[p0:p1 + 1] = row[p0:p1 + 1]
            new[:p0 - s] = row[s:p0]                         # left part moves left
            new[p0 - s:p0] = leg_colour(row, p0 - 1, -1)     # repeat the leg's colour next to the plate
            new[p1 + 1 + s:] = row[p1 + 1:192 - s]           # right part moves right
            new[p1 + 1:p1 + 1 + s] = leg_colour(row, p1 + 1, +1)
        else:
            new[:96 - s] = row[s:96]
            new[96 + s:] = row[96:192 - s]
            if row[95, 3]: new[96 - s:96] = row[95]
            if row[96, 3]: new[96:96 + s] = row[96]
        out[y] = new
    return out
for f in sorted(os.listdir(src)):
    if f == 's.png' or (f.startswith('s_f') and f.endswith('.png')):
        a = np.array(Image.open(os.path.join(src, f)).convert('RGBA'))
        assert not a[:, :SHIFT, 3].any() and not a[:, 192 - SHIFT:, 3].any()
        Image.fromarray(widen(a)).save(os.path.join(dst, f)); print('widened', f)
