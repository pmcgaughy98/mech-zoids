"""Front and back walk rows timed to the Retro side walk, 8 frames (Claude, 2026-11-04).

Preston on the Retro test: "front and back look like galloping rather than the walking gait for side view".
Retro moved both front legs (front view) and both hind legs (back view) together, which reads as a bound.
These rows are built from the approved ground-pound frame 0 with walk_frontback.build (legs keep their length,
body never comes apart from them), but with a four-beat walk taken from the Retro side row:
- side row, measured from its near (left-side) feet: the left front swings f1-f4, the left hind swings f3-f6;
  the right legs run half a cycle (4 frames) later.
- so one foot of a pair is up at a time, with both down between steps: front view LF up f1-f3, RF up f5-f7,
  both down f0 and f4; back view LH up f3-f5, RH up f7-f1, both down f2 and f6. Lift 2, 4, 2 px.
- body drops 1 px on the frames where the visible pair are both down (weight on two feet), level otherwise.
Writes walk8/{front,side,back}_f0..f7.png (side copied from frames/, already finished) plus a board and GIF.
"""
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).parent
ANIM = HERE.parent
sys.path.insert(0, str(ANIM))
from selout_rhino import selout  # noqa: E402
from walk_frontback import build  # noqa: E402

GP = ANIM / "codex-ground-pound/clean/frames"
OUT = HERE / "walk8"
SWING = (2, 4, 2)


def swing(start):
    """Frame -> lift for a foot that lifts for three frames starting at `start` (wraps round the 8)."""
    return {(start + k) % 8: SWING[k] for k in range(3)}


LF, RF, LH, RH = swing(1), swing(5), swing(3), swing(7)
VISIBLE = {"front": ("LF", "RF"), "back": ("LH", "RH")}


def plan(i):
    return {k: v.get(i, 0) for k, v in (("LF", LF), ("RF", RF), ("LH", LH), ("RH", RH)) if v.get(i, 0)}


def main():
    OUT.mkdir(exist_ok=True)
    rows = {}
    for view in ("front", "back"):
        base = np.asarray(Image.open(GP / f"{view}_f0.png").convert("RGBA"))
        rows[view] = []
        for i in range(8):
            lifts = plan(i)
            both_down = not any(lifts.get(k) for k in VISIBLE[view])
            a = build(base, view, 1 if both_down else 0, lifts)
            assert np.where(a[..., 3] > 0)[0].max() == 160, (view, i)
            a, _, _ = selout(a)
            Image.fromarray(a).save(OUT / f"{view}_f{i}.png")
            rows[view].append(a)
            print(view, i, {k: v for k, v in lifts.items() if k in VISIBLE[view]} or "both down, body down 1")
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
        gy = j * h + (161 - crop[1]) * k + k
        dr.line((0, gy, 8 * w, gy), fill=(120, 126, 140, 255))
    board.save(OUT / "board-walk8.png")
    gifs = []
    for i in list(range(8)) * 3:
        g = Image.new("RGBA", (3 * w, h), (0x3D, 0x43, 0x50, 255))
        for j, v in enumerate(order):
            g.alpha_composite(Image.fromarray(rows[v][i]).crop(crop).resize((w, h), Image.NEAREST), (j * w, 0))
        gifs.append(g.convert("RGB"))
    gifs[0].save(OUT / "preview-walk8.gif", save_all=True, append_images=gifs[1:], duration=125, loop=0)
    print("saved walk8/board-walk8.png and preview-walk8.gif")


if __name__ == "__main__":
    main()
