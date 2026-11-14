"""Front and back walk rows with more motion, to sit beside the Retro side walk (Claude, 2026-11-04).

Preston: Retro's side walk is too fluid next to the stiff script front and back ("it wouldnt look right"), and
Retro itself gallops in those views. Built from the approved ground-pound frame 0 like frontback_8.py (same
four-beat timing taken from the Retro side), with four more motions:
- foot arc: a stepping foot peels 1 px the frame before it swings, then rises 3, 5, 2 px;
- weight shift: while one foot is up, the body slides 1 px toward the planted foot;
- shoulder roll: while a foot is 3 px or more up, the shoulder above it rises 1 px (outer columns only, so the
  head and horn do not tear);
- bob: body drops 1 px on the two frames with both visible feet down.
Legs keep their length (they move whole) and stay joined to the body (legs draw over the body's lower edge).
Writes walk8f/{front,side,back}_f0..f7.png (side copied from the Retro frames), board-walk8f.png, preview GIF.
"""
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = Path(__file__).parent
ANIM = HERE.parent
sys.path.insert(0, str(ANIM))
from selout_rhino import selout  # noqa: E402

GP = ANIM / "codex-ground-pound/clean/frames"
OUT = HERE / "walk8f"
LEG_TOP = {"front": 149, "back": 145}
ARC = (1, 3, 5, 2)  # frames start-1 .. start+2
# swing start per leg (rhino's own sides); right legs half a cycle after the left
START = {"LF": 1, "RF": 5, "LH": 3, "RH": 7}
# which half of the picture each visible leg is in
VIEW_LEGS = {"front": {"LF": "right", "RF": "left"}, "back": {"LH": "left", "RH": "right"}}
CORE = 16  # half-width of the head/horn band that never rolls


def lift(leg, i):
    for k, v in enumerate(ARC):
        if (START[leg] - 1 + k) % 8 == i:
            return v
    return 0


def shift(a, dx, dy):
    out = np.zeros_like(a)
    h, w = a.shape[:2]
    ys, xs = np.where(a[..., 3] > 0)
    ok = (ys + dy >= 0) & (ys + dy < h) & (xs + dx >= 0) & (xs + dx < w)
    out[ys[ok] + dy, xs[ok] + dx] = a[ys[ok], xs[ok]]
    return out


def build(base, view, i):
    lt = LEG_TOP[view]
    xs = np.where((base[..., 3] > 0).any(0))[0]
    cx = (xs.min() + xs.max()) // 2
    lifts = {VIEW_LEGS[view][k]: lift(k, i) for k in VIEW_LEGS[view]}
    up = [s for s, v in lifts.items() if v >= 2]
    bob = 1 if not up else 0
    sway = 0
    if up:  # body slides toward the planted side
        sway = -1 if up[0] == "right" else 1
    body = base.copy()
    body[lt:] = 0
    legs = base.copy()
    legs[:lt] = 0
    # shoulder roll before the slide, outer columns on the lifted side
    for side, v in lifts.items():
        if v >= 3:
            cols = np.zeros(192, bool)
            if side == "left":
                cols[:cx - CORE] = True
            else:
                cols[cx + CORE + 1:] = True
            part = body.copy()
            part[:, ~cols] = 0
            rest = body.copy()
            rest[:, cols] = 0
            part = shift(part, 0, -1)
            # fill the row the shoulder left behind at its lower edge with what was there
            body = rest
            m = part[..., 3] > 0
            body[m] = part[m]
    out = shift(body, sway, bob)
    for side in ("left", "right"):
        leg = legs.copy()
        if side == "left":
            leg[:, cx + 1:] = 0
        else:
            leg[:, :cx + 1] = 0
        leg = shift(leg, 0, -lifts.get(side, 0))
        m = leg[..., 3] > 0
        out[m] = leg[m]
    return out, lifts, sway, bob


def fill_new_holes(out, base):
    """The slide can leave a 1 px hole where body and leg meet (closed by the outline pass): fill enclosed
    single pixels whose four neighbours are all opaque, unless the base frame has a hole there too."""
    op, op0 = out[..., 3] > 0, base[..., 3] > 0
    hole = ndimage.binary_fill_holes(op) & ~op & ~(ndimage.binary_fill_holes(op0) & ~op0)
    for y, x in zip(*np.where(hole)):
        nb = [out[y + dy, x + dx] for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)) if out[y + dy, x + dx, 3]]
        if len(nb) == 4:
            out[y, x] = nb[0]
    return out


def main():
    OUT.mkdir(exist_ok=True)
    rows = {}
    for view in ("front", "back"):
        base = np.asarray(Image.open(GP / f"{view}_f0.png").convert("RGBA"))
        rows[view] = []
        for i in range(8):
            a, lifts, sway, bob = build(base, view, i)
            assert np.where(a[..., 3] > 0)[0].max() == 160, (view, i)
            a, _, _ = selout(a)
            a = fill_new_holes(a, selout(base)[0])
            Image.fromarray(a).save(OUT / f"{view}_f{i}.png")
            rows[view].append(a)
            print(f"{view} f{i}: lift {lifts} sway {sway:+d} bob {bob}")
    rows["side"] = []
    for i in range(8):
        shutil.copy(HERE / "frames" / f"side_f{i}.png", OUT / f"side_f{i}.png")
        rows["side"].append(np.asarray(Image.open(OUT / f"side_f{i}.png").convert("RGBA")))
    k, crop = 3, (24, 72, 168, 166)
    w, h = (crop[2] - crop[0]) * k, (crop[3] - crop[1]) * k
    order = ("front", "side", "back")
    board = Image.new("RGBA", (8 * w, 3 * h), (0x3D, 0x43, 0x50, 255))
    dr = ImageDraw.Draw(board)
    for j, v in enumerate(order):
        for i, a in enumerate(rows[v]):
            board.alpha_composite(Image.fromarray(a).crop(crop).resize((w, h), Image.NEAREST), (i * w, j * h))
            dr.text((i * w + 4, j * h + 2), f"{v} f{i}", fill=(235, 235, 240, 255))
    board.save(OUT / "board-walk8f.png")
    gifs = []
    for i in list(range(8)) * 3:
        g = Image.new("RGBA", (3 * w, h), (0x3D, 0x43, 0x50, 255))
        for j, v in enumerate(order):
            g.alpha_composite(Image.fromarray(rows[v][i]).crop(crop).resize((w, h), Image.NEAREST), (j * w, 0))
        gifs.append(g.convert("RGB"))
    gifs[0].save(OUT / "preview-walk8f.gif", save_all=True, append_images=gifs[1:], duration=125, loop=0)
    print("saved walk8f/")


if __name__ == "__main__":
    main()
