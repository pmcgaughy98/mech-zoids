"""Free lens fix for the chameleon's 35-degree views (Chameleon session, Claude, 2026-11-06).
Preston: "Lens fix, then turn test". Codex drew the lenses about 30% small and without their glint in s, se and e.
This paints each lens back from the approved view of the same direction, the machine's own approved art:
- The approved lens pattern (amber ring, bright gold, glint) is shrunk top to bottom by cos 35 (0.82), since a lens
  facing sideways is seen from 35 degrees above.
- It goes where Codex drew the lens, with the two glow cores aligned.
- Lens pixels go only on opaque pixels, so the outline stays the same.
- Old lens pixels it doesn't cover take their most common non-lens neighbour's colour (most are jaw shadow or turret
  steel).
ne and n have no lens and are copied unchanged. views_cam35/ is left as Codex delivered it.
Run from docs/art/moba: python chameleon_m/take-b/cam35/fix_lenses.py
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

TAKE = Path("chameleon_m/take-b")
APPROVED, NEW, OUT = TAKE / "views", TAKE / "views_cam35", TAKE / "cam35/fixed"
RING, BRIGHT, GLINT = (0xC4, 0x62, 0x0A), (0xFF, 0xD8, 0x4A), (0xFF, 0xFB, 0xE6)
LENS = (RING, BRIGHT, GLINT)
SQUASH = math.cos(math.radians(35))


def lens_mask(a):
    m = np.zeros(a.shape[:2], bool)
    for c in LENS:
        m |= (a[..., :3] == c).all(2) & (a[..., 3] > 0)
    return m


def groups(a, min_px=5):
    """Lens groups, left to right: (mask, core centre) where the core is the bright and glint pixels."""
    lab, n = ndimage.label(lens_mask(a))
    out = []
    for i in range(1, n + 1):
        g = lab == i
        if g.sum() < min_px:
            continue
        core = g & ((a[..., :3] == BRIGHT).all(2) | (a[..., :3] == GLINT).all(2))
        ys, xs = np.where(core if core.any() else g)
        out.append((g, (ys.mean(), xs.mean())))
    return sorted(out, key=lambda t: np.where(t[0])[1].mean())


def pattern(a, g):
    """The approved lens as a small RGBA block, squashed top to bottom by cos 35, and its core centre."""
    ys, xs = np.where(g)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    blk = a[y0:y1, x0:x1].copy()
    blk[~g[y0:y1, x0:x1]] = 0
    h = blk.shape[0]
    nh = max(1, round(h * SQUASH))
    rows = [min(h - 1, int((i + 0.5) * h / nh)) for i in range(nh)]  # nearest rows, first and last kept
    rows[0], rows[-1] = 0, h - 1
    blk = blk[rows]
    core = (blk[..., :3] == BRIGHT).all(2) | (blk[..., :3] == GLINT).all(2)
    cy, cx = np.where(core)
    return blk, (cy.mean(), cx.mean())


def fill_left(a, left, m_lens):
    """Old lens pixels left uncovered take the most common opaque non-lens neighbour colour, working inwards."""
    left = left.copy()
    for _ in range(10):
        if not left.any():
            break
        done = []
        for y, x in zip(*np.where(left)):
            votes = {}
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if (dy or dx) and a[yy, xx, 3] > 0 and not m_lens[yy, xx] and not left[yy, xx]:
                        k = tuple(a[yy, xx, :3])
                        votes[k] = votes.get(k, 0) + 1
            if votes:
                a[y, x, :3] = max(votes, key=votes.get)
                done.append((y, x))
        for y, x in done:
            left[y, x] = False


def fix(view):
    ap = np.array(Image.open(APPROVED / f"{view}.png").convert("RGBA"))
    a = np.array(Image.open(NEW / f"{view}.png").convert("RGBA"))
    olds, refs = groups(a), groups(ap)
    if len(olds) != len(refs):
        raise SystemExit(f"{view}: {len(olds)} lenses drawn, {len(refs)} approved")
    report = []
    for (g_old, (oy, ox)), (g_ref, _) in zip(olds, refs):
        blk, (cy, cx) = pattern(ap, g_ref)
        ty, tx = round(oy - cy), round(ox - cx)
        new = np.zeros(a.shape[:2], bool)
        for y in range(blk.shape[0]):
            for x in range(blk.shape[1]):
                yy, xx = ty + y, tx + x
                if blk[y, x, 3] and a[yy, xx, 3] > 0:  # never past the outline
                    a[yy, xx] = blk[y, x]
                    new[yy, xx] = True
        fill_left(a, g_old & ~new, lens_mask(a) & new)
        report.append(f"{int(g_old.sum())} -> {int(new.sum())} (approved {int(g_ref.sum())})")
    lab, n = ndimage.label(lens_mask(a))  # a stray lens pixel or two left by the squash goes to its neighbours
    for i in range(1, n + 1):
        g = lab == i
        if g.sum() < 3:
            fill_left(a, g, lens_mask(a) & ~g)
    Image.fromarray(a).save(OUT / f"{view}.png")
    return report


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for v in ("s", "se", "e"):
        print(v, "; ".join(fix(v)))
    for v in ("ne", "n"):
        Image.open(NEW / f"{v}.png").save(OUT / f"{v}.png")
        print(v, "copied unchanged (no lens)")


if __name__ == "__main__":
    main()
