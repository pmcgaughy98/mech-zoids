"""The fennec's front and back trot, posed by hand from the approved trot frame (Claude, animation lane, 2026-11-04).

Preston: "Yes, pose them", on the Codex front and back trot, whose legs barely move. PixelLab animate_with_skeleton_v3
was tried first on the front (job 6555b2ae, 3 free generations, skeleton.py): the legs alternate but the design is
lost (a generic fox with long thin legs, a grey ruff and no chest plate; alpha IoU 0.63 with the input). Not used;
the raw frames are in raw/.

Measured after that: the Codex front and back trot are not static. Each foot already lifts 2-4 px in the side trot's
rhythm (front: viewer's right foot up f0-f2, left f4-f7; back: right f1-f3, left f5-f7) with the knee bend drawn in,
so a hand pose of frame 0 (lifting 3-4 px) came out worse than Codex's own drawing. This script keeps the Codex frames
and amplifies their own lifts instead:
  - lift: in each frame, a leg whose foot is up U px (lowest opaque row 160 - U in its column band) gets its lower
    part (from row CUT down) moved up a further min(U, EXTRA_MAX) px when U >= 2, drawn over the upper leg, so the step reads
    about twice as high; the ground under it shows.
  - bob: on frames where a foot is up 2 px or more, the body above CUT rises BOB px; the row at CUT is repeated.
Originals go once to walk/frames_pre_pose/. Usage: python leg_pose.py [--apply]  (without --apply: board and gif only)
"""
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).parent
WALK = HERE.parent / "codex-set-a/walk"
KEEP = WALK / "frames_pre_pose"
CUT = 149  # just below the knee discs, in the 192 canvas
LEGS = {"front": {"L": (79, 93), "R": (100, 113)}, "back": {"L": (79, 91), "R": (103, 116)}}  # viewer's left/right columns
EXTRA_MAX = 3
BOB = 1
sys.path.insert(0, str(HERE.parents[3] / "rhino_l/take-a/anim"))


def foot_up(a, x0, x1):
    ys = np.nonzero((a[:, x0:x1, 3] > 0).any(1))[0]
    return 160 - int(ys.max())


def pose(a, view):
    out = a.copy()
    ups = {side: foot_up(a, *cols) for side, cols in LEGS[view].items()}
    if max(ups.values()) >= 2:  # body up BOB px, the row at CUT repeated under it
        out[:CUT - BOB] = a[BOB:CUT]
        out[CUT - BOB:CUT] = a[CUT - 1:CUT]
    for side, up in ups.items():
        k = min(up, EXTRA_MAX)
        if up < 2:  # a 1 px lift is a landing or take-off; Codex's frame is kept
            continue
        x0, x1 = LEGS[view][side]
        low = a[CUT:161, x0:x1].copy()
        m = low[..., 3] > 0
        region = out[:, x0:x1]
        region[CUT:161][m] = 0  # clear the leg's old lower part
        dst = region[CUT - k:161 - k]
        dst[m] = low[m]  # the lifted lower leg over the upper leg
    return out


def main():
    apply = "--apply" in sys.argv
    src = KEEP if KEEP.exists() else WALK / "frames"
    from selout_rhino import selout  # noqa: E402
    import selout_rhino
    selout_rhino.OUTLINE = np.array([0x14, 0x12, 0x18], np.uint8)
    rows, gif = [], []
    for view in ("front", "back"):
        old = [np.asarray(Image.open(src / f"{view}_f{i}.png").convert("RGBA")) for i in range(8)]
        new = [pose(a, view) for a in old]
        rows += [old, new]
        if apply:
            if not KEEP.exists():
                shutil.copytree(WALK / "frames", KEEP)
            for i, a in enumerate(new):
                Image.fromarray(a).save(WALK / "frames" / f"{view}_f{i}.png")
    # board: rows front before, front after, back before, back after (sel-out on, as the game shows it)
    box, z = (60, 60, 132, 164), 3
    w, h = (box[2] - box[0]) * z, (box[3] - box[1]) * z
    board = Image.new("RGBA", (8 * w, 4 * h), (0x3D, 0x43, 0x50, 255))
    tiles = [[Image.fromarray(selout(a)[0]).crop(box).resize((w, h), Image.NEAREST) for a in r] for r in rows]
    for r, row in enumerate(tiles):
        for c, t in enumerate(row):
            board.alpha_composite(t, (c * w, r * h))
    board.save(HERE / "leg-pose-board.png")
    # gif: before and after side by side, front then back, at the game's 10 fps
    frames = []
    for i in range(8):
        f = Image.new("RGBA", (4 * w, h), (0x3D, 0x43, 0x50, 255))
        for c, r in enumerate((0, 1, 2, 3)):
            f.alpha_composite(tiles[r][i], (c * w, 0))
        frames.append(f.convert("RGB"))
    frames[0].save(HERE / "leg-pose.gif", save_all=True, append_images=frames[1:], duration=100, loop=0)
    print("board leg-pose-board.png, gif leg-pose.gif;", "applied" if apply else "dry run")


if __name__ == "__main__":
    main()
