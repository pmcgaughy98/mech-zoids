"""Walk front and back rows built from the approved sprites (Claude, 2026-11-04).

Preston: "walking needs redone". Both Codex walks failed in the front and back rows (the first barely moved, the
second floated and shortened legs). The first walk's side row reads as a walk, so it stays; the front and back
rows are built here from the approved ground-pound frame 0 (eyes included), timed to that side row:
- body bob: everything above the legs moves with the side row's top edge (capped at 2 px); a gap under a raised
  body is filled by repeating the leg's top row, so legs never come apart from the body.
- leg lifts: the whole leg below the body moves up, so it keeps its length and draws over the body's lower edge.
  Front view shows the front legs (the rhino's left front is on the viewer's right); back view shows the hind
  legs (the rhino's left hind is on the viewer's left).
Lift plan per frame, matching the side row's measured foot lifts (f1 hind 2, f3 front 5, f4 front 2, f6 front 4):
  diagonal pair A = left front + right hind (f3 up, f4 coming down), pair B = right front + left hind (f6 up,
  f1 coming down), f2 and f5 all four feet down.
"""
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ANIM = Path(__file__).parent
GP = ANIM / "codex-ground-pound/clean/frames"
WALK = ANIM / "codex-set-a/walk"
LEG_TOP = {"front": 149, "back": 145}
# frame: {leg: lift px}; legs named by the rhino's own side
LIFT = {0: {}, 1: {"LH": 2}, 2: {}, 3: {"LF": 5, "RH": 4}, 4: {"LF": 2, "RH": 2}, 5: {}, 6: {"RF": 5, "LH": 4}}
VIEW_LEGS = {"front": {"LF": "right", "RF": "left"}, "back": {"LH": "left", "RH": "right"}}


def top_y(a):
    return np.where((a[..., 3] > 0).any(1))[0][0]


def build(base, view, bob, lifts):
    lt = LEG_TOP[view]
    out = np.zeros_like(base)
    body, legs = base.copy(), base.copy()
    body[lt:] = 0
    legs[:lt] = 0
    # body moves by bob (positive = down)
    if bob >= 0:
        out[bob:] = body[:192 - bob] if bob else body
    else:
        out[:bob] = body[-bob:]
    # legs: planted ones stay, lifted ones move up whole
    xs = np.arange(192)
    for side in ("left", "right"):
        cols = xs < 96 if side == "left" else xs >= 96
        leg = np.zeros_like(base)
        leg[:, cols] = legs[:, cols]
        lift = max([v for k, v in lifts.items() if VIEW_LEGS[view].get(k) == side] or [0])
        if lift:
            leg = np.roll(leg, -lift, axis=0)
        if bob < 0:  # body raised: repeat the leg's top row up into the gap so nothing comes apart
            row = leg[lt - lift].copy()
            for y in range(lt - lift + bob, lt - lift):
                fill = (row[..., 3] > 0) & (out[y, :, 3] == 0)
                out[y][fill] = row[fill]
        m = leg[..., 3] > 0
        out[m] = leg[m]
    return out


def main():
    side = [np.asarray(Image.open(WALK / "frames" / f"side_f{i}.png").convert("RGBA")) for i in range(7)]
    t0 = top_y(side[0])
    bobs = [int(np.clip(top_y(s) - t0, -2, 2)) for s in side]
    print("side top-edge bob per frame:", bobs)
    rows = {}
    for view in ("front", "back"):
        base = np.asarray(Image.open(GP / f"{view}_f0.png").convert("RGBA"))
        rows[view] = []
        for i in range(7):
            a = base.copy() if i == 0 else build(base, view, bobs[i], LIFT[i])
            assert np.where(a[..., 3] > 0)[0].max() == 160, (view, i)
            Image.fromarray(a).save(WALK / "frames" / f"{view}_f{i}.png")
            rows[view].append(a)
    # review: three rows at 3x on grey, ground line marked
    k, crop = 3, (40, 76, 152, 164)
    w, h = (crop[2] - crop[0]) * k, (crop[3] - crop[1]) * k
    board = Image.new("RGBA", (7 * w, 3 * h), (0x80, 0x80, 0x80, 255))
    dr = ImageDraw.Draw(board)
    for j, (v, frames) in enumerate((("front", rows["front"]), ("side", side), ("back", rows["back"]))):
        for i, a in enumerate(frames):
            c = (crop[0] - 16, crop[1], crop[2] + 16, crop[3]) if v == "side" else crop
            im = Image.fromarray(a).crop(c).resize((w, h), Image.NEAREST)
            board.alpha_composite(im, (i * w, j * h))
        dr.line((0, j * h + (160 - crop[1]) * k + k, 7 * w, j * h + (160 - crop[1]) * k + k), fill=(255, 255, 255, 255))
    board.save(WALK / "review-walk-v2.png")
    gifs = []
    for i in list(range(1, 7)) * 2:
        g = Image.new("RGBA", (3 * w, h), (0x3D, 0x43, 0x50, 255))
        for j, (v, frames) in enumerate((("front", rows["front"]), ("side", side), ("back", rows["back"]))):
            c = (crop[0] - 16, crop[1], crop[2] + 16, crop[3]) if v == "side" else crop
            g.alpha_composite(Image.fromarray(frames[i]).crop(c).resize((w, h), Image.NEAREST), (j * w, 0))
        gifs.append(g.convert("RGB"))
    gifs[0].save(WALK / "preview-walk-v2.gif", save_all=True, append_images=gifs[1:], duration=130, loop=0)
    print("saved review-walk-v2.png and preview-walk-v2.gif")


if __name__ == "__main__":
    main()
