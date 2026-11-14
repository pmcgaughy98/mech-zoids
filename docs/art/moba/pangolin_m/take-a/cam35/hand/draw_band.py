"""Hand-drawn back band for the pangolin's 35-degree side view (Pangolin session, 2026-11-05).

Base: cam35/side2/e.png (Codex's second try: right length, far front foot raised, but the spine is still the
top outline). Target top outline: the 35-degree angle guide's side view (hull_guide.py, cut from the approved
outlines), smoothed. Between the old top (the spine ridge) and the new top, draw the far half of the back as rows
of new scale plates in the fixed palette. Nothing is cut and re-placed: every added pixel is drawn here.
Reads only; writes into OUTDIR (argv[1]).
Usage: python draw_band.py OUTDIR [scale_w row_h smooth]
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

M = Path("D:/dev/new-mech-rpg/docs/art/moba/pangolin_m/take-a")
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
SW = int(sys.argv[2]) if len(sys.argv) > 2 else 9      # scale width along the body
RH = int(sys.argv[3]) if len(sys.argv) > 3 else 5      # scale row height across the band
SM = int(sys.argv[4]) if len(sys.argv) > 4 else 9      # smoothing window for the new top outline

def hx(h): return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)] + [255], np.uint8)
HI, BASE, SH, DEEP = hx("fff09a"), hx("ffc61a"), hx("d0850a"), hx("7a4006")
ACC = hx("141218")
PAL = ["fff09a", "ffc61a", "d0850a", "7a4006", "5a5766", "3d3a44", "211e27", "e4e4ea", "a3a1ab", "5e5b66",
       "5ef2e6", "e8fffb", "141218"]

e = np.array(Image.open(M / "cam35/side2/e.png").convert("RGBA"))
op = e[..., 3] > 0
ys, xs = np.nonzero(op)
x0, x1, ybot = xs.min(), xs.max(), ys.max()
W = x1 - x0 + 1
top_e = np.array([np.nonzero(op[:, x])[0].min() for x in range(x0, x1 + 1)])

# --- the guide's side view at 35 degrees, back to 1x ---
g = np.array(Image.open(M / "cam35/refs/angle_guide.png").convert("RGB")).astype(int)
mag = (g[..., 0] > 200) & (g[..., 1] < 80) & (g[..., 2] > 200)
cols = np.nonzero((~mag).any(axis=0))[0]
runs, start = [], cols[0]
for a, b in zip(cols[:-1], cols[1:]):
    if b - a > 8:
        runs.append((start, a)); start = b
runs.append((start, cols[-1]))
c0, c1 = runs[2]                                         # s, se, e, ne, n -> the third is e
sub = ~mag[:, c0:c1 + 1]
r0 = np.nonzero(sub.any(axis=1))[0].min(); r1 = np.nonzero(sub.any(axis=1))[0].max()
hull = sub[r0:r1 + 1][2::4, 2::4]
hh, hw = hull.shape
top_h = np.array([np.nonzero(hull[:, j])[0].min() if hull[:, j].any() else hh for j in range(hw)])
# map guide columns onto the drawing's columns, bottom rows aligned on the feet row
jj = np.clip(np.round(np.arange(W) * (hw - 1) / max(W - 1, 1)).astype(int), 0, hw - 1)
target = (ybot - (hh - 1)) + top_h[jj]
k = np.ones(SM) / SM
target_s = np.round(np.convolve(np.pad(target, SM // 2, mode="edge"), k, mode="valid")).astype(int)
target_s = np.minimum(target_s, top_e)                  # never cut into the drawing
# taper: the band belongs to the arched back only, fading to nothing over the tail and the head
thick = (top_e - target_s).astype(float)
peak = int(np.argmin(top_e))                            # the arch: the run of high columns around the peak,
ARCH = int(sys.argv[7]) if len(sys.argv) > 7 else 12   # how far below the peak still counts as the back
ok = top_e <= top_e.min() + ARCH                        # so the separate tail tip on the left is left out
a0 = peak
while a0 > 0 and ok[a0 - 1]:
    a0 -= 1
a1 = peak
while a1 < W - 1 and ok[a1 + 1]:
    a1 += 1
RAMP = int(sys.argv[5]) if len(sys.argv) > 5 else 12
print(f"arch columns {a0}..{a1} of {W}")
env = np.zeros(W)
for i in range(W):
    if a0 <= i <= a1:
        env[i] = min(1.0, (i - a0 + 1) / RAMP, (a1 - i + 1) / RAMP)
TMAX = int(sys.argv[6]) if len(sys.argv) > 6 else 0
if TMAX:                                                # even band that follows the arch's own curve, eased ends
    s = env * env * (3 - 2 * env)
    thick = np.round(TMAX * s).astype(int)
else:
    thick = np.round(thick * env).astype(int)
target_s = top_e - thick

out = e.copy()
band = np.zeros(op.shape, bool)
added = 0
for i in range(W):
    x = x0 + i
    t0, t1 = target_s[i], top_e[i]                       # band rows t0 .. t1-1
    for y in range(t0, t1):
        d = y - t0
        r, v = d // RH, d % RH
        u = (x + (r % 2) * (SW // 2)) % SW
        edge = abs(v - RH // 2) // 3                     # rear edge slightly pointed toward the tail (left)
        uu = u - edge
        if y == t1 - 1:
            c = BASE                                     # no split line: the back reads as one surface
        elif uu == 0 and v == RH - 1:
            c = ACC                                      # one seam pixel at each plate's rear corner
        elif uu == 0 or v == RH - 1:
            c = SH                                       # rear edge and lower edge of each plate
        elif v <= 1 and 1 <= uu <= int(SW * 0.6) and not (r == 0 and v == 0):
            c = HI                                       # lit upper-left cap; the far-edge row a step darker
        else:
            c = BASE
        out[y, x] = c
        band[y, x] = True
        added += 1

# cleanup: an added pixel whose four neighbours all differ takes the commonest neighbour colour
def lone_mask(img, only=None):
    o = img[..., 3] > 0
    same = np.zeros(o.shape, int)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        sh = np.roll(np.roll(img, dy, 0), dx, 1)
        same += (np.all(sh == img, axis=2) & o)
    m = o & (same == 0)
    return m if only is None else m & only
base_lone = int(lone_mask(e).sum())
for _ in range(2):
    for y, x in zip(*np.nonzero(lone_mask(out, band))):
        nb = [tuple(out[y + dy, x + dx]) for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)) if out[y + dy, x + dx, 3] > 0]
        if nb:
            out[y, x] = max(set(nb), key=nb.count)
print(f"lone px in the base drawing {base_lone}; in the added band after cleanup {int(lone_mask(out, band).sum())}")
# holes: a see-through pixel the band closed in (PixelLab's score flagged one at row 125, column 83 in v5)
holes = ndimage.binary_fill_holes(out[..., 3] > 0) & ~(out[..., 3] > 0) & ~ndimage.binary_fill_holes(op)
for y, x in zip(*np.nonzero(holes)):
    nb = [tuple(out[y + dy, x + dx]) for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)) if out[y + dy, x + dx, 3] > 0]
    out[y, x] = max(set(nb), key=nb.count)
print(f"holes filled {int(holes.sum())}")

# --- score ---
op2 = out[..., 3] > 0
ys2, xs2 = np.nonzero(op2)
H2 = ys2.max() - ys2.min() + 1
def share(img, hexes):
    o = img[..., 3] > 0
    m = np.zeros(o.shape, bool)
    for h in hexes:
        m |= np.all(img[..., :3] == hx(h)[:3], axis=2)
    return 100 * (m & o).sum() / o.sum()
rgb = out[..., :3][op2]
pal = np.array([hx(h)[:3] for h in PAL])
off = int((~(rgb[:, None, :] == pal[None]).all(-1).any(1)).sum())
# lone pixels: opaque pixels whose four neighbours are all a different colour
q = out.astype(int); lone = 0
for y, x in zip(ys2, xs2):
    same = 0
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        yy, xx = y + dy, x + dx
        if 0 <= yy < 192 and 0 <= xx < 192 and q[yy, xx, 3] > 0 and (q[yy, xx] == q[y, x]).all():
            same += 1
    lone += same == 0
nbr = {v: share(np.array(Image.open(M / f"views_cam35/{v}.png").convert("RGBA")), ["fff09a"]) for v in ("se", "ne")}
print(f"guide e cell {hw}x{hh}; drawing {W} wide, old height {ybot - top_e.min() + 1}, new height {H2} (target 54, se 61, ne 60)")
print(f"band thickness min/median/max {int((top_e - target_s).min())}/{int(np.median(top_e - target_s))}/{int((top_e - target_s).max())}; added px {added}")
print(f"lightest yellow {share(out, ['fff09a']):.1f}% (old {share(e, ['fff09a']):.1f}%, se {nbr['se']:.1f}%, ne {nbr['ne']:.1f}%)")
print(f"accent {share(out, ['141218']):.2f}% (target 1.8); off-palette {off}; lone px {lone}; top row {ys2.min()}; border clear {ys2.min() > 0 and xs2.min() > 0 and xs2.max() < 191}")
Image.fromarray(out).save(OUT / "e.png")

# --- preview: approved e, side2 e, hand e, run-1 se and ne at 4x; then the turn s se e ne n at game size ---
def crop(p):
    im = Image.open(p).convert("RGBA") if not isinstance(p, Image.Image) else p
    return im.crop(im.getbbox())
row = [crop(M / "views/e.png"), crop(M / "cam35/side2/e.png"), crop(Image.fromarray(out)),
       crop(M / "views_cam35/se.png"), crop(M / "views_cam35/ne.png")]
K, G = 4, 24
wtot = sum(c.width * K for c in row) + G * (len(row) + 1)
htop = max(c.height for c in row) * K + 2 * G
turn = [crop(M / "views_cam35/s.png"), crop(M / "views_cam35/se.png"), crop(Image.fromarray(out)),
        crop(M / "views_cam35/ne.png"), crop(M / "views_cam35/n.png")]
K2 = 2
hbot = max(c.height for c in turn) * K2 + 2 * G
sheet = Image.new("RGBA", (wtot, htop + hbot), (92, 96, 84, 255))
x = G
for c in row:
    b = c.resize((c.width * K, c.height * K), Image.NEAREST)
    sheet.alpha_composite(b, (x, htop - G - b.height)); x += b.width + G
x = G
for c in turn:
    b = c.resize((c.width * K2, c.height * K2), Image.NEAREST)
    sheet.alpha_composite(b, (x, htop + hbot - G - b.height)); x += b.width + G
sheet.save(OUT / "preview.png")
print("preview", sheet.size)
