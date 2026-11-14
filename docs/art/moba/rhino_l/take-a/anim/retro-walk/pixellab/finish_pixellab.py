"""Finish the PixelLab pose-guided walk frames like finish_retro.py (Claude, 2026-11-04), with one difference:
no grounding. PixelLab kept the body exactly where the input has it (top row 41 in every frame); the feet move
up and down because a foot stepping toward the camera sits lower on screen, so the frames keep their place.
Usage: python finish_pixellab.py front   (reads pixellab/{view}_skel_0..7.png)
Writes pixellab/frames128/ and pixellab/frames/ (192 canvas, same offset as the Retro frames).
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent.parent))
from finish_retro import GP, snap, eye_groups, place_eyes  # noqa: E402
from selout_rhino import selout  # noqa: E402

for v in sys.argv[1:]:
    inp = np.asarray(Image.open(HERE.parent / "input" / f"{v}_128.png").convert("RGBA"))
    groups = eye_groups(inp)
    gp_path = GP / f"{v}_f0.png"
    if gp_path.exists():
        gp = np.asarray(Image.open(gp_path).convert("RGBA"))
    else:  # diagonals have no ground-pound frames: the approved still view, outlined, is where the input was cut from
        view = HERE.parent.parent.parent / "views" / f"{v}.png"
        gp = selout(np.asarray(Image.open(view).convert("RGBA")))[0]
    gy, gx = [w.min() for w in np.where(gp[..., 3] > 0)]
    iy, ix = [w.min() for w in np.where(inp[..., 3] > 0)]
    dx, dy = gx - ix, gy - iy
    (HERE / "frames128").mkdir(exist_ok=True)
    (HERE / "frames").mkdir(exist_ok=True)
    for i in range(8):
        f = np.asarray(Image.open(HERE / f"{v}_skel_{i}.png").convert("RGBA")).copy()
        f[..., 3] = np.where(f[..., 3] > 127, 255, 0)
        f = snap(f)
        moves = place_eyes(f, snap(inp), groups) if groups else []
        f, added, _ = selout(f)
        Image.fromarray(f).save(HERE / "frames128" / f"{v}_f{i}.png")
        big = np.zeros((192, 192, 4), np.uint8)
        ys, xs = np.where(f[..., 3] > 0)
        big[ys + dy, xs + dx] = f[ys, xs]
        Image.fromarray(big).save(HERE / "frames" / f"{v}_f{i}.png")
        print(f"{v}_f{i}: eyes {moves}, outline added {added}, top {ys.min() + dy}, bottom {ys.max() + dy}")
