"""Shape-aware angle guide and angle measure, cut from a machine's own approved views (fleet redraw lane, Claude, 2026-11-04).

Why: the elliptic guide (minion_s/take-a/cam35/angle_guide.py) is a flat-topped tub. It fit the drone, which is tub-shaped,
but the rhino's drawing did not move with it, and its height ratio cannot tell angle from shape. This builds a rough solid
from the approved silhouettes instead (a "visual hull": the s outline pushed back along the length, the e outline pushed
across the width, keep what is inside both, trimmed by the se outline), so the guide has the machine's own hump, low head,
limbs and gaps.

Two uses:
  guide    python hull_guide.py guide VIEWS_DIR OUT.png [pitch_low pitch_high]
           Two rows of five (s, se, e, ne, n) on magenta at 4x: top row the solid at the reference camera (6 degrees),
           bottom row at the game camera (35). Top surfaces light, the front green, sides grey, four flat bands.
           Prints each view's size in texels at both pitches.
  measure  python hull_guide.py measure VIEWS_DIR DRAWN_DIR [DRAWN_DIR ...]
           For each drawn view, the pitch (0 to 70 degrees) at which the solid's outline best matches the drawn outline
           (intersection over union after lining up the lowest row and the centre), and the pitch at which the solid's
           height first reaches the drawn height. Information only: the eye and the in-game turn are the gate.
The solid is never shown as a design: it is grey and blocky and the prompt says so.
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

VIEWS = ["s", "se", "e", "ne", "n"]
HEAD = {"s": 180, "se": 135, "e": 90, "ne": 45, "n": 0}  # compass heading the machine faces; the camera is south
R2 = math.sqrt(0.5)


def mask(p):
    a = np.asarray(Image.open(p).convert("RGBA"))[..., 3] > 0
    ys, xs = np.nonzero(a)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def build_hull(vdir):
    vdir = Path(vdir)
    s, e, se, ne = (mask(vdir / f"{v}.png") for v in ("s", "e", "se", "ne"))
    Z = max(m.shape[0] for m in (s, e, se, ne))
    pad = lambda m: np.vstack([np.zeros((Z - m.shape[0], m.shape[1]), bool), m])[::-1]  # row 0 = ground
    s, e, se, ne = pad(s), pad(e), pad(se), pad(ne)
    Fn, Ln = e.shape[1], s.shape[1]
    # hull[f, l, z]: f forward (e view: right is the front), l the machine's left (s view: right is its left), z up
    hull = e.T[:, None, :] & s.T[None, :, :]
    f = np.arange(Fn)[:, None] - (Fn - 1) / 2
    l = np.arange(Ln)[None, :] - (Ln - 1) / 2
    # trim with the diagonal outlines: se screen x = (f + l) / sqrt 2, ne screen x = (f - l) / sqrt 2, both centred
    for m, sx in ((se, (f + l) * R2), (ne, (f - l) * R2)):
        md = ndimage.binary_dilation(m, iterations=1)
        col = np.round(sx + (m.shape[1] - 1) / 2).astype(int)
        ok = (col >= 0) & (col < m.shape[1])
        hull &= md.T[np.clip(col, 0, m.shape[1] - 1)] & ok[..., None]  # (F, L, Z)
    return hull


def project(hull, view, pitch, sub=3):
    soft = ndimage.gaussian_filter(hull.astype(np.float32), 2.2)  # wide, so the silhouette terraces do not shade as stripes
    gf, gl, gz = np.gradient(soft)
    surf = hull & ~ndimage.binary_erosion(hull)
    fi, li, zi = np.nonzero(surf)
    off = (np.arange(sub) + 0.5) / sub - 0.5
    of, ol, oz = (o.ravel() for o in np.meshgrid(off, off, off, indexing="ij"))
    fF = (fi[:, None] - (hull.shape[0] - 1) / 2 + of[None]).ravel()
    lL = (li[:, None] - (hull.shape[1] - 1) / 2 + ol[None]).ravel()
    zz = (zi[:, None] + 0.5 + oz[None]).ravel()
    h, p = math.radians(HEAD[view]), math.radians(pitch)
    Fv = np.array([math.sin(h), math.cos(h)])
    Lv = np.array([-math.cos(h), math.sin(h)])
    east = fF * Fv[0] + lL * Lv[0]
    north = fF * Fv[1] + lL * Lv[1]
    y = zz * math.cos(p) + north * math.sin(p)
    depth = -north * math.cos(p) + zz * math.sin(p)
    n_f, n_l, n_z = -gf[fi, li, zi], -gl[fi, li, zi], -gz[fi, li, zi]
    nn = np.sqrt(n_f ** 2 + n_l ** 2 + n_z ** 2) + 1e-6
    rep = lambda a: np.repeat(a, sub ** 3)
    fwd = rep(fi >= 0.62 * hull.shape[0])  # the front third of the length: only it may be tinted as the front
    return east, y, depth, rep(n_f / nn), rep(n_l / nn), rep(n_z / nn), Fv, Lv, p, fwd


def raster(hull, view, pitch, K=1):
    x, y, depth, n_f, n_l, n_z, Fv, Lv, p, fwd = project(hull, view, pitch)
    px = np.floor((x - x.min()) * K).astype(int)
    py = np.floor((y.max() - y) * K).astype(int)
    Wd, Ht = px.max() + 1, py.max() + 1
    idx = py * Wd + px
    order = np.lexsort((-depth, idx))
    first = np.ones(len(order), bool)
    first[1:] = idx[order][1:] != idx[order][:-1]
    win = order[first]
    m = np.zeros(Ht * Wd, bool)
    m[idx[win]] = True
    m = m.reshape(Ht, Wd)
    m = m | (ndimage.binary_closing(np.pad(m, 1), iterations=1)[1:-1, 1:-1])
    return m, (idx, win, n_f, n_l, n_z, Fv, Lv, p, Wd, Ht, fwd)


def shade(hull, view, pitch, K=1):
    m, (idx, win, n_f, n_l, n_z, Fv, Lv, p, Wd, Ht, fwd) = raster(hull, view, pitch, K)
    img = np.zeros((Ht * Wd, 3), np.int32)
    img[:] = (255, 0, 255)
    nf, nl, nz = n_f[win], n_l[win], n_z[win]
    ne_ = nf * Fv[0] + nl * Lv[0]
    nn_ = nf * Fv[1] + nl * Lv[1]
    light = np.clip(-0.55 * ne_ + 0.25 * nn_ + 0.8 * nz, 0, 1)  # light from the upper left
    band = np.round((0.35 + 0.65 * light) * 3) / 3  # four flat bands
    g = (96 + 110 * band).astype(int)
    col = np.stack([g, g, g + 6], 1)
    top = nz > 0.6
    col[top] = np.stack([g[top] + 24, g[top] + 24, g[top] + 30], 1)
    front = (nf > 0.6) & ~top & fwd[win]
    col[front] = np.stack([g[front] - 40, g[front] + 20, g[front] - 50], 1)
    img[idx[win]] = col
    img = np.clip(img.reshape(Ht, Wd, 3), 0, 255).astype(np.uint8)
    img[~m] = (255, 0, 255)
    hole = m & np.all(img == (255, 0, 255), axis=2)
    if hole.any():
        _, (iy, ix) = ndimage.distance_transform_edt(hole | ~m, return_indices=True)
        img[hole] = img[iy[hole], ix[hole]]
    return img, m


def size(m):
    ys, xs = np.nonzero(m)
    return int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)


def guide(vdir, out, lo=6.0, hi=35.0):
    hull = build_hull(vdir)
    K, PAD, GAP = 4, 24, 48
    rows, sizes = [], {}
    for pitch in (lo, hi):
        panels = []
        for v in VIEWS:
            img, m = shade(hull, v, pitch)
            sizes[(pitch, v)] = size(m)
            panels.append(Image.fromarray(img).resize((img.shape[1] * K, img.shape[0] * K), Image.NEAREST))
        rows.append(panels)
    colw = [max(rows[0][i].width, rows[1][i].width) for i in range(5)]
    rowh = [max(p.height for p in r) for r in rows]
    sheet = Image.new("RGB", (sum(colw) + GAP * 4 + 2 * PAD, sum(rowh) + GAP + 2 * PAD), (255, 0, 255))
    yb = PAD
    for r, panels in enumerate(rows):
        x = PAD
        for i, pnl in enumerate(panels):
            sheet.paste(pnl, (x + (colw[i] - pnl.width) // 2, yb + rowh[r] - pnl.height))
            x += colw[i] + GAP
        yb += rowh[r] + GAP
    sheet.save(out)
    print("hull", hull.shape, "(long, wide, high texels)")
    for pitch in (lo, hi):
        print(f"hull guide at {pitch:g} deg (W x H texels):",
              ", ".join(f"{v} {sizes[(pitch, v)][0]}x{sizes[(pitch, v)][1]}" for v in VIEWS))


def measure(vdir, drawn_dirs):
    hull = build_hull(vdir)
    pitches = list(range(0, 71))
    cache = {v: [raster(hull, v, p)[0] for p in pitches] for v in VIEWS}
    print(f"hull from {vdir}: {hull.shape} (long, wide, high texels)")
    for d in drawn_dirs:
        res = []
        for v in VIEWS:
            dm = mask(Path(d) / f"{v}.png")
            best, bp, hp = -1, None, None
            for p, hm in zip(pitches, cache[v]):
                ys, xs = np.nonzero(hm)
                hm = hm[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
                H = max(hm.shape[0], dm.shape[0]); W = max(hm.shape[1], dm.shape[1]) + 2
                A = np.zeros((H, W), bool); B = np.zeros((H, W), bool)
                a0, b0 = (W - hm.shape[1]) // 2, (W - dm.shape[1]) // 2
                A[H - hm.shape[0]:, a0:a0 + hm.shape[1]] = hm
                B[H - dm.shape[0]:, b0:b0 + dm.shape[1]] = dm
                iou = (A & B).sum() / (A | B).sum()
                if iou > best:
                    best, bp = iou, p
                if hp is None and hm.shape[0] >= dm.shape[0]:
                    hp = p
            res.append(f"{v:>2} {dm.shape[1]:>3}x{dm.shape[0]:<3} fit {bp:>2} deg (IoU {best:.2f})  height-match {hp if hp is not None else '>70'}")
        print(f"  {d}:\n    " + "\n    ".join(res))


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "guide":
        guide(sys.argv[2], sys.argv[3], *(float(a) for a in sys.argv[4:]))
    elif mode == "measure":
        measure(sys.argv[2], sys.argv[3:])
    else:
        sys.exit(__doc__)
