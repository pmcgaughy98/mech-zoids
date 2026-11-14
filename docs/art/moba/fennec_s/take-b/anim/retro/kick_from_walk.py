"""The fennec's back (n) and ne sand kick, built from on-model frames (Claude, animation lane, 2026-11-04).

Retro's custom_action sand kick failed in both views ($0.25 each, raw/kick_*_sheet.png): from frame 2 on it stands
the fennec on its hind legs, turns its cream chest to the camera and gives it clawed arms. Only its crouch frame held.
So the kick is built from the Retro walk's frame 0 (the standing fennec, design held) and the approved still:
  f0 still | f1 standing (walk f0) | f2 dig: head and ears down 3 px | f3 release: head up 2 px | f4 settle: head
  down 1 px | f5 still.  Timing stays [260, 130, 130, 90, 160, 280]; the sand itself is the game feel lane's effect.
The head is everything above CUT (the top 45% of the standing frame); lowering paints it over the body, raising
repeats the row at CUT under it. Writes frames/kick_<v>_f<i>.png (over the failed Retro ones) and zoom boards.
"""
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).parent
TAKE = HERE.parents[1]
HEAD_DY = {2: 3, 3: -2, 4: 1}


def still(v):
    c = np.zeros((192, 192, 4), np.uint8)
    c[20:180, 16:176] = np.asarray(Image.open(TAKE / "views" / f"{v}.png").convert("RGBA"))
    return c


def head_lift(a, k, cut):
    """Head up k px; the row at the cut repeats under it."""
    out = a.copy()
    out[:cut - k] = a[k:cut]
    out[cut - k:cut] = a[cut - 1]
    return out


def main():
    for v in ("n", "ne"):
        stand = np.asarray(Image.open(HERE / "frames" / f"walk_{v}_f0.png").convert("RGBA"))
        ys = np.nonzero((stand[..., 3] > 0).any(1))[0]
        cut = int(ys.min() + 0.45 * (ys.max() - ys.min()))
        frames = [still(v), stand]
        for i in (2, 3, 4):
            dy = HEAD_DY[i]
            if dy > 0:
                f = stand.copy()
                f[:cut] = 0
                f[cut:] = stand[cut:]
                head = np.zeros_like(stand)
                head[dy:cut + dy] = stand[:cut]
                m = head[..., 3] > 0
                f[m] = head[m]
                frames.append(f)
            else:
                frames.append(head_lift(stand, -dy, cut))
        frames.append(still(v))
        for i, f in enumerate(frames):
            Image.fromarray(f).save(HERE / "frames" / f"kick_{v}_f{i}.png")
        print(f"kick_{v}: cut row {cut}, bottoms {[int(np.nonzero((f[..., 3] > 0).any(1))[0].max()) for f in frames]}")


if __name__ == "__main__":
    main()
