"""Gives the rhino's 35-degree walk the touch-up lane's colours (Claude, animation lane, 2026-11-04).

Why: the walk (walk35/) was drawn from views_cam35, but Preston kept the touch-up lane's recolour of those views
("Keep, game sel-out", views_cam35_touchup: same alpha, colours only) and the idle was rebuilt from it. So the walk
and the idle differed in colour in every view; the game feel lane saw the back plate flicker lighter at n when the
rhino started and stopped walking.

The touch-up is not a plain colour swap (4 of the 11 colours go to more than one new colour), so each walk pixel takes
its colour from the place it came from in the still:
  1. body pixels equal the still at the frame's body offset (0, or 1 px down on f0/f4): take the touch-up there;
  2. else a pixel equal to the still at the same place (legs at rest): take the touch-up there;
  3. else (moved legs, drawn joints): the nearest pixel of the same colour in the old still, and its touch-up colour.
Alpha is untouched. Backs up walk35/walk/frames to frames_pre_touchup once. Then run walk35_selout.py and repack.
Ran 2026-11-04: bodies equal the touch-up still in all 40 frames; packed. Preston on the legs board
(walk35/claude-touchup-legs.png): "Looks right".
"""
from pathlib import Path

import numpy as np
from PIL import Image

ANIM = Path(__file__).resolve().parent
TAKE = ANIM.parent
FR = ANIM / "walk35" / "walk" / "frames"
BACKUP = ANIM / "walk35" / "walk" / "frames_pre_touchup"
VIEWS = ("s", "se", "e", "ne", "n")


def load(p):
    return np.asarray(Image.open(p).convert("RGBA")).copy()


def body_dy(a, st, top=110):
    best = (-1, 0)
    for dy in (0, 1, 2):
        sh = np.zeros_like(st)
        sh[dy:] = st[:st.shape[0] - dy]
        m = (a[:top, :, 3] > 0) & (sh[:top, :, 3] > 0)
        n = int((a[:top][m] == sh[:top][m]).all(1).sum())
        best = max(best, (n, dy))
    return best[1]


def main():
    if not BACKUP.exists():
        BACKUP.mkdir()
        for p in FR.glob("*_f[0-7].png"):
            Image.open(p).save(BACKUP / p.name)
    stats = {"body": 0, "rest": 0, "nearest": 0, "nearest_ambiguous": 0}
    for v in VIEWS:
        st, tu = load(TAKE / "views_cam35" / f"{v}.png"), load(TAKE / "views_cam35_touchup" / f"{v}.png")
        op = st[..., 3] > 0
        amb = {}
        for o, n in zip(map(tuple, st[op][:, :3]), map(tuple, tu[op][:, :3])):
            amb.setdefault(o, set()).add(n)
        where = {c: np.argwhere(op & (st[..., :3] == c).all(2)) for c in amb}
        for i in range(8):
            a = load(BACKUP / f"{v}_f{i}.png")
            dy = body_dy(a, st)
            out = a.copy()
            for y, x in np.argwhere(a[..., 3] > 0):
                c = tuple(a[y, x, :3])
                hit = None
                for d, key in ((dy, "body"), (0, "rest")):
                    sy = y - d
                    if 0 <= sy < st.shape[0] and st[sy, x, 3] > 0 and tuple(st[sy, x, :3]) == c:
                        hit = (sy, x, key)
                        break
                if hit is None:
                    pts = where[c]
                    k = int(np.argmin(((pts - [y - dy, x]) ** 2).sum(1)))
                    hit = (pts[k][0], pts[k][1], "nearest")
                    stats["nearest_ambiguous"] += len(amb[c]) > 1
                out[y, x, :3] = tu[hit[0], hit[1], :3]
                stats[hit[2]] += 1
            Image.fromarray(out).save(FR / f"{v}_f{i}.png")
    print("pixels by rule:", stats)


if __name__ == "__main__":
    main()
