"""Detail ink: black interior lines between parts, baked per pixel (Claude, 2026-11-04).

Preston on the posed front walk: "simple fix for the shoulders would be the black outlines and detail on the
others. That model is just flat." The side and three-quarter walks carry dark interior lines between plates,
joints and body; the front (and the other PixelLab views) barely do.

The rule is the detail-ink mode of the Hollowtide sel-out shader (sel_out.gdshaderinc, detail_ink), which
selout_rhino.py left off for creatures. For an opaque pixel with luma L:
  boundary    = smoothstep(0.12, 0.23, brightest 4-neighbour luma - L) * (1 - smoothstep(0.36, 0.48, L))
  dark_joint  = 1 - smoothstep(0.13, 0.25, L)
  carved_seam = smoothstep(0.055, 0.13, across - L) * (1 - smoothstep(0.72, 0.86, L)),
                across = brightest of min(luma) over the four opposing neighbour pairs (n-s, e-w, ne-sw, nw-se)
The shader blends toward the outline colour by the largest of the three; baked sprites stay on the palette, so a
pixel becomes the outline colour #141218 when that value is 0.5 or more.

Measured first: the share of interior pixels (opaque, not on the silhouette edge) that are outline-coloured, per
view. Views whose share is under the lowest of the views Preston likes (se, side) get the ink pass.
Usage: python detail_ink.py <frames dir> [views...]   (writes in place; originals kept in <dir>/pre_ink/)
"""
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

OUTLINE = np.array([0x14, 0x12, 0x18], np.uint8)  # the rhino's darkest; other machines use their own (darkest())


def darkest(a):
    """The machine's own outline colour: its darkest opaque colour by luma (#141218 rhino, #141a16 gorilla).
    Fixed 2026-11-04 after the gorilla read 0% interior ink in every view against the rhino's colour."""
    cols = np.unique(a[a[..., 3] > 0][:, :3], axis=0)
    return cols[int(np.argmin(luma(cols)))].astype(np.uint8) if len(cols) else OUTLINE


def luma(rgb):
    return (rgb[..., :3].astype(np.float32) / 255.0) @ np.array([0.299, 0.587, 0.114], np.float32)


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def nb(a, dx, dy):
    """Neighbour at (x+dx, y+dy); transparent outside the canvas."""
    out = np.roll(a, (-dy, -dx), axis=(0, 1))  # out[y, x] = a[y + dy, x + dx]
    if dy > 0:
        out[-dy:] = 0
    if dy < 0:
        out[:-dy] = 0
    if dx > 0:
        out[:, -dx:] = 0
    if dx < 0:
        out[:, :-dx] = 0
    return out


def ink(a, mode="contour"):
    """mode 'full' is the shader rule; 'contour' (default, 2026-11-04) keeps only its boundary term on dark body
    pixels (luma under 0.3) beside a much brighter neighbour: a one-pixel line where body meets plate, matching
    the ink share of the se and side walks. 'full' measured 4-5x their share and blacked out the underbody."""
    op = a[..., 3] > 0
    L = luma(a)
    lum = {}
    for d in ((0, -1), (0, 1), (1, 0), (-1, 0), (1, -1), (-1, 1), (-1, -1), (1, 1)):
        n = nb(a, *d)
        lum[d] = luma(n) * (n[..., 3] > 0)
    brightest = np.maximum.reduce([lum[d] for d in ((0, -1), (0, 1), (1, 0), (-1, 0))])
    boundary = smooth(0.12, 0.23, brightest - L) * (1 - smooth(0.36, 0.48, L))
    dark_joint = 1 - smooth(0.13, 0.25, L)
    across = np.maximum.reduce([np.minimum(lum[p], lum[q]) for p, q in
                                (((0, -1), (0, 1)), ((1, 0), (-1, 0)), ((1, -1), (-1, 1)), ((-1, -1), (1, 1)))])
    seam = smooth(0.055, 0.13, across - L) * (1 - smooth(0.72, 0.86, L))
    if mode == "full":
        hit = op & (np.maximum.reduce([boundary, dark_joint, seam]) >= 0.5)
    else:
        hit = op & (boundary >= 0.5) & (L < 0.3)
    out = a.copy()
    dark = darkest(a)
    out[hit, :3] = dark
    return out, int((hit & np.any(a[..., :3] != dark, -1)).sum())


def interior_ink(a):
    op = a[..., 3] > 0
    edge = np.zeros_like(op)
    for d in ((0, -1), (0, 1), (1, 0), (-1, 0)):
        edge |= op & ~(nb(a, *d)[..., 3] > 0)
    inner = op & ~edge
    return float((inner & np.all(a[..., :3] == darkest(a), -1)).sum() / max(1, inner.sum()))


def main():
    run(Path(sys.argv[1]), sys.argv[2:])


def run(d, views=None):
    views = views or ["front", "se", "side", "ne", "back"]
    share = {v: np.mean([interior_ink(np.asarray(Image.open(d / f"{v}_f{i}.png").convert("RGBA")))
                         for i in range(8)]) for v in views}
    liked = [share[v] for v in ("se", "side") if v in share]
    target = min(liked) if liked else 0.0
    print("interior ink share before:", {v: round(s, 3) for v, s in share.items()}, "target", round(target, 3))
    keep = d / "pre_ink"
    keep.mkdir(exist_ok=True)
    for v in views:
        if v in ("se", "side") or share[v] >= target:
            continue
        added = []
        for i in range(8):
            p = d / f"{v}_f{i}.png"
            if not (keep / p.name).exists():
                shutil.copy(p, keep / p.name)
            out, n = ink(np.asarray(Image.open(keep / p.name).convert("RGBA")))
            Image.fromarray(out).save(p)
            added.append(n)
        after = np.mean([interior_ink(np.asarray(Image.open(d / f"{v}_f{i}.png").convert("RGBA"))) for i in range(8)])
        print(f"{v}: inked {min(added)}-{max(added)} px per frame, share {share[v]:.3f} -> {after:.3f}")


if __name__ == "__main__":
    main()
