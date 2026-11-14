"""The gorilla's back hex plate, touched up in the hex shield's back views (Claude, animation lane, 2026-11-04).

Preston: "for backview activating shield the shield on the back dissapea4 for some frames needs touched up with
tools". In Codex set C's hex_shield ne row the grey hex bezel around the green back gem breaks: its top edge goes
dark or missing, and stray dark pixels sit above it.

Method: the plate (bezel greys, gem greens, and the dark ring they enclose) is cut from the approved still (frame 0).
In each frame the gem is found by matching the still's gem mask within SEARCH px of where it sits in the still, and
the still's plate is pasted there. Above the pasted plate's highest row, over its columns and CLEAR_SIDE past them, every pixel is cleared (the
still has nothing there), which removes the dark blob and the stray specks. Frames whose plate already matches the still at
KEEP or better are left alone. Originals are kept once in <frames>/../frames_pre_plate/.
Usage: python back_plate.py [--apply]   (without --apply it only measures and writes the board)
"""
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ANIM = Path(__file__).parent
JOBS = [(ANIM / "codex-set-c/hex_shield", "ne", 6), (ANIM / "codex-set-a/hex_shield", "back", 6)]
GEM = [(0x1b, 0x9a, 0x52), (0x3f, 0xe0, 0x7f), (0xd6, 0xff, 0xe6)]
BEZEL = [(0x4a, 0x49, 0x50), (0x8a, 0x8a, 0x93), (0xdf, 0xe2, 0xe9)]
SEARCH = 10
KEEP = 0.9
CLEAR_ABOVE = 6
RING = 7  # the bezel's silver cap sits 5-6 px above the gem
CLEAR_SIDE = 2  # also clear one or two columns past the plate's edge


def has(a, cols):
    return np.any([np.all(a[..., :3] == c, -1) for c in cols], 0) & (a[..., 3] > 0)


def plate_mask(a):
    """The back plate in the still: the gem component nearest the top of the body, its bezel, and the ring between."""
    gem = has(a, GEM)
    lab, n = ndimage.label(gem)
    top = min(range(1, n + 1), key=lambda k: np.nonzero(lab == k)[0].min())  # the back gem is the highest gem
    g = lab == top
    ring = ndimage.binary_dilation(g, np.ones((3, 3), bool), iterations=RING)  # square, so the cap corners count
    lab2, _ = ndimage.label(has(a, GEM + BEZEL) & ring)
    plate = np.isin(lab2, np.unique(lab2[g]))
    return ndimage.binary_fill_holes(plate), g


def shift(m, dx, dy):
    return np.roll(m, (dy, dx), (0, 1))


def locate(gem0, a):
    gem = has(a, GEM)
    best = max(((int((shift(gem0, dx, dy) & gem).sum()), dx, dy)
                for dy in range(-SEARCH, SEARCH + 1) for dx in range(-SEARCH, SEARCH + 1)))
    return best[1], best[2], best[0] / gem0.sum()


def fix(still, a):
    plate, gem0 = plate_mask(still)
    dx, dy, gem_hit = locate(gem0, a)
    p = shift(plate, dx, dy)
    src = np.roll(still, (dy, dx), (0, 1))
    match = float(np.all(a[p] == src[p], -1).mean())
    out = a.copy()
    out[p] = src[p]
    ys, xs = np.nonzero(p)
    # Clear the box above the plate's highest row (the cap), CLEAR_SIDE past its columns: the still has nothing
    # there, and in the broken frames it holds the dark blob and the specks. Rows level with the cap and below are
    # the frame's own body outline and stay.
    y0, x0, x1 = ys.min(), max(0, xs.min() - CLEAR_SIDE), xs.max() + CLEAR_SIDE + 1
    box = out[max(0, y0 - CLEAR_ABOVE):y0, x0:x1]
    cleared = int((box[..., 3] > 0).sum())
    box[...] = 0
    # Upper-left of the cap: the broken frames leave a dark band hugging the bezel's diagonal, where the still's
    # bezel is itself the silhouette. Dark pixels there, outside the plate, where the still is transparent, go.
    # (The right side is left alone: the dark run there is the frame's own shoulder outline.)
    xc = int(xs.mean())
    dark = has(out, [(0x14, 0x1a, 0x16), (0x22, 0x30, 0x1d)])
    zone = np.zeros_like(p)
    zone[y0:y0 + 6, max(0, xs.min() - 4):xc] = True
    band = zone & dark & ~p & (src[..., 3] == 0)
    out[band] = 0
    cleared += int(band.sum())
    # A pixel the clear left stranded (one opaque 4-neighbour or none) next to the plate goes too.
    near = ndimage.binary_dilation(p, np.ones((3, 3), bool), iterations=3) & ~p
    op = out[..., 3] > 0
    nbrs = sum(np.roll(op, d, ax) for d in (1, -1) for ax in (0, 1))
    lone = near & op & (nbrs <= 1)
    out[lone] = 0
    cleared += int(lone.sum())
    return out, dict(dx=dx, dy=dy, gem_hit=round(gem_hit, 3), match=round(match, 3), cleared=cleared)


def main():
    apply = "--apply" in sys.argv
    tiles = []
    for job, v, n in JOBS:
        frames = job / "frames"
        still = np.asarray(Image.open(frames / f"{v}_f0.png").convert("RGBA"))
        row = []
        for i in range(n):
            a = np.asarray(Image.open(frames / f"{v}_f{i}.png").convert("RGBA"))
            out, info = fix(still, a)
            todo = i > 0 and info["match"] < KEEP
            print(f"{job.parent.name}/{job.name} {v}_f{i}: {info} -> {'FIX' if todo else 'keep'}")
            row.append((a, out if todo else a))
            if todo and apply:
                keep = job / "frames_pre_plate"
                keep.mkdir(exist_ok=True)
                if not (keep / f"{v}_f{i}.png").exists():
                    shutil.copy(frames / f"{v}_f{i}.png", keep / f"{v}_f{i}.png")
                Image.fromarray(out).save(frames / f"{v}_f{i}.png")
        tiles.append(row)
    # board: per job, a before row and an after row of the upper body at 4x
    X0, Y0, W, H, Z = 52, 80, 88, 48, 4
    board = Image.new("RGBA", (6 * W * Z, 4 * H * Z), (88, 92, 84, 255))
    for j, row in enumerate(tiles):
        for k in (0, 1):
            for i, pair in enumerate(row):
                t = Image.fromarray(pair[k]).crop((X0, Y0, X0 + W, Y0 + H)).resize((W * Z, H * Z), Image.NEAREST)
                board.alpha_composite(t, (i * W * Z, (2 * j + k) * H * Z))
    board.save(ANIM / "back-plate-board.png")
    print("board: rows ne before, ne after, back before, back after;", "applied" if apply else "dry run")


if __name__ == "__main__":
    main()
